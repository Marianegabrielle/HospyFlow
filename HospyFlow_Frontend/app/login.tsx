import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ImageBackground, Alert, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import { router } from 'expo-router';
import apiService from '@/services/api';

export default function LoginScreen() {
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleLogin = async () => {
        if (!username || !password) {
            Alert.alert('Erreur', 'Veuillez remplir tous les champs');
            return;
        }

        setIsLoading(true);
        try {
            const response = await apiService.login({ username, password });

            // Navigate based on role
            if (response.user.role === 'ADMIN') {
                Alert.alert('Bienvenue', `Bonjour ${response.user.first_name}, vous êtes connecté en tant qu'administrateur`);
            } else {
                Alert.alert('Bienvenue', `Bonjour ${response.user.first_name}`);
            }

            // Navigate to main app
            router.replace('/(tabs)');
        } catch (error: any) {
            console.error('Login error:', error);
            const errorMessage = error.response?.data?.detail || 'Identifiants incorrects';
            Alert.alert('Erreur de connexion', errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDemoLogin = (role: 'admin' | 'personnel') => {
        if (role === 'admin') {
            setUsername('admin');
            setPassword('admin123');
        } else {
            setUsername('nurse1');
            setPassword('nurse123');
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
                <KeyboardAvoidingView
                    behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                    style={styles.keyboardView}
                >
                    <View style={styles.content}>
                        {/* Logo/Header */}
                        <View style={styles.header}>
                            <View style={[styles.logoContainer, { backgroundColor: theme.primary + '20' }]}>
                                <Ionicons name="medical" size={48} color={theme.primary} />
                            </View>
                            <Text style={styles.title}>HospyFlow</Text>
                            <Text style={styles.subtitle}>ClinicFlow Analytics</Text>
                        </View>

                        {/* Login Form */}
                        <GlassView intensity={50} borderRadius={32} style={styles.formCard}>
                            <Text style={styles.formTitle}>Connexion</Text>

                            {/* Username Input */}
                            <View style={styles.inputContainer}>
                                <Ionicons name="person-outline" size={20} color="rgba(255,255,255,0.5)" />
                                <TextInput
                                    style={styles.input}
                                    placeholder="Nom d'utilisateur"
                                    placeholderTextColor="rgba(255,255,255,0.4)"
                                    value={username}
                                    onChangeText={setUsername}
                                    autoCapitalize="none"
                                    autoCorrect={false}
                                />
                            </View>

                            {/* Password Input */}
                            <View style={styles.inputContainer}>
                                <Ionicons name="lock-closed-outline" size={20} color="rgba(255,255,255,0.5)" />
                                <TextInput
                                    style={styles.input}
                                    placeholder="Mot de passe"
                                    placeholderTextColor="rgba(255,255,255,0.4)"
                                    value={password}
                                    onChangeText={setPassword}
                                    secureTextEntry={!showPassword}
                                    autoCapitalize="none"
                                />
                                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                    <Ionicons
                                        name={showPassword ? "eye-outline" : "eye-off-outline"}
                                        size={20}
                                        color="rgba(255,255,255,0.5)"
                                    />
                                </TouchableOpacity>
                            </View>

                            {/* Login Button */}
                            <TouchableOpacity
                                style={[styles.loginButton, { backgroundColor: theme.primary }]}
                                onPress={handleLogin}
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <ActivityIndicator color="#fff" />
                                ) : (
                                    <>
                                        <Text style={styles.loginButtonText}>Se connecter</Text>
                                        <Ionicons name="arrow-forward" size={20} color="#fff" />
                                    </>
                                )}
                            </TouchableOpacity>

                            {/* Demo Logins */}
                            <View style={styles.demoSection}>
                                <Text style={styles.demoTitle}>Connexion Démo</Text>
                                <View style={styles.demoButtons}>
                                    <TouchableOpacity
                                        style={styles.demoButton}
                                        onPress={() => handleDemoLogin('admin')}
                                    >
                                        <Ionicons name="shield-checkmark" size={16} color={theme.primary} />
                                        <Text style={styles.demoButtonText}>Admin</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={styles.demoButton}
                                        onPress={() => handleDemoLogin('personnel')}
                                    >
                                        <Ionicons name="people" size={16} color={theme.success} />
                                        <Text style={styles.demoButtonText}>Personnel</Text>
                                    </TouchableOpacity>
                                </View>
                            </View>
                        </GlassView>

                        {/* Footer */}
                        <Text style={styles.footer}>© 2026 HospyFlow - ClinicFlow Analytics</Text>
                    </View>
                </KeyboardAvoidingView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    backgroundImage: { flex: 1 },
    container: { flex: 1 },
    keyboardView: { flex: 1 },
    content: {
        flex: 1,
        justifyContent: 'center',
        padding: 20,
    },
    header: {
        alignItems: 'center',
        marginBottom: 40,
    },
    logoContainer: {
        width: 100,
        height: 100,
        borderRadius: 50,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 20,
    },
    title: {
        color: '#fff',
        fontSize: 32,
        fontWeight: '800',
        marginBottom: 4,
    },
    subtitle: {
        color: 'rgba(255,255,255,0.6)',
        fontSize: 14,
        fontWeight: '500',
    },
    formCard: {
        padding: 32,
    },
    formTitle: {
        color: '#fff',
        fontSize: 24,
        fontWeight: '700',
        marginBottom: 24,
        textAlign: 'center',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderRadius: 16,
        paddingHorizontal: 16,
        marginBottom: 16,
        height: 56,
    },
    input: {
        flex: 1,
        color: '#fff',
        fontSize: 16,
        marginLeft: 12,
    },
    loginButton: {
        height: 56,
        borderRadius: 16,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 8,
        gap: 8,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '700',
    },
    demoSection: {
        marginTop: 24,
        paddingTop: 24,
        borderTopWidth: 1,
        borderTopColor: 'rgba(255,255,255,0.1)',
    },
    demoTitle: {
        color: 'rgba(255,255,255,0.5)',
        fontSize: 12,
        fontWeight: '600',
        textAlign: 'center',
        marginBottom: 12,
    },
    demoButtons: {
        flexDirection: 'row',
        gap: 12,
    },
    demoButton: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderRadius: 12,
        paddingVertical: 12,
        gap: 6,
    },
    demoButtonText: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 13,
        fontWeight: '600',
    },
    footer: {
        color: 'rgba(255,255,255,0.3)',
        fontSize: 11,
        textAlign: 'center',
        marginTop: 32,
    },
});
