import json, re, subprocess, sys, difflib, numpy as np
from faster_whisper import WhisperModel
SEG = {
 "a": ["Katanya, pasangan yang cocok itu nggak pernah bertengkar.",
       "Faktanya, konflik itu normal. Yang menentukan bukan ada atau tidaknya, tapi cara kalian menghadapinya.",
       "Wajar, karena kalian dua orang dengan latar yang berbeda.",
       "Riset Gottman bahkan menemukan, sekitar enam puluh sembilan persen konflik pasangan adalah masalah yang terus berulang.",
       "Jadi, debat boleh. Asal fokus ke masalah, bukan menyerang pribadi. Berani jeda saat emosi memuncak. Dan cari solusi, bukan siapa yang menang.",
       "Belajar berbeda pendapat dengan baik, sebelum akad.",
       "Rumah tangga yang kuat bukan yang tanpa masalah, tapi yang tahu cara menyelesaikannya.",
       "Cek kesiapanmu, gratis, di siapnikah titik id."],
 "b": ["Takut nikah karena merasa belum mapan? Dengarkan ayat ini dulu.",
       "Banyak yang menunda menikah, karena merasa penghasilannya belum cukup.",
       "Padahal dalam surah An-Nur ayat tiga puluh dua: jika mereka miskin, Allah akan memberi kemampuan kepada mereka dengan karunia-Nya. Dan Allah Mahaluas, Maha Mengetahui.",
       "Janji yang menenangkan. Tapi bukan alasan untuk asal-asalan.",
       "Ayat setelahnya mengingatkan: yang belum mampu, diminta menjaga diri, sampai Allah memampukan.",
       "Mampu bukan berarti harus kaya. Yang perlu disiapkan: mau bekerja dan menafkahi, terbuka soal keuangan, dan siap hidup sederhana, berdua.",
       "Rezeki dijemput dengan ikhtiar, dan dijalani dengan syukur.",
       "Pertolongan-Nya datang, saat kamu bersiap.",
       "Cek kesiapanmu, gratis, di siapnikah titik id."]}
norm=lambda w: re.sub(r"[^a-z0-9]","",w.lower())
m=WhisperModel("small",device="cpu",compute_type="int8")
out={}
for key in "ab":
    raw=subprocess.run(["ffmpeg","-loglevel","error","-i",f"/tmp/vo-{key}.wav","-ac","1","-ar","16000","-f","s16le","-"],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    segs,_=m.transcribe(a,language="id",word_timestamps=True)
    words=[(norm(w.word),w.start,w.end) for s in segs for w in s.words if norm(w.word)]
    tw=[w[0] for w in words]
    sw=[]; owner=[]
    for i,s in enumerate(SEG[key]):
        for w in s.split():
            if norm(w): sw.append(norm(w)); owner.append(i)
    sm=difflib.SequenceMatcher(None,sw,tw,autojunk=False)
    mp={}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): mp[blk.a+k]=blk.b+k
    starts=[];ends=[]
    for i in range(len(SEG[key])):
        idx=[j for j,o in enumerate(owner) if o==i and j in mp]
        starts.append(words[mp[idx[0]]][1] if idx else None); ends.append(words[mp[idx[-1]]][2] if idx else None)
    dur=len(a)/16000
    out[key]={"dur":dur,"seg":[[SEG[key][i],starts[i],ends[i]] for i in range(len(SEG[key]))],"text":" ".join(w for w,_,_ in words)}
    print(key, round(dur,2))
    for s,st,en in out[key]["seg"]: print(f"  {st} {en}  {s[:50]}")
json.dump(out,open("/tmp/job/align.json","w"),ensure_ascii=False,indent=1)
