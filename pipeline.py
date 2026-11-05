"""Local render/package CLI. No network calls or publishing side effects."""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
from physics import quantities as screw_quantities
from hydraulics import quantities as hydraulic_quantities

def episode_quantities(c):
    if c.get("mechanism")=="hydraulic_syringes": return hydraulic_quantities(c["physics"])
    return screw_quantities(c["physics"])

ROOT = Path(__file__).resolve().parent


def run(args, **kwargs):
    subprocess.run([str(x) for x in args], check=True, **kwargs)


def load(path):
    c = json.loads(path.read_text())
    episode_quantities(c)
    if not c['id'].replace('_', '').isalnum() or c['language'] != 'en':
        raise ValueError('Use a simple episode id and English for this pilot')
    for key in ('width', 'height', 'fps'):
        if type(c[key]) is not int or c[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    if c['width'] % 2 or c['height'] % 2:
        raise ValueError('Dimensions must be even for yuv420p')
    if not math.isfinite(c['duration']) or c['duration'] <= 0:
        raise ValueError('Invalid duration')
    for start, end, text in c['captions']:
        if not 0 <= start < end <= c['duration'] or not text.strip():
            raise ValueError('Invalid caption')
    if 'shots' in c:
        cursor = 0
        ids = set()
        for shot in c['shots']:
            if shot['start'] != cursor or shot['end'] <= cursor or shot['id'] in ids:
                raise ValueError('Shots must be contiguous, ordered and uniquely named')
            if shot['scale'] <= 0 or len(shot['camera']) != 3 or len(shot['target']) != 3:
                raise ValueError('Invalid camera definition')
            ids.add(shot['id'])
            cursor = shot['end']
        if cursor != c['duration'] or not 0 < c['contact_time'] <= c['duration']:
            raise ValueError('Storyboard/contact timing must match the episode')
    if 'narration' in c:
        cursor=0
        for seg in c['narration']['segments']:
            if not cursor <= seg['start'] < seg['end'] <= c['duration'] or not seg['text'].strip():
                raise ValueError('Narration segments must be ordered and non-overlapping')
            cursor=seg['end']
    cursor=0
    for eq in c.get('equations',[]):
        if not cursor <= eq['start'] < eq['end'] <= c['duration'] or not eq['expression'].strip():
            raise ValueError('Equation cues must be ordered and non-overlapping')
        cursor=eq['end']
    return c


def timestamp(t):
    ms = round(t*1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def package(config, out):
    c = load(config)
    video = out/'video.mp4'
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)]))
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    if 'narration' in c and not any(s['codec_type']=='audio' for s in probe['streams']):
        raise ValueError('Narrated episode is missing its audio track')
    if stream['width'] >= stream['height']:
        raise ValueError('Expected vertical video')
    if abs(float(probe['format']['duration'])-c['duration']) > .3:
        raise ValueError('Unexpected duration')
    expected_fps=c['preview']['fps'] if stream['width']==c['preview']['width'] and stream['height']==c['preview']['height'] else c['fps']
    if Fraction(stream['r_frame_rate'])!=expected_fps:
        raise ValueError('Encoded frame rate does not match the selected profile')
    if c.get('music',{}).get('credit') and c['music']['credit'].strip() not in c['description']:
        raise ValueError('Music attribution is missing from the upload description')
    manifest = {'episode': c['id'], 'video': 'video.mp4', 'sha256': digest(video),
                'title': c['title'], 'description': c['description'],
                'language': c['language'], 'youtube': c['youtube'],
                'width': stream['width'], 'height': stream['height'],
                'fps': stream['r_frame_rate'],
                'duration': float(probe['format']['duration']),
                'physics': episode_quantities(c), 'status': 'awaiting_review',
                'preview': stream['width'] != c['width'] or stream['height'] != c['height']}
    (out/'upload.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Validated package: {out}/upload.json (no upload performed)')


def render(config, preview):
    c = load(config)
    out = ROOT/'output'/c['id']/('preview' if preview else 'final')
    out.mkdir(parents=True, exist_ok=True)
    (out/'episode.json').write_text(json.dumps(c, indent=2)+'\n')
    fps = c['preview']['fps'] if preview else c['fps']
    # Refuse stale frame sequences rather than accidentally assembling an older render.
    frames = out/'frames'
    if frames.exists():
        shutil.rmtree(frames)
    command = ['blender', '--background', '--threads', '4', '--python-exit-code', '1',
               '--python', ROOT/c.get('scene_script','scene.py'), '--', '--config', out/'episode.json', '--output', out]
    if preview:
        command.append('--preview')
    with (out/'render.log').open('w') as log:
        run(command, stdout=log, stderr=subprocess.STDOUT)
    if 'narration' in c:
        run([ROOT/'.venv/bin/python', ROOT/'narration.py','--episode',out/'episode.json','--output',out])
    if c.get('annotation_style')=='flat':
        study=out/'arrow-study'
        run(['blender','--background','--threads','2',out/'scene.blend','--python-exit-code','1',
             '--python',ROOT/'export_arrow_study.py','--','--config',out/'episode.json','--output',study])
        anchors=json.loads((study/'anchors.json').read_text())
        for row in anchors['frames']:
            name=f"{row['frame']:04}.png"
            shutil.copy2(out/'frames'/name,study/'clean'/name)
        run([sys.executable,ROOT/'arrow_graphics.py','--directory',study,'--source',out,'--raw-only'])
        for path in (study/'annotated').glob('*.png'):
            shutil.copy2(path,out/'frames'/path.name)
    if c.get('annotation_style')=='hydraulic_flat':
        run([sys.executable,ROOT/'hydraulic_graphics.py','--output',out])
    assemble(c, out, preview)


def assemble(c, out, preview):
    fps = c['preview']['fps'] if preview else c['fps']
    (out/'episode.json').write_text(json.dumps(c,indent=2,ensure_ascii=False)+'\n')
    narrated='narration' in c
    if narrated and not (out/'narration.json').exists():
        raise ValueError('Run .venv/bin/python narration.py before assembling this episode')
    if narrated:
        report=json.loads((out/'narration.json').read_text())
        if [row['text'] for row in report['segments']] != [row['text'] for row in c['narration']['segments']]:
            raise ValueError('Narration script changed; regenerate the audio')
        shutil.copy2(out/'narration.srt',out/'captions.srt')
    width = c['preview']['width'] if preview else c['width']
    (out/'screen-titles.srt').write_text('\n\n'.join(
        f'{i}\n{timestamp(a)} --> {timestamp(b)}\n{text}'
        for i, (a, b, text) in enumerate(c['captions'], 1))+'\n')
    size = max(12, round(width*.044))
    font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    layers = [
        'drawbox=x=0:y=0:w=iw:h=ih*0.235:color=0x172130@0.95:t=fill',
        'drawbox=x=0:y=ih*0.76:w=iw:h=ih*0.24:color=0x172130@0.95:t=fill',
        'drawbox=x=iw*0.07:y=ih*0.225:w=iw*0.86:h=2:color=0x60DDCE@0.7:t=fill']
    equation_windows = '+'.join(f"gte(t,{e['start']})*lt(t,{e['end']})" for e in c.get('equations',[])) or '0'
    for i, (start, end, text) in enumerate(c['captions']):
        (out/f'caption-{i}.txt').write_text(textwrap.fill(text, width=32))
        layers.append(f"drawtext=fontfile={font}:textfile=caption-{i}.txt:"
                      f"fontsize={size}:fontcolor=white:line_spacing=5:"
                      f"x=(w-tw)/2:y=h*0.14:enable='gte(t,{start})*lt(t,{end})*not({equation_windows})'")
    for i, shot in enumerate(c['shots']):
        (out/f'shot-{i}.txt').write_text(shot['label'])
        (out/f'detail-{i}.txt').write_text(textwrap.fill(shot['detail'], width=43))
        elements=[(f'shot-{i}', .07, '0x60DDCE', .029)]
        if not narrated:
            elements.append((f'detail-{i}', .79, 'white', .029))
        for name, y, color, factor in elements:
            layers.append(f"drawtext=fontfile={font}:textfile={name}.txt:"
                          f"fontsize={max(11,round(width*factor))}:fontcolor={color}:"
                          f"x=(w-tw)/2:y=h*{y}:line_spacing=5:"
                          f"enable='gte(t,{shot['start']})*lt(t,{shot['end']})'")
    for i, eq in enumerate(c.get('equations',[])):
        (out/f'equation-{i}.txt').write_text(eq['expression'])
        (out/f'definition-{i}.txt').write_text(eq['definition'])
        for name,y,factor,color in [(f'equation-{i}',.135,.048,'white'),
                                    (f'definition-{i}',.195,.027,'0x60DDCE')]:
            layers.append(f"drawtext=fontfile={font}:textfile={name}.txt:"
                          f"fontsize={max(11,round(width*factor))}:fontcolor={color}:"
                          f"x=(w-tw)/2:y=h*{y}:enable='gte(t,{eq['start']})*lt(t,{eq['end']})'")
    if narrated and c.get('subtitle_style')!='shorts':
        for i,(start,end,text) in enumerate(report['cues']):
            (out/f'subtitle-{i}.txt').write_text(textwrap.fill(text,width=36))
            layers.append(f"drawtext=fontfile={font}:textfile=subtitle-{i}.txt:"
                          f"fontsize={max(13,round(width*.040))}:fontcolor=white:line_spacing=6:"
                          f"x=(w-tw)/2:y=h*0.815:enable='gte(t,{start})*lt(t,{end})'")
    (out/'model-note.txt').write_text(c.get('model_note','Idealized motion | Schematic force arrows'))
    layers.append(f"drawtext=fontfile={font}:textfile=model-note.txt:"
                  f"fontsize={max(10,round(width*.023))}:fontcolor=0xA8B6C5:x=(w-tw)/2:y=h*0.94"
                  +(f":enable='lt(t,{c['duration']-3})'" if c.get('music',{}).get('path') else ''))
    if c.get('music',{}).get('path'):
        (out/'music-credit-screen.txt').write_text(f"Music: {c['music']['title']} — {c['music']['artist']}")
        (out/'music-license-screen.txt').write_text('CC BY 3.0 · incompetech.com · edited excerpt')
        for name,y,factor in [('music-credit-screen',.94,.021),('music-license-screen',.965,.018)]:
            layers.append(f"drawtext=fontfile={font}:textfile={name}.txt:fontsize={max(10,round(width*factor))}:"
                          f"fontcolor=0xA8B6C5:x=(w-tw)/2:y=h*{y}:enable='gte(t,{c['duration']-3})'")
    filters = ','.join(layers)
    audio_input='narration.wav'
    if narrated and c.get('music',{}).get('path'):
        run([sys.executable,ROOT/'mix_audio.py','--episode',out/'episode.json','--output',out])
        audio_input='soundtrack.wav'
    command=['ffmpeg','-y','-v','error','-framerate',fps,'-i','frames/%04d.png']
    if narrated:
        command+=['-i',audio_input,'-i','narration.srt']
    else:
        shutil.copy2(out/'screen-titles.srt',out/'captions.srt')
    if narrated and c.get('subtitle_style')=='shorts':
        run([sys.executable,ROOT/'shorts_captions.py','--episode',out/'episode.json','--output',out,'--profile','preview' if preview else 'final'])
        command+=['-framerate',fps,'-i','shorts-captions/%04d.png']
        if c.get('annotation_style')=='hydraulic_flat':
            command+=['-framerate',fps,'-i','hydraulic-overlays/%04d.png']
            graph=f'[0:v][4:v]overlay=0:0:format=auto[scene];[scene]{filters}[base];[base][3:v]overlay=0:0:format=auto[v]'
        else:
            graph=f'[0:v]{filters}[base];[base][3:v]overlay=0:0:format=auto[v]'
        command+=['-filter_complex',graph,'-map','[v]']
    else:
        command+=['-vf',filters,'-map','0:v:0']
    if narrated:
        command+=['-map','1:a:0','-map','2:0','-c:a','aac','-b:a','160k','-c:s','mov_text',
                  '-metadata:s:a:0','language=eng','-metadata:s:s:0','language=eng',
                  '-disposition:s:0','0','-t',c['duration']]
    if c.get('music',{}).get('credit'):
        command+=['-metadata','comment='+c['music']['credit']]
    command+=['-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','video.mp4']
    run(command,cwd=out)
    run(['ffmpeg', '-y', '-v', 'error', '-ss', '2', '-i', 'video.mp4',
         '-frames:v', '1', 'poster.png'], cwd=out)
    for shot in c['shots']:
        moment = (shot['start']+shot['end'])/2
        run(['ffmpeg', '-y', '-v', 'error', '-ss', moment, '-i', 'video.mp4',
             '-frames:v', '1', f"shot-{shot['id']}.png"], cwd=out)
    shutil.copy2(out/'video.mp4', out/f"{c['id']}_v{c.get('revision', 2)}.mp4")
    package(out/'episode.json', out)
    print(out/'video.mp4')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['doctor', 'render', 'narrate', 'assemble', 'package'])
    parser.add_argument('--episode', type=Path, default=ROOT/'episodes/bench_vise.json')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--output', type=Path)
    a = parser.parse_args()
    if a.command == 'doctor':
        for binary in ('blender', 'ffmpeg', 'ffprobe'):
            print(binary, shutil.which(binary) or 'MISSING')
        c = load(a.episode)
        print('Ideal quantities (SI):', episode_quantities(c))
        print('YouTube: offline; no upload attempted')
    elif a.command == 'render':
        render(a.episode.resolve(), a.preview)
    elif a.command == 'narrate':
        c=load(a.episode.resolve())
        out=a.output.resolve() if a.output else ROOT/'output'/c['id']/('preview' if a.preview else 'final')
        run([ROOT/'.venv/bin/python', ROOT/'narration.py','--episode',a.episode.resolve(),'--output',out])
    elif a.command == 'assemble':
        c = load(a.episode.resolve())
        out = a.output.resolve() if a.output else ROOT/'output'/c['id']/('preview' if a.preview else 'final')
        assemble(c, out, a.preview)
    else:
        if not a.output:
            parser.error('package requires --output')
        package(a.episode.resolve(), a.output.resolve())


if __name__ == '__main__':
    main()
