"""Flat, antialiased educational vectors from Blender's projected 3D anchors."""
import json
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/bench_vise/arrow-study'
CYAN=(70,231,218,255); AMBER=(255,195,87,255); GREY=(162,178,197,255)
INK=(20,30,46,255); WHITE=(241,247,252,255)
S=3
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'


def unit(a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    n=math.hypot(dx,dy)
    if n<.001: raise ValueError('Degenerate projected arrow direction')
    return dx/n,dy/n


def render(directory=None,source=None,raw_only=False):
    global OUT
    if directory is not None:OUT=directory
    source=source or ROOT/'output/bench_vise/preview'
    data=json.loads((OUT/'anchors.json').read_text())
    report=json.loads((source/'narration.json').read_text())
    native_w,native_h=data['width'],data['height']
    w,h=450,800
    factor=native_w/w
    for row in data['frames']:
        for name in ['application','tangent','axis']:
            row[name]=[value/factor for value in row[name]]
        row['torque_arc']=[[value/factor for value in point] for point in row['torque_arc']]
    folder=OUT/'composited';folder.mkdir(exist_ok=True)
    (OUT/'annotated').mkdir(exist_ok=True)
    positions={}
    for i,row in enumerate(data['frames']):
        base=Image.open(OUT/'clean'/f"{row['frame']:04}.png").convert('RGBA').resize((w*S,h*S),Image.Resampling.LANCZOS)
        d=ImageDraw.Draw(base)
        def P(xy):return tuple(round(v*S) for v in xy)
        def line(points,color,width=2):d.line([P(p) for p in points],fill=color,width=round(width*S),joint='curve')
        def text(x,y,value,size=15,color=WHITE):
            d.text(P((x,y)),value,font=ImageFont.truetype(FONT,round(size*S)),fill=color)
        def dashed(a,b,color):
            ux,uy=unit(a,b);length=math.dist(a,b)
            for offset in range(0,round(length),9):
                stop=min(length,offset+4)
                line([(a[0]+ux*offset,a[1]+uy*offset),(a[0]+ux*stop,a[1]+uy*stop)],color,1.3)
        def arrow(points,color,width=2.8):
            line(points,color,width)
            end=points[-1];ux,uy=unit(points[-2],end)
            size=11;half=4.7
            a=(end[0]-ux*size-uy*half,end[1]-uy*size+ux*half)
            b=(end[0]-ux*size+uy*half,end[1]-uy*size-ux*half)
            d.polygon([P(end),P(a),P(b)],fill=color)
        boxes=[]
        def label(key,value,desired,color):
            font=ImageFont.truetype(FONT,14*S)
            bb=d.textbbox((0,0),value,font=font)
            bw=(bb[2]-bb[0])/S+16;bh=27
            x=max(14,min(w-bw-14,desired[0]));y=max(205,min(574,desired[1]))
            # Prefer a nearby clear position when two annotations would collide.
            for trial in [y,y+32,y-32]:
                if 205<=trial<=574 and not any(x<b[2]+5 and x+bw>b[0]-5 and trial<b[3]+5 and trial+bh>b[1]-5 for b in boxes):
                    y=trial;break
            previous=positions.get(key,(x,y))
            alpha=1-.65**(16/data['fps'])
            x=(1-alpha)*previous[0]+alpha*x;y=(1-alpha)*previous[1]+alpha*y
            positions[key]=(x,y);boxes.append((x,y,x+bw,y+bh))
            d.rounded_rectangle([P((x,y)),P((x+bw,y+bh))],radius=5*S,fill=INK,outline=(*color[:3],230),width=S)
            text(x+8,y+4,value,14,color)
        a=row['application'];c=row['axis'];u=unit(a,row['tangent']);t=row['t']
        # Keep width/arrowhead size constant in screen pixels, regardless of camera zoom.
        if t>=.12:
            growth=min(1,(t-.12)/.3);growth=growth*growth*(3-2*growth)
            length=58*growth
            for k,(lo,hi) in enumerate([(12,w-12),(198,600)]):
                if u[k]>0:length=min(length,(hi-a[k])/u[k])
                elif u[k]<0:length=min(length,(lo-a[k])/u[k])
            end=(a[0]+u[0]*max(12,length),a[1]+u[1]*max(12,length))
            arrow([a,end],CYAN,3.0)
            d.ellipse([P((a[0]-3.1,a[1]-3.1)),P((a[0]+3.1,a[1]+3.1))],fill=CYAN)
            label('force','F = 20 N',(end[0]+10,end[1]-30),CYAN)
        if t>=.40:
            dashed(c,a,GREY)
            d.ellipse([P((c[0]-3,c[1]-3)),P((c[0]+3,c[1]+3))],outline=GREY,width=S)
            label('radius','r = 65 mm',((a[0]+c[0])/2-42,(a[1]+c[1])/2+16),GREY)
        if t>=.85:
            arc=row['torque_arc']
            count=max(3,round(len(arc)*min(1,(t-.85)/.65)))
            arrow(arc[:count],AMBER,2.7)
            label('torque','τ = 1.3 N·m',(w-138,228),AMBER)
        base.resize((native_w,native_h),Image.Resampling.LANCZOS).convert('RGB').save(OUT/'annotated'/f"{row['frame']:04}.png")
        if raw_only:continue
        # Panels, formula and actual spoken subtitle, retained from the narrated prototype.
        d.rectangle([P((0,0)),P((w,h*.235))],fill=INK)
        d.rectangle([P((0,h*.76)),P((w,h))],fill=INK)
        line([(w*.07,h*.225),(w*.93,h*.225)],(74,171,164,255),1.5)
        def centered(value,y,size,color=WHITE):
            bb=d.textbbox((0,0),value,font=ImageFont.truetype(FONT,round(size*S)))
            text((w-(bb[2]-bb[0])/S)/2,y,value,size,color)
        centered('04 / FORCE TO TORQUE',h*.07,13,CYAN)
        centered('τ = r·F' if t<2.2 else 'τ = 0.065 × 20 = 1.3 N·m',h*.135,21)
        centered('Perpendicular force at the handle',h*.195,12,CYAN)
        absolute=t+data['start']
        import textwrap
        for start,end,words in report['cues']:
            if start<=absolute<end:
                for j,chunk in enumerate(textwrap.wrap(words,width=36)):
                    centered(chunk,h*.815+j*25,18)
        centered('Force',h*.94,11,CYAN)
        text(24,h*.94,'Radius',11,GREY)
        text(w-71,h*.94,'Torque',11,AMBER)
        base.resize((native_w,native_h),Image.Resampling.LANCZOS).convert('RGB').save(folder/f'{i+1:04}.png')
    if raw_only:
        print('Composited',len(data['frames']),'native annotation frames');return
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(data['fps']),'-i',str(folder/'%04d.png'),
        '-ss',str(data['start']),'-t',str(data['duration']),'-i',str(source/'narration.wav'),
        '-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','160k','-t',str(data['duration']),'-movflags','+faststart',str(OUT/'flat-arrows.mp4')],check=True)
    if (source/'bench_vise_v4.mp4').exists():
        subprocess.run(['ffmpeg','-y','-v','error','-ss','10','-i',str(source/'bench_vise_v4.mp4'),
            '-t','4','-c:v','libx264','-crf','18','-c:a','aac',str(OUT/'original-3d-arrows.mp4')],check=True)
    print(OUT/'flat-arrows.mp4')


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path);p.add_argument('--source',type=Path);p.add_argument('--raw-only',action='store_true')
    a=p.parse_args();render(a.directory,a.source,a.raw_only)
