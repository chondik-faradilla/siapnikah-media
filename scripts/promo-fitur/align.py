import numpy as np, subprocess, json, re, difflib
from faster_whisper import WhisperModel
m=WhisperModel('small',device='cpu',compute_type='int8')
S=json.load(open('scripts.json')); out={}
def norm(w): return re.sub(r'[^a-z0-9]','',w.lower())
for s in S:
    f=f"vo/{s['id']}.wav"
    raw=subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout
    a=np.frombuffer(raw,np.int16).astype(np.float32)/32768
    dur=len(a)/16000
    ss,_=m.transcribe(a,language='id',word_timestamps=True)
    W=[(w.start,w.end,norm(w.word)) for x in ss for w in x.words]
    text=' '.join(w[2] for w in W)
    # sentence starts: match first 2 words of each line sequentially
    starts=[];idx=0
    for ln in s['lines']:
        first=[norm(x) for x in ln.split()[:3]]
        best=None
        for j in range(idx,min(len(W),idx+40)):
            sc=sum(difflib.SequenceMatcher(None,first[k],W[j+k][2]).ratio() for k in range(min(len(first),len(W)-j)))
            if best is None or sc>best[0]: best=(sc,j)
            if sc>=2.4: break
        if best is None: starts.append(round(W[-1][0],2)); continue
        starts.append(round(W[best[1]][0],2)); idx=best[1]+1
    ends=[round(W[-1][1],2)]
    out[s['id']]={'dur':round(dur,2),'starts':starts,'end':ends[0]}
    print(s['id'],round(dur,1),starts,'|',text[:120])
json.dump(out,open('timing.json','w'),indent=1)
