
import React, { useState } from 'react';
import {
    StyleSheet,
    Text,
    View,
    TextInput,
    TouchableOpacity,
    ScrollView,
    Platform,
    useColorScheme,
    KeyboardAvoidingView,
    SafeAreaView
} from 'react-native';
import { Colors } from '@/constants/Colors';
import { Ionicons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const ROLES = [
    { id: 'doctor', label: 'Doctor', icon: 'medical' },
    { id: 'nurse', label: 'Nurse', icon: 'medkit' },
    { id: 'lab', label: 'Lab Staff', icon: 'flask' },
    { id: 'admin', label: 'Admin', icon: 'shield' },
];

export default function AuthScreen() {
    const [isLogin, setIsLogin] = useState(true);
    const [selectedRole, setSelectedRole] = useState('doctor');
    const [roleScrollIndex, setRoleScrollIndex] = useState(0);
    const [showPassword, setShowPassword] = useState(false);
    const colorScheme = useColorScheme();
    const theme = Colors[colorScheme === 'dark' ? 'dark' : 'light'];

    return (
        <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
            <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={{ flex: 1 }}
            >
                <ScrollView contentContainerStyle={styles.scrollContent}>

                    {/* Header */}
                    <View style={styles.header}>
                        <View style={[styles.logoContainer, { backgroundColor: theme.primary }]}>
                            <Ionicons name="medical" size={32} color="#fff" />
                        </View>
                        <Text style={[styles.title, { color: theme.text }]}>HospyFlow</Text>
                        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
                            Système d'Excellence Opérationnelle
                        </Text>
                    </View>

                    {/* Tab Switcher */}
                    <View style={[styles.tabContainer, { borderColor: theme.border, backgroundColor: theme.surface }]}>
                        <TouchableOpacity
                            style={[
                                styles.tab,
                                isLogin && { backgroundColor: theme.primary + '15' } // 15 = roughly 8% opacity hex if simple append works, else just use subtle tint
                            ]}
                            onPress={() => setIsLogin(true)}
                        >
                            <Text style={[
                                styles.tabText,
                                { color: isLogin ? theme.primary : theme.textSecondary, fontWeight: isLogin ? '600' : '400' }
                            ]}>Login</Text>
                            {isLogin && <View style={[styles.activeTabIndicator, { backgroundColor: theme.primary }]} />}
                        </TouchableOpacity>

                        <TouchableOpacity
                            style={[
                                styles.tab,
                                !isLogin && { backgroundColor: theme.primary + '15' }
                            ]}
                            onPress={() => setIsLogin(false)}
                        >
                            <Text style={[
                                styles.tabText,
                                { color: !isLogin ? theme.primary : theme.textSecondary, fontWeight: !isLogin ? '600' : '400' }
                            ]}>Register</Text>
                            {!isLogin && <View style={[styles.activeTabIndicator, { backgroundColor: theme.primary }]} />}
                        </TouchableOpacity>
                    </View>

                    {/* Role Selection */}
                    <View style={styles.roleSection}>
                        <Text style={[styles.sectionLabel, { color: theme.text }]}>Select Role</Text>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.roleScroll}>
                            {ROLES.map((role) => (
                                <TouchableOpacity
                                    key={role.id}
                                    style={[
                                        styles.rolePill,
                                        {
                                            backgroundColor: selectedRole === role.id ? theme.primary : theme.surface,
                                            borderColor: selectedRole === role.id ? theme.primary : theme.border
                                        }
                                    ]}
                                    onPress={() => setSelectedRole(role.id)}
                                >
                                    <Ionicons
                                        name={role.icon as any}
                                        size={20}
                                        color={selectedRole === role.id ? '#fff' : theme.textSecondary}
                                    />
                                    <Text style={[
                                        styles.roleText,
                                        { color: selectedRole === role.id ? '#fff' : theme.textSecondary }
                                    ]}>
                                        {role.label}
                                    </Text>
                                </TouchableOpacity>
                            ))}
                        </ScrollView>
                    </View>

                    {/* Form */}
                    <View style={styles.formContainer}>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { color: theme.text }]}>Professional ID</Text>
                            <View style={[styles.inputContainer, { backgroundColor: theme.surface, borderColor: theme.border }]}>
                                <Ionicons name="card-outline" size={20} color={theme.textSecondary} style={styles.inputIcon} />
                                <TextInput
                                    placeholder="e.g. 849302"
                                    placeholderTextColor={theme.textSecondary}
                                    style={[styles.input, { color: theme.text }]}
                                    keyboardType="number-pad"
                                />
                            </View>
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { color: theme.text }]}>Hospital Email</Text>
                            <View style={[styles.inputContainer, { backgroundColor: theme.surface, borderColor: theme.border }]}>
                                <Ionicons name="mail-outline" size={20} color={theme.textSecondary} style={styles.inputIcon} />
                                <TextInput
                                    placeholder="staff@clinicflow.com"
                                    placeholderTextColor={theme.textSecondary}
                                    style={[styles.input, { color: theme.text }]}
                                    keyboardType="email-address"
                                    autoCapitalize="none"
                                />
                            </View>
                        </View>

                        <View style={styles.inputGroup}>
                            <Text style={[styles.label, { color: theme.text }]}>Password</Text>
                            <View style={[styles.inputContainer, { backgroundColor: theme.surface, borderColor: theme.border }]}>
                                <Ionicons name="lock-closed-outline" size={20} color={theme.textSecondary} style={styles.inputIcon} />
                                <TextInput
                                    placeholder="••••••"
                                    placeholderTextColor={theme.textSecondary}
                                    style={[styles.input, { color: theme.text }]}
                                    secureTextEntry={!showPassword}
                                />
                                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                                    <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20} color={theme.textSecondary} />
                                </TouchableOpacity>
                            </View>
                        </View>

                        <TouchableOpacity style={[styles.primaryButton, { backgroundColor: theme.primary }]}>
                            <Text style={styles.primaryButtonText}>
                                {isLogin ? 'Access Dashboard' : 'Create Account'}
                            </Text>
                            <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginLeft: 8 }} />
                        </TouchableOpacity>

                        <View style={styles.footer}>
                            <TouchableOpacity>
                                <Text style={[styles.footerLink, { color: theme.textSecondary }]}>Forgot Password?</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={{ marginTop: 12 }}>
                                <Text style={[styles.footerLink, { color: theme.primary }]}>Need Help? Contact IT Support</Text>
                            </TouchableOpacity>
                        </View>

                    </View>

                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollContent: {
        padding: 24,
        paddingTop: 60,
    },
    header: {
        alignItems: 'center',
        marginBottom: 32,
    },
    logoContainer: {
        width: 64,
        height: 64,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
        shadowColor: '#005EB8',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 8,
        elevation: 4,
    },
    title: {
        fontSize: 24,
        fontWeight: '700',
        marginBottom: 8,
        textAlign: 'center',
    },
    subtitle: {
        fontSize: 14,
        textAlign: 'center',
    },
    tabContainer: {
        flexDirection: 'row',
        borderWidth: 1,
        borderRadius: 12,
        marginBottom: 32,
        overflow: 'hidden',
    },
    tab: {
        flex: 1,
        paddingVertical: 12,
        alignItems: 'center',
        position: 'relative',
    },
    tabText: {
        fontSize: 14,
    },
    activeTabIndicator: {
        position: 'absolute',
        bottom: 0,
        height: 2,
        width: '40%',
        borderTopLeftRadius: 2,
        borderTopRightRadius: 2,
    },
    roleSection: {
        marginBottom: 32,
    },
    sectionLabel: {
        fontSize: 14,
        fontWeight: '600',
        marginBottom: 12,
    },
    roleScroll: {
        flexDirection: 'row',
        overflow: 'visible'
    },
    rolePill: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 10,
        borderRadius: 24,
        borderWidth: 1,
        marginRight: 12,
        height: 44,
    },
    roleText: {
        marginLeft: 8,
        fontSize: 13,
        fontWeight: '600',
    },
    formContainer: {
        gap: 20,
    },
    inputGroup: {
        gap: 8,
    },
    label: {
        fontSize: 14,
        fontWeight: '500',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        borderWidth: 1,
        borderRadius: 8,
        paddingHorizontal: 16,
        height: 52,
    },
    inputIcon: {
        marginRight: 12,
    },
    input: {
        flex: 1,
        fontSize: 16,
        height: '100%',
    },
    primaryButton: {
        height: 56,
        borderRadius: 12,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 8,
        shadowColor: '#005EB8',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 6,
    },
    primaryButtonText: {
        color: '#fff',
        fontSize: 18,
        fontWeight: '600',
    },
    footer: {
        alignItems: 'center',
        marginTop: 16,
    },
    footerLink: {
        fontSize: 14,
        fontWeight: '500',
    }

});
