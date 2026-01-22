
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
    Dimensions
} from 'react-native';
import { Colors } from '@/constants/theme';
import { GlassView } from '@/components/ui/GlassView';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { router } from 'expo-router';

const { width } = Dimensions.get('window');

const ROLES = [
    { id: 'doctor', label: 'Doctor', icon: 'medical' },
    { id: 'nurse', label: 'Nurse', icon: 'medkit' },
    { id: 'lab', label: 'Lab Staff', icon: 'flask' },
    { id: 'admin', label: 'Admin', icon: 'shield' },
];

export default function AuthScreen() {
    const [isLogin, setIsLogin] = useState(true);
    const [selectedRole, setSelectedRole] = useState('nurse');
    const [showPassword, setShowPassword] = useState(false);
    const colorScheme = useColorScheme() ?? 'light';
    const theme = Colors[colorScheme];

    const handleAccess = () => {
        // Mock login
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
                    <View style={styles.content}>
                        {/* Header */}
                        <View style={styles.header}>
                            <GlassView intensity={30} borderRadius={20} style={styles.logoContainer}>
                                <Ionicons name="medical" size={40} color={theme.primary} />
                            </GlassView>
                            <Text style={styles.title}>HospyFlow</Text>
                            <Text style={styles.subtitle}>Intelligence Opérationnelle</Text>
                        </View>

                        {/* Main Login Card */}
                        <GlassView intensity={60} borderRadius={32} style={styles.glassCard}>
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

                            <View style={styles.form}>
                                <View style={styles.inputGroup}>
                                    <View style={styles.iconInput}>
                                        <Ionicons name="person-outline" size={20} color={theme.primary} />
                                        <TextInput
                                            placeholder="Identifiant Professionnel"
                                            placeholderTextColor={theme.textSecondary}
                                            style={[styles.input, { color: theme.text }]}
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
                                        />
                                        <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                            <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color={theme.textSecondary} />
                                        </TouchableOpacity>
                                    </View>
                                </View>

                                <TouchableOpacity
                                    onPress={handleAccess}
                                    style={[styles.loginButton, { backgroundColor: theme.primary }]}
                                >
                                    <Text style={styles.loginButtonText}>Accéder aux Services</Text>
                                    <Ionicons name="chevron-forward" size={20} color="#fff" />
                                </TouchableOpacity>
                            </View>
                        </GlassView>

                        <Text style={styles.footerText}>
                            © 2026 HospyFlow • Innovation Santé
                        </Text>
                    </View>
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
    content: {
        flex: 1,
        paddingHorizontal: 24,
        justifyContent: 'center',
    },
    header: {
        alignItems: 'center',
        marginBottom: 40,
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
        marginBottom: 32,
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
        gap: 16,
    },
    inputGroup: {
        marginBottom: 8,
    },
    iconInput: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(255, 255, 255, 0.5)',
        borderRadius: 16,
        paddingHorizontal: 16,
        height: 60,
    },
    input: {
        flex: 1,
        marginLeft: 12,
        fontSize: 16,
        fontWeight: '500',
    },
    loginButton: {
        height: 60,
        borderRadius: 18,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 16,
        shadowColor: '#1E88E5',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 15,
        elevation: 10,
    },
    loginButtonText: {
        color: '#fff',
        fontSize: 17,
        fontWeight: '700',
        marginRight: 8,
    },
    footerText: {
        textAlign: 'center',
        color: 'rgba(255, 255, 255, 0.6)',
        marginTop: 40,
        fontSize: 13,
        fontWeight: '500',
    }
});
