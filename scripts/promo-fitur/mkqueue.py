import json
D={
'kesehatan':('2026-11-25',"Sebelum menikah, sudah cek kondisimu? 🩺\n\nKesiapan menikah bukan cuma soal hati. Kondisi badan dan pikiran juga ikut menentukan. Di siapnikah.id ada cek kesehatan pranikah yang bisa kamu isi sendiri, gratis, dan hasilnya langsung keluar.\n\nKamu sudah pernah cek kesehatan pranikah? Cerita di komentar ya 👇",
 "#siapnikah #persiapannikah #cekkesehatanpranikah #nikahmuda #calonpengantin #taaruf #menikah #kesehatanpranikah #nikahberkah",
 "Nikah itu menyatukan dua hidup, termasuk dua kondisi kesehatan. Sudah cek punyamu? Ada cek kesehatan pranikah gratis di siapnikah.id."),
'biaya':('2026-11-26',"Nikah butuh biaya berapa sih? 💸\n\nDaripada menebak-nebak, hitung saja. Kalkulator biaya nikah di siapnikah.id membantu kamu merinci pos akad, walimah, mahar, sampai tabungan per bulan yang perlu disisihkan.\n\nMenurutmu pos biaya nikah paling besar itu apa? Tulis di komentar 👇",
 "#siapnikah #biayanikah #persiapannikah #nikahhemat #walimah #calonpengantin #menikah #tabungannikah #nikahsederhana",
 "Biaya nikah sering bikin ragu melangkah. Padahal kalau dirinci, jadi jelas harus nabung berapa per bulan. Coba kalkulatornya gratis di siapnikah.id."),
'kua':('2026-11-27',"3 langkah urusan KUA tanpa panik 📋\n\n1️⃣ Isi tanggal akad rencanamu\n2️⃣ Lihat batas daftar KUA yang dihitung otomatis\n3️⃣ Centang persiapan satu per satu, dari lamaran sampai setelah akad\n\nSimpan postingan ini biar nggak lupa. Mau akad bulan apa? 👇",
 "#siapnikah #daftarKUA #persiapannikah #checklistnikah #calonpengantin #akadnikah #menikah #nikah2027 #urusanKUA",
 "Daftar ke KUA itu ada batas waktunya. Biar nggak mepet, isi tanggal akadmu dan biarkan checklist di siapnikah.id menghitung sisanya."),
'kenali':('2026-11-28',"Seberapa jujur kamu mengenal dirimu? 🪞\n\nSebelum mengenal calon, kenali dulu dirimu: cara kamu marah, cara kamu menyayangi, apa yang kamu butuhkan. Tes kepribadian dan kesiapan di siapnikah.id bantu kamu melihatnya lebih jernih.\n\nSatu kata yang paling menggambarkan dirimu? Tulis di komentar 👇",
 "#siapnikah #kenalidiri #persiapannikah #tesKepribadian #selflove #taaruf #menikah #kesiapanmenikah #muhasabah",
 "Banyak yang sibuk mencari yang tepat, tapi lupa jadi pribadi yang siap. Mulai dari mengenal diri sendiri, gratis di siapnikah.id."),
'cv':('2026-11-29',"Bingung menyusun CV taaruf? 📝\n\nCV taaruf yang baik itu jujur, jelas, dan tidak berlebihan. Di siapnikah.id ada panduan isinya, dari latar belakang, visi pernikahan, sampai harapan pada calon, tinggal kamu lengkapi.\n\nBagian CV taaruf mana yang paling susah kamu tulis? 👇",
 "#siapnikah #cvtaaruf #taaruf #persiapannikah #nikahsyari #calonpengantin #menikah #jodoh #ikhtiarjodoh",
 "CV taaruf bukan ajang pamer, tapi cara jujur memperkenalkan diri. Susun yang rapi dengan panduan gratis di siapnikah.id."),
'kenalan':('2026-11-30',"3 langkah berkenalan dengan cara yang baik 🤝\n\nKenalan yang serius dimulai dengan niat yang jelas dan cara yang terjaga. Lengkapi profil, kirim minat ke yang cocok, lalu lanjutkan obrolan dengan adab, semuanya di siapnikah.id.\n\nMenurutmu apa adab kenalan yang paling penting? 👇",
 "#siapnikah #taaruf #kenalanserius #persiapannikah #jodoh #menikah #ikhtiarjodoh #calonpasangan #nikahberkah",
 "Serius mau menikah, kenalannya juga harus serius dan terjaga. Begini caranya di siapnikah.id."),
}
CDN='https://cdn.jsdelivr.net/gh/chondik-faradilla/siapnikah-media@main/'
for vid,(d,cap,tags,th) in D.items():
    item={'publish_after':f'{d}T16:30:00+07:00','video_url':CDN+f'reels/{d}-c.mp4','cover_url':CDN+f'reels/{d}-c.jpg',
          'caption':cap+'\n\nCek kesiapanmu gratis di siapnikah.id (link di bio)\n\n'+tags,'threads':[th]}
    json.dump(item,open(f'queue/{d}-c.json','w'),ensure_ascii=False,indent=2)
    print(vid,d)
