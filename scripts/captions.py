import sys,json,wave,subprocess,unicodedata,re,difflib,argparse
from pathlib import Path
import numpy as np,imageio_ffmpeg
from faster_whisper import WhisperModel
from PIL import ImageFont
parser=argparse.ArgumentParser(description='Align local narration to the approved script and export SRT/ASS.')
parser.add_argument('--work',required=True)
parser.add_argument('--model-path',required=True)
args=parser.parse_args()
root=Path(args.work).resolve()
model_path=Path(args.model_path).resolve()
if not model_path.is_dir() or not (model_path/'model.bin').exists():
    raise ValueError('Provide the installed faster-whisper model directory containing model.bin; this command does not download weights.')
plan=json.loads((root/'plan.json').read_text(encoding='utf-8'));speed=plan['speed']
model=WhisperModel(str(model_path),device='cpu',compute_type='int8',local_files_only=True)
ff=imageio_ffmpeg.get_ffmpeg_exe()
def norm(s):return re.sub('[^a-z0-9]','', ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn'))
allwords=[];reports=[]
for i,row in enumerate(plan['caption_sources']):
    cache=root/f'words-{i:02}.json';identity={'file':row['file'],'text':row['text']}
    if cache.exists():
        stored=json.loads(cache.read_text(encoding='utf-8'));assert stored['identity']==identity;words=stored['words']
    else:
        p=root/f'asr-{i:02}.wav';subprocess.run([ff,'-y','-v','error','-i',row['file'],'-ar','16000','-ac','1',str(p)],check=True)
        with wave.open(str(p),'rb') as f:a=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
        segments,_=model.transcribe(a,language='pt',beam_size=5,word_timestamps=True)
        words=[{'word':w.word.strip(),'start':w.start,'end':w.end} for seg in segments for w in seg.words]
        cache.write_text(json.dumps({'identity':identity,'words':words},ensure_ascii=False,indent=2),encoding='utf-8')
    expected=row['text'].split();actual=[w['word'] for w in words];assert words
    times=[None]*len(expected)
    for tag,es,ee,as_,ae in difflib.SequenceMatcher(None,list(map(norm,expected)),list(map(norm,actual)),autojunk=False).get_opcodes():
        if tag=='equal':
            for x,y in zip(range(es,ee),range(as_,ae)):times[x]=(words[y]['start'],words[y]['end'])
        elif tag in ('replace','delete'):
            if ae>as_:begin=words[as_]['start'];end=words[ae-1]['end']
            else:
                begin=words[as_-1]['end'] if as_ else words[0]['start'];end=words[as_]['start'] if as_<len(words) else words[-1]['end']
            if end<=begin:end=begin+.08*(ee-es)
            for x in range(es,ee):times[x]=(begin+(end-begin)*(x-es)/(ee-es),begin+(end-begin)*(x-es+1)/(ee-es))
    assert all(t is not None for t in times)
    for text,(a,b) in zip(expected,times):allwords.append({'text':text,'start':(row['start']+a)/speed,'end':(row['start']+b)/speed})
    similarity=difflib.SequenceMatcher(None,list(map(norm,expected)),list(map(norm,actual)),autojunk=False).ratio()
    reports.append({**identity,'transcript':' '.join(actual),'similarity':similarity,'tail_recognized':norm(expected[-1]) in [norm(w) for w in actual[-3:]]})
    print('ALIGNED',i+1,len(plan['caption_sources']),round(similarity,2),flush=True)
font=ImageFont.truetype(str(root/'fonts/InstrumentSans-Bold.ttf'),40)
def wrap(tokens):
    if font.getlength(' '.join(tokens))<=850:return ' '.join(tokens)
    candidates=[(' '.join(tokens[:i]),' '.join(tokens[i:])) for i in range(1,len(tokens))]
    best=min(candidates,key=lambda p:max(font.getlength(p[0]),font.getlength(p[1]))+.08*abs(font.getlength(p[0])-font.getlength(p[1])))
    assert max(map(font.getlength,best))<=870,best
    return '\n'.join(best)
groups=[];current=[]
for w in allwords:
    if current and (len(current)>=7 or len(' '.join(x['text'] for x in current+[w]))>60 or w['start']-current[-1]['end']>.35):groups.append(current);current=[]
    current.append(w)
    if w['text'].rstrip('”').endswith(('.', '?','!')) and len(current)>=3:groups.append(current);current=[]
if current:groups.append(current)
# Avoid a single short word flashing alone at the end of a phrase.
for i in range(1,len(groups)):
    if len(groups[i])<3 and len(groups[i-1])>4 and not groups[i-1][-1]['text'].rstrip('”').endswith(('.', '?','!')):
        moved=groups[i-1][-2:];groups[i-1]=groups[i-1][:-2];groups[i]=moved+groups[i]
captions=[]
for i,g in enumerate(groups):
    start=max(0,g[0]['start']-.035);end=g[-1]['end']+.12
    if i+1<len(groups):end=min(end,groups[i+1][0]['start']-.06)
    end=min(end,plan['body_duration']);assert end>start
    text=wrap([w['text'] for w in g]);captions.append({'start':start,'end':end,'text':text})
def stamp(t,srt=False):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}' if srt else f'{h}:{m:02}:{s:02}.{ms//10:02}'
srt='\n\n'.join(f"{i+1}\n{stamp(c['start'],True)} --> {stamp(c['end'],True)}\n{c['text']}" for i,c in enumerate(captions))+'\n'
(root/'captions.srt').write_text(srt,encoding='utf-8')
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Instrument Sans,40,&H00EFF5F7,&H005CA4C4,&H00151311,&H80151311,-1,0,0,0,100,100,0,0,1,1.5,1.5,2,105,105,1160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
keys={'anuncio','imovel','espera','preco','condominio','iptu','inflacao','cdb','mercado','envie','vendendo'}
for c in captions:
    tokens=c['text'].split(' ');colored=False
    for i,token in enumerate(tokens):
        if not colored and any(norm(part) in keys for part in token.split('\n')):
            tokens[i]='{\\c&H5CA4C4&}'+token+'{\\c&HEFF5F7&}';colored=True
    text=' '.join(tokens).replace('\n','\\N')
    ass+=f"Dialogue: 0,{stamp(c['start'])},{stamp(c['end'])},Default,,0,0,0,,{text}\n"
(root/'captions.ass').write_text(ass,encoding='utf-8-sig')
(root/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'asr-validation.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
print('CAPTIONS_COMPLETE',len(captions),flush=True)
