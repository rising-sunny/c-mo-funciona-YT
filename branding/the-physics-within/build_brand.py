"""Vector-first YouTube identity; no generated illustration or raster textures."""
import html
import math
from pathlib import Path
import zipfile
from PIL import Image,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

OUT=Path(__file__).resolve().parent
INK='#14212A';PAPER='#F3F0E6';GOLD='#D3B66F';MUTED='#A8B4B9';DECOR='#1B2B35'
FONT='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf'
BOLD='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf'
NAME='The Physics Within'
TAGLINE='See what makes the world work.'
SS=2


def symbol(draw,center,scale,ring=PAPER,core=GOLD):
    cx,cy=center
    def pos(x,y):return ((cx+x*scale)*SS,(cy+y*scale)*SS)
    points=[pos(64*math.cos(math.radians(a)),64*math.sin(math.radians(a))) for a in range(45,316)]
    width=12*scale*SS
    draw.arc([pos(-70,-70),pos(70,70)],start=45,end=315,fill=ring,width=round(width))
    for x,y in (points[0],points[-1]):draw.ellipse((x-width/2,y-width/2,x+width/2,y+width/2),fill=ring)
    a=pos(-10,-10);b=pos(10,10);draw.ellipse((*a,*b),fill=core)
    draw.line([pos(29,0),pos(70,0)],fill=core,width=round(5*scale*SS))
    for x in (29,70):
        px,py=pos(x,0);r=2.5*scale*SS;draw.ellipse((px-r,py-r,px+r,py+r),fill=core)


def svg_symbol(cx,cy,scale,ring=PAPER,core=GOLD):
    return f'<g transform="translate({cx} {cy}) scale({scale})"><path d="M45.255 45.255 A64 64 0 1 1 45.255 -45.255" fill="none" stroke="{ring}" stroke-width="12" stroke-linecap="round"/><circle r="10" fill="{core}"/><path d="M29 0 H70" fill="none" stroke="{core}" stroke-width="5" stroke-linecap="round"/></g>'


def svg_text(text,x,baseline,size,color,font_path):
    font=TTFont(font_path);glyphs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm
    measuring=ImageFont.truetype(font_path,size)
    paths=[]
    for i,ch in enumerate(text):
        glyph=cmap.get(ord(ch))
        if not glyph:continue
        pen=SVGPathPen(glyphs);glyphs[glyph].draw(pen)
        xx=x+measuring.getlength(text[:i])
        paths.append(f'<path transform="translate({xx:.4f} {baseline}) scale({size/upm:.7f} {-size/upm:.7f})" d="{pen.getCommands()}"/>')
    return f'<g fill="{color}" aria-label="{html.escape(text)}">'+''.join(paths)+'</g>'


def save_svg(name,w,h,parts):
    (OUT/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{NAME}</title>'+''.join(parts)+'</svg>')


# All essential information sits within YouTube's centred 1546 × 423 safe area.
w,h=2560,1440
font=ImageFont.truetype(BOLD,88)
name_width=font.getlength(NAME)
mark_width=180;gap=48
left=(w-(mark_width+gap+name_width))/2
cx=left+mark_width/2
text_x=left+mark_width+gap
banner=Image.new('RGB',(w*SS,h*SS),INK);d=ImageDraw.Draw(banner)
# A single oversized cutaway motif is confined to the TV-only edge.
symbol(d,(2480,720),5,DECOR,DECOR)
symbol(d,(cx,720),1.16)
d.text((text_x*SS,714*SS),NAME,font=ImageFont.truetype(BOLD,88*SS),fill=PAPER,anchor='ls')
d.text((text_x*SS,777*SS),TAGLINE,font=ImageFont.truetype(FONT,32*SS),fill=MUTED,anchor='ls')
banner=banner.resize((w,h),Image.Resampling.LANCZOS)
banner.save(OUT/'banner-2560x1440.png',optimize=True)
parts=[f'<rect width="{w}" height="{h}" fill="{INK}"/>',svg_symbol(2480,720,5,DECOR,DECOR),svg_symbol(cx,720,1.16),
       svg_text(NAME,text_x,714,88,PAPER,BOLD),svg_text(TAGLINE,text_x,777,32,MUTED,FONT)]
save_svg('banner-editable.svg',w,h,parts)
# Square upload file; circular cropping leaves generous breathing room.
profile=Image.new('RGB',(1024*SS,1024*SS),INK);symbol(ImageDraw.Draw(profile),(512,512),4.5)
profile=profile.resize((1024,1024),Image.Resampling.LANCZOS)
profile.save(OUT/'profile-1024x1024.png',optimize=True)
save_svg('profile-editable.svg',1024,1024,[f'<rect width="1024" height="1024" fill="{INK}"/>',svg_symbol(512,512,4.5)])
# Device crops and safe area proof are review files, not the upload master.
safe=(507,508,2053,931)
mobile=banner.crop(safe);mobile.save(OUT/'mobile-crop-preview.png',optimize=True)
guide=banner.copy();gd=ImageDraw.Draw(guide)
gd.rectangle(safe,outline=GOLD,width=3)
gd.text((517,464),'MOBILE SAFE AREA · 1546 × 423',font=ImageFont.truetype(FONT,23),fill=GOLD)
guide.save(OUT/'safe-area-preview.png',optimize=True)
regular=ImageFont.truetype(FONT,22);bold=ImageFont.truetype(BOLD,30)
review=Image.new('RGB',(1600,1440),'#E9E7E0');rd=ImageDraw.Draw(review)
rd.text((64,40),NAME,font=bold,fill=INK)
rd.text((64,90),'Banner · Profile · Mobile-safe layout',font=regular,fill='#56626A')
rd.text((64,145),'BANNER / 2560 × 1440',font=regular,fill=INK)
review.paste(banner.resize((1472,828),Image.Resampling.LANCZOS),(64,182))
rd.text((64,1050),'PROFILE',font=regular,fill=INK)
profile_small=profile.resize((200,200),Image.Resampling.LANCZOS)
mask=Image.new('L',(200,200));ImageDraw.Draw(mask).ellipse((0,0,199,199),fill=255)
review.paste(profile_small,(64,1090),mask)
rd.text((350,1050),'MOBILE / SAFE AREA',font=regular,fill=INK)
review.paste(mobile.resize((1160,317),Image.Resampling.LANCZOS),(350,1090))
review.save(OUT/'design-preview.png',optimize=True)
(OUT/'README.txt').write_text('THE PHYSICS WITHIN — YouTube identity\n\nUpload banner-2560x1440.png as the channel banner.\nUpload profile-1024x1024.png as the profile picture.\n\nThe banner keeps name, symbol and tagline inside the centred 1546×423 mobile-safe area.\nThe SVG files contain outlined lettering, with no external font dependencies.\nColours: ink '+INK+', warm white '+PAPER+', gold '+GOLD+'.\nTypography: Nimbus Sans.\nThe symbol is a cutaway ring with a revealed core, not a gear or atom illustration.\nPreview and guide files are for review, not for upload.\nNo channel changes or uploads have been performed.\n')
with zipfile.ZipFile(OUT/'the-physics-within-brand-kit.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['banner-2560x1440.png','profile-1024x1024.png','banner-editable.svg','profile-editable.svg','README.txt']:
        z.write(OUT/name,name)
print(OUT)
print('Essential width',round(mark_width+gap+name_width),'px; safe area 1546 px')
