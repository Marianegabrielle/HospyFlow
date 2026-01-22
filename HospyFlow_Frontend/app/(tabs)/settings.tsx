import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, Switch, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

export default function SettingsScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];
    const [isExporting, setIsExporting] = useState(false);

    const handleExport = async (format: 'pdf' | 'csv') => {
        setIsExporting(true);
        try {
            await apiService.generateRapport({
                plage_date: `Semaine ${new Date().toLocaleDateString()}`,
                donnees_metriques: {
                    'Incidents': 12,
                    'Taux Surcharge': '15%',
                    'Top Service': 'Urgences'
                },
                format: format
            });
            Alert.alert("Succès", `Rapport ${format.toUpperCase()} généré avec succès dans le dossier media du serveur.`);
        } catch (error) {
            console.error("Export error", error);
            Alert.alert("Erreur", "Impossible de générer le rapport");
        } finally {
            setIsExporting(false);
        }
    };

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
                        <Text style={styles.title}>Paramètres</Text>
                        <Text style={styles.subtitle}>Configuration du système ClinicFlow</Text>
                    </View>

                    <SettingSection title="Notifications & Alertes">
                        <SettingItem icon="notifications-outline" label="Push Alertes critiques" value={true} />
                        <SettingItem icon="mail-outline" label="Rapports par email" value={false} />
                    </SettingSection>

                    <SettingSection title="Génération de Rapports (Strategy Pattern)">
                        {isExporting ? (
                            <View style={{ padding: 20, alignItems: 'center' }}>
                                <ActivityIndicator color={theme.primary} />
                                <Text style={{ color: '#fff', marginTop: 10 }}>Génération en cours...</Text>
                            </View>
                        ) : (
                            <>
                                <TouchableOpacity onPress={() => handleExport('pdf')}>
                                    <SettingItem
                                        icon="document-text-outline"
                                        label="Exporter en PDF Premium"
                                        subLabel="Génère un PDF stylisé"
                                        iconColor={theme.primary}
                                    />
                                </TouchableOpacity>
                                <TouchableOpacity onPress={() => handleExport('csv')}>
                                    <SettingItem
                                        icon="grid-outline"
                                        label="Exporter en CSV (Excel)"
                                        subLabel="Données brutes pour analyse"
                                        iconColor={theme.success}
                                    />
                                </TouchableOpacity>
                            </>
                        )}
                    </SettingSection>

                    <SettingSection title="Système">
                        <SettingItem icon="cloud-upload-outline" label="Synchronisation Auto" value={true} />
                        <SettingItem icon="shield-checkmark-outline" label="Sécurité RBAC" subLabel="Activée" />
                    </SettingSection>

                    <View style={styles.footer}>
                        <Text style={styles.versionText}>ClinicFlow Analytics v1.0.4</Text>
                        <Text style={styles.legalText}>© 2026 Innovative Health Solutions</Text>
                    </View>

                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

function SettingSection({ title, children }: any) {
    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>{title}</Text>
            <GlassView intensity={40} borderRadius={24} style={styles.sectionCard}>
                {children}
            </GlassView>
        </View>
    );
}

function SettingItem({ icon, label, subLabel, value, iconColor }: any) {
    return (
        <View style={styles.settingItem}>
            <View style={[styles.iconBox, { backgroundColor: (iconColor || '#fff') + '10' }]}>
                <Ionicons name={icon} size={20} color={iconColor || 'rgba(255,255,255,0.7)'} />
            </View>
            <View style={{ flex: 1, marginLeft: 16 }}>
                <Text style={styles.itemLabel}>{label}</Text>
                {subLabel && <Text style={styles.itemSubLabel}>{subLabel}</Text>}
            </View>
            {value !== undefined ? (
                <Switch
                    value={value}
                    trackColor={{ false: 'rgba(255,255,255,0.1)', true: '#1E88E5' }}
                    thumbColor="#fff"
                />
            ) : (
                <Ionicons name="chevron-forward" size={18} color="rgba(255,255,255,0.2)" />
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    backgroundImage: { flex: 1 },
    container: { flex: 1 },
    scrollContent: { padding: 20 },
    header: { marginBottom: 32, marginTop: 10 },
    title: { color: '#fff', fontSize: 26, fontWeight: '800' },
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 14 },
    section: { marginBottom: 24 },
    sectionTitle: { color: 'rgba(255,255,255,0.5)', fontSize: 13, fontWeight: '700', textTransform: 'uppercase', marginBottom: 12, marginLeft: 4 },
    sectionCard: { overflow: 'hidden' },
    settingItem: { flexDirection: 'row', alignItems: 'center', padding: 16, borderBottomWidth: 0.5, borderBottomColor: 'rgba(255,255,255,0.05)' },
    iconBox: { width: 36, height: 36, borderRadius: 10, alignItems: 'center', justifyContent: 'center' },
    itemLabel: { color: '#fff', fontSize: 15, fontWeight: '600' },
    itemSubLabel: { color: 'rgba(255,255,255,0.4)', fontSize: 12, marginTop: 1 },
    footer: { marginTop: 20, alignItems: 'center', paddingBottom: 40 },
    versionText: { color: 'rgba(255,255,255,0.3)', fontSize: 12, fontWeight: '600' },
    legalText: { color: 'rgba(255,255,255,0.2)', fontSize: 10, marginTop: 4 }
});
