import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import { apiClient } from '@/services/api';

export default function IncidentsScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const [incidents, setIncidents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadIncidents();
    }, []);

    const loadIncidents = async () => {
        try {
            const data = await apiClient.get('/evenements/');
            setIncidents(data.data);
        } catch (error) {
            console.error("Failed to load incidents", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
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
                        <TouchableOpacity onPress={() => console.log('back')} style={styles.backButton}>
                            <Ionicons name="chevron-back" size={24} color="#fff" />
                        </TouchableOpacity>
                        <View>
                            <Text style={styles.title}>Incidents & Retards</Text>
                            <Text style={styles.subtitle}>Historique complet des micro-événements</Text>
                        </View>
                    </View>

                    <View style={styles.filterContainer}>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 10 }}>
                            {['Tous', 'Critiques', 'Aujourd\'hui', 'Ce mois'].map((f) => (
                                <GlassView key={f} intensity={30} borderRadius={12} style={styles.filterChip}>
                                    <Text style={styles.filterText}>{f}</Text>
                                </GlassView>
                            ))}
                        </ScrollView>
                    </View>

                    <View style={styles.list}>
                        {incidents.map((item) => (
                            <GlassView key={item.id} intensity={40} borderRadius={20} style={styles.listItem}>
                                <View style={styles.listHeader}>
                                    <Text style={styles.dateText}>{new Date(item.horodatage).toLocaleString('fr-FR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</Text>
                                    <View style={[styles.gravityBadge, { backgroundColor: getGravityColor(item.niveau_gravite, theme) }]}>
                                        <Text style={styles.gravityText}>{item.niveau_gravite}</Text>
                                    </View>
                                </View>

                                <View style={styles.listBody}>
                                    <View>
                                        <Text style={styles.serviceName}>{item.service_nom || 'Service'}</Text>
                                        <Text style={styles.incidentType}>{item.flux_nom || 'Événement'}</Text>
                                    </View>
                                    <View style={styles.durationBox}>
                                        <Ionicons name="information-circle-outline" size={16} color="rgba(255,255,255,0.4)" />
                                        <Text style={styles.durationText}>{item.description?.substring(0, 15)}...</Text>
                                    </View>
                                </View>
                            </GlassView>
                        ))}
                    </View>

                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

function getGravityColor(gravity: string, theme: any) {
    switch (gravity) {
        case 'CRITICAL': return theme.error;
        case 'WARNING': return theme.warning;
        default: return theme.success;
    }
}

const styles = StyleSheet.create({
    backgroundImage: { flex: 1 },
    container: { flex: 1 },
    scrollContent: { padding: 20 },
    header: { flexDirection: 'row', alignItems: 'center', marginBottom: 24, marginTop: 10, gap: 12 },
    backButton: { width: 40, height: 40, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.1)', alignItems: 'center', justifyContent: 'center' },
    title: { color: '#fff', fontSize: 24, fontWeight: '800' },
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 13 },
    filterContainer: { marginBottom: 20 },
    filterChip: { paddingHorizontal: 16, paddingVertical: 8 },
    filterText: { color: '#fff', fontSize: 13, fontWeight: '600' },
    list: { gap: 12 },
    listItem: { padding: 16 },
    listHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
    dateText: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
    gravityBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 6 },
    gravityText: { color: '#fff', fontSize: 9, fontWeight: '800' },
    listBody: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end' },
    serviceName: { color: 'rgba(255,255,255,0.6)', fontSize: 12, fontWeight: '700', textTransform: 'uppercase' },
    incidentType: { color: '#fff', fontSize: 18, fontWeight: '700', marginTop: 2 },
    durationBox: { flexDirection: 'row', alignItems: 'center', gap: 4 },
    durationText: { color: 'rgba(255,255,255,0.8)', fontSize: 14, fontWeight: '600' }
});
