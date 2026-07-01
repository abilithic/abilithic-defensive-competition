import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";
import { isAdmin } from "@/lib/auth";

export const dynamic = "force-dynamic";

// GET /api/v1/admin/participants?comp=<id> — daftar peserta sebuah sesi
export async function GET(req: NextRequest) {
  if (!isAdmin(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const compId = new URL(req.url).searchParams.get("comp");
  if (!compId) return NextResponse.json({ participants: [] });

  const db = supabaseAdmin();
  const { data } = await db
    .from("participants")
    .select("id, full_name, school, status, agent_version, last_heartbeat, created_at")
    .eq("competition_id", compId)
    .order("created_at", { ascending: true });
  return NextResponse.json({ participants: data ?? [] });
}

// POST /api/v1/admin/participants  { action: "disqualify"|"remove", participant_id }
export async function POST(req: NextRequest) {
  if (!isAdmin(req)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const body = await req.json().catch(() => ({}));
  const db = supabaseAdmin();
  const pid = body.participant_id;
  if (!pid) return NextResponse.json({ error: "participant_id wajib" }, { status: 400 });

  if (body.action === "remove") {
    const { error } = await db.from("participants").delete().eq("id", pid);
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ ok: true });
  }
  if (body.action === "disqualify") {
    const { error } = await db.from("participants").update({ status: "disqualified" }).eq("id", pid);
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ ok: true });
  }
  if (body.action === "requalify") {
    // batalkan diskualifikasi (mis. tidak sengaja ter-klik) -> kembali online
    const { error } = await db.from("participants").update({ status: "online" }).eq("id", pid);
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ ok: true });
  }
  return NextResponse.json({ error: "action tidak dikenal" }, { status: 400 });
}
