import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

export default function AlertsScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const [alerts, setAlerts] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState<number | null>(null);

    useEffect(() => {
        loadAlerts();
    }, []);

    const loadAlerts = async () => {
        try {
            const data = await apiService.getActiveAlerts();
            setAlerts(data);
        } catch (error) {
            console.error("Failed to load alerts", error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAcknowledgeAlert = async (id: number) => {
        try {
            setActionLoading(id);
            await apiService.acknowledgeAlert(id);
            await loadAlerts(); // Refresh list
            Alert.alert("Succès", "Alerte acquittée avec succès");
        } catch (error) {
            console.error("Failed to acknowledge alert", error);
            Alert.alert("Erreur", "Impossible d'acquitter l'alerte");
        } finally {
            setActionLoading(null);
        }
    };

    const handleResolveAlert = async (id: number) => {
        try {
            setActionLoading(id);
            await apiService.resolveAlert(id);
            await loadAlerts(); // Refresh list
            Alert.alert("Succès", "Alerte résolue avec succès");
        } catch (error) {
            console.error("Failed to resolve alert", error);
            Alert.alert("Erreur", "Impossible de résoudre l'alerte");
        } finally {
            setActionLoading(null);
        }
    };

    if (isLoading) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }]}>
                <ActivityIndicator size="large" color={theme.primary} />
            </View>
        );
    }

    return (
        <ImageBackground
            source={require('@/assets/images/bg.png')}
            style={styles.backgroundImage}
            blurRadius={10}
        >
            <SafeAreaView style={styles.container}>
                <StatusBar style="light" />
                <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>

                    <View style={styles.header}>
                        <Text style={styles.title}>Alertes & Risques</Text>
                        <Text style={styles.subtitle}>Réagissez rapidement aux goulots détectés</Text>
                    </View>

                    <View style={styles.list}>
                        {alerts.length === 0 ? (
                            <Text style={{ color: 'rgba(255,255,255,0.4)', textAlign: 'center', marginTop: 40 }}>Aucune alerte active</Text>
                        ) : (
                            alerts.map((alert, index) => (
                                <GlassView key={alert.id} intensity={50} borderRadius={24} style={styles.alertCard}>
                                    <View style={styles.alertHeader}>
                                        <View style={[styles.badge, { backgroundColor: alert.niveau_gravite === 'CRITICAL' ? theme.error : theme.warning }]}>
                                            <Text style={styles.badgeText}>{alert.niveau_gravite}</Text>
                                        </View>
                                        <Text style={styles.timeText}>{new Date(alert.genere_le).toLocaleTimeString()}</Text>
                                    </View>

                                    <View style={styles.content}>
                                        <Text style={styles.serviceName}>{alert.service_nom}</Text>
                                        <Text style={styles.riskTitle}>{alert.message}</Text>
                                    </View>

                                    <View style={styles.actions}>
                                        <TouchableOpacity
                                            style={[styles.primaryButton, { backgroundColor: theme.primary, flex: 1 }]}
                                            onPress={() => handleAcknowledgeAlert(alert.id)}
                                            disabled={actionLoading === alert.id}
                                        >
                                            {actionLoading === alert.id ? (
                                                <ActivityIndicator color="#fff" size="small" />
                                            ) : (
                                                <>
                                                    <Text style={styles.buttonText}>Marquer Traité</Text>
                                                    <Ionicons name="checkmark-circle" size={18} color="#fff" style={{ marginLeft: 6 }} />
                                                </>
                                            )}
                                        </TouchableOpacity>
                                    </View>
                                </GlassView>
                            ))
                        )}
                    </View>

                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    backgroundImage: { flex: 1 },
    container: { flex: 1 },
    scrollContent: { padding: 20 },
    header: { marginBottom: 24, marginTop: 10 },
    title: { color: '#fff', fontSize: 26, fontWeight: '800' },
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 14, marginTop: 4 },
    list: { gap: 16 },
    alertCard: { padding: 20 },
    alertHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
    badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
    badgeText: { color: '#fff', fontSize: 10, fontWeight: '800' },
    timeText: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
    content: { marginBottom: 20 },
    serviceName: { color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: '600', textTransform: 'uppercase' },
    riskTitle: { color: '#fff', fontSize: 20, fontWeight: '700', marginTop: 4 },
    freqRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 8 },
    freqText: { color: 'rgba(255,255,255,0.4)', fontSize: 14 },
    actions: { flexDirection: 'row', gap: 12 },
    primaryButton: { flex: 1, height: 48, borderRadius: 14, flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
    secondaryButton: { flex: 0.4, height: 48, borderRadius: 14, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)', alignItems: 'center', justifyContent: 'center' },
    buttonText: { color: '#fff', fontSize: 14, fontWeight: '700' }
});
