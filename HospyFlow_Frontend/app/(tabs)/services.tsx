import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

export default function ServicesScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const [services, setServices] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadServices();
    }, []);

    const loadServices = async () => {
        try {
            const data = await apiService.getServices();
            setServices(data);
        } catch (error) {
            console.error("Failed to load services", error);
        } finally {
            setIsLoading(false);
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
                        <Text style={styles.title}>Services Hospitaliers</Text>
                        <Text style={styles.subtitle}>Comparaison des performances en temps réel</Text>
                    </View>

                    <View style={styles.grid}>
                        {services.map((service, index) => (
                            <TouchableOpacity key={service.id} style={styles.gridItem}>
                                <GlassView intensity={40} borderRadius={24} style={styles.card}>
                                    <View style={[styles.indicator, { backgroundColor: service.etat === 'TENSION' ? theme.error : theme.success }]} />
                                    <Text style={styles.serviceName}>{service.nom}</Text>

                                    <View style={styles.statRow}>
                                        <Ionicons name="time-outline" size={16} color="rgba(255,255,255,0.6)" />
                                        <Text style={styles.statText}>Attente: --</Text>
                                    </View>

                                    <View style={styles.statRow}>
                                        <Ionicons name="warning-outline" size={16} color="rgba(255,255,255,0.6)" />
                                        <Text style={styles.statText}>État: {service.etat}</Text>
                                    </View>

                                    <View style={styles.trendRow}>
                                        <Ionicons
                                            name={service.etat === 'TENSION' ? 'trending-up' : 'trending-down'}
                                            size={20}
                                            color={service.etat === 'TENSION' ? theme.error : theme.success}
                                        />
                                        <Text style={[
                                            styles.trendText,
                                            { color: service.etat === 'TENSION' ? theme.error : theme.success }
                                        ]}>
                                            {service.etat === 'TENSION' ? 'Tension' : 'Normal'}
                                        </Text>
                                    </View>
                                </GlassView>
                            </TouchableOpacity>
                        ))}
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
    grid: { flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -8 },
    gridItem: { width: '50%', padding: 8 },
    card: { padding: 20, height: 180, justifyContent: 'space-between' },
    indicator: { width: 30, height: 4, borderRadius: 2, marginBottom: 8 },
    serviceName: { color: '#fff', fontSize: 18, fontWeight: '700' },
    statRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 4 },
    statText: { color: 'rgba(255,255,255,0.8)', fontSize: 13, fontWeight: '500' },
    trendRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 10 },
    trendText: { fontSize: 12, fontWeight: '700' }
});
