import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

export const dynamic = "force-dynamic";

// GET /api/v1/leaderboard?comp=<id>  (publik) — data papan skor
// Tanpa comp: ambil sesi aktif terbaru (running/paused/waiting).
export async function GET(req: NextRequest) {
  const db = supabaseAdmin();
  const url = new URL(req.url);
  let compId = url.searchParams.get("comp");

  let comp: any;
  if (compId) {
    const { data } = await db.from("competitions").select("*").eq("id", compId).maybeSingle();
    comp = data;
  } else {
    const { data } = await db
      .from("competitions")
      .select("*")
      .in("status", ["running", "paused", "waiting", "ended"])
      .order("created_at", { ascending: false })
      .limit(1)
      .maybeSingle();
    comp = data;
  }

  if (!comp) return NextResponse.json({ competition: null, rows: [] });

  const { data: rows } = await db
    .from("leaderboard")
    .select("*")
    .eq("competition_id", comp.id)
    .order("rank", { ascending: true });

  return NextResponse.json({
    competition: {
      id: comp.id,
      name: comp.name,
      difficulty: comp.difficulty,
      status: comp.status,
      ends_at_ms: comp.ends_at ? new Date(comp.ends_at).getTime() : null,
      server_time_ms: Date.now(),
    },
    rows: rows ?? [],
  });
}
