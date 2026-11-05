"""Independent 2D annotation renderer. No bpy import and no 3D arrow/field meshes."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
CYAN=(73,231,213,255);GOLD=(255,194,80,255);WHITE=(226,236,244,255);INK=(20,31,46,245)


def project(point,matrix,w,h):
 v=[*point,1];clip=[sum(matrix[i][j]*v[j] for j in range(4)) for i in range(4)]
 return [(clip[0]/clip[3]+1)*w/2,(1-clip[1]/clip[3])*h/2]


def impacts(data):
 hits=[]
 for a,b in zip(data['frames'],data['frames'][1:]):
  if a['shot']!=b['shot'] or b['physical_time']<=a['physical_time']:continue
  for event in data['physical_events']:
   if event['type']=='strike' and a['physical_time']<=event['t']<b['physical_time']:
    f=(event['t']-a['physical_time'])/(b['physical_time']-a['physical_time'])
    hits.append({'t':a['t']+(b['t']-a['t'])*f,'speed':event['speed']})
 return hits


def generate(out):
 data=json.loads((out/'bell-anchors.json').read_text());w,h=data['width'],data['height'];S=w/450
 folder=out/'bell-overlays';folder.mkdir(exist_ok=True);font=ImageFont.truetype(FONT,round(13*S))
 hit_times=impacts(data)
 for row in data['frames']:
  im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im)
  def P(p):return tuple(round(v*S) for v in p)
  def point(k):return [v/S for v in row[k]]
  def line(points,color,width=2):d.line([P(p) for p in points],fill=color,width=max(1,round(width*S)),joint='curve')
  def label(text,xy,color):
   bw=d.textlength(text,font=font)/S+16;bh=25
   x=max(12,min(388-bw,xy[0]));y=max(203,min(575,xy[1]))
   d.rounded_rectangle([P((x,y)),P((x+bw,y+bh))],radius=round(4*S),fill=INK,outline=color,width=max(1,round(S)))
   d.text(P((x+8,y+4)),text,font=font,fill=color)
  def arrow(a,b,color,text):
   dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy)
   if n<.01:return
   dx/=n;dy/=n;length=49
   end=(a[0]+dx*length,a[1]+dy*length)
   line([a,end],color,2.8)
   d.polygon([P(end),P((end[0]-dx*10-dy*4.5,end[1]-dy*10+dx*4.5)),P((end[0]-dx*10+dy*4.5,end[1]-dy*10-dx*4.5))],fill=color)
   d.ellipse([P((a[0]-2.8,a[1]-2.8)),P((a[0]+2.8,a[1]+2.8))],fill=color)
   label(text,(end[0]+8 if dx>0 else end[0]-114,end[1]-34),color)
  shot=row['shot'];strength=max(0,min(1,row['current']/.5))
  if shot in ('overview','finish'):
   xy=project((-.104,-.03,.033),row['view_projection'],w,h);label('6 V BATTERY',(xy[0]/S-48,xy[1]/S+13),WHITE)
  if shot in ('button','coil') and row['closed']:
   # Conventional current follows the series wires; colour is explanatory, not a voltage scale.
   color=(*CYAN[:3],round(210*strength))
   for wire in row['wires']:
    points=[[v/S for v in p] for p in wire];line(points,color,2.2)
    if len(points)>1:
     a,b=points[-2:];dx,dy=b[0]-a[0],b[1]-a[1];n=max(.001,math.hypot(dx,dy));dx/=n;dy/=n
     d.polygon([P(b),P((b[0]-7*dx-3*dy,b[1]-7*dy+3*dx)),P((b[0]-7*dx+3*dy,b[1]-7*dy-3*dx))],fill=color)
  if shot=='button':
   xy=point('button');label('BUTTON HELD',(xy[0]-60,xy[1]-55),CYAN)
  if shot in ('coil','release') and strength>.025:
   # Flux paths are projected as mathematical curves, then drawn entirely as flat pixels.
   color=(*CYAN[:3],round(225*strength))
   for path in data['field_paths']:
    pts=[project(p,row['view_projection'],w,h) for p in path]
    line([[v/S for v in p] for p in pts],color,1.8)
  if shot=='coil' and strength>.20:
   arrow(point('armature'),point('mag_direction'),CYAN,'MAGNETIC PULL')
  if shot=='spring':arrow(point('armature'),point('spring_direction'),GOLD,'SPRING RETURN')
  if shot in ('contact','repeat'):
   p=point('contact');q=point('fixed_contact')
   color=CYAN if row['closed'] else GOLD
   if row['closed']:line([p,q],CYAN,3)
   d.ellipse([P((p[0]-5,p[1]-5)),P((p[0]+5,p[1]+5))],outline=color,width=max(1,round(S)))
   label('CONTACT CLOSED' if row['closed'] else 'CONTACT OPEN',(p[0]-76,p[1]-50),color)
  if shot in ('coil','contact','release'):
   x,y=20,552
   d.rounded_rectangle([P((x-6,y-18)),P((x+110,y+24))],radius=round(4*S),fill=INK)
   d.text(P((x,y-16)),'COIL CURRENT',font=ImageFont.truetype(FONT,round(10*S)),fill=WHITE)
   d.rectangle([P((x,y+5)),P((x+96,y+11))],fill=(72,91,106,255))
   if strength>0:d.rectangle([P((x,y+5)),P((x+96*strength,y+11))],fill=CYAN)
  recent=[e for e in hit_times if 0<=row['t']-e['t']<.28]
  if recent and shot in ('overview','release','repeat','finish'):
   xy=point('hammer');u=(row['t']-recent[-1]['t'])/.28
   for r in (10+u*16,17+u*18):
    d.arc([P((xy[0]-r,xy[1]-r)),P((xy[0]+r,xy[1]+r))],-70,70,fill=(*GOLD[:3],round(230*(1-u))),width=round(1.8*S))
  im.save(folder/f"{row['frame']:04}.png",compress_level=1)
 (out/'bell-overlay-info.json').write_text(json.dumps({'frames':len(data['frames']),'width':w,'height':h,'fps':data['fps'],'displayed_impacts':hit_times},indent=2)+'\n')
 print('Generated',len(data['frames']),'independent 2D overlays and',len(hit_times),'displayed strike cues')


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();generate(a.output)
