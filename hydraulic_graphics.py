"""Camera-anchored hydraulic annotations; independent transparent 2D graphics."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
CYAN=(77,231,215,255);GOLD=(255,194,80,255);WHITE=(229,239,247,255);GREY=(154,177,194,255);INK=(20,31,46,245)


def generate(out):
 data=json.loads((out/'hydraulic-anchors.json').read_text());w,h=data['width'],data['height'];S=w/450
 dest=out/'hydraulic-overlays';dest.mkdir(exist_ok=True)
 font=ImageFont.truetype(FONT,round(13*S));written=0
 for row in data['frames']:
  im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
  def xy(p):return (round(p[0]*S),round(p[1]*S))
  def point(key):return [v/S for v in row[key]]
  def line(points,color,width=2):d.line([xy(p) for p in points],fill=color,width=round(width*S))
  def arrow(a,b,color,length=48):
   dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
   if n<.01:return
   dx/=n;dy/=n
   end=[a[0]+dx*length,a[1]+dy*length]
   line([a,end],color,2.7)
   p1=[end[0]-dx*10-dy*4.5,end[1]-dy*10+dx*4.5]
   p2=[end[0]-dx*10+dy*4.5,end[1]-dy*10-dx*4.5]
   d.polygon([xy(end),xy(p1),xy(p2)],fill=color)
   d.ellipse([xy([a[0]-2.7,a[1]-2.7]),xy([a[0]+2.7,a[1]+2.7])],fill=color)
   return end
  def label(text,position,color):
   tw=d.textlength(text,font=font)/S;bw=tw+16;bh=25
   x=max(12,min(438-bw,position[0]));y=max(204,min(578,position[1]))
   d.rounded_rectangle([xy([x,y]),xy([x+bw,y+bh])],radius=round(4*S),fill=INK,outline=color,width=round(S))
   d.text(xy([x+8,y+4]),text,font=font,fill=color)
  def dimension(a,b,text,color):
   if math.dist(a,b)<8:return
   dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);nx,ny=-dy/n,dx/n
   line([a,b],color,1.6)
   for p in (a,b):line([[p[0]-nx*5,p[1]-ny*5],[p[0]+nx*5,p[1]+ny*5]],color,1.8)
   label(text,[(a[0]+b[0])/2+8,(a[1]+b[1])/2-12],color)
  shot=row['shot'];a=point('input');b=point('output');pa=point('area1');pb=point('area2')
  if shot=='overview':
   label('INPUT',[pa[0]-60,pa[1]+18],CYAN);label('OUTPUT',[pb[0]+12,pb[1]+18],GOLD)
  elif shot=='input':
   if 190<a[1]<580:
    end=arrow(a,point('input_direction'),CYAN)
    if end:label('F₁ = 10 N',[end[0]+14,end[1]-8],CYAN)
   label('p = 20 kPa',[24,530],WHITE)
  elif shot=='areas':
   label('A₁ = 5 cm²',[pa[0]-70,pa[1]+12],CYAN)
   label('A₂ = 20 cm²',[pb[0]+10,pb[1]+15],GOLD)
  elif shot=='output':
   if 198<b[1]<602:
    end=arrow(b,point('output_direction'),GOLD,length=52)
    if end:label('F₂ = 40 N',[end[0]+18,end[1]-12],GOLD)
   label('p = 20 kPa',[22,540],WHITE)
  elif shot=='travel':
   dimension(point('input_start'),point('input_end'),f"{80*row['progress']:.1f} mm",CYAN)
   dimension(point('output_start'),point('output_end'),f"{20*row['progress']:.1f} mm",GOLD)
  elif shot=='energy':
   label('0.8 J in',[pa[0]-65,pa[1]+20],CYAN);label('0.8 J out',[pb[0]+12,pb[1]+20],GOLD)
  im.save(dest/f"{row['frame']:04}.png",compress_level=1)
  written+=1
 (out/'hydraulic-overlay-info.json').write_text(json.dumps({'frames':written,'width':w,'height':h,'fps':data['fps']},indent=2)+'\n')
 print('Generated',written,'camera-anchored hydraulic overlays')


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();generate(a.output)
