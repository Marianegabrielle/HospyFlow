import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

const QUICK_ACTIONS = [
  { id: 'delay', label: 'Retard Flux', icon: 'time-outline', color: '#FF9500', typeId: 1, gravity: 'MEDIUM' },
  { id: 'breakdown', label: 'Panne Matériel', icon: 'construct-outline', color: '#FF3B30', typeId: 2, gravity: 'HIGH' },
  { id: 'missing', label: 'Manque Personnel', icon: 'people-outline', color: '#7E57C2', typeId: 3, gravity: 'HIGH' },
  { id: 'crowd', label: 'Saturation', icon: 'alert-circle-outline', color: '#E53935', typeId: 4, gravity: 'CRITICAL' },
];

export default function StaffDashboard() {
  const colorScheme = useColorScheme() ?? 'light';
  const theme = Colors[colorScheme];

  const [currentService, setCurrentService] = useState<any>(null);
  const [recentEvents, setRecentEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const services = await apiService.getServices();
      // For PoC/MVP, we pick the first service as "Current"
      if (services.length > 0) {
        setCurrentService(services[0]);
      }

      // In a real app, we'd have a dedicated recent events endpoint
      // Mocking for now as the backend ViewSet returns all
      setRecentEvents([
        { title: "Panne ECG", time: "10 min", status: "Traitée", icon: "construct", color: "#E53935" },
        { title: "Saturation", time: "45 min", status: "En cours", icon: "alert-circle", color: "#FB8C00" }
      ]);
    } catch (error) {
      console.error("Dashboard error", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickSignal = async (action: any) => {
    if (!currentService) return;

    try {
      const signalData = {
        personnel: 1, // Mock admin user ID
        service: currentService.id,
        type_flux: action.typeId,
        description: `Signal express: ${action.label}`,
        niveau_gravite: action.gravity as any,
      };

      await apiService.createEvent(signalData);
      alert("Signal envoyé avec succès !");

      // Refresh to see if state changed to TENSION
      loadDashboardData();
    } catch (error) {
      console.error("Signal error", error);
      alert("Erreur lors de l'envoi du signal.");
    }
  };

  const isTension = currentService?.etat === "TENSION";

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }]}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
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

          {/* Header */}
          <View style={styles.header}>
            <View>
              <Text style={styles.greeting}>Bonjour, Infirmier Lucas</Text>
              <Text style={styles.serviceName}>{currentService?.nom || 'Chargement...'}</Text>
            </View>
            <GlassView intensity={20} borderRadius={15} style={styles.statusPill}>
              <View style={[styles.statusDot, { backgroundColor: isTension ? theme.error : theme.success }]} />
              <Text style={styles.statusText}>{isTension ? 'ÉTAT : TENSION' : 'ÉTAT : NORMAL'}</Text>
            </GlassView>
          </View>

          {/* Quick Signaling Section */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Signaler en 1 clic</Text>
            <View style={styles.grid}>
              {QUICK_ACTIONS.map((action) => (
                <TouchableOpacity
                  key={action.id}
                  style={styles.gridItem}
                  onPress={() => handleQuickSignal(action)}
                >
                  <GlassView intensity={40} borderRadius={24} style={styles.actionCard}>
                    <View style={[styles.iconCircle, { backgroundColor: action.color + '20' }]}>
                      <Ionicons name={action.icon as any} size={28} color={action.color} />
                    </View>
                    <Text style={styles.actionLabel}>{action.label}</Text>
                  </GlassView>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* AI Bottleneck analysis */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Analyse IA (Moteur Singleton)</Text>
            <GlassView intensity={50} borderRadius={24} style={styles.aiCard}>
              <View style={styles.aiHeader}>
                <Ionicons name="sparkles" size={20} color={theme.primary} />
                <Text style={styles.aiTitle}>Prédiction de Flux</Text>
              </View>
              <Text style={styles.aiDescription}>
                Risque de saturation élevé prévu en {currentService?.nom} d'ici 1h. Renforcement conseillé.
              </Text>
            </GlassView>
          </View>

          {/* Recent Events */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Historique Récent</Text>
            </View>
            <View style={styles.historyList}>
              {recentEvents.map((event, idx) => (
                <HistoryItem
                  key={idx}
                  title={event.title}
                  time={`Il y a ${event.time}`}
                  status={event.status}
                  icon={event.icon}
                  color={event.color}
                />
              ))}
            </View>
          </View>

        </ScrollView>
      </SafeAreaView>
    </ImageBackground>
  );
}

function HistoryItem({ title, time, status, icon, color }: any) {
  return (
    <GlassView intensity={30} borderRadius={18} style={styles.historyItem}>
      <View style={[styles.historyIcon, { backgroundColor: color + '15' }]}>
        <Ionicons name={icon} size={20} color={color} />
      </View>
      <View style={{ flex: 1, marginLeft: 12 }}>
        <Text style={styles.historyTitle}>{title}</Text>
        <Text style={styles.historyTime}>{time}</Text>
      </View>
      <View style={styles.statusLabel}>
        <Text style={styles.statusLabelText}>{status}</Text>
      </View>
    </GlassView>
  );
}

const styles = StyleSheet.create({
  backgroundImage: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 32,
    marginTop: 10,
  },
  greeting: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 14,
    fontWeight: '500',
  },
  serviceName: {
    color: '#fff',
    fontSize: 22,
    fontWeight: '700',
    marginTop: 2,
  },
  statusPill: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    marginLeft: 4,
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -8,
  },
  gridItem: {
    width: '50%',
    padding: 8,
  },
  actionCard: {
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    height: 140,
  },
  iconCircle: {
    width: 60,
    height: 60,
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  actionLabel: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  aiCard: {
    padding: 20,
  },
  aiHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  aiTitle: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
    marginLeft: 8,
  },
  aiDescription: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 20,
  },
  aiButton: {
    height: 44,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  aiButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  historyList: {
    gap: 12,
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  historyIcon: {
    width: 40,
    height: 40,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  historyTitle: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
  },
  historyTime: {
    color: 'rgba(255, 255, 255, 0.5)',
    fontSize: 12,
    marginTop: 2,
  },
  statusLabel: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusLabelText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: 11,
    fontWeight: '600',
  }
});
