import { NextRequest, NextResponse } from "next/server";
import { ADMIN_COOKIE, adminToken, passwordValid, isAdmin } from "@/lib/auth";

export const dynamic = "force-dynamic";

// GET /api/v1/admin/login  -> cek status sesi (untuk auto-detect login di UI)
export async function GET(req: NextRequest) {
  return NextResponse.json({ authed: isAdmin(req) });
}

// POST /api/v1/admin/login  { password }  -> set cookie sesi
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  if (!passwordValid(body.password || "")) {
    return NextResponse.json({ ok: false, error: "Password salah" }, { status: 401 });
  }
  const res = NextResponse.json({ ok: true });
  res.cookies.set(ADMIN_COOKIE, adminToken(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production", // https di Vercel; http saat dev lokal
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 12, // 12 jam
  });
  return res;
}

// DELETE /api/v1/admin/login  -> logout
export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.cookies.set(ADMIN_COOKIE, "", { httpOnly: true, path: "/", maxAge: 0 });
  return res;
}
