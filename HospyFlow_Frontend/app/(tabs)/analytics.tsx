import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ImageBackground, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { GlassView } from '@/components/ui/GlassView';
import { StatusBar } from 'expo-status-bar';
import apiService from '@/services/api';

export default function AdminAnalytics() {
  const colorScheme = useColorScheme() ?? 'light';
  const theme = Colors[colorScheme];
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [data, setData] = useState<any>(null);

  const fetchData = async () => {
    try {
      const summary = await apiService.getServicesSummary();
      setData(summary);
    } catch (error) {
      console.error("Failed to fetch analytics:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading && !refreshing) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center', backgroundColor: '#000' }]}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  const kpis = data?.kpis || { waiting_avg: '--', flux_hour: 0, risk_score: '--' };
  const services = data?.services || [];

  const STAT_CONFIG = [
    { label: 'Attente Moy.', value: kpis.waiting_avg, icon: 'time', color: '#007AFF' },
    { label: 'Flux / Heure', value: kpis.flux_hour.toString(), icon: 'trending-up', color: '#34C759' },
    { label: 'Score Risque', value: kpis.risk_score, icon: 'speedometer', color: '#FF9500' },
  ];

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
              <Text style={styles.greeting}>Console Administrative</Text>
              <Text style={styles.title}>Vue Analytique</Text>
            </View>
            <TouchableOpacity style={styles.filterButton} onPress={onRefresh}>
              <GlassView intensity={20} borderRadius={12} style={styles.filterGlass}>
                <Ionicons name="refresh-outline" size={20} color="#fff" />
              </GlassView>
            </TouchableOpacity>
          </View>

          {/* KPI Row */}
          <View style={styles.statGrid}>
            {STAT_CONFIG.map((stat, index) => (
              <GlassView key={index} intensity={40} borderRadius={20} style={styles.statCard}>
                <Ionicons name={stat.icon as any} size={24} color={stat.color} />
                <Text style={styles.statValue}>{stat.value}</Text>
                <Text style={styles.statLabel}>{stat.label}</Text>
              </GlassView>
            ))}
          </View>

          {/* Real-time Heatmap */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Saturation des Services</Text>
            <GlassView intensity={50} borderRadius={24} style={styles.heatmapCard}>
              {services.map((s: any) => (
                <HeatmapRow
                  key={s.id}
                  name={s.nom}
                  value={s.saturation}
                  color={s.etat === 'TENSION' ? '#FF3B30' : (s.saturation > 70 ? '#FF9500' : '#34C759')}
                />
              ))}
              {services.length === 0 && (
                <Text style={{ color: 'rgba(255,255,255,0.5)', textAlign: 'center' }}>Aucune donnée disponible</Text>
              )}
            </GlassView>
          </View>

          {/* Design Pattern Integration Info */}
          <View style={styles.section}>
            <GlassView intensity={30} borderRadius={20} style={styles.infoCard}>
              <View style={styles.infoHeader}>
                <Ionicons name="code-working" size={20} color={theme.primary} />
                <Text style={styles.infoTitle}>Pattern Strategy : Rapports</Text>
              </View>
              <Text style={styles.infoText}>
                Générez des rapports décisionnels basés sur les algorithmes de flux.
              </Text>
              <View style={styles.actionRow}>
                <TouchableOpacity style={styles.secondaryButton}>
                  <Text style={styles.buttonText}>Export CSV</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.primaryButton, { backgroundColor: theme.primary }]}>
                  <Text style={styles.buttonText}>Export PDF</Text>
                </TouchableOpacity>
              </View>
            </GlassView>
          </View>

        </ScrollView>
      </SafeAreaView>
    </ImageBackground>
  );
}

function HeatmapRow({ name, value, color }: any) {
  return (
    <View style={styles.heatmapRow}>
      <View style={styles.heatmapLabels}>
        <Text style={styles.serviceName}>{name}</Text>
        <Text style={styles.percentageText}>{value}%</Text>
      </View>
      <View style={styles.barBackground}>
        <View style={[styles.barFill, { width: `${value}%`, backgroundColor: color }]} />
      </View>
    </View>
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
    alignItems: 'center',
    marginBottom: 32,
    marginTop: 10,
  },
  greeting: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 14,
    fontWeight: '500',
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: '700',
  },
  filterButton: {
    width: 44,
    height: 44,
  },
  filterGlass: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 32,
  },
  statCard: {
    width: '31%',
    padding: 16,
    alignItems: 'center',
  },
  statValue: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '700',
    marginTop: 8,
  },
  statLabel: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 10,
    fontWeight: '600',
    marginTop: 2,
    textAlign: 'center',
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
  heatmapCard: {
    padding: 24,
    gap: 20,
  },
  heatmapRow: {
    width: '100%',
  },
  heatmapLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  serviceName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  percentageText: {
    color: 'rgba(255, 255, 255, 0.6)',
    fontSize: 14,
    fontWeight: '500',
  },
  barBackground: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
  },
  infoCard: {
    padding: 20,
  },
  infoHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  infoTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 8,
  },
  infoText: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 20,
  },
  actionRow: {
    flexDirection: 'row',
    gap: 12,
  },
  primaryButton: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryButton: {
    flex: 1,
    height: 48,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  }
});
