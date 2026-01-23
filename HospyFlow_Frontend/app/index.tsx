import React, { useState } from 'react';
import {
    StyleSheet,
    Text,
    View,
    TextInput,
    TouchableOpacity,
    ImageBackground,
    KeyboardAvoidingView,
    Platform,
    SafeAreaView,
    Dimensions,
    ScrollView,
    Alert,
    ActivityIndicator
} from 'react-native';
import { Colors } from '@/constants/theme';
import { GlassView } from '@/components/ui/GlassView';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { router } from 'expo-router';
import apiService from '@/services/api';

const { width } = Dimensions.get('window');

const ROLES = [
    { id: 'NURSE', label: 'Infirmier', icon: 'medkit' },
    { id: 'DOCTOR', label: 'Médecin', icon: 'medical' },
    { id: 'LAB_TECH', label: 'Technicien Labo', icon: 'flask' },
    { id: 'ADMIN', label: 'Administrateur', icon: 'shield' },
];

export default function AuthScreen() {
    const [isLogin, setIsLogin] = useState(true);
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    // Login form state
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // Registration form state
    const [regUsername, setRegUsername] = useState('');
    const [regEmail, setRegEmail] = useState('');
    const [regPassword, setRegPassword] = useState('');
    const [regConfirmPassword, setRegConfirmPassword] = useState('');
    const [regFirstName, setRegFirstName] = useState('');
    const [regLastName, setRegLastName] = useState('');
    const [selectedRole, setSelectedRole] = useState('NURSE');

    const handleLogin = async () => {
        if (!username || !password) {
            Alert.alert('Erreur', 'Veuillez remplir tous les champs');
            return;
        }

        setIsLoading(true);
        try {
            const response = await apiService.login({ username, password });

            if (response.user.role === 'ADMIN') {
                Alert.alert('Bienvenue', `Bonjour ${response.user.first_name || response.user.username}, vous êtes connecté en tant qu'administrateur`);
            } else {
                Alert.alert('Bienvenue', `Bonjour ${response.user.first_name || response.user.username}`);
            }

            router.replace('/(tabs)');
        } catch (error: any) {
            console.error('Login error:', error);
            const errorMessage = error.response?.data?.detail || 'Identifiants incorrects';
            Alert.alert('Erreur de connexion', errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegister = async () => {
        // Validation
        if (!regUsername || !regEmail || !regPassword || !regFirstName || !regLastName) {
            Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires');
            return;
        }

        if (regPassword !== regConfirmPassword) {
            Alert.alert('Erreur', 'Les mots de passe ne correspondent pas');
            return;
        }

        if (regPassword.length < 6) {
            Alert.alert('Erreur', 'Le mot de passe doit contenir au moins 6 caractères');
            return;
        }

        setIsLoading(true);
        try {
            await apiService.register({
                username: regUsername,
                email: regEmail,
                password: regPassword,
                first_name: regFirstName,
                last_name: regLastName,
                role: selectedRole as any,
            });

            Alert.alert(
                'Inscription réussie',
                'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.',
                [{
                    text: 'OK', onPress: () => {
                        setIsLogin(true);
                        setUsername(regUsername);
                    }
                }]
            );
        } catch (error: any) {
            console.error('Registration error:', error);
            const errorMessage = error.response?.data?.detail ||
                error.response?.data?.username?.[0] ||
                error.response?.data?.email?.[0] ||
                'Erreur lors de l\'inscription';
            Alert.alert('Erreur d\'inscription', errorMessage);
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

    const handleMockAccess = () => {
        // Quick access without backend (for testing UI)
        router.replace('/(tabs)');
    };

    return (
        <ImageBackground
            source={require('@/assets/images/bg.png')}
            style={styles.backgroundImage}
            blurRadius={2}
        >
            <SafeAreaView style={styles.container}>
                <StatusBar style="light" />
                <KeyboardAvoidingView
                    behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                    style={{ flex: 1 }}
                >
                    <ScrollView
                        contentContainerStyle={styles.scrollContent}
                        showsVerticalScrollIndicator={false}
                    >
                        <View style={styles.content}>
                            {/* Header */}
                            <View style={styles.header}>
                                <GlassView intensity={30} borderRadius={20} style={styles.logoContainer}>
                                    <Ionicons name="medical" size={40} color={theme.primary} />
                                </GlassView>
                                <Text style={styles.title}>HospyFlow</Text>
                                <Text style={styles.subtitle}>Intelligence Opérationnelle</Text>
                            </View>

                            {/* Main Card */}
                            <GlassView intensity={60} borderRadius={32} style={styles.glassCard}>
                                {/* Tabs */}
                                <View style={styles.tabContainer}>
                                    <TouchableOpacity
                                        onPress={() => setIsLogin(true)}
                                        style={[styles.tab, isLogin && styles.activeTab]}
                                    >
                                        <Text style={[styles.tabText, isLogin ? styles.activeTabText : { color: theme.textSecondary }]}>
                                            Connexion
                                        </Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        onPress={() => setIsLogin(false)}
                                        style={[styles.tab, !isLogin && styles.activeTab]}
                                    >
                                        <Text style={[styles.tabText, !isLogin ? styles.activeTabText : { color: theme.textSecondary }]}>
                                            Inscription
                                        </Text>
                                    </TouchableOpacity>
                                </View>

                                {/* Login Form */}
                                {isLogin ? (
                                    <View style={styles.form}>
                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="person-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Nom d'utilisateur"
                                                    placeholderTextColor={theme.textSecondary}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={username}
                                                    onChangeText={setUsername}
                                                    autoCapitalize="none"
                                                    autoCorrect={false}
                                                />
                                            </View>
                                        </View>

                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="lock-closed-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Mot de passe"
                                                    placeholderTextColor={theme.textSecondary}
                                                    secureTextEntry={!showPassword}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={password}
                                                    onChangeText={setPassword}
                                                    autoCapitalize="none"
                                                />
                                                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                                    <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color={theme.textSecondary} />
                                                </TouchableOpacity>
                                            </View>
                                        </View>

                                        <TouchableOpacity
                                            onPress={handleLogin}
                                            style={[styles.loginButton, { backgroundColor: theme.primary }]}
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

                                        {/* Demo Buttons */}
                                        <View style={styles.demoSection}>
                                            <Text style={styles.demoTitle}>Connexion Démo (Test)</Text>
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

                                        {/* Quick Access (No Backend) */}
                                        <TouchableOpacity
                                            onPress={handleMockAccess}
                                            style={styles.quickAccessButton}
                                        >
                                            <Ionicons name="flash-outline" size={16} color="rgba(255,255,255,0.6)" />
                                            <Text style={styles.quickAccessText}>Accès rapide (sans backend)</Text>
                                        </TouchableOpacity>
                                    </View>
                                ) : (
                                    /* Registration Form */
                                    <View style={styles.form}>
                                        <View style={styles.inputRow}>
                                            <View style={[styles.inputGroup, { flex: 1, marginRight: 8 }]}>
                                                <View style={styles.iconInput}>
                                                    <TextInput
                                                        placeholder="Prénom"
                                                        placeholderTextColor={theme.textSecondary}
                                                        style={[styles.input, { color: theme.text, marginLeft: 0 }]}
                                                        value={regFirstName}
                                                        onChangeText={setRegFirstName}
                                                    />
                                                </View>
                                            </View>
                                            <View style={[styles.inputGroup, { flex: 1, marginLeft: 8 }]}>
                                                <View style={styles.iconInput}>
                                                    <TextInput
                                                        placeholder="Nom"
                                                        placeholderTextColor={theme.textSecondary}
                                                        style={[styles.input, { color: theme.text, marginLeft: 0 }]}
                                                        value={regLastName}
                                                        onChangeText={setRegLastName}
                                                    />
                                                </View>
                                            </View>
                                        </View>

                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="person-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Nom d'utilisateur"
                                                    placeholderTextColor={theme.textSecondary}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={regUsername}
                                                    onChangeText={setRegUsername}
                                                    autoCapitalize="none"
                                                    autoCorrect={false}
                                                />
                                            </View>
                                        </View>

                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="mail-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Email"
                                                    placeholderTextColor={theme.textSecondary}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={regEmail}
                                                    onChangeText={setRegEmail}
                                                    autoCapitalize="none"
                                                    keyboardType="email-address"
                                                />
                                            </View>
                                        </View>

                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="lock-closed-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Mot de passe"
                                                    placeholderTextColor={theme.textSecondary}
                                                    secureTextEntry={!showPassword}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={regPassword}
                                                    onChangeText={setRegPassword}
                                                    autoCapitalize="none"
                                                />
                                            </View>
                                        </View>

                                        <View style={styles.inputGroup}>
                                            <View style={styles.iconInput}>
                                                <Ionicons name="lock-closed-outline" size={20} color={theme.primary} />
                                                <TextInput
                                                    placeholder="Confirmer mot de passe"
                                                    placeholderTextColor={theme.textSecondary}
                                                    secureTextEntry={!showPassword}
                                                    style={[styles.input, { color: theme.text }]}
                                                    value={regConfirmPassword}
                                                    onChangeText={setRegConfirmPassword}
                                                    autoCapitalize="none"
                                                />
                                                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                                    <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color={theme.textSecondary} />
                                                </TouchableOpacity>
                                            </View>
                                        </View>

                                        {/* Role Selection */}
                                        <Text style={styles.roleLabel}>Sélectionnez votre rôle:</Text>
                                        <View style={styles.roleGrid}>
                                            {ROLES.map((role) => (
                                                <TouchableOpacity
                                                    key={role.id}
                                                    onPress={() => setSelectedRole(role.id)}
                                                    style={[
                                                        styles.roleCard,
                                                        selectedRole === role.id && {
                                                            backgroundColor: theme.primary + '20',
                                                            borderColor: theme.primary
                                                        }
                                                    ]}
                                                >
                                                    <Ionicons
                                                        name={role.icon as any}
                                                        size={20}
                                                        color={selectedRole === role.id ? theme.primary : 'rgba(255,255,255,0.6)'}
                                                    />
                                                    <Text style={[
                                                        styles.roleText,
                                                        selectedRole === role.id && { color: theme.primary }
                                                    ]}>
                                                        {role.label}
                                                    </Text>
                                                </TouchableOpacity>
                                            ))}
                                        </View>

                                        <TouchableOpacity
                                            onPress={handleRegister}
                                            style={[styles.loginButton, { backgroundColor: theme.success }]}
                                            disabled={isLoading}
                                        >
                                            {isLoading ? (
                                                <ActivityIndicator color="#fff" />
                                            ) : (
                                                <>
                                                    <Text style={styles.loginButtonText}>Créer mon compte</Text>
                                                    <Ionicons name="checkmark-circle" size={20} color="#fff" />
                                                </>
                                            )}
                                        </TouchableOpacity>
                                    </View>
                                )}
                            </GlassView>

                            <Text style={styles.footerText}>
                                © 2026 HospyFlow • Innovation Santé
                            </Text>
                        </View>
                    </ScrollView>
                </KeyboardAvoidingView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    backgroundImage: {
        flex: 1,
        width: '100%',
        height: '100%',
    },
    container: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'center',
    },
    content: {
        flex: 1,
        paddingHorizontal: 24,
        justifyContent: 'center',
        paddingVertical: 40,
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
    },
    logoContainer: {
        width: 80,
        height: 80,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
    },
    title: {
        fontSize: 32,
        fontWeight: '800',
        color: '#fff',
        letterSpacing: 1,
    },
    subtitle: {
        fontSize: 16,
        color: 'rgba(255, 255, 255, 0.8)',
        marginTop: 4,
        fontWeight: '500',
    },
    glassCard: {
        padding: 24,
        width: '100%',
    },
    tabContainer: {
        flexDirection: 'row',
        backgroundColor: 'rgba(0, 0, 0, 0.05)',
        borderRadius: 16,
        padding: 4,
        marginBottom: 24,
    },
    tab: {
        flex: 1,
        paddingVertical: 12,
        alignItems: 'center',
        borderRadius: 12,
    },
    activeTab: {
        backgroundColor: '#fff',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 2,
    },
    tabText: {
        fontSize: 15,
        fontWeight: '600',
    },
    activeTabText: {
        color: '#1E88E5',
    },
    form: {
        gap: 12,
    },
    inputGroup: {
        marginBottom: 4,
    },
    inputRow: {
        flexDirection: 'row',
    },
    iconInput: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
        borderRadius: 16,
        paddingHorizontal: 16,
        height: 56,
    },
    input: {
        flex: 1,
        marginLeft: 12,
        fontSize: 16,
        fontWeight: '500',
    },
    loginButton: {
        height: 56,
        borderRadius: 16,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 12,
        gap: 8,
        shadowColor: '#1E88E5',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.3,
        shadowRadius: 12,
        elevation: 8,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 17,
        fontWeight: '700',
    },
    demoSection: {
        marginTop: 20,
        paddingTop: 20,
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
        backgroundColor: 'rgba(255,255,255,0.1)',
        borderRadius: 12,
        paddingVertical: 12,
        gap: 6,
    },
    demoButtonText: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 13,
        fontWeight: '600',
    },
    quickAccessButton: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 16,
        gap: 6,
    },
    quickAccessText: {
        color: 'rgba(255,255,255,0.5)',
        fontSize: 12,
        fontWeight: '500',
    },
    roleLabel: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 14,
        fontWeight: '600',
        marginTop: 8,
        marginBottom: 8,
    },
    roleGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 8,
        marginBottom: 8,
    },
    roleCard: {
        width: '48%',
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 12,
        borderRadius: 12,
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderWidth: 1,
        borderColor: 'transparent',
        gap: 8,
    },
    roleText: {
        color: 'rgba(255,255,255,0.8)',
        fontSize: 12,
        fontWeight: '600',
    },
    footerText: {
        textAlign: 'center',
        color: 'rgba(255, 255, 255, 0.6)',
        marginTop: 32,
        fontSize: 13,
        fontWeight: '500',
    }
});
