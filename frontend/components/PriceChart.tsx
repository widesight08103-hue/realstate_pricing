"use client";

import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PricePoint } from "@/lib/api";

const COLORS = {
  light: { series: "#2a78d6", grid: "#e1e0d9", axis: "#898781", surface: "#fcfcfb", text: "#0b0b0b" },
  dark: { series: "#3987e5", grid: "#2c2c2a", axis: "#898781", surface: "#1a1a19", text: "#ffffff" },
};

function useIsDarkMode(): boolean {
  const [isDark, setIsDark] = useState(false);
  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    setIsDark(mql.matches);
    const listener = (e: MediaQueryListEvent) => setIsDark(e.matches);
    mql.addEventListener("change", listener);
    return () => mql.removeEventListener("change", listener);
  }, []);
  return isDark;
}

function CustomTooltip({ active, payload, label, palette }: any) {
  if (!active || !payload?.length) return null;
  const point: PricePoint = payload[0].payload;
  return (
    <div
      style={{
        background: palette.surface,
        border: `1px solid ${palette.grid}`,
        borderRadius: 8,
        padding: "8px 12px",
        fontSize: 13,
        color: palette.text,
      }}
    >
      <div style={{ fontWeight: 600 }}>{label}</div>
      <div>평당가 {point.avg_price_per_pyeong.toLocaleString()}만원</div>
      <div style={{ color: palette.axis }}>거래 {point.transaction_count}건</div>
    </div>
  );
}

export default function PriceChart({ points }: { points: PricePoint[] }) {
  const isDark = useIsDarkMode();
  const palette = isDark ? COLORS.dark : COLORS.light;

  return (
    <ResponsiveContainer width="100%" height={320}>
      <LineChart data={points} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
        <CartesianGrid vertical={false} stroke={palette.grid} />
        <XAxis
          dataKey="period"
          tick={{ fill: palette.axis, fontSize: 12 }}
          axisLine={{ stroke: palette.grid }}
          tickLine={false}
          minTickGap={24}
        />
        <YAxis
          tick={{ fill: palette.axis, fontSize: 12 }}
          axisLine={false}
          tickLine={false}
          width={64}
          tickFormatter={(v: number) => `${Math.round(v / 100) / 10}천`}
        />
        <Tooltip content={<CustomTooltip palette={palette} />} />
        <Line
          type="monotone"
          dataKey="avg_price_per_pyeong"
          stroke={palette.series}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
