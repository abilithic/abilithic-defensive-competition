import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";
import { deriveSecret, sha256 } from "@/lib/hmac";
import crypto from "crypto";

export const dynamic = "force-dynamic";

// POST /api/v1/register  (TDD §16.1)
export async function POST(req: NextRequest) {
  let body: any;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
  const name = (body.name || "").trim();
  const school = (body.school || "").trim();
  const sessionCode = (body.session_code || "").trim();
  if (!name || !sessionCode) {
    return NextResponse.json({ error: "name & session_code wajib" }, { status: 400 });
  }

  const db = supabaseAdmin();

  // cari sesi by kode
  const { data: comp } = await db
    .from("competitions")
    .select("id,status,difficulty,hint_policy")
    .eq("session_code", sessionCode)
    .maybeSingle();

  if (!comp) {
    return NextResponse.json({ error: "kode sesi tidak ditemukan" }, { status: 404 });
  }
  if (!["waiting", "running"].includes(comp.status)) {
    return NextResponse.json({ error: "sesi belum dibuka / sudah selesai" }, { status: 409 });
  }

  // buat peserta
  const token = crypto.randomBytes(24).toString("hex");
  const { data: participant, error } = await db
    .from("participants")
    .insert({
      competition_id: comp.id,
      full_name: name,
      school: school || null,
      agent_token_hash: sha256(token),
      agent_secret_hash: "derived", // secret diturunkan dari participant_id (TDD §11)
      status: "online",
      last_heartbeat: new Date().toISOString(),
    })
    .select("id")
    .single();

  if (error) {
    // unik (competition_id, full_name, school) bisa bentrok
    return NextResponse.json({ error: "peserta sudah terdaftar / gagal", detail: error.message }, { status: 409 });
  }

  const secret = deriveSecret(participant.id);

  await db.from("event_logs").insert({
    competition_id: comp.id,
    participant_id: participant.id,
    type: "register",
    level: "AUDIT",
    payload: { name, school },
  });

  return NextResponse.json({
    participant_id: participant.id,
    agent_token: token,
    agent_secret: secret,
    competition_id: comp.id,
    status: comp.status,
  });
}
