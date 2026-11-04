"""Mix licensed background music under narration with voice-driven ducking."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from pipeline import load,digest

ROOT=Path(__file__).resolve().parent


def mix(config,out):
    c=load(config);music=c['music'];track=ROOT/music['path']
    if digest(track)!=music['sha256']:raise ValueError('Music provenance hash mismatch')
    duration=c['duration'];fade=duration-1.2
    graph=(f"[1:a]atrim=start={music.get('start',0)}:duration={duration},asetpts=PTS-STARTPTS,"
           f"loudnorm=I={music.get('bed_lufs',-26)}:TP=-4:LRA=7,aresample=48000,"
           f"afade=t=in:d=0.35,afade=t=out:st={fade}:d=1.2[bed];"
           "[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[voice][detector];"
           "[bed][detector]sidechaincompress=threshold=0.025:ratio=5:attack=15:release=300:knee=2[ducked];"
           "[voice][ducked]amix=inputs=2:duration=first:normalize=0,"
           "loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json,aresample=48000[mix]")
    result=subprocess.run(['ffmpeg','-y','-hide_banner','-i',str(out/'narration.wav'),'-i',str(track),
                           '-filter_complex',graph,'-map','[mix]','-t',str(duration),
                           '-c:a','pcm_s24le',str(out/'soundtrack.wav')],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr[-2500:])
    matches=re.findall(r'\{\s*"input_i".*?\}',result.stderr,re.S)
    meters=json.loads(matches[-1]) if matches else {}
    report={'music':music['title'],'artist':music['artist'],'music_sha256':music['sha256'],
            'duration':duration,'music_target_lufs':music.get('bed_lufs',-26),
            'ducking':{'threshold':.025,'ratio':5,'attack_ms':15,'release_ms':300},
            'master_target_lufs':-16,'master_true_peak_db':-1.5,'meters':meters}
    (out/'audio-mix.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'MUSIC_CREDITS.txt').write_text(music['credit'])
    print('Music mixed under narration:',music['title'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--episode',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();mix(a.episode.resolve(),a.output.resolve())
