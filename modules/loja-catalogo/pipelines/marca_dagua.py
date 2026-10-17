#!/usr/bin/env python3
"""Marca d'água sutil anti-cópia para fotos de produto (módulo loja-catalogo do claude-mind).

Duas camadas: (1) o selo/logo da loja num canto, com sombra suave para ler tanto em fundo claro
quanto escuro; (2) uma camada MUITO sutil do nome da loja repetido na diagonal cobrindo todo o
quadro — é o que impede clonar recortando o canto, sem atrapalhar a visualização.

A logo entra como PNG com fundo transparente (idealmente a marca em branco). Validado na Chronos Lab
(2026-10-17): selo 16,5% da largura, logo branco a 73%, camada diagonal a ~5%.

Dependências: pip install pillow

Uso:
  python3 marca_dagua.py logo.png foto1.jpg foto2.jpg --out marcadas/ --nome "CHRONOS LAB"
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def _font(size):
    for p in ("/System/Library/Fonts/Futura.ttc","/System/Library/Fonts/Supplemental/Arial Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(p, size, index=2 if p.endswith("Futura.ttc") else 0)
        except Exception: continue
    return ImageFont.load_default()

def _faint(W, H, nome, alpha=13, deg=-28):
    f=_font(int(W*0.020)); tb=ImageDraw.Draw(Image.new("RGBA",(1,1))).textbbox((0,0),nome,font=f)
    tw,th=tb[2]-tb[0],tb[3]-tb[1]; stepx,stepy=tw+int(W*0.10),int(th*4.0); big=W+H
    tile=Image.new("RGBA",(big,big),(0,0,0,0)); d=ImageDraw.Draw(tile)
    for yi,y in enumerate(range(-th,big,stepy)):
        xoff=(stepx//2) if yi%2 else 0
        for x in range(-tw,big,stepx): d.text((x+xoff,y),nome,font=f,fill=(255,255,255,alpha))
    tile=tile.rotate(deg,resample=Image.BICUBIC,expand=False); cx,cy=tile.width//2,tile.height//2
    return tile.crop((cx-W//2,cy-H//2,cx-W//2+W,cy-H//2+H))

def apply(img, logo, nome, frac=0.165, margin=0.038, logo_alpha=185, faint_alpha=13):
    img=img.convert("RGBA"); W,H=img.size
    if faint_alpha>0 and nome: img.alpha_composite(_faint(W,H,nome,faint_alpha))
    s=int(W*frac); m=int(W*margin); lg=logo.convert("RGBA").resize((s,s),Image.LANCZOS)
    r,g,b,a=lg.split()
    white=Image.merge("RGBA",(r.point(lambda _:255),g.point(lambda _:255),b.point(lambda _:255),a.point(lambda v:int(v*logo_alpha/255))))
    shadow=Image.merge("RGBA",(r.point(lambda _:0),g.point(lambda _:0),b.point(lambda _:0),a.point(lambda v:int(v*150/255)))).filter(ImageFilter.GaussianBlur(int(s*0.018)))
    pos=(W-s-m,H-s-m); img.alpha_composite(shadow,(pos[0]+int(s*0.01),pos[1]+int(s*0.015))); img.alpha_composite(white,pos)
    return img.convert("RGB")

def main():
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logo"); ap.add_argument("fotos",nargs="+"); ap.add_argument("--out",default="marcadas")
    ap.add_argument("--nome",default=""); ap.add_argument("--frac",type=float,default=0.165); ap.add_argument("--faint",type=int,default=13)
    a=ap.parse_args(); logo=Image.open(a.logo); os.makedirs(a.out,exist_ok=True)
    for p in a.fotos:
        out=apply(Image.open(p),logo,a.nome,frac=a.frac,faint_alpha=a.faint)
        dst=os.path.join(a.out,os.path.basename(p)); out.save(dst,quality=92,subsampling=1,optimize=True); print(f"{os.path.basename(p)} -> {dst}")

if __name__=="__main__": main()
