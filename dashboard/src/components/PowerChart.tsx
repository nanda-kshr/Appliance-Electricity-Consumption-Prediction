"use client";

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface PowerChartProps {
    data: any[];
}

export default function PowerChart({ data }: PowerChartProps) {
    // Format data for chart
    const formattedData = data.map((item) => ({
        time: new Date(item.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        }),
        power: item.power,
    }));

    if (!data || data.length === 0) {
        return (
            <div className="chart-empty">
                <p>Waiting for data...</p>
            </div>
        );
    }

    return (
        <div style={{ width: "100%", height: "300px" }}>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                    data={formattedData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                >
                    <defs>
                        <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorPowerCritical" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                        dataKey="time"
                        stroke="#94a3b8"
                        tick={{ fontSize: 12 }}
                        interval="preserveStartEnd"
                        minTickGap={30}
                    />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: "rgba(15, 23, 42, 0.9)",
                            border: "1px solid rgba(255,255,255,0.1)",
                            borderRadius: "8px",
                            color: "#f1f5f9",
                        }}
                    />
                    <Area
                        type="monotone"
                        dataKey="power"
                        stroke="#10b981"
                        fillOpacity={1}
                        fill="url(#colorPower)"
                        animationDuration={500}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
