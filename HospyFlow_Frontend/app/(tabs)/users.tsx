import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, Image, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import { apiClient } from '@/services/api';
import authService from '@/services/auth';

const USERS = [
    { id: '1', name: 'Dr. Sarah Meyer', role: 'Administrateur', service: 'Direction', status: 'Online' },
    { id: '2', name: 'Lucas Bernard', role: 'Infirmier Chef', service: 'Urgences', status: 'In service' },
    { id: '3', name: 'Dr. Marc Volat', role: 'Praticien', service: 'Radiologie', status: 'Offline' },
    { id: '4', name: 'Julie Rossi', role: 'Cadre Santé', service: 'Pédiatrie', status: 'In service' },
];

export default function UsersScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];
    const [users, setUsers] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isAdmin, setIsAdmin] = useState(false);

    useEffect(() => {
        checkAccess();
    }, []);

    const checkAccess = async () => {
        try {
            const user = await authService.getUser();
            if (user && user.role === 'ADMIN') {
                setIsAdmin(true);
                loadUsers();
            } else {
                setIsLoading(false);
                Alert.alert('Accès refusé', 'Cette page est réservée aux administrateurs');
            }
        } catch (error) {
            console.error('Failed to check access', error);
            setIsLoading(false);
        }
    };

    const loadUsers = async () => {
        try {
            setIsLoading(true);
            const response = await apiClient.get('/auth/users/');
            setUsers(response.data);
        } catch (error) {
            console.error('Failed to load users', error);
            Alert.alert('Erreur', 'Impossible de charger les utilisateurs');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddUser = () => {
        Alert.alert('Fonctionnalité à venir', 'La création d\'utilisateur sera disponible prochainement');
    };

    const handleEditUser = (userId: number) => {
        Alert.alert('Fonctionnalité à venir', `Édition de l'utilisateur #${userId} sera disponible prochainement`);
    };

    if (isLoading) {
        return (
            <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }]}>
                <ActivityIndicator size="large" color={theme.primary} />
            </View>
        );
    }

    if (!isAdmin) {
        return (
            <ImageBackground
                source={require('@/assets/images/bg.png')}
                style={styles.backgroundImage}
                blurRadius={10}
            >
                <SafeAreaView style={styles.container}>
                    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
                        <Ionicons name="lock-closed" size={64} color="rgba(255,255,255,0.3)" />
                        <Text style={{ color: '#fff', fontSize: 20, fontWeight: '700', marginTop: 20, textAlign: 'center' }}>
                            Accès Restreint
                        </Text>
                        <Text style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14, marginTop: 8, textAlign: 'center' }}>
                            Cette page est réservée aux administrateurs
                        </Text>
                    </View>
                </SafeAreaView>
            </ImageBackground>
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
                        <Text style={styles.title}>Gestion Utilisateurs</Text>
                        <Text style={styles.subtitle}>Contrôlez les accès et rôles du personnel</Text>
                    </View>

                    <View style={styles.actions}>
                        <TouchableOpacity
                            style={[styles.addButton, { backgroundColor: theme.primary }]}
                            onPress={handleAddUser}
                        >
                            <Ionicons name="person-add" size={20} color="#fff" />
                            <Text style={styles.addButtonText}>Nouvel Utilisateur</Text>
                        </TouchableOpacity>
                    </View>

                    <View style={styles.userList}>
                        {USERS.map((user) => (
                            <GlassView key={user.id} intensity={40} borderRadius={24} style={styles.userCard}>
                                <View style={styles.avatarContainer}>
                                    <View style={[styles.avatar, { backgroundColor: theme.primary + '30' }]}>
                                        <Text style={[styles.avatarText, { color: theme.primary }]}>{user.name.charAt(0)}</Text>
                                    </View>
                                    <View style={[styles.statusDot, { backgroundColor: user.status === 'Offline' ? '#8E8E93' : theme.success }]} />
                                </View>

                                <View style={styles.userInfo}>
                                    <Text style={styles.userName}>{user.name}</Text>
                                    <Text style={styles.userRole}>{user.role} • {user.service}</Text>
                                </View>

                                <TouchableOpacity
                                    style={styles.editButton}
                                    onPress={() => handleEditUser(parseInt(user.id))}
                                >
                                    <Ionicons name="ellipsis-vertical" size={20} color="rgba(255,255,255,0.4)" />
                                </TouchableOpacity>
                            </GlassView>
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
    subtitle: { color: 'rgba(255,255,255,0.6)', fontSize: 14 },
    actions: { marginBottom: 24 },
    addButton: { height: 50, borderRadius: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 },
    addButtonText: { color: '#fff', fontSize: 15, fontWeight: '700' },
    userList: { gap: 12 },
    userCard: { padding: 16, flexDirection: 'row', alignItems: 'center' },
    avatarContainer: { position: 'relative' },
    avatar: { width: 50, height: 50, borderRadius: 25, alignItems: 'center', justifyContent: 'center' },
    avatarText: { fontSize: 20, fontWeight: '800' },
    statusDot: { width: 12, height: 12, borderRadius: 6, position: 'absolute', bottom: 0, right: 0, borderWidth: 2, borderColor: '#1A1C1E' },
    userInfo: { flex: 1, marginLeft: 16 },
    userName: { color: '#fff', fontSize: 16, fontWeight: '700' },
    userRole: { color: 'rgba(255,255,255,0.5)', fontSize: 13, marginTop: 2 },
    editButton: { padding: 8 }
});
