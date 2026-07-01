import { NextRequest, NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase";
import { verifyAgentRequest } from "@/lib/hmac";

export const dynamic = "force-dynamic";

// POST /api/v1/heartbeat  (TDD §16.5)
export async function POST(req: NextRequest) {
  const raw = await req.text();
  const auth = await verifyAgentRequest(req, "/api/v1/heartbeat", raw);
  if (!auth.ok) return NextResponse.json({ error: auth.reason }, { status: 401 });

  let body: any = {};
  try { body = JSON.parse(raw || "{}"); } catch { /* ignore */ }

  const db = supabaseAdmin();
  await db
    .from("participants")
    .update({
      status: "online",
      last_heartbeat: new Date().toISOString(),
      agent_version: body.agent_version ?? null,
    })
    .eq("id", auth.participantId);

  return NextResponse.json({ ok: true });
}
