import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, TextInput, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

const INCIDENT_TYPES = [
    { label: 'Retard Flux', icon: 'time', id: 1 },
    { label: 'Panne Matériel', icon: 'construct', id: 2 },
    { label: 'Manque Personnel', icon: 'people', id: 3 },
    { label: 'Saturation', icon: 'alert-circle', id: 4 },
];

export default function ReportScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const [services, setServices] = useState<any[]>([]);
    const [fluxTypes, setFluxTypes] = useState<any[]>([]);
    const [selectedService, setSelectedService] = useState<number | null>(null);
    const [selectedType, setSelectedType] = useState<number | null>(null);
    const [description, setDescription] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            const [servicesData, categoriesData] = await Promise.all([
                apiService.getServices(),
                apiService.getEventCategories()
            ]);
            setServices(servicesData);
            setFluxTypes(categoriesData);
            if (servicesData.length > 0) setSelectedService(servicesData[0].id);
            if (categoriesData.length > 0) setSelectedType(categoriesData[0].id);
        } catch (error) {
            console.error("Failed to load data", error);
        }
    };

    const handleSubmit = async () => {
        if (!selectedService || !selectedType) {
            Alert.alert("Erreur", "Veuillez sélectionner un service et un type");
            return;
        }

        setIsLoading(true);
        try {
            // personnel id 1 is 'admin' (seeded)
            await apiService.createEvent({
                personnel: 1,
                service: selectedService,
                type_flux: selectedType,
                description: description,
                niveau_gravite: description.toLowerCase().includes('urgent') ? 'CRITICAL' : 'MEDIUM'
            });

            Alert.alert("Succès", "Signalement envoyé avec succès");
            setDescription('');
        } catch (error) {
            console.error("Failed to submit signal", error);
            Alert.alert("Erreur", "Impossible d'envoyer le signalement");
        } finally {
            setIsLoading(false);
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
                        <Text style={styles.title}>Signalement Rapide</Text>
                        <Text style={styles.subtitle}>Enregistrez un micro-événement en quelques secondes</Text>
                    </View>

                    <GlassView intensity={50} borderRadius={32} style={styles.card}>
                        {/* Service Selection */}
                        <View style={styles.section}>
                            <Text style={styles.label}>1. Service concerné</Text>
                            <View style={styles.serviceGrid}>
                                {services.map((s) => (
                                    <TouchableOpacity
                                        key={s.id}
                                        onPress={() => setSelectedService(s.id)}
                                        style={[
                                            styles.servicePill,
                                            selectedService === s.id && { backgroundColor: theme.primary }
                                        ]}
                                    >
                                        <Text style={[styles.serviceText, selectedService === s.id && { color: '#fff' }]}>{s.nom}</Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>

                        {/* Type Selection */}
                        <View style={styles.section}>
                            <Text style={styles.label}>2. Type de flux</Text>
                            <View style={styles.typeGrid}>
                                {fluxTypes.map((t) => (
                                    <TouchableOpacity
                                        key={t.id}
                                        onPress={() => setSelectedType(t.id)}
                                        style={[
                                            styles.typeCard,
                                            selectedType === t.id && { backgroundColor: theme.primary + '20', borderColor: theme.primary }
                                        ]}
                                    >
                                        <Ionicons
                                            name="git-network-outline"
                                            size={24}
                                            color={selectedType === t.id ? theme.primary : 'rgba(255,255,255,0.6)'}
                                        />
                                        <Text style={[styles.typeText, selectedType === t.id && { color: theme.primary }]}>{t.nom}</Text>
                                    </TouchableOpacity>
                                ))}
                            </View>
                        </View>

                        {/* Additional Info */}
                        <View style={styles.section}>
                            <Text style={styles.label}>3. Détails (Optionnel)</Text>
                            <TextInput
                                placeholder="Description courte..."
                                placeholderTextColor="rgba(255,255,255,0.4)"
                                style={styles.input}
                                multiline
                                value={description}
                                onChangeText={setDescription}
                            />
                        </View>

                        <TouchableOpacity
                            style={[styles.submitButton, { backgroundColor: theme.primary, opacity: isLoading ? 0.6 : 1 }]}
                            onPress={handleSubmit}
                            disabled={isLoading}
                        >
                            <Text style={styles.submitText}>{isLoading ? 'Envoi...' : 'Envoyer le Signal'}</Text>
                            {!isLoading && <Ionicons name="paper-plane" size={20} color="#fff" style={{ marginLeft: 8 }} />}
                        </TouchableOpacity>
                    </GlassView>

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
    title: { color: '#fff', fontSize: 28, fontWeight: '800' },
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 16, marginTop: 4 },
    card: { padding: 24 },
    section: { marginBottom: 24 },
    label: { color: '#fff', fontSize: 16, fontWeight: '600', marginBottom: 16 },
    serviceGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
    servicePill: {
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 20,
        backgroundColor: 'rgba(255,255,255,0.1)',
    },
    serviceText: { color: 'rgba(255,255,255,0.8)', fontSize: 14, fontWeight: '500' },
    typeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
    typeCard: {
        width: '47%',
        padding: 16,
        borderRadius: 20,
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderWidth: 1,
        borderColor: 'transparent',
        alignItems: 'center',
        gap: 8,
    },
    typeText: { color: 'rgba(255,255,255,0.6)', fontSize: 13, fontWeight: '600', textAlign: 'center' },
    input: {
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderRadius: 16,
        padding: 16,
        color: '#fff',
        fontSize: 16,
        height: 100,
        textAlignVertical: 'top',
    },
    submitButton: {
        height: 60,
        borderRadius: 18,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#1E88E5',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 15,
        elevation: 10,
    },
    submitText: { color: '#fff', fontSize: 18, fontWeight: '700' }
});
