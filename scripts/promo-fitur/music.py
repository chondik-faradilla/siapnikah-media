import numpy as np, wave, sys
exec(open('/home/claude/trailer/audio.py').read().split('BPM=96')[0])
def make(name,BPM,chords,roots,TOTAL=27.0,arpon=True,kickg=0.25):
    beat=60/BPM; bar=4*beat
    mus=np.zeros(int((TOTAL+2)*SR))
    def add(sig,t,g):
        i=int(t*SR); j=min(len(mus),i+len(sig)); mus[i:j]+=g*sig[:j-i]
    arp=[0,1,2,1,2,1,0,2]; t=0;k=0
    while t<TOTAL:
        c=chords[k%4]
        for m in c: add(note(m2f(m),bar+0.4,'pad'),t,0.10)
        add(note(m2f(roots[k%4]),bar,'bass'),t,0.22)
        add(note(m2f(roots[k%4]),beat*2,'bass'),t+2*beat,0.14)
        if arpon:
            for i in range(8): add(note(m2f(c[arp[i]]+12),0.6,'pluck'),t+i*beat/2,0.09)
        t+=bar;k+=1
    t=0
    while t<TOTAL-1:
        n=int(0.25*SR); tt=np.arange(n)/SR
        add(np.sin(2*np.pi*(55+60*np.exp(-tt*30))*tt)*np.exp(-tt*14),t,kickg); t+=beat
    fi=int(0.5*SR); fo=int(2*SR); end=int(TOTAL*SR)
    mus[:fi]*=np.linspace(0,1,fi); mus[end-fo:end]*=np.linspace(1,0,fo); mus[end:]=0
    mus/=np.abs(mus).max()*1.25
    x=np.clip(mus,-1,1); w=wave.open(name,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x*32767).astype(np.int16).tobytes()); w.close()
# A: D mayor 100bpm ceria
make('music_A.wav',100,[[62,66,69],[57,61,64],[59,62,66],[55,59,62]],[38,33,35,31])
# B: F mayor 88bpm hangat
make('music_B.wav',88,[[65,69,72],[62,65,69],[58,62,65],[60,64,67]],[41,38,34,36],kickg=0.18)
# C: A minor-ish 108bpm langkah tegas
make('music_C.wav',108,[[57,60,64],[53,57,60],[60,64,67],[55,59,62]],[33,29,36,31],kickg=0.3)
print('ok')
