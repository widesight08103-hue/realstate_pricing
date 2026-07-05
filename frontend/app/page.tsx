"use client";

import { useEffect, useState } from "react";
import {
  AreaOption,
  ComplexOut,
  PriceSeries,
  Score,
  getAreas,
  getPriceSeries,
  getScore,
  searchComplexes,
} from "@/lib/api";
import PriceChart from "@/components/PriceChart";
import ScoreBadge from "@/components/ScoreBadge";

function formatPct(v: number | null): string {
  if (v === null) return "—";
  const pct = (v * 100).toFixed(1);
  return v > 0 ? `+${pct}%` : `${pct}%`;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ComplexOut[]>([]);
  const [selectedComplex, setSelectedComplex] = useState<ComplexOut | null>(null);
  const [areas, setAreas] = useState<AreaOption[]>([]);
  const [selectedArea, setSelectedArea] = useState<number | null>(null);
  const [series, setSeries] = useState<PriceSeries | null>(null);
  const [score, setScore] = useState<Score | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.trim().length === 0) {
      setResults([]);
      return;
    }
    const timer = setTimeout(() => {
      searchComplexes(query).then(setResults).catch((e) => setError(e.message));
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    if (!selectedComplex) return;
    setAreas([]);
    setSelectedArea(null);
    getAreas(selectedComplex.id)
      .then((data) => {
        setAreas(data);
        if (data.length > 0) setSelectedArea(data[0].area);
      })
      .catch((e) => setError(e.message));
  }, [selectedComplex]);

  useEffect(() => {
    if (!selectedComplex || selectedArea === null) return;
    setError(null);
    Promise.all([
      getPriceSeries(selectedComplex.id, selectedArea),
      getScore(selectedComplex.id, selectedArea),
    ])
      .then(([s, sc]) => {
        setSeries(s);
        setScore(sc);
      })
      .catch((e) => setError(e.message));
  }, [selectedComplex, selectedArea]);

  return (
    <div className="min-h-screen bg-[#f9f9f7] dark:bg-[#0d0d0d] text-[#0b0b0b] dark:text-white">
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="text-2xl font-semibold mb-1">부동산 가치 분석</h1>
        <p className="text-sm text-[#52514e] dark:text-[#c3c2b7] mb-8">
          아파트 단지를 검색해 가격 매력도 점수와 시세 추이를 확인하세요.
        </p>

        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSelectedComplex(null);
          }}
          placeholder="단지명 검색 (예: 개포자이)"
          className="w-full rounded-lg border border-[#e1e0d9] dark:border-[#2c2c2a] bg-[#fcfcfb] dark:bg-[#1a1a19] px-4 py-2.5 text-sm outline-none focus:border-[#2a78d6]"
        />

        {results.length > 0 && !selectedComplex && (
          <ul className="mt-2 divide-y divide-[#e1e0d9] dark:divide-[#2c2c2a] rounded-lg border border-[#e1e0d9] dark:border-[#2c2c2a] overflow-hidden">
            {results.map((c) => (
              <li key={c.id}>
                <button
                  onClick={() => {
                    setSelectedComplex(c);
                    setResults([]);
                    setQuery(c.name);
                  }}
                  className="w-full text-left px-4 py-2.5 text-sm hover:bg-[#f0efec] dark:hover:bg-[#242423]"
                >
                  <span className="font-medium">{c.name}</span>
                  <span className="text-[#898781]"> · {c.legal_dong}</span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {error && <p className="mt-4 text-sm text-[#d03b3b]">{error}</p>}

        {selectedComplex && areas.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold">{selectedComplex.name}</h2>
                <p className="text-sm text-[#898781]">{selectedComplex.legal_dong}</p>
              </div>
              <select
                value={selectedArea ?? ""}
                onChange={(e) => setSelectedArea(Number(e.target.value))}
                className="rounded-lg border border-[#e1e0d9] dark:border-[#2c2c2a] bg-[#fcfcfb] dark:bg-[#1a1a19] px-3 py-2 text-sm"
              >
                {areas.map((a) => (
                  <option key={a.area} value={a.area}>
                    전용 {a.area}㎡ ({a.transaction_count}건)
                  </option>
                ))}
              </select>
            </div>

            {score && (
              <div className="mb-6 rounded-xl border border-[#e1e0d9] dark:border-[#2c2c2a] p-5">
                <p className="text-sm text-[#898781] mb-2">가격 매력도 점수</p>
                <ScoreBadge score={score.score} />
                <dl className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                  <div>
                    <dt className="text-[#898781]">전고점 대비</dt>
                    <dd className="tabular-nums">{score.detail.discount_pct_from_high.toFixed(1)}%</dd>
                  </div>
                  <div>
                    <dt className="text-[#898781]">1개월</dt>
                    <dd className="tabular-nums">{formatPct(score.detail.change_1m)}</dd>
                  </div>
                  <div>
                    <dt className="text-[#898781]">3개월</dt>
                    <dd className="tabular-nums">{formatPct(score.detail.change_3m)}</dd>
                  </div>
                  <div>
                    <dt className="text-[#898781]">1년</dt>
                    <dd className="tabular-nums">{formatPct(score.detail.change_1y)}</dd>
                  </div>
                </dl>
              </div>
            )}

            {series && series.points.length > 0 && <PriceChart points={series.points} />}
          </div>
        )}
      </main>
    </div>
  );
}
