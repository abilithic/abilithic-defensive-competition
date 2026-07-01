import { createClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;

/** Server-side client (service_role) — HANYA dipakai di API routes. */
export function supabaseAdmin() {
  return createClient(url, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}

/** Browser client (anon) — untuk subscribe Realtime leaderboard. */
export function supabaseBrowser() {
  return createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!);
}
