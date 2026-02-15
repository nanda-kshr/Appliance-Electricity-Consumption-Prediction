"use client";

import { useEffect, useState } from "react";
import {
  Zap,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Activity
} from "lucide-react";
import PowerChart from "@/components/PowerChart";

interface Alert {
  _id: string;
  timestamp: string;
  appliance_id: string;
  power: number;
  threshold: number;
  message: string;
}

interface Reading {
  _id: string;
  timestamp: string;
  power: number;
}

export default function Home() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch Alerts
      const resAlerts = await fetch("http://localhost:8000/alerts/recent");
      const dataAlerts = await resAlerts.json();
      setAlerts(dataAlerts.alerts);

      // Fetch Readings (for Chart)
      const resReadings = await fetch("http://localhost:8000/readings/recent");
      const dataReadings = await resReadings.json();
      setReadings(dataReadings.readings);

      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 10 seconds for "Live" feel
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const latestAlert = alerts.length > 0 ? alerts[0] : null;

  // Determine status
  const isCritical = latestAlert &&
    (new Date().getTime() - new Date(latestAlert.timestamp).getTime()) < 5 * 60 * 1000;

  return (
    <main className="container">
      <header className="header">
        <div className="logo-section">
          <div className="logo-icon-bg">
            <Zap className="logo-icon" size={28} />
          </div>
          <h1>Energy Monitor</h1>
        </div>

        <div className={`status-badge ${isCritical ? 'critical' : 'normal'}`}>
          {isCritical ? (
            <>
              <AlertTriangle size={16} /> CRITICAL ALERT
            </>
          ) : (
            <>
              <CheckCircle size={16} /> SYSTEM NORMAL
            </>
          )}
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Real-time Current Status */}
        <div className="card hero-card">
          <div className="card-header-simple">
            <h2><Activity size={20} /> Current Status</h2>
          </div>

          <div className="hero-content">
            <div className={`hero-icon-lg ${isCritical ? 'animate-pulse-fast' : ''}`}>
              {isCritical ? <AlertTriangle size={64} color="#ef4444" /> : <CheckCircle size={64} color="#10b981" />}
            </div>
            <div className="hero-text">
              {isCritical ? (
                <>
                  <h3 className="text-red">Spike Detected!</h3>
                  <p className="status-desc">{latestAlert?.message}</p>
                </>
              ) : (
                <>
                  <h3 className="text-green">All Systems Safe</h3>
                  <p className="status-desc">Power consumption is within expected range.</p>
                </>
              )}
            </div>
          </div>
          <div className="updated-at">
            Last updated: {lastUpdated?.toLocaleTimeString()}
          </div>
        </div>

        {/* Live Power Chart */}
        <div className="card chart-card">
          <div className="card-header-simple">
            <h2><Zap size={20} /> Live Power Usage (Last Hour)</h2>
          </div>
          <div className="chart-container">
            <PowerChart data={readings} />
          </div>
        </div>

        {/* Recent Alerts List (Full Width on Mobile, Col span 2 on Desktop if desired, or just below) */}
        <div className="card list-card full-width">
          <div className="card-header">
            <h2>Recent Alerts</h2>
            <button onClick={fetchData} className="refresh-btn">
              <RefreshCw size={14} className={loading ? "spin" : ""} /> Refresh
            </button>
          </div>

          <div className="alerts-list">
            {alerts.length === 0 ? (
              <div className="empty-state">
                <CheckCircle size={48} className="text-muted" />
                <p>No alerts in the last hour. Great job!</p>
              </div>
            ) : (
              alerts.map((alert) => (
                <div key={alert._id} className="alert-item">
                  <div className="alert-icon">
                    <AlertTriangle size={20} color="#ef4444" />
                  </div>
                  <div className="alert-content">
                    <div className="alert-top">
                      <span className="appliance-tag">{alert.appliance_id}</span>
                      <span className="alert-time">
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="alert-values">
                      <span className="power-val">{alert.power}W</span>
                      <span className="threshold-val"> / {alert.threshold.toFixed(2)}W Limit</span>
                    </div>
                    <div className="alert-msg">{alert.message}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
