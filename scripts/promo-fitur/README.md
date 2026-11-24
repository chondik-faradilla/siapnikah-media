# Video promo fitur (slot -c, 16.30 WIB)

Video promo singkat fitur siapnikah.id, berformat 9:16 dan berdurasi 18–25 detik. Isinya VO dari Gemini, cuplikan rekaman layar dari video panduan, musik, dan SFX. Ada 3 gaya:

- **A**: hijau, transisi slideleft
- **B**: krem, transisi smoothup
- **C**: langkah bernomor 1-2-3, latar gelap

Contoh yang sudah lolos QA adalah reels/2026-11-25-c … 2026-11-30-c.

## Alur

1. Siapkan alat:
   `pip install faster-whisper pillow numpy --break-system-packages`
2. Unduh video panduan ke `src/`:
   `for f in panduan-1-memulai panduan-2-alat-gratis panduan-3-cek-kesehatan panduan-4-menu-member; do curl -s -o src/$f.mp4 https://cdn.jsdelivr.net/gh/chondik-faradilla/siapnikah-media@main/panduan/$f.mp4; done`
3. Tulis `scripts.json`. Formatnya bisa dilihat di contoh. Tiap entri berisi:
   - `id`, `style` (A/B/C), `pose` (nama file di pose/), `hook`
   - `lines`: kalimat VO. Yang pertama hook, yang terakhir CTA.
   - `caps`: null untuk hook dan CTA, selain itu teks keterangan pendek.
   - `clips`: null, atau `[file, detik_mulai]`. Pilih detik dengan melihat frame video panduan.
   - `steps`: khusus gaya C, berisi `[null,"1","2","3",null]`.
4. Buat VO dengan Gemini Sulap Suara:
   - Suara: Achernar.
   - Gaya bicara: "Hangat, bersemangat, ramah, seperti kakak yang mengajak dengan senyum".
   - Satu wav per id, simpan sebagai `vo/<id>.wav`.
5. Jalankan `python3 align.py` untuk menghasilkan `timing.json`. Periksa hasilnya: urutan starts harus naik dan sesuai dengan jumlah lines.
6. Jalankan `python3 music.py`, sekali saja, untuk membuat music_A/B/C.wav.
7. Jalankan `python3 render.py [id ...]`. Hasilnya ada di `final/<id>.mp4` dan `final/<id>.jpg` (cover).
8. QA:
   - Transkripsi whisper 8–14 detik pertama harus memunculkan kalimat hook.
   - Loudness sekitar -15 LUFS.
   - Periksa lembar frame.
   - Cek tidak ada kata "AI", "robot", atau "coach".
9. Salin hasil ke `reels/<tanggal>-c.mp4/.jpg`. Lalu buat `queue/<tanggal>-c.json`:
   - `publish_after`: `<tanggal>T16:30:00+07:00`
   - `video_url` dan `cover_url`: URL jsDelivr
   - `caption`: hook, isi, ajakan komentar, baris "Cek kesiapanmu gratis di siapnikah.id (link di bio)", lalu 8–10 hashtag

autopost.yml punya cron 37 9 * * * UTC, yaitu 16.37 WIB, untuk slot ini.
