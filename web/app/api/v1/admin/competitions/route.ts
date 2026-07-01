import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

export const dynamic = "force-dynamic";

// Admin auth sederhana v0.1 (TDD §37: JWT penuh menyusul)
function checkAdmin(req: NextRequest): boolean {
  const pw = req.headers.get("x-admin-password") || "";
  return pw === (process.env.ADMIN_PASSWORD || "");
}

function genCode(): string {
  const s = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let out = "DHC-";
  for (let i = 0; i < 4; i++) out += s[Math.floor(Math.random() * s.length)];
  return out;
}

// GET /api/v1/admin/competitions — daftar sesi + peserta ringkas
export async function GET(req: NextRequest) {
  if (!checkAdmin(req)) return NextResponse.json({ error: "unauthorized" }, { status: 403 });
  const db = supabaseAdmin();
  const { data: comps } = await db
    .from("competitions")
    .select("*")
    .order("created_at", { ascending: false });
  return NextResponse.json({ competitions: comps ?? [] });
}

// POST /api/v1/admin/competitions
//   { action: "create", name, difficulty }                       -> buat sesi
//   { action: "start"|"pause"|"resume"|"stop", competition_id }  -> kontrol
export async function POST(req: NextRequest) {
  if (!checkAdmin(req)) return NextResponse.json({ error: "unauthorized" }, { status: 403 });
  const body = await req.json().catch(() => ({}));
  const db = supabaseAdmin();
  const action = body.action;

  if (action === "create") {
    const difficulty = ["easy", "medium", "hard"].includes(body.difficulty) ? body.difficulty : "easy";
    const { data: diff } = await db
      .from("difficulties")
      .select("hint_policy,penalty_weight,default_duration_sec")
      .eq("key", difficulty)
      .single();
    const { data: comp, error } = await db
      .from("competitions")
      .insert({
        name: (body.name || "Lomba DHC").trim(),
        difficulty,
        status: "waiting",
        duration_sec: diff?.default_duration_sec ?? 5400,
        hint_policy: diff?.hint_policy ?? "full",
        penalty_weight: diff?.penalty_weight ?? 1.0,
        session_code: genCode(),
      })
      .select("*")
      .single();
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ competition: comp });
  }

  const id = body.competition_id;
  if (!id) return NextResponse.json({ error: "competition_id wajib" }, { status: 400 });

  const { data: comp } = await db.from("competitions").select("*").eq("id", id).single();
  if (!comp) return NextResponse.json({ error: "sesi tidak ditemukan" }, { status: 404 });

  let patch: any = {};
  const now = Date.now();

  if (action === "start") {
    patch = {
      status: "running",
      started_at: new Date(now).toISOString(),
      ends_at: new Date(now + comp.duration_sec * 1000).toISOString(),
    };
  } else if (action === "pause") {
    patch = { status: "paused" };
  } else if (action === "resume") {
    // geser ends_at sebesar sisa (sederhana: pertahankan ends_at)
    patch = { status: "running" };
  } else if (action === "stop") {
    patch = { status: "ended" };
  } else {
    return NextResponse.json({ error: "action tidak dikenal" }, { status: 400 });
  }

  const { data: updated, error } = await db
    .from("competitions").update(patch).eq("id", id).select("*").single();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  await db.from("event_logs").insert({
    competition_id: id, type: `competition_${action}`, level: "AUDIT", payload: patch,
  });

  return NextResponse.json({ competition: updated });
}
