import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import { router } from 'expo-router';

const MENU_ITEMS = [
    { id: 'incidents', label: 'Historique des Incidents', icon: 'list', route: '/(tabs)/incidents' },
    { id: 'analytics', label: 'Analytics & Goulots (IA)', icon: 'analytics', route: '/(tabs)/analytics' },
    { id: 'users', label: 'Gestion Utilisateurs', icon: 'people', route: '/(tabs)/users' },
    { id: 'settings', label: 'Paramètres Système', icon: 'settings', route: '/(tabs)/settings' },
];

export default function MenuScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

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
                        <Text style={styles.title}>Plus d'options</Text>
                        <Text style={styles.subtitle}>Gérez le système et consultez les archives</Text>
                    </View>

                    <GlassView intensity={50} borderRadius={30} style={styles.menuCard}>
                        {MENU_ITEMS.map((item, index) => (
                            <TouchableOpacity
                                key={item.id}
                                onPress={() => router.push(item.route as any)}
                                style={[styles.menuItem, index !== MENU_ITEMS.length - 1 && styles.border]}
                            >
                                <View style={styles.iconContainer}>
                                    <Ionicons name={item.icon as any} size={22} color={theme.primary} />
                                </View>
                                <Text style={styles.menuLabel}>{item.label}</Text>
                                <Ionicons name="chevron-forward" size={20} color="rgba(255,255,255,0.3)" />
                            </TouchableOpacity>
                        ))}
                    </GlassView>

                    <TouchableOpacity
                        onPress={() => router.replace('/')}
                        style={styles.logoutButton}
                    >
                        <Ionicons name="log-out-outline" size={20} color={theme.error} />
                        <Text style={[styles.logoutText, { color: theme.error }]}>Se déconnecter</Text>
                    </TouchableOpacity>

                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    backgroundImage: { flex: 1 },
    container: { flex: 1 },
    scrollContent: { padding: 20 },
    header: { marginBottom: 32, marginTop: 10 },
    title: { color: '#fff', fontSize: 26, fontWeight: '800' },
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 14, marginTop: 4 },
    menuCard: { overflow: 'hidden' },
    menuItem: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 20,
    },
    border: { borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)' },
    iconContainer: {
        width: 40,
        height: 40,
        borderRadius: 12,
        backgroundColor: 'rgba(255,255,255,0.1)',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    menuLabel: { flex: 1, color: '#fff', fontSize: 16, fontWeight: '600' },
    logoutButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 32,
        gap: 8,
        padding: 20,
        backgroundColor: 'rgba(229, 57, 53, 0.1)',
        borderRadius: 20,
    },
    logoutText: { fontSize: 16, fontWeight: '700' }
});
