import React from 'react';
import { StyleSheet, View, ViewProps, Platform } from 'react-native';
import { BlurView } from 'expo-blur';
import { Glass, Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

interface GlassViewProps extends ViewProps {
    intensity?: number;
    borderRadius?: number;
}

export function GlassView({
    children,
    style,
    intensity = 50,
    borderRadius = 16,
    ...props
}: GlassViewProps) {
    const colorScheme = useColorScheme() ?? 'light';
    const glassStyle = Glass[colorScheme];

    if (Platform.OS === 'ios') {
        return (
            <BlurView
                intensity={intensity}
                tint={colorScheme}
                style={[
                    styles.glass,
                    glassStyle,
                    { borderRadius, overflow: 'hidden' },
                    style
                ]}
                {...props}
            >
                {children}
            </BlurView>
        );
    }

    // Android/Web Fallback
    return (
        <View
            style={[
                styles.glass,
                glassStyle,
                { borderRadius },
                style
            ]}
            {...props}
        >
            {children}
        </View>
    );
}

const styles = StyleSheet.create({
    glass: {
        borderWidth: 1,
    },
});
