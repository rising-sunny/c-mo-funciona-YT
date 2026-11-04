"""Adapt the existing vector identity to a responsive Facebook Page cover."""
from pathlib import Path
import shutil
import zipfile
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent
parent=OUT.parent
# Reuse only the trusted local drawing definitions; do not rerun YouTube exports.
source=(parent/'build_brand.py').read_text()
namespace={ '__file__':str(parent/'build_brand.py') }
exec(compile(source.split('# All essential information')[0],str(parent/'build_brand.py'),'exec'),namespace)
namespace['OUT']=OUT
symbol=namespace['symbol'];svg_symbol=namespace['svg_symbol'];svg_text=namespace['svg_text'];save_svg=namespace['save_svg']
INK=namespace['INK'];PAPER=namespace['PAPER'];GOLD=namespace['GOLD'];MUTED=namespace['MUTED'];DECOR=namespace['DECOR']
FONT=namespace['FONT'];BOLD=namespace['BOLD'];NAME=namespace['NAME'];TAGLINE=namespace['TAGLINE'];SS=2

w,h=1640,720
size=72
width=ImageFont.truetype(BOLD,size).getlength(NAME)
mark_width=148;gap=40
left=(w-mark_width-gap-width)/2
cx=left+mark_width/2;tx=left+mark_width+gap
cover=Image.new('RGB',(w*SS,h*SS),INK);draw=ImageDraw.Draw(cover)
symbol(draw,(1640,360),3.5,DECOR,DECOR)
symbol(draw,(cx,322),1.06)
draw.text((tx*SS,312*SS),NAME,font=ImageFont.truetype(BOLD,size*SS),fill=PAPER,anchor='ls')
draw.text((tx*SS,363*SS),TAGLINE,font=ImageFont.truetype(FONT,28*SS),fill=MUTED,anchor='ls')
cover=cover.resize((w,h),Image.Resampling.LANCZOS)
cover.save(OUT/'facebook-cover-1640x720.png',optimize=True)
save_svg('facebook-cover-editable.svg',w,h,[f'<rect width="{w}" height="{h}" fill="{INK}"/>',
 svg_symbol(1640,360,3.5,DECOR,DECOR),svg_symbol(cx,322,1.06),
 svg_text(NAME,tx,312,size,PAPER,BOLD),svg_text(TAGLINE,tx,363,28,MUTED,FONT)])
shutil.copy2(parent/'profile-1024x1024.png',OUT/'facebook-profile-1024x1024.png')
shutil.copy2(parent/'profile-editable.svg',OUT/'facebook-profile-editable.svg')
# Typical centred desktop and mobile crops; actual Facebook UI may vary.
desktop=cover.crop((0,48,1640,672));desktop.save(OUT/'desktop-crop-preview.png',optimize=True)
mobile=cover.crop((180,0,1460,720));mobile.save(OUT/'mobile-crop-preview.png',optimize=True)
guide=cover.copy();gd=ImageDraw.Draw(guide)
gd.rectangle((180,48,1460,672),outline=GOLD,width=3)
gd.rectangle((0,480,500,719),outline=MUTED,width=2)
gd.text((24,30),'CROP GUIDE / DO NOT UPLOAD',font=ImageFont.truetype(FONT,22),fill=MUTED)
guide.save(OUT/'crop-guide-preview.png',optimize=True)
# Faithful aspect ratios in the review sheet, plus a circular avatar proof.
board=Image.new('RGB',(1600,1450),'#E9E7E0');bd=ImageDraw.Draw(board)
bold=ImageFont.truetype(BOLD,32);regular=ImageFont.truetype(FONT,23)
bd.text((64,42),NAME,font=bold,fill=INK)
bd.text((64,94),'Facebook Page / Cover and profile image',font=regular,fill='#56626A')
bd.text((64,160),'DESKTOP / APPROXIMATE CENTRED CROP',font=regular,fill=INK)
board.paste(desktop.resize((1472,560),Image.Resampling.LANCZOS),(64,205))
bd.text((64,840),'PROFILE / CIRCULAR DISPLAY',font=regular,fill=INK)
bd.text((625,840),'MOBILE / APPROXIMATE CENTRED CROP',font=regular,fill=INK)
profile=Image.open(OUT/'facebook-profile-1024x1024.png').convert('RGB')
small=profile.resize((300,300),Image.Resampling.LANCZOS)
mask=Image.new('L',(300,300));ImageDraw.Draw(mask).ellipse((0,0,299,299),fill=255)
board.paste(small,(130,940),mask)
board.paste(mobile.resize((896,504),Image.Resampling.LANCZOS),(625,895))
board.save(OUT/'facebook-design-preview.png',optimize=True)
(OUT/'README.txt').write_text('THE PHYSICS WITHIN — FACEBOOK PAGE\n\nUpload facebook-cover-1640x720.png as the Page cover.\nUpload facebook-profile-1024x1024.png as the profile picture.\n\nThe cover is composed on a 1640×720 master. Name, icon and tagline sit\ninside the intersection of typical centred desktop and mobile crops.\nEssential details avoid the lower-left profile overlap region.\nFacebook layouts can vary; keep the image centred when positioning it.\n\nPreview and crop-guide files are for checking, not uploading.\nSVG files use outlined typography and need no external fonts.\nIdentity matches the YouTube artwork. No Facebook changes were made.\n')
with zipfile.ZipFile(OUT/'the-physics-within-facebook-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['facebook-cover-1640x720.png','facebook-profile-1024x1024.png','facebook-cover-editable.svg','facebook-profile-editable.svg','README.txt']:
  z.write(OUT/name,name)
# All important geometry fits the common centred region and above profile overlaps.
assert left>=180 and tx+width<=1460
assert 322-75>=48 and 363<=480
print(OUT)
