const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export type ComplexOut = {
  id: number;
  name: string;
  legal_dong: string;
  sigungu_code: string;
  jibun: string | null;
  build_year: number | null;
};

export type AreaOption = {
  area: number;
  transaction_count: number;
};

export type PricePoint = {
  period: string;
  avg_price_per_pyeong: number;
  transaction_count: number;
};

export type PriceSeries = {
  complex_id: number;
  area: number;
  points: PricePoint[];
};

export type ScoreDetail = {
  discount_pct_from_high: number;
  change_1m: number | null;
  change_3m: number | null;
  change_6m: number | null;
  change_1y: number | null;
  recent_volume: number;
  baseline_volume: number;
};

export type Score = {
  complex_id: number;
  area: number;
  score: number;
  detail: ScoreDetail;
};

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `요청 실패 (${res.status})`);
  }
  return res.json();
}

export function searchComplexes(query: string): Promise<ComplexOut[]> {
  return getJson(`/api/complexes?query=${encodeURIComponent(query)}`);
}

export function getAreas(complexId: number): Promise<AreaOption[]> {
  return getJson(`/api/complexes/${complexId}/areas`);
}

export function getPriceSeries(complexId: number, area: number): Promise<PriceSeries> {
  return getJson(`/api/complexes/${complexId}/price-series?area=${area}`);
}

export function getScore(complexId: number, area: number): Promise<Score> {
  return getJson(`/api/complexes/${complexId}/score?area=${area}`);
}
