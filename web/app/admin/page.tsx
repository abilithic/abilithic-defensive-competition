"use client";
import { useEffect, useState } from "react";

type Comp = {
  id: string; name: string; difficulty: string; status: string;
  session_code: string; duration_sec: number;
};

export default function Admin() {
  const [pw, setPw] = useState("");
  const [authed, setAuthed] = useState(false);
  const [comps, setComps] = useState<Comp[]>([]);
  const [name, setName] = useState("Lomba DHC #1");
  const [difficulty, setDifficulty] = useState("easy");
  const [msg, setMsg] = useState("");

  async function api(method: string, body?: any) {
    const r = await fetch("/api/v1/admin/competitions", {
      method,
      headers: { "Content-Type": "application/json", "x-admin-password": pw },
      body: body ? JSON.stringify(body) : undefined,
    });
    return r;
  }

  async function load() {
    const r = await api("GET");
    if (r.status === 403) { setAuthed(false); setMsg("Password admin salah."); return; }
    const j = await r.json();
    setAuthed(true); setMsg("");
    setComps(j.competitions || []);
  }

  async function create() {
    const r = await api("POST", { action: "create", name, difficulty });
    const j = await r.json();
    if (j.competition) setMsg(`Sesi dibuat. Kode: ${j.competition.session_code}`);
    load();
  }

  async function control(id: string, action: string) {
    if (action === "stop" && !confirm("Hentikan lomba? Skor akan dibekukan.")) return;
    await api("POST", { action, competition_id: id });
    load();
  }

  useEffect(() => { /* tunggu login */ }, []);

  if (!authed) {
    return (
      <div className="wrap" style={{ maxWidth: 420 }}>
        <div className="brand">abilithic DHC · Admin</div>
        <div className="tag">Masuk untuk mengelola lomba.</div>
        <div className="card">
          <label>Password Admin</label>
          <input type="password" value={pw} onChange={(e) => setPw(e.target.value)}
                 onKeyDown={(e) => e.key === "Enter" && load()} placeholder="••••••••" />
          <div className="row-actions"><button onClick={load}>Masuk</button></div>
          {msg && <div className="muted" style={{ marginTop: 10 }}>{msg}</div>}
        </div>
        <div className="muted" style={{ fontSize: 12 }}><a href="/">← Leaderboard</a></div>
      </div>
    );
  }

  return (
    <div className="wrap">
      <div className="head">
        <div>
          <div className="brand">abilithic DHC · Admin</div>
          <div className="tag">Kelola sesi & kontrol lomba.</div>
        </div>
        <a href="/" className="pill">Lihat Leaderboard →</a>
      </div>

      <div className="card">
        <strong>Buat Sesi Baru</strong>
        <div className="grid2" style={{ marginTop: 8 }}>
          <div>
            <label>Nama lomba</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div>
            <label>Tingkat kesulitan</label>
            <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="easy">Mudah (Easy)</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>
        <div className="row-actions"><button onClick={create}>+ Buat Sesi</button></div>
        {msg && <div className="muted" style={{ marginTop: 10 }}>{msg}</div>}
      </div>

      <div className="card">
        <strong>Daftar Sesi</strong>
        {comps.length === 0 && <div className="muted" style={{ marginTop: 10 }}>Belum ada sesi.</div>}
        {comps.map((c) => (
          <div key={c.id} style={{ borderTop: "1px solid var(--line)", paddingTop: 12, marginTop: 12 }}>
            <div className="head">
              <div>
                <div style={{ fontWeight: 700 }}>{c.name}</div>
                <div className="muted" style={{ fontSize: 13 }}>
                  Tingkat {c.difficulty.toUpperCase()} · Kode: <span className="code">{c.session_code}</span> · Status: <b>{c.status}</b>
                </div>
              </div>
            </div>
            <div className="row-actions">
              <button onClick={() => control(c.id, "start")} disabled={c.status !== "waiting" && c.status !== "paused"}>▶ Start</button>
              <button className="sec" onClick={() => control(c.id, "pause")} disabled={c.status !== "running"}>⏸ Pause</button>
              <button className="danger" onClick={() => control(c.id, "stop")} disabled={c.status === "ended" || c.status === "archived"}>⏹ Stop</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
