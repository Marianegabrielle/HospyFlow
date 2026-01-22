import { Tabs } from 'expo-router';
import React from 'react';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function TabLayout() {
  const colorScheme = useColorScheme() ?? 'light';
  const theme = Colors[colorScheme];

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: theme.primary,
        tabBarInactiveTintColor: 'rgba(142, 142, 147, 0.8)',
        headerShown: false,
        tabBarStyle: {
          backgroundColor: colorScheme === 'dark' ? '#000' : '#fff',
          borderTopWidth: 0,
          elevation: 0,
          height: 60,
          paddingBottom: 10,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color }) => <Ionicons size={24} name="grid-outline" color={color} />,
        }}
      />
      <Tabs.Screen
        name="report"
        options={{
          title: 'Signaler',
          tabBarIcon: ({ color }) => <Ionicons size={24} name="add-circle" color={color} />,
        }}
      />
      <Tabs.Screen
        name="services"
        options={{
          title: 'Services',
          tabBarIcon: ({ color }) => <Ionicons size={24} name="business" color={color} />,
        }}
      />
      <Tabs.Screen
        name="alerts"
        options={{
          title: 'Alertes',
          tabBarIcon: ({ color }) => <Ionicons size={24} name="notifications" color={color} />,
        }}
      />
      <Tabs.Screen
        name="menu"
        options={{
          title: 'Plus',
          tabBarIcon: ({ color }) => <Ionicons size={24} name="ellipsis-horizontal-circle" color={color} />,
        }}
      />

      {/* Hidden Screens from the tab bar but accessible via navigation */}
      <Tabs.Screen name="incidents" options={{ href: null }} />
      <Tabs.Screen name="analytics" options={{ href: null }} />
      <Tabs.Screen name="users" options={{ href: null }} />
      <Tabs.Screen name="settings" options={{ href: null }} />
    </Tabs>
  );
}
