import crypto from "crypto";
import { NextRequest } from "next/server";

const SECRET = process.env.AGENT_HMAC_SECRET || "dev-secret";
export const ADMIN_COOKIE = "dhc_admin";

/** Token sesi admin (hanya bisa dihasilkan server yang tahu ADMIN_PASSWORD). */
export function adminToken(): string {
  return crypto
    .createHmac("sha256", SECRET)
    .update("dhc-admin-session::" + (process.env.ADMIN_PASSWORD || ""))
    .digest("hex");
}

export function passwordValid(pw: string): boolean {
  const expected = process.env.ADMIN_PASSWORD || "";
  if (!expected) return false;
  const a = Buffer.from(pw);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

/** Verifikasi cookie sesi admin pada request. */
export function isAdmin(req: NextRequest): boolean {
  const c = req.cookies.get(ADMIN_COOKIE)?.value;
  if (!c) return false;
  const expected = adminToken();
  const a = Buffer.from(c);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
