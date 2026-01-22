import React from 'react';
import { StyleSheet, Text, View, ScrollView, Dimensions, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/use-color-scheme';

const { width } = Dimensions.get('window');

// Mock Data for the chart
const HOURLY_FLOW = [30, 45, 28, 80, 99, 43, 50, 60, 70, 40, 30, 20];

export default function DashboardScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={[styles.greeting, { color: theme.textSecondary }]}>Bienvenue, Dr. Admin</Text>
            <Text style={[styles.title, { color: theme.text }]}>Dashboard Global</Text>
          </View>
          <TouchableOpacity style={[styles.profileButton, { backgroundColor: theme.surface }]}>
            <Ionicons name="notifications-outline" size={24} color={theme.text} />
            <View style={styles.badge} />
          </TouchableOpacity>
        </View>

        {/* KPI Cards */}
        <View style={styles.kpiContainer}>
          <KpiCard
            title="Incidents"
            value="3"
            icon="warning"
            color={theme.error}
            theme={theme}
            trend="+1 vs hier"
          />
          <KpiCard
            title="Temps d'attente"
            value="45m"
            icon="time"
            color={theme.primary}
            theme={theme}
            trend="-5m"
            trendPositive
          />
          <KpiCard
            title="Alertes Actives"
            value="12"
            icon="notifications-circle"
            color="#F57C00"
            theme={theme}
          />
        </View>

        {/* Main Chart Section */}
        <View style={[styles.section, { backgroundColor: theme.surface }]}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Flux Opérationnel</Text>
            <Text style={[styles.sectionSubtitle, { color: theme.textSecondary }]}>Passages aux urgences / heure</Text>
          </View>

          <View style={styles.chartContainer}>
            {/* Simple Bar Chart Visualization */}
            <View style={styles.chart}>
              {HOURLY_FLOW.map((value, index) => (
                <View key={index} style={styles.barContainer}>
                  <View
                    style={[
                      styles.bar,
                      {
                        height: `${value}%`,
                        backgroundColor: value > 80 ? theme.error : theme.primary
                      }
                    ]}
                  />
                  <Text style={[styles.barLabel, { color: theme.textSecondary }]}>{index}h</Text>
                </View>
              ))}
            </View>
          </View>
        </View>

        {/* Critical Services Summary */}
        <View style={styles.sectionContainer}>
          <Text style={[styles.sectionHeading, { color: theme.text }]}>Services Sous Pression</Text>

          <ServiceCard
            name="Urgences"
            status="Critique"
            occupancy={95}
            waitingTime="2h 15m"
            theme={theme}
            isCritical
          />
          <ServiceCard
            name="Radiologie"
            status="Chargé"
            occupancy={78}
            waitingTime="45m"
            theme={theme}
          />
          <ServiceCard
            name="Cardiologie"
            status="Normal"
            occupancy={40}
            waitingTime="10m"
            theme={theme}
          />
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

// Sub-components
function KpiCard({ title, value, icon, color, theme, trend, trendPositive }: any) {
  return (
    <View style={[styles.card, { backgroundColor: theme.surface }]}>
      <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
        <Ionicons name={icon} size={24} color={color} />
      </View>
      <View>
        <Text style={[styles.cardValue, { color: theme.text }]}>{value}</Text>
        <Text style={[styles.cardTitle, { color: theme.textSecondary }]}>{title}</Text>
        {trend && (
          <Text style={[styles.trend, { color: trendPositive ? theme.success : theme.error }]}>
            {trend}
          </Text>
        )}
      </View>
    </View>
  );
}

function ServiceCard({ name, status, occupancy, waitingTime, theme, isCritical }: any) {
  return (
    <View style={[styles.serviceCard, { backgroundColor: theme.surface }]}>
      <View style={styles.serviceHeader}>
        <Text style={[styles.serviceName, { color: theme.text }]}>{name}</Text>
        <View style={[styles.statusBadge, { backgroundColor: isCritical ? theme.error + '20' : theme.success + '20' }]}>
          <Text style={[styles.statusText, { color: isCritical ? theme.error : theme.success }]}>{status}</Text>
        </View>
      </View>

      <View style={styles.serviceStats}>
        <View>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Occupation</Text>
          <Text style={[styles.statValue, { color: theme.text }]}>{occupancy}%</Text>
        </View>
        <View>
          <Text style={[styles.statLabel, { color: theme.textSecondary }]}>Attente</Text>
          <Text style={[styles.statValue, { color: theme.text }]}>{waitingTime}</Text>
        </View>
        <View style={{ flex: 1, alignItems: 'flex-end', justifyContent: 'center' }}>
          <Ionicons name="chevron-forward" size={20} color={theme.textSecondary} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
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
    marginBottom: 24,
  },
  greeting: {
    fontSize: 14,
    fontWeight: '500',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
  },
  profileButton: {
    padding: 10,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  badge: {
    position: 'absolute',
    top: 10,
    right: 12,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#D32F2F',
    borderWidth: 1,
    borderColor: '#fff',
  },
  kpiContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
    gap: 12,
  },
  card: {
    flex: 1,
    padding: 16,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
    alignItems: 'flex-start',
    gap: 12,
  },
  iconContainer: {
    padding: 8,
    borderRadius: 10,
  },
  cardValue: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 12,
    fontWeight: '500',
  },
  trend: {
    fontSize: 12,
    fontWeight: '600',
    marginTop: 4,
  },
  section: {
    borderRadius: 20,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
  },
  sectionHeader: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 13,
    fontWeight: '400',
  },
  chartContainer: {
    height: 180,
  },
  chart: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    gap: 8,
  },
  barContainer: {
    flex: 1,
    height: '100%',
    justifyContent: 'flex-end',
    alignItems: 'center',
    gap: 8,
  },
  bar: {
    width: '100%',
    borderRadius: 6,
    minHeight: 4,
  },
  barLabel: {
    fontSize: 10,
  },
  sectionContainer: {
    gap: 16,
  },
  sectionHeading: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 4,
  },
  serviceCard: {
    padding: 16,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  serviceStats: {
    flexDirection: 'row',
    gap: 24,
  },
  statLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
  },
});
