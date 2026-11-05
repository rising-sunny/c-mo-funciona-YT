"""Generate bold short-form caption overlays; phrase timestamps are measured.
Within-phrase word highlighting uses estimated syllable-weight timing, not ASR alignment.
"""
import argparse
import json
import re
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def word_cues(cues):
    rows=[]
    for start,end,phrase in cues:
        words=phrase.split()
        weights=[max(1,len(re.findall('[aeiouy]+',w.lower())))+.20*len(w)+(.8 if w.endswith(('.', '!', '?')) else 0) for w in words]
        groups=[];chunk=[]
        for index,word in enumerate(words):
            chunk.append(index)
            if len(chunk)==3 or re.search(r'[.,!?;:]$',word):
                groups.append(chunk);chunk=[]
        if chunk:groups.append(chunk)
        if len(groups)>1 and len(groups[-1])==1 and not re.search(r'[.!?]$',words[groups[-2][-1]]):
            if len(groups[-2])==2:
                tail=groups.pop()
                groups[-1].extend(tail)
            elif len(groups[-2])==3:
                groups[-1].insert(0,groups[-2].pop())
        membership={index:group for group in groups for index in group}
        total=sum(weights);cursor=start
        for i,word in enumerate(words):
            stop=cursor+(end-start)*weights[i]/total
            group=membership[i]
            rows.append({'start':cursor,'end':stop,'words':[words[j] for j in group],
                         'active':group.index(i),'phrase':phrase})
            cursor=stop
    return rows


def generate(config,out,profile='preview'):
    c=json.loads(config.read_text());report=json.loads((out/'narration.json').read_text())
    preset=c['preview'] if profile=='preview' else c
    w,h,fps=preset['width'],preset['height'],preset['fps']
    scale=w/450
    rows=word_cues(report['cues'])
    folder=out/'shorts-captions';folder.mkdir(exist_ok=True)
    total_frames=round(c['duration']*fps)
    cache_key=hashlib.sha256(json.dumps({'version':4,'size':[w,h,fps],
        'duration':c['duration'],'cues':report['cues']},sort_keys=True).encode()).hexdigest()
    cache_file=out/'caption-cache.json'
    if cache_file.exists() and json.loads(cache_file.read_text()).get('key')==cache_key and len(list(folder.glob('*.png')))==total_frames:
        print('Reusing',total_frames,'verified caption overlays');return
    ss=2 if w<720 else 1
    font=ImageFont.truetype(FONT,round(32*ss*scale))
    for i in range(round(c['duration']*fps)):
        t=i/fps
        image=Image.new('RGBA',(w*ss,h*ss),(0,0,0,0));d=ImageDraw.Draw(image)
        cue=next((r for r in rows if r['start']<=t<r['end']),None)
        if cue:
            words=[w.upper() for w in cue['words']]
            space=d.textlength(' ',font=font)
            lines=[[]]
            for index,word in enumerate(words):
                width=sum(d.textlength(text,font=font) for _,text in lines[-1])+space*max(0,len(lines[-1])-1)
                if lines[-1] and width+space+d.textlength(word,font=font)>w*ss*.86:lines.append([])
                lines[-1].append((index,word))
            for j,line in enumerate(lines):
                width=sum(d.textlength(text,font=font) for _,text in line)+space*(len(line)-1)
                x=(w*ss-width)/2;y=(h*.79+j*43*scale)*ss
                for index,word in line:
                    color=(255,210,72,255) if index==cue['active'] else (255,255,255,255)
                    d.text((x+2*ss*scale,y+3*ss*scale),word,font=font,fill=(0,0,0,180),stroke_width=round(3*ss*scale),stroke_fill=(0,0,0,180))
                    d.text((x,y),word,font=font,fill=color,stroke_width=round(2*ss*scale),stroke_fill=(7,12,20,255))
                    x+=d.textlength(word,font=font)+space
        canvas=image.resize((w,h),Image.Resampling.LANCZOS) if ss!=1 else image
        canvas.save(folder/f'{i+1:04}.png',compress_level=1)
    (out/'word-cues.json').write_text(json.dumps({'timing':'syllable-weight estimate within measured phrase bounds','cues':rows},indent=2)+'\n')
    cache_file.write_text(json.dumps({'key':cache_key,'frames':total_frames})+'\n')
    print('Generated',total_frames,'short-form caption overlays')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episode',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',choices=['preview','final'],default='preview')
    a=p.parse_args();generate(a.episode,a.output,a.profile)
