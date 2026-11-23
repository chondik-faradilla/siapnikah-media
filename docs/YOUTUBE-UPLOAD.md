# Upload YouTube Shorts otomatis (channel @kata2positif)

Teruji 24 Nov 2026 (2 video terjadwal sukses). API YouTube TIDAK dipakai: upload lewat API dari project yang belum diaudit dikunci private. Jalur: YouTube Studio di Chrome pengguna (sudah login), dikendalikan alat Claude in Chrome.

- Channel: Kata Kata Positif / @kata2positif, ID `UCZcijfe6fh05j3Vqk3bXXvA`. Pastikan URL Studio memuat ID ini sebelum upload.
- Jadwal tayang: slot -a 11.30, slot -b 19.30 di tanggal yang sama dengan queue (zona GMT+0700 default — cek label "Default disetel ke zona waktu lokal (GMT+0700)").

## Langkah (per video)
1. Buka `https://studio.youtube.com/channel/UCZcijfe6fh05j3Vqk3bXXvA`, klik ikon upload (kanan atas).
2. Isi file TANPA file picker (file_upload dibatasi 3,8 MB): via javascript_tool
   ```js
   const inp=document.querySelector('input[type=file]');
   const b=await (await fetch('https://cdn.jsdelivr.net/gh/chondik-faradilla/siapnikah-media@main/reels/<file>.mp4')).blob();
   const dt=new DataTransfer(); dt.items.add(new File([b],'<nama>.mp4',{type:'video/mp4'}));
   inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));
   ```
   (video harus sudah ter-push & URL jsDelivr membalas 200).
3. Tunggu ±5 dtk, isi judul & deskripsi:
   ```js
   function put(sel,t){const el=document.querySelector(sel);el.focus();document.execCommand('selectAll');document.execCommand('insertText',false,t);el.blur();}
   put('#title-textarea #textbox', judul);       // ≤100 karakter, diakhiri #shorts
   put('#description-textarea #textbox', desk);  // caption IG, "link di bio" → https://siapnikah.id, tambah #shorts
   ```
   JANGAN tekan Escape (menutup dialog → upload terputus → draf "Tidak dapat diproses"; kalau terjadi: hapus draf itu di Konten → Video, lalu ulangi).
4. Audiens: klik `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]`.
5. Klik `ytcp-uploads-dialog #next-button` 3x (jeda 1,5 dtk) sampai tab Visibilitas.
6. Klik `#second-container-expand-button` (Jadwalkan). Tanggal: buka pemilih tanggal di `ytcp-visibility-scheduler`, klik angka hari yang benar (default-nya besok). Jam: klik `ytcp-visibility-scheduler input`, lalu pilih `tp-yt-paper-item` berteks "11.30" / "19.30" (mengetik jam tidak berpengaruh).
7. Klik `ytcp-uploads-dialog #done-button` ("Jadwalkan"). Bila muncul "Kami masih memeriksa konten Anda", klik "Oke". Dialog "Video dijadwalkan" memuat link `youtube.com/shorts/<id>` — catat di field `youtube` item queue.
8. Cek di Konten → Shorts: status "Dijadwalkan" dengan tanggal benar.
