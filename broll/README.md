# B-roll Pixabay untuk reel siapnikah

- `katalog-pixabay.json` — 198 klip (29 tema) hasil pencarian Pixabay API, hanya URL CDN + tag. API key TIDAK disimpan di repo (ada di laptop: MARKBro-Studio/_sistem/pixabay.env).
- `ditolak.json` — id klip yang tidak boleh dipakai beserta alasannya.
- `terpakai.json` — tanggal terakhir tiap klip dipakai (rotasi 14 hari).
- Ambil & olah klip: `python3 scripts/broll.py --tema cincin,sholat --detik 3.5 --out /tmp/broll` (lihat `--daftar`).
- Lisensi Pixabay: boleh dipakai komersial tanpa kredit, tapi file mentah tidak boleh didistribusikan — jangan commit klip mentah, hanya video jadi.
- Perbarui katalog dari laptop (perlu API key) bila tema kurang.
