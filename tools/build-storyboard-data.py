#!/usr/bin/env python3
"""Builds storyboard-data.js from story-bible/chapter-1/pages-*.md plus the panel layouts below.
Run from the repo root:  python3 tools/build-storyboard-data.py
Layouts: rows from top to bottom. Each row is (height weight, "cells"). Cells are listed in READING ORDER,
so the first cell sits on the LEFT (the book reads left to right, changed 2026-11-08). A cell is a width weight, like 1.2,
or a vertical stack, like 1.1[1,1,1] (width 1.1, three panels stacked). Panels are numbered in the order listed.
"""
import glob, json, re

LAYOUTS = {
 # Pages 1 to 10: the approved introduction.
 # Pages 11 to 14: the Sangkapuluan myth inside Sir Archie's lesson, inserted 2026-11-23.
 # Pages 15 to 32: the new arc (these were 11 to 28 before the insert).
 # Pages 33 to 54: draft by Claude 2026-11-17 (these were 29 to 50 before the insert).
 1: [(22, '1'), (30, '1.2 1'), (48, '1')],
 2: [(20, '1'), (16, '1 1'), (44, '0.8 1.2')],
 3: [(16, '1'), (44, '0.9 1.1[1,1,1]'), (40, '1')],
 4: [(20, '1'), (26, '1 1'), (30, '1'), (24, '1')],
 5: [(22, '0.6 1.4'), (24, '1 1 1'), (54, '1')],
 6: [(18, '1'), (22, '1 1'), (14, '1'), (46, '1')],
 7: [(100, '1')],
 8: [(16, '1'), (18, '1 1'), (24, '1.4 0.9'), (20, '1')],
 9: [(18, '1'), (24, '0.8 1.4 0.8'), (58, '1')],
 10: [(24, '1 1.5'), (22, '0.8 1.2'), (24, '1 1')],
 11: [(20, '1'), (22, '1'), (18, '1 1'), (40, '1')],
 12: [(20, '1'), (18, '1 1'), (22, '1'), (40, '1')],
 13: [(100, '1')],
 14: [(20, '1 1 1'), (20, '1'), (16, '1'), (44, '1')],
 15: [(22, '1'), (18, '1 1'), (14, '1'), (46, '1')],
 16: [(40, '1.3 0.7'), (20, '1 1'), (40, '1')],
 17: [(18, '1 1'), (22, '1'), (60, '1')],
 18: [(22, '1'), (20, '1 1'), (20, '1'), (38, '1')],
 19: [(20, '1'), (14, '1 1'), (66, '1')],
 20: [(24, '1'), (18, '1 1'), (58, '1 1')],
 21: [(20, '1 1'), (30, '1.2 0.8'), (50, '1')],
 22: [(24, '1'), (26, '1 1'), (50, '1 1')],
 23: [(22, '1 1'), (26, '1'), (26, '1'), (26, '1')],
 24: [(22, '1'), (18, '1 1'), (60, '1.2 0.8')],
 25: [(24, '1 1'), (40, '1'), (36, '1 1')],
 26: [(24, '1'), (24, '1 1'), (52, '1')],
 27: [(22, '1'), (20, '1 1'), (58, '1 1')],
 28: [(50, '1'), (20, '1 1'), (30, '1')],
 29: [(30, '1'), (20, '1 1'), (50, '1')],
 30: [(24, '1 1'), (20, '1'), (56, '1')],
 31: [(24, '1'), (20, '1 1 1'), (56, '1')],
 32: [(20, '1'), (20, '1 1'), (20, '1'), (40, '1')],
 33: [(24, '1'), (20, '1 1'), (56, '1')],
 34: [(20, '1 1'), (28, '1'), (52, '1 1')],
 35: [(100, '1')],
 36: [(24, '1'), (20, '1 1'), (56, '1 1')],
 37: [(24, '1'), (18, '1 1'), (58, '1.3 0.7')],
 38: [(26, '1'), (22, '1 1 1'), (52, '1')],
 39: [(26, '1'), (20, '1 1'), (54, '1.3 0.7')],
 40: [(20, '1 1'), (22, '1'), (58, '1')],
 41: [(24, '1'), (20, '1 1'), (56, '1 1')],
 42: [(44, '1 1[1,1]'), (56, '1')],
 43: [(20, '1 1'), (24, '1'), (56, '1 1')],
 44: [(26, '1'), (20, '1 1'), (54, '1.3 0.7')],
 45: [(20, '1 1'), (24, '1'), (56, '1')],
 46: [(24, '1'), (20, '1 1 1'), (56, '1')],
 47: [(20, '1 1'), (26, '1'), (54, '1 1')],
 48: [(26, '1'), (20, '1 1'), (54, '1')],
 49: [(20, '1 1 1'), (24, '1'), (56, '1')],
 50: [(50, '1 1'), (25, '1'), (25, '1')],
 51: [(26, '1'), (20, '1 1'), (54, '1')],
 52: [(26, '1'), (22, '1 1 1'), (52, '1')],
 53: [(100, '1')],
 54: [(26, '1'), (20, '1 1'), (54, '1 1')],
}
# pages 29 to 50: draft by Claude (2026-11-17)
PAD, GX, GY = 3.0, 2.4, 1.6

def rects(layout):
    out=[]; nrows=len(layout); tot=sum(h for h,_ in layout)
    H=100-2*PAD-GY*(nrows-1); y=PAD
    for h,cells in layout:
        rh=H*h/tot; parsed=[]
        for c in cells.split():
            m=re.match(r'([\d.]+)(?:\[([\d.,]+)\])?$',c)
            parsed.append((float(m.group(1)), [float(v) for v in m.group(2).split(',')] if m.group(2) else None))
        W=100-2*PAD-GX*(len(parsed)-1); wt=sum(w for w,_ in parsed); x=PAD  # start at the left edge
        for w,stack in parsed:
            cw=W*w/wt; x0=x
            if stack:
                sh=(rh-GY*(len(stack)-1)); st=sum(stack); yy=y
                for s in stack:
                    hh=sh*s/st; out.append([round(x0,2),round(yy,2),round(cw,2),round(hh,2)]); yy+=hh+GY
            else:
                out.append([round(x0,2),round(y,2),round(cw,2),round(rh,2)])
            x=x0+cw+GX
        y+=rh+GY
    return out

dlg=re.compile(r"^([A-Z][A-Z' 0-9]*?)(?: \(([^)]*)\))?: (.*)$")
pages=[]
for f in sorted(glob.glob('story-bible/chapter-1/pages-*.md')):
    for blk in re.split(r'\n## (?=Page )',open(f).read())[1:]:
        lines=blk.split('\n'); h=re.match(r'Page (\d+) \(([^)]*)\): (.*)',lines[0])
        n=int(h.group(1)); kind=h.group(2); title=h.group(3).strip()
        layout='';panels=[];cur=None;note=''
        for ln in lines[1:]:
            ln=ln.strip()
            if not ln or ln=='---': continue
            if ln.startswith('Layout:'): layout=ln[7:].strip(); continue
            if ln.startswith('Art note:'): note=ln[9:].strip(); continue
            m=re.match(r'\*\*(\d+)\. ([^*]*?)\.\*\*\s*(.*)',ln)
            if m: cur={'n':int(m.group(1)),'size':re.sub(r'\s*\(.*','',m.group(2)).strip().title(),'desc':m.group(3),'lines':[]}; panels.append(cur); continue
            if cur is None: continue
            th=re.match(r'^Then(?:,)?(?: ([a-z ]+))?: "(.*)"\.?$',ln)
            prev=[x for x in cur['lines'] if x['k']=='say']
            if th and prev:
                cur['lines'].append({'k':'say','who':prev[-1]['who'],'mod':(th.group(1) or '').strip(),'t':'"'+th.group(2)+'"'}); continue
            d=dlg.match(ln)
            if d:
                who,mod,t=d.groups(); k='say'
                if who=='CAPTION': k='cap'
                elif who=='SFX': k='sfx'
                cur['lines'].append({'k':k,'who':who.title() if k=='say' else '', 'mod':mod or '', 't':t.strip()})
            else: cur['desc']+=' '+ln
        r=rects(LAYOUTS[n]); assert len(r)==len(panels),(n,len(r),len(panels))
        for i,p in enumerate(panels): p['rect']=r[i]
        pages.append({'n':n,'title':title,'splash':'SPLASH' in kind,'layout':layout,'note':note,'panels':panels})
pages.sort(key=lambda p:p['n']); assert len(pages)==54
open('storyboard-data.js','w').write('// Built by tools/build-storyboard-data.py from the storyboard files. Do not edit by hand.\nvar STORY = '+json.dumps(pages,ensure_ascii=False,separators=(',',':'))+';\n')
print('ok',len(pages))
