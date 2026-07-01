import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";

export const dynamic = "force-dynamic";
export const revalidate = 0;

// GET /api/v1/leaderboard?comp=<id>  (publik) — data papan skor
// Tanpa comp: ambil sesi aktif terbaru (running/paused/waiting/ended).
// Menyertakan blok "debug" untuk diagnosa (aman dibuka publik: tak ada rahasia).
export async function GET(req: NextRequest) {
  const db = supabaseAdmin();
  const url = new URL(req.url);
  const compId = url.searchParams.get("comp");

  // Diagnostik: berapa total sesi yang DILIHAT oleh deployment ini?
  const { count: totalComps, error: countErr } = await db
    .from("competitions")
    .select("*", { count: "exact", head: true });

  let comp: any = null;
  let selErr: string | null = null;

  if (compId) {
    const { data, error } = await db
      .from("competitions").select("*").eq("id", compId).limit(1);
    comp = data?.[0] ?? null;
    selErr = error?.message ?? null;
  } else {
    const { data, error } = await db
      .from("competitions")
      .select("*")
      .in("status", ["running", "paused", "waiting", "ended"])
      .order("created_at", { ascending: false })
      .limit(1);
    comp = data?.[0] ?? null;
    selErr = error?.message ?? null;
  }

  if (!comp) {
    return NextResponse.json({
      competition: null,
      rows: [],
      debug: {
        total_competitions: totalComps ?? null,
        count_error: countErr?.message ?? null,
        select_error: selErr,
      },
    });
  }

  const { data: rows, error: rowsErr } = await db
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
    debug: {
      total_competitions: totalComps ?? null,
      rows_error: rowsErr?.message ?? null,
    },
  });
}
