"use client";
import { useEffect, useRef, useState } from "react";
import { supabaseBrowser } from "@/lib/supabase";

type Row = { participant_id: string; full_name: string; school: string | null;
  total_score: number; rank: number; status: string };
type Comp = { id: string; name: string; difficulty: string; status: string;
  ends_at_ms: number | null; server_time_ms: number } | null;

const STATUS_LABEL: Record<string, string> = {
  waiting: "Menunggu", running: "Berlangsung", paused: "Jeda", ended: "Selesai", archived: "Arsip",
};
const DIFF_LABEL: Record<string, string> = { easy: "Mudah", medium: "Medium", hard: "Hard" };
const MEDAL = ["🥇", "🥈", "🥉"];

export default function Leaderboard() {
  const [comp, setComp] = useState<Comp>(null);
  const [rows, setRows] = useState<Row[]>([]);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);
  const offsetRef = useRef(0);

  async function load() {
    try {
      const r = await fetch("/api/v1/leaderboard", { cache: "no-store" });
      const j = await r.json();
      setComp(j.competition);
      setRows(j.rows || []);
      if (j.competition?.server_time_ms) offsetRef.current = j.competition.server_time_ms - Date.now();
    } catch { /* diam */ } finally { setLoaded(true); }
  }

  useEffect(() => {
    load();
    const poll = setInterval(load, 4000);
    let channel: any;
    try {
      const sb: any = supabaseBrowser();
      channel = sb.channel("scores-stream")
        .on("postgres_changes", { event: "INSERT", schema: "public", table: "scores" }, load)
        .subscribe();
    } catch { /* realtime opsional */ }
    return () => { clearInterval(poll); try { channel?.unsubscribe(); } catch {} };
  }, []);

  useEffect(() => {
    const t = setInterval(() => {
      if (comp?.status === "running" && comp.ends_at_ms) {
        const now = Date.now() + offsetRef.current;
        setRemaining(Math.max(0, Math.floor((comp.ends_at_ms - now) / 1000)));
      } else setRemaining(null);
    }, 1000);
    return () => clearInterval(t);
  }, [comp]);

  const fmt = (s: number | null) =>
    s == null ? "--:--" : `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  return (
    <div className="wrap">
      <div className="topbar">
        <div className="brand">
          <div className="logo"><img src="/abilithic-icon-256.png" alt="abilithic" /></div>
          <div><h1>abilithic DHC</h1><div className="sub">Defend · Harden · Compete</div></div>
        </div>
        <a href="/admin" className="badge">Panitia</a>
      </div>

      <div className="card">
        <div className="head">
          <div>
            <div style={{ fontWeight: 800, fontSize: 20 }}>{comp?.name ?? (loaded ? "Belum ada sesi aktif" : "Memuat…")}</div>
            <div className="small muted" style={{ marginTop: 5, display: "flex", gap: 8, alignItems: "center" }}>
              {comp ? (<>
                <span className={"badge " + comp.status}>{STATUS_LABEL[comp.status] ?? comp.status}</span>
                <span>Tingkat {DIFF_LABEL[comp.difficulty] ?? comp.difficulty}</span>
              </>) : "Menunggu panitia membuat & memulai sesi."}
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="small muted">SISA WAKTU</div>
            <div className="timer" style={{ color: remaining !== null && remaining < 60 ? "var(--danger)" : "var(--fg)" }}>{fmt(remaining)}</div>
          </div>
        </div>
      </div>

      <div className="card">
        <table>
          <thead><tr><th>#</th><th>Peserta</th><th>Sekolah</th><th style={{ textAlign: "right" }}>Skor</th></tr></thead>
          <tbody>
            {!loaded && [0, 1, 2].map((i) => (
              <tr key={i}>
                <td><div className="skel-row" style={{ width: 20 }} /></td>
                <td><div className="skel-row" style={{ width: 140 }} /></td>
                <td><div className="skel-row" style={{ width: 90 }} /></td>
                <td><div className="skel-row" style={{ width: 50, marginLeft: "auto" }} /></td>
              </tr>
            ))}
            {loaded && rows.length === 0 && <tr><td colSpan={4} className="empty">Belum ada peserta terdaftar.</td></tr>}
            {rows.map((r) => (
              <tr key={r.participant_id} className={r.rank === 1 ? "top1" : ""}>
                <td className="rank">{r.rank <= 3 ? MEDAL[r.rank - 1] : r.rank}</td>
                <td>
                  <span style={{ fontWeight: 600 }}>{r.full_name}</span>
                  {r.status === "offline" && <span className="small muted"> · offline</span>}
                  {r.status === "disqualified" && <span className="small" style={{ color: "var(--danger)" }}> · DQ</span>}
                </td>
                <td className="muted">{r.school ?? "—"}</td>
                <td className="score">{r.total_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="small muted" style={{ textAlign: "center", display: "flex", justifyContent: "center", gap: 8, alignItems: "center" }}>
        <span className="live-tag"><span className="live-dot" /> Live</span>
        <span>· Papan skor memperbarui otomatis · abilithic DHC</span>
      </div>
    </div>
  );
}
