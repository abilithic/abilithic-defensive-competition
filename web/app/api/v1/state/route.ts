import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";
import { verifyAgentRequest } from "@/lib/hmac";

export const dynamic = "force-dynamic";

// GET /api/v1/state  (TDD §16.2) — polling inti
export async function GET(req: NextRequest) {
  const auth = await verifyAgentRequest(req, "/api/v1/state", "");
  if (!auth.ok) {
    return NextResponse.json({ error: auth.reason }, { status: 401 });
  }

  const db = supabaseAdmin();
  const { data: participant } = await db
    .from("participants")
    .select("id,competition_id")
    .eq("id", auth.participantId)
    .maybeSingle();
  if (!participant) {
    return NextResponse.json({ error: "participant tidak dikenal" }, { status: 401 });
  }

  const { data: comp } = await db
    .from("competitions")
    .select("status,difficulty,hint_policy,penalty_weight,ends_at")
    .eq("id", participant.competition_id)
    .single();
  if (!comp) return NextResponse.json({ error: "sesi tidak ditemukan" }, { status: 404 });

  // ambil daftar check aktif dari preset difficulty
  const { data: diff } = await db
    .from("difficulties")
    .select("active_check_codes")
    .eq("key", comp.difficulty)
    .maybeSingle();

  return NextResponse.json({
    status: comp.status,
    server_time_ms: Date.now(),
    ends_at_ms: comp.ends_at ? new Date(comp.ends_at).getTime() : null,
    difficulty: comp.difficulty,
    hint_policy: comp.hint_policy,
    penalty_weight: comp.penalty_weight,
    active_check_codes: diff?.active_check_codes ?? [],
  });
}
