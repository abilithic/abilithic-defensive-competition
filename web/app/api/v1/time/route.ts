import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;
export const fetchCache = "force-no-store";

const NO_CACHE = {
  "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
  "CDN-Cache-Control": "no-store",
  "Vercel-CDN-Cache-Control": "no-store",
};

// GET /api/v1/time — TIDAK di-signing, sengaja publik & tanpa auth.
//
// Alasan (lihat docs/REVIEW-AND-CONCEPT-v2.md §2.1): endpoint agen lain (/state,
// /score, /heartbeat, /snapshot) mewajibkan HMAC + jendela toleransi jam
// (±5 menit, lihat lib/hmac.ts). Bila jam VM peserta ngaco (umum pada VM
// hasil clone/template VMware tanpa NTP), SEMUA request bersanding gagal
// diam-diam sampai jam VM dikoreksi manual — inilah akar masalah "skor/
// timestamp tidak update otomatis".
//
// Endpoint ini memberi agen cara mengukur clock-skew-nya SEBELUM mengirim
// request ber-signing apa pun (ayam-telur: butuh request untuk tahu skew,
// tapi request ber-signing butuh jam yang sudah benar). Agen memanggil ini
// tiap siklus sinkron, menghitung offset = server_time_ms - waktu_lokal, lalu
// menambahkan offset itu ke timestamp yang dipakai untuk menandatangani
// request berikutnya. Hasilnya: benar-benar otomatis, tanpa perlu refresh
// jam Ubuntu/VMware secara manual.
export async function GET() {
  return NextResponse.json({ server_time_ms: Date.now() }, { headers: NO_CACHE });
}
