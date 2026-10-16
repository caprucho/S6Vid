"""Prepare, preview, render and verify portable S6Vid infographic projects."""
import argparse,json,math,subprocess,wave,re,shutil
from pathlib import Path
import numpy as np,imageio_ffmpeg,qrcode,zxingcpp
from PIL import Image,ImageDraw,ImageFont
from music import read,write,mix
ASSETS=Path(__file__).resolve().parents[1]/'assets';CFG=json.loads((ASSETS/'padrao.json').read_text(encoding='utf-8'))
W,H,FPS=1080,1920,24;BG=CFG['brand']['background'];GOLD=CFG['brand']['gold'];WHITE=CFG['brand']['white'];GRAY=CFG['brand']['gray'];PANEL=CFG['brand']['panel']
FONT={};LOGO=Image.open(ASSETS/'s6-logo-oficial.png').convert('RGBA')
def font(n,b=False):
    key=(n,b)
    if key not in FONT:FONT[key]=ImageFont.truetype(str(ASSETS/('InstrumentSans-Bold.ttf' if b else 'InstrumentSans-Regular.ttf')),n)
    return FONT[key]
def image(scene,t=5,opening=False,closing=False,url=None):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    def text(xy,s,n=42,b=False,color=WHITE,anchor=None):
        maximum=924 if anchor and 'm' in anchor else W-xy[0]-78
        while n>24 and any(font(n,b).getlength(line)>maximum for line in s.split('\n')):n-=1
        d.multiline_text(xy,s,font=font(n,b),fill=color,anchor=anchor,spacing=14,align='center' if anchor and 'm' in anchor else 'left')
    def logo(x,y,w):
        lg=LOGO.resize((w,round(w*LOGO.height/LOGO.width)),Image.Resampling.LANCZOS);im.paste(lg,(x,y),lg)
    def building(x,y,w=240,h=350):
        d.rounded_rectangle((x,y,x+w,y+h),8,fill=PANEL,outline=GOLD,width=5)
        for row in range(4):
            for col in range(3):
                if t>.3+row*.12:
                    xx=x+w*.12+col*w*.28;yy=y+35+row*(h-95)/4
                    d.rectangle((xx,yy,xx+w*.15,yy+40),fill=GOLD if (row+col)%4==0 else BG,outline=GOLD,width=2)
        d.rectangle((x+w*.4,y+h-60,x+w*.62,y+h),fill=BG,outline=GOLD,width=4)
    site=CFG['brand']['site'];target=url or CFG['brand']['url']
    d.line((72,1770,1008,1770),fill='#383B3E',width=2);text((540,1836),site,39,color=GOLD,anchor='mm')
    if closing:
        logo(396,92,288);text((540,688),scene.get('title','Seu imóvel merece\numa boa estratégia.'),78,True,anchor='mm');text((540,868),scene.get('cta','Converse com a S6 Imóveis.'),43,color=GOLD,anchor='mm')
        qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=16,border=4);qr.add_data(target);qr.make(fit=True)
        q=qr.make_image(fill_color='black',back_color='white').convert('RGB').resize((522,522),Image.Resampling.NEAREST);im.paste(q,(279,987));text((540,1586),'Aponte a câmera e acesse nosso site.',37,anchor='mm');return im
    if opening:
        text((540,280),scene.get('eyebrow','S6 IMÓVEIS'),36,True,GOLD,'mm');text((540,435),scene['title'],81,True,anchor='mm');logo(345,840,390);return im
    logo(78,57,132);text((78,334),scene.get('eyebrow','S6 IMÓVEIS'),30,True,GOLD);text((78,410),scene['title'],84,True);d.line((81,666,249,666),fill=GOLD,width=7)
    kind=scene.get('kind','cards');items=scene.get('items',[])
    if kind=='building':building(405,840,270,390)
    elif kind=='comparison':
        for j,x in enumerate([78,570]):
            d.rounded_rectangle((x,810,x+432,1450),22,fill=PANEL,outline=GOLD if j==0 else '#383B3E',width=4);building(x+105,875,220,320)
            text((x+216,1330),items[j] if len(items)>j else ['OPÇÃO A','OPÇÃO B'][j],32,True,GOLD,'mm')
    elif kind=='chart':
        d.line((140,1350,945,1350),fill=GRAY,width=3);d.line((140,1350,140,840),fill=GRAY,width=3)
        points=[(170,1300),(330,1220),(490,1160),(650,1020),(820,940),(935,870)];count=max(2,min(len(points),round(t*2)));d.line(points[:count],fill=GOLD,width=7,joint='curve')
        text((540,1470),items[0] if items else 'ILUSTRAÇÃO DO RACIOCÍNIO',35,True,GOLD,'mm')
    elif kind=='clock':
        d.ellipse((320,835,760,1275),outline=GOLD,width=7);d.line((540,880,540,1055,650,1120),fill=GOLD,width=8)
    else:
        values=items or ['Primeiro ponto','Segundo ponto','Terceiro ponto']
        if len(values)>3:raise ValueError('Use up to three cards per scene to preserve readable space.')
        for j,value in enumerate(values):
            if t>j*.4:
                y=810+j*205;d.rounded_rectangle((78,y,1002,y+160),20,fill=PANEL,outline='#383B3E',width=3);text((125,y+80),value,48,True,anchor='lm')
    text((540,1660),scene.get('note',''),37,color=GRAY,anchor='mm');return im
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def prepare(args):
    project=load(args.project);ledger_path=Path(args.ledger).resolve();ledger=load(ledger_path);work=Path(args.work).resolve();work.mkdir(parents=True,exist_ok=True)
    pieces=[];timeline=[];sources=[];offset=0;rate=48000
    for i,scene in enumerate(project['scenes']):
        takes=[r for r in ledger if r['scene']==scene['id']]
        if not takes:raise ValueError('Missing narration: '+scene['id'])
        local=.12 if i==0 else 0;parts=[np.zeros(round(local*rate))]
        for row in takes:
            p=(ledger_path.parent/row['file']).resolve();a,sr=read(p)
            if sr!=rate or a.ndim!=1:raise ValueError('Expected 48 kHz mono narration.')
            sources.append({'file':str(p),'text':row['text'],'start':offset+local});local+=len(a)/rate+CFG['voice']['pause_seconds'];parts.extend([a,np.zeros(round(CFG['voice']['pause_seconds']*rate))])
        a=np.concatenate(parts);frames=math.ceil(len(a)/rate*FPS)
        if i==0:frames=max(frames,round(CFG['video']['opening_seconds']*CFG['video']['speed']*FPS))
        a=np.pad(a,(0,round(frames/FPS*rate)-len(a)));pieces.append(a*CFG['voice']['gain']);timeline.append({**scene,'start':offset,'duration':frames/FPS,'frames':frames});offset+=frames/FPS
    write(work/'voice-native.wav',np.concatenate(pieces),rate);speed=CFG['video']['speed'];body_frames=math.ceil(offset*FPS/speed);duration=body_frames/FPS
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-i',str(work/'voice-native.wav'),'-af',f'atempo={speed},apad','-t',str(duration),str(work/'voice-final.wav')],check=True)
    total=mix(work/'voice-final.wav',work/'mix.wav',CFG['video']['closing_seconds'])
    plan={'timeline':timeline,'caption_sources':sources,'native_duration':offset,'body_duration':duration,'total_duration':total,'speed':speed,'qr_seconds':CFG['video']['closing_seconds'],'closing':project.get('closing',{})}
    (work/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8');fonts=work/'fonts';fonts.mkdir(exist_ok=True)
    for n in ['InstrumentSans-Regular.ttf','InstrumentSans-Bold.ttf']:shutil.copyfile(ASSETS/n,fonts/n)
    (work/'roteiro.txt').write_text('\n\n'.join(s['narration'] for s in project['scenes']),encoding='utf-8');print('PREPARED',round(total,2))
def preview(args):
    project=load(args.project);scenes=project['scenes'];work=Path(args.work);work.mkdir(parents=True,exist_ok=True);count=len(scenes)+1;sheet=Image.new('RGB',(270*min(4,count),480*math.ceil(count/4)),BG)
    for i in range(count):
        im=image(scenes[i],opening=i==0) if i<len(scenes) else image(project.get('closing',{}),closing=True)
        im.save(work/f'preview-{i:02}.png');sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%4)*270,(i//4)*480))
    image(scenes[0],opening=False).save(work/'preview-first-body.png')
    sheet.save(work/'storyboard.jpg',quality=94);print(work/'storyboard.jpg')
def render(args):
    work=Path(args.work).resolve();plan=load(work/'plan.json');ass=work/'captions.ass'
    if not ass.exists():raise ValueError('Generate and review narration captions before rendering.')
    output=Path(args.output).resolve();output.parent.mkdir(parents=True,exist_ok=True);ff=imageio_ffmpeg.get_ffmpeg_exe();raw=work/'visual-native.mp4'
    cmd=[ff,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','24','-i','-','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(raw)]
    with open(work/'render.log','w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i,row in enumerate(plan['timeline']):
                cached={}
                for fr in range(row['frames']):
                    t=fr/FPS;opening=i==0 and t/plan['speed']<CFG['video']['opening_seconds'];bucket=min(24,round(t*8))
                    key=(opening,bucket)
                    if key not in cached:cached[key]=image(row,min(3,t),opening=opening).tobytes()
                    proc.stdin.write(cached[key])
                print('SCENE',i+1,flush=True)
            proc.stdin.close();code=proc.wait()
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
        if code:raise RuntimeError('Visual render failed; see render.log')
    closing=work/'closing.png';image(plan.get('closing',{}),closing=True).save(closing)
    # Relative paths keep libass filters portable across Windows and Unix.
    cmd=[ff,'-y','-v','warning','-i',str(raw),'-loop','1','-framerate','24','-t',str(plan['qr_seconds']),'-i','closing.png','-i','mix.wav','-filter_complex',f"[0:v]setpts=PTS/{plan['speed']},fps=24,trim=duration={plan['body_duration']}[body];[1:v]format=yuv420p,setsar=1,setpts=PTS-STARTPTS[qr];[body][qr]concat=n=2:v=1:a=0,ass=captions.ass:fontsdir=fonts,fps=24[v]",'-map','[v]','-map','2:a','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(output)]
    subprocess.run(cmd,cwd=work,check=True);shutil.copyfile(work/'captions.srt',output.with_suffix('.srt'));shutil.copyfile(work/'roteiro.txt',output.with_suffix('.txt'));print(output)
def verify(args):
    ff=imageio_ffmpeg.get_ffmpeg_exe();p=Path(args.video).resolve();r=subprocess.run([ff,'-hide_banner','-i',str(p),'-af','volumedetect','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if r.returncode:raise RuntimeError('Full video decode failed.')
    if not all(s in r.stderr for s in ['Video: h264','Audio: aac','1080x1920']):raise ValueError('Unexpected export format.')
    peak=float(re.search(r'max_volume: ([\-\d.]+) dB',r.stderr)[1])
    if peak>=-.5:raise ValueError('Insufficient audio headroom.')
    if args.qr_url:
        still=p.with_name(p.stem+'-qr-check.png');subprocess.run([ff,'-y','-v','error','-sseof','-4','-i',str(p),'-frames:v','1',str(still)],check=True)
        result=zxingcpp.read_barcode(Image.open(still))
        if not result or result.text!=args.qr_url:raise ValueError('QR validation failed in exported video.')
    print(json.dumps({'file':str(p),'full_decode':'passed','peak_dbfs':peak,'qr':'passed' if args.qr_url else 'not checked'},indent=2))
def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ['prepare','preview','render']:
        s=sub.add_parser(name);s.add_argument('project');s.add_argument('--work',required=True)
        if name=='prepare':s.add_argument('--ledger',required=True)
        if name=='render':s.add_argument('--output',required=True)
    s=sub.add_parser('verify');s.add_argument('video');s.add_argument('--qr-url');args=p.parse_args();globals()[args.command](args)
if __name__=='__main__':main()
