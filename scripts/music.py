"""Mix the original local S6Vid instrumental quietly beneath narration."""
import json,subprocess,wave
from pathlib import Path
import numpy as np,imageio_ffmpeg
ASSETS=Path(__file__).resolve().parents[1]/'assets'
def read(path):
    with wave.open(str(path),'rb') as f:
        if f.getsampwidth()!=2:raise ValueError('Expected 16-bit PCM.')
        a=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float64)/32768
        return (a.reshape(-1,f.getnchannels()) if f.getnchannels()>1 else a),f.getframerate()
def write(path,a,rate=48000):
    if np.max(np.abs(a))>=.99:raise ValueError('Mix peak too high; inspect the sources instead of normalizing the approved voice.')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(a.shape[1] if a.ndim==2 else 1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(np.rint(a*32767).astype(np.int16).tobytes())
def mix(voice_path,out,closing=8):
    cfg=json.loads((ASSETS/'padrao.json').read_text(encoding='utf-8'))['music'];voice,rate=read(voice_path)
    if voice.ndim!=1:raise ValueError('Expected mono voice.')
    active=voice[np.abs(voice)>.025]
    if not len(active):raise ValueError('No active narration found.')
    voice=np.concatenate([voice,np.zeros(round(closing*rate))]);duration=len(voice)/rate
    music_path=Path(out).with_name('music-decoded.wav');music_path.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-stream_loop','-1','-i',str(ASSETS/cfg['asset']),'-t',str(duration),'-ar',str(rate),'-ac','2',str(music_path)],check=True)
    music,_=read(music_path);music=music[:len(voice)];rms=float(np.sqrt(np.mean(music**2)))
    music*=float(np.sqrt(np.mean(active**2)))*10**(cfg['relative_to_active_speech_db']/20)/rms
    t=np.arange(len(voice))/rate;music*=np.minimum(t/cfg['fade_in'],1)[:,None]*np.minimum((duration-t)/cfg['fade_out'],1)[:,None]
    write(out,voice[:,None]+music,rate);return duration
