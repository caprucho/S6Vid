"""Portable VoiceStudio profile registration and resumable S6Vid narration."""
import argparse, hashlib, json, re, urllib.request, urllib.error, uuid, wave
from pathlib import Path
ASSETS=Path(__file__).resolve().parents[1]/'assets'
CFG=json.loads((ASSETS/'padrao.json').read_text(encoding='utf-8'))['voice']
def call(base,path,data=None,content_type='application/json'):
    if isinstance(data,dict):data=json.dumps(data).encode()
    req=urllib.request.Request(base.rstrip('/')+path,data=data,headers={'Content-Type':content_type})
    try:
        with urllib.request.urlopen(req,timeout=900) as r:return r.read()
    except urllib.error.HTTPError as e:raise RuntimeError(f'VoiceStudio HTTP {e.code}: '+e.read().decode('utf-8',errors='replace')) from e
def register(base,state):
    reference=ASSETS/CFG['reference'];digest=hashlib.sha256(reference.read_bytes()).hexdigest()
    state=Path(state)
    if state.exists():
        prior=json.loads(state.read_text(encoding='utf-8'))
        if prior.get('base')==base and prior.get('reference_sha256')==digest:
            live=json.loads(call(base,'/profiles/'+prior['profile_id']))
            if live.get('id')==prior['profile_id']:
                actual=call(base,'/profiles/'+prior['profile_id']+'/audio')
                if hashlib.sha256(actual).hexdigest()!=digest:raise RuntimeError('The saved voice reference changed; inspect the profile before generating.')
                return prior['profile_id']
    name=CFG['profile_name']+' '+digest[:8]
    rows=json.loads(call(base,'/profiles'));rows=rows if isinstance(rows,list) else rows.get('profiles',[])
    profile=next((r for r in rows if r.get('name')==name),None)
    if profile:
        pid=profile['id']
        live_audio=call(base,'/profiles/'+pid+'/audio')
        if hashlib.sha256(live_audio).hexdigest()!=digest:raise RuntimeError('Existing named profile has a different reference; inspect it before reuse.')
    else:
        boundary='S6Vid'+uuid.uuid4().hex;parts=[]
        for k,v in {'name':name,'kind':'clone','language':CFG['language'],'ref_text':CFG['transcript'],'seed':str(CFG['seed'])}.items():parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="ref_audio"; filename="approved-synthetic-voice.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()+reference.read_bytes()+b'\r\n')
        profile=json.loads(call(base,'/profiles',b''.join(parts)+f'--{boundary}--\r\n'.encode(),'multipart/form-data; boundary='+boundary));pid=profile.get('id') or profile['profile']['id']
    state.parent.mkdir(parents=True,exist_ok=True);state.write_text(json.dumps({'base':base,'profile_id':pid,'reference_sha256':digest},indent=2),encoding='utf-8');return pid
def readiness(base):
    models=json.loads(call(base,'/models')).get('models',[])
    row=next((r for r in models if r.get('repo_id')=='openbmb/VoxCPM2'),None)
    return {'repo_id':'openbmb/VoxCPM2','ready':bool(row and row.get('installed') and not row.get('incomplete')),'installed':row and row.get('installed'),'incomplete':row and row.get('incomplete')}
def generate(args):
    if not readiness(args.base)['ready']:raise RuntimeError('VoxCPM2 weights are missing, incomplete or not confirmed by this backend. Configure them in VoiceStudio before generation; no download was started.')
    project=json.loads(Path(args.project).read_text(encoding='utf-8'));out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    pid=register(args.base,out/'voice-state.json');ledger=[]
    for scene in project['scenes']:
        sentences=re.split(r'(?<=[.!?])\s+',scene['narration'].strip());chunks=[];current=''
        for sentence in sentences:
            if len(sentence)>350:raise ValueError('Split this long sentence editorially before generating: '+sentence)
            if current and len(current+' '+sentence)>CFG['chunk_characters']:chunks.append(current);current=sentence
            else:current=(current+' '+sentence).strip()
        if current:chunks.append(current)
        for text in chunks:
            key=hashlib.sha256((text+'\n'+pid).encode()).hexdigest()[:16];p=out/(key+'.wav')
            if not p.exists():
                data=call(args.base,'/v1/audio/speech',{'model':CFG['engine'],'voice':pid,'input':text.replace('CDB','C D B'),'language':'pt','response_format':'wav','speed':1.0,'seed':CFG['seed']})
                if data[:4]!=b'RIFF':raise ValueError('Speech endpoint did not return WAV audio.')
                p.write_bytes(data)
            with wave.open(str(p),'rb') as f:
                if f.getnchannels()!=1 or f.getsampwidth()!=2:raise ValueError('Expected mono 16-bit WAV.')
                row={'scene':scene['id'],'text':text,'file':p.name,'duration':f.getnframes()/f.getframerate(),'sample_rate':f.getframerate(),'profile_id':pid}
            ledger.append(row);(out/'ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8');print('TAKE',scene['id'],row['duration'],flush=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',default='http://localhost:3900');subs=p.add_subparsers(dest='command',required=True)
    subs.add_parser('doctor');r=subs.add_parser('register');r.add_argument('--state',required=True)
    g=subs.add_parser('generate');g.add_argument('project');g.add_argument('--out',required=True);args=p.parse_args()
    if args.command=='doctor':
        health=json.loads(call(args.base,'/health'));catalog=json.loads(call(args.base,'/v1/audio/voices'));engine=next((e for e in catalog.get('engines',[]) if e.get('id')==CFG['engine']),None)
        print(json.dumps({'health':health,'engine':engine and {k:engine.get(k) for k in ['id','available','reason']},'weights':readiness(args.base)},ensure_ascii=False,indent=2))
    elif args.command=='register':print(register(args.base,args.state))
    else:generate(args)
if __name__=='__main__':main()
