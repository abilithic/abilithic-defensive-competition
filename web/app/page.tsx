"use client";
import { useEffect, useRef, useState } from "react";
import { supabaseBrowser } from "@/lib/supabase";

type Row = { participant_id: string; full_name: string; school: string | null;
  total_score: number; rank: number; status: string };
type Comp = { id: string; name: string; difficulty: string; status: string;
  ends_at_ms: number | null; server_time_ms: number } | null;

const STATUS_LABEL: Record<string, string> = {
  waiting: "Menunggu", running: "Berlangsung", paused: "Jeda", ended: "Selesai",
};

export default function Leaderboard() {
  const [comp, setComp] = useState<Comp>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const offsetRef = useRef(0); // selisih jam server-klien

  async function load() {
    try {
      const r = await fetch("/api/v1/leaderboard", { cache: "no-store" });
      const j = await r.json();
      setComp(j.competition);
      setRows(j.rows || []);
      if (j.competition?.server_time_ms) {
        offsetRef.current = j.competition.server_time_ms - Date.now();
      }
    } catch { /* sabar */ }
  }

  useEffect(() => {
    load();
    const poll = setInterval(load, 4000); // fallback polling

    // realtime: refetch saat ada skor baru (best-effort)
    let channel: any;
    try {
      const sb: any = supabaseBrowser();
      channel = sb
        .channel("scores-stream")
        .on("postgres_changes", { event: "INSERT", schema: "public", table: "scores" }, load)
        .subscribe();
    } catch { /* realtime opsional */ }

    return () => { clearInterval(poll); try { channel?.unsubscribe(); } catch {} };
  }, []);

  // countdown tiap detik
  useEffect(() => {
    const t = setInterval(() => {
      if (comp?.status === "running" && comp.ends_at_ms) {
        const now = Date.now() + offsetRef.current;
        setRemaining(Math.max(0, Math.floor((comp.ends_at_ms - now) / 1000)));
      } else {
        setRemaining(null);
      }
    }, 1000);
    return () => clearInterval(t);
  }, [comp]);

  const fmt = (s: number | null) =>
    s == null ? "--:--" : `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="wrap">
      <div className="brand">abilithic DHC</div>
      <div className="tag">Defend. Harden. Compete. — papan skor realtime</div>

      <div className="card">
        <div className="head">
          <div>
            <div style={{ fontWeight: 700, fontSize: 18 }}>{comp?.name ?? "Belum ada sesi aktif"}</div>
            <div className="muted" style={{ fontSize: 13 }}>
              {comp ? <>Tingkat: <b>{comp.difficulty.toUpperCase()}</b></> : "Menunggu panitia membuat sesi."}
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            {comp && (
              <span className={"pill " + (comp.status === "running" ? "run" : comp.status === "waiting" ? "wait" : "")}>
                {STATUS_LABEL[comp.status] ?? comp.status}
              </span>
            )}
            <div className="timer">{fmt(remaining)}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr><th>#</th><th>Peserta</th><th>Sekolah</th><th style={{ textAlign: "right" }}>Skor</th></tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr><td colSpan={4} className="muted" style={{ padding: 20 }}>Belum ada peserta / skor.</td></tr>
            )}
            {rows.map((r) => (
              <tr key={r.participant_id} className={r.rank === 1 ? "top1" : ""}>
                <td className="rank">{r.rank}</td>
                <td>{r.full_name} {r.status === "offline" && <span className="muted">· offline</span>}</td>
                <td className="muted">{r.school ?? "—"}</td>
                <td className="score">{r.total_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="muted" style={{ fontSize: 12 }}>
        Panitia? Buka <a href="/admin">halaman admin</a>.
      </div>
    </div>
  );
}
