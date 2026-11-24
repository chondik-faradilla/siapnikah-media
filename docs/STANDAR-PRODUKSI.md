# Standar produksi konten sosmed siapnikah.id

Ditetapkan pemilik (Chondik), 24 Nov 2026. WAJIB dibaca dan dipatuhi setiap run produksi.

## Goal
- **2 posting video per hari, tiap hari:** slot -a tayang 11:30 WIB, slot -b tayang 19:30 WIB, di IG Reels + FB Reels (Halaman Siapnikah.id) + **YouTube Shorts @kata2positif** (dijadwalkan lewat YouTube Studio di Chrome, lihat `docs/YOUTUBE-UPLOAD.md`). Threads menyusul setelah THREADS_TOKEN diisi.
- Tujuan bisnis: mendatangkan orang yang serius menikah ke siapnikah.id (CTA "Cek kesiapanmu, gratis — siapnikah.id").
- Tanpa menunggu instruksi pemilik: selama laptop menyala, produksi, QA, dan perbaikan dikerjakan sendiri. Pemilik cukup menerima laporan.

## Standar setiap video (tidak boleh kurang satu pun)
1. **Voice over** — Gemini "Sulap Suara" (https://gemini.google.com/share/360bcd383090 → Tulisan ke Suara), suara Achernar (perempuan) atau variasi laki-laki, Gaya Bicara "Hangat, tenang, seperti kakak yang bijak". File .wav diunduh ke C:\Users\Lenovo\Downloads lalu diambil lewat alat perangkat. Satu kalimat VO per scene.
2. **Motion graphic** 9:16 1080x1920 gaya brand (krem #F8F4E3, hijau #105C43/#2D6A4F, mint #95D5B2, oranye #E76F51; Plus Jakarta Sans + aksen Fraunces italic; karakter pose siapnikah; logo). Panjang tiap scene mengikuti kalimat VO-nya (perlambat animasi maks 1,35x lalu tahan frame terakhir).
3. **B-roll Pixabay 2–4 klip** per video, 2,5–5 detik, berselang-seling dengan scene grafis, masing-masing membawa kalimat VO sendiri dan teks ringkas (Plus Jakarta Sans ExtraBold putih di atas gradasi gelap bawah + garis aksen oranye + pil "siapnikah.id" kiri atas). Ambil via `scripts/broll.py`. Pilih klip dengan melihat frame-nya, bukan acak.
4. **Musik latar** `MARKBro-Studio/_pustaka/musik/calm-reassuring.mp3` ±13 dB di bawah VO (volume ~0.16), fade in 1 dtk, fade out 2 dtk.
5. **SFX**: `_pustaka/sfx/halus/transition_whoosh.wav` di setiap masuk/keluar B-roll (~0.35), `proper_ding.wav` halus di awal CTA.
6. **Cover** 1080x1920 (aman dipotong 1080x1350), judul hook besar + karakter.
7. **Caption** IG/FB (hook, isi, ajakan komentar, "Cek kesiapanmu gratis di siapnikah.id (link di bio)", 8–10 hashtag, sumber singkat bila ada dalil/riset) + 1 teks Threads.
8. Loudness akhir ±-15 LUFS, video < 20 MB, H.264 + AAC, faststart.

## QA wajib sebelum masuk antrean (kalau gagal, perbaiki — jangan kirim)
- **VO benar-benar ada**: transkripsi 14 detik pertama dengan faster-whisper (model small, bahasa id). Harus keluar kalimat naskah. Kalau hanya "Terima kasih"/kosong = TIDAK ADA VO → ulangi VO.
- Lembar 12 frame: teks tidak terpotong, B-roll bertema benar, teks B-roll tampil.
- Isi video = isi caption (topik sama).
- Item queue punya `video_url` + `cover_url`; cek URL jsDelivr membalas 200.
- B-roll ditolak: minuman keras/gelas mirip alkohol, pakaian terbuka, kemesraan berlebihan, simbol/kitab agama lain, uang dolar, layar hijau/kartun murahan, binatang/benda tak nyambung. Catat di `broll/ditolak.json`.

## Konten
- Tone hangat, bijak, islami-friendly; dilarang kata "AI", "robot", "coach" di konten publik.
- Pilar "Benefit Menikah" di slot -b tiap Selasa, Kamis, Sabtu, Minggu (bank ide di instruksi tugas). Dalil/riset diverifikasi, tanpa hadits dhaif, tanpa klaim berlebihan, tanpa konten seksual eksplisit.

## Jadwal & pengaman
- Tugas harian 16:47 WIB: picu `wp-cron.yml` (run cadangan menyambung 3x ≈ 21 jam: ping artikel + picu autopost bila item jatuh tempo), lalu produksi 2 video untuk besok.
- `autopost.yml` jadwal 11:37 & 19:37 WIB sebagai lapis kedua; item yang tak bisa diposting dilewati ("skipped").
- Bila laptop/Chrome tidak terhubung: tetap buat video (tanpa VO) agar slot terisi, laporkan, dan begitu laptop terhubung lagi rakit ulang dengan VO.

## Rutinitas tambahan di tugas harian (setelah produksi selesai)

### 1. Balas komentar (setiap run, maks ±20 menit)
Lewat Chrome pengguna (sudah login), cek komentar BARU 24 jam terakhir di:
- Instagram & Facebook: Meta Business Suite → Kotak Masuk → Komentar (https://business.facebook.com/latest/inbox/all).
- YouTube: Studio → Komentar channel UCZcijfe6fh05j3Vqk3bXXvA (tab "Belum dibalas").
- Threads: tab Aktivitas akun siapnikahindo.

Aturan balasan:
- Hangat, singkat (1–2 kalimat), bahasa santai-sopan, sapa dengan "Kak". Boleh ajak ke tes kesiapan: "cek di siapnikah.id ya Kak". Tanpa kata "AI/robot/coach".
- Balas: pertanyaan umum, apresiasi, cerita ringan, mitos yang perlu diluruskan (singkat + rujuk dalil/riset yang sudah dipakai di video).
- JANGAN balas / lewati dan laporkan: spam, provokasi agama/politik, ujaran kasar, curhat krisis (KDRT, bunuh diri, kekerasan) — untuk curhat krisis cukup balas empatik singkat + sarankan menghubungi tenaga profesional/orang tepercaya, tanpa nasihat medis/hukum.
- Jangan pernah membalas DM, menghapus/menyembunyikan komentar, memblokir akun, atau menjanjikan apa pun soal harga/akun. Jangan menulis data pribadi siapa pun.
- Catat jumlah komentar dibalas/dilewati per platform di laporan harian.

### 2. Laporan performa mingguan (hanya run hari SENIN WIB)
- Kumpulkan data 7 hari terakhir: IG & FB (Meta Business Suite → Insight → Konten: tayangan, jangkauan, suka, komentar, simpan, bagikan per reel), YouTube (Studio → Analytics → Konten: penayangan & durasi tonton per Shorts), Threads (Insight akun: tayangan & balasan per posting).
- Tulis `laporan/<YYYY>-W<nn>.md`: tabel per konten, 3 konten terbaik & 3 terlemah + dugaan penyebab (hook, topik, durasi, jam), pertumbuhan pengikut tiap platform, dan 3 keputusan untuk minggu depan (topik/format yang diperbanyak/dikurangi).
- Terapkan keputusan itu ke pemilihan topik run-run berikutnya (baca laporan terbaru sebelum memilih topik).
- Commit + push, dan sertakan ringkasan 5 baris di laporan SendUserMessage hari itu.

## Contoh rakitan yang sudah lolos standar
`scripts/contoh-rakit-vo/` (24 Nov 2026): `align.py` (cocokkan kalimat naskah ↔ waktu VO via whisper) dan `build.py` (retime scene ke VO, sisip B-roll berteks, musik, whoosh, ding, loudnorm).
