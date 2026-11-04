"""Generate a locally synthesized, shot-aligned English narration with matching SRT."""
import argparse
import json
import subprocess
from pathlib import Path
from pipeline import load, timestamp

ROOT = Path(__file__).resolve().parent


def generate(config, out):
    import numpy as np
    import soundfile as sf
    import sherpa_onnx
    c = load(config)
    voice = c['narration']
    model = ROOT/voice['model']
    onnx = next(model.glob('*.onnx'), None)
    if onnx is None:
        raise FileNotFoundError(f'Voice model missing at {model}')
    if voice['engine']=='kokoro':
        model_config=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(onnx),
                voices=str(model/'voices.bin'),tokens=str(model/'tokens.txt'),
                data_dir=str(model/'espeak-ng-data'),lang='en-us'),num_threads=3,provider='cpu')
    else:
        model_config=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=str(onnx),tokens=str(model/'tokens.txt'),
                data_dir=str(model/'espeak-ng-data')),num_threads=3,provider='cpu')
    tts=sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=model_config,max_num_sentences=1))
    out.mkdir(parents=True,exist_ok=True)
    rate = tts.sample_rate
    mix = np.zeros(round(c['duration']*rate), dtype=np.float32)
    cues=[]
    report=[]
    for i, segment in enumerate(voice['segments']):
        start, end, text = segment['start'], segment['end'], segment['text']
        generated=tts.generate(text,sid=voice.get('speaker_id',0),speed=segment.get('speed',1.0))
        raw=out/f'voice-{i}-raw.wav'
        sf.write(raw, generated.samples, rate, subtype='PCM_16')
        # Trim synth padding, then fit only if needed; keep at least 80 ms shot gap.
        clean=out/f'voice-{i}-clean.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',
            'silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,'
            'areverse,silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB,areverse',
            str(clean)],check=True)
        samples,_=sf.read(clean,dtype='float32')
        natural=len(samples)/rate
        speed=max(1.0,natural/(end-start))
        if speed>1.30:
            raise ValueError(f'Phrase {i} too long ({natural:.2f}s); shorten the narration text')
        fitted=out/f'voice-{i}.wav'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(clean),'-af',
                        f'atempo={speed:.6f},afade=t=in:d=0.008,areverse,afade=t=in:d=0.012,areverse',
                        str(fitted)],check=True)
        samples,_=sf.read(fitted,dtype='float32')
        # Avoid crossing a scene boundary due to filter rounding.
        samples=samples[:round((end-start)*rate)]
        offset=round(start*rate)
        mix[offset:offset+len(samples)]+=samples
        actual_end=start+len(samples)/rate
        cues.append((start,actual_end,text))
        report.append(dict(segment, natural_duration=natural, tempo=speed, actual_end=actual_end))
        print(f'Phrase {i+1}: {start:.2f}–{actual_end:.2f}s, tempo {speed:.2f}',flush=True)
    sf.write(out/'narration-raw.wav',mix,rate,subtype='PCM_16')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(out/'narration-raw.wav'),
                    '-af','loudnorm=I=-16:TP=-1.5:LRA=7','-ar','48000',str(out/'narration.wav')],check=True)
    (out/'narration.srt').write_text('\n\n'.join(
        f'{i}\n{timestamp(a)} --> {timestamp(b)}\n{text}' for i,(a,b,text) in enumerate(cues,1))+'\n')
    (out/'narration.json').write_text(json.dumps({'voice':voice['voice'], 'sample_rate':rate,
        'segments':report,'cues':cues},indent=2)+'\n')
    (out/'transcript.txt').write_text('\n'.join(item['text'] for item in voice['segments'])+'\n')
    print(out/'narration.wav')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--episode',type=Path,default=ROOT/'episodes/bench_vise.json')
    p.add_argument('--output',type=Path,default=ROOT/'output/bench_vise/preview')
    args=p.parse_args()
    generate(args.episode.resolve(),args.output.resolve())


if __name__=='__main__':
    main()
