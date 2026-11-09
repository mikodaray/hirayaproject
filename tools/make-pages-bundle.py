#!/usr/bin/env python3
"""Makes ONE zip with prompts for a range of pages plus a shared references folder (character sheets, school image).
Run from the repo root:  python3 tools/make-pages-bundle.py 1 10 --out /path/to/out
Each prompts/page-NN.txt says which reference files to attach. Rules applied: sheets for the look only (no written
face descriptions), scene expressions per page (EXPR below), joints rule, school image on school pages."""
import argparse, re, zipfile, os, importlib.util
spec = importlib.util.spec_from_file_location('mpb', 'tools/make-prompt-bundle.py'); mpb = importlib.util.module_from_spec(spec); spec.loader.exec_module(mpb)

SCHOOL = 'art/places/durian-city-high-school-v1.png'
SCHOOL_PAGES = {1, 2, 3, 4, 8}

LOOK = ("Characters: draw every named character exactly as on their attached character sheet (the sheets are in color, draw them in black and white with screentone for the colors): same face, hair, body type and clothes. "
        "Use the sheets for the look only, do not copy the sheet poses or the sheet expressions. Sizes: Mel is the tallest and biggest (6'2\"), Jeff is second tallest (5'10\"), Nikki is shorter (5'4\"), Hal is the shortest (5'0\"), Sir Archie is a little shorter than Jeff. ")
EXPR_RULE = ("FACES: every face must be animated and show a clear emotion that matches its panel, with the head turned and the eyes looking where the story needs. "
             "Do not give everyone the same resting face. Use these emotions for this page:\n")
INTRO_PAGE = {'jeff': 1, 'hal': 2, 'mel': 3, 'nikki': 4}
NAMES = {'jeff': 'Jeff', 'hal': 'Hal', 'mel': 'Mel', 'nikki': 'Nikki'}
def intro_block(n, chars):
    done = [NAMES[c] for c in INTRO_PAGE if INTRO_PAGE[c] < n and c in chars]
    if not done: return ''
    return ('ALREADY INTRODUCED. ' + ', '.join(done) + (' were' if len(done) > 1 else ' was') + ' introduced with a name caption on an earlier page. '
            'On this page draw NO name caption, NO introduction and NO description for ' + ('them' if len(done) > 1 else 'him or her') + ', even when they stand in the scene, unless the CAPTIONS MUST READ EXACTLY block lists one. ')
PAGE_NOTES = {6: ("PAGE 6 NOTES. GLASSES EXCEPTION: Nikki still holds Hal's round glasses in one hand, so on this page Hal is drawn WITHOUT glasses, squinting, and Nikki's hand holding his glasses stays visible when she is in frame. "
                  "FOCUS: panels 1, 2 and 3 Jeff, panel 4 Hal, panel 5 Nikki. Darken the others and the background in those panels. "),
               5: ("PAGE 5 NOTES. GLASSES EXCEPTION: in panels 2, 3 and 4 Nikki has taken Hal's round glasses off his face, so Hal is drawn WITHOUT glasses in those panels, squinting, and Nikki holds his glasses up high. In panels 1, 5 and 6 Hal wears his round glasses if he is visible. "
                  "Panel 3 is Hal's blurry point of view, so draw only soft blurred shapes and smears, no faces in focus, and a cloud shaped thought bubble with small trailing circles that reads \"I can't see anything\". "
                  "FOCUS: panel 1 Hal, panel 2 Nikki, panel 4 Hal, panel 5 Mel, panel 6 Jeff. Darken the others and the background in those panels. ")}
CROWD = {4: ("Page 4 poses. Panel 1, the girls entering the gate all move differently: one holds a bag strap, one talks while turning toward a friend, one brushes hair from her face, one carries books against her chest, one swings her arms, one checks her phone while walking. "
             "Panel 3, the crowd parts like a wave and every student reacts differently: one steps backward, one pivots sideways, one leans away, one turns to watch Nikki, one pulls a friend aside, one pauses mid step, one looks over a shoulder. Nikki stays centered. "
             "Panel 4, Nikki's friends have unique poses: one laughs with a hand over her mouth, one adjusts her hair, one carries a shoulder bag, one walks with hands behind her back, one looks toward Nikki, and they are staggered in depth around her, not in a line. "
             "No identical body language anywhere in panels 1, 3 or 4. Every figure reads as a different person at silhouette level.")}
EXPR = {
 1: "Panel 4, Jeff: calm and quietly confident, eyes on the road ahead, a faint private smile, a little distant as if thinking about old spirits. Nearby students look at him with puzzled or amused faces.",
 2: "Panel 2, Jeff: deadpan and amused, eyes forward, one eyebrow slightly raised, a tiny smirk while counting down. Panel 3, Hal: flustered and dazed after the crash. Panel 4, Hal: offended pout, huge eyes, puffed cheeks. Panel 5, Hal: beaming and proud, bag held high; Jeff: warm and amused, grinning down at him.",
 3: "Mel: serene, eyes closed, lost in the music, then a gentle surprised smile in panel 4. Hal: excited and bouncing. Jeff: relaxed and warm, a small genuine smile. The students on the stairs: dreamy and listening.",
 4: "Panel 2, Hal: frozen with horror, jaw dropped, mid bite. Panel 4, Nikki: smug, chin up, half lidded confident eyes and a sly grin, friends giggling behind her. Panel 5, Nikki: mocking and playful, one eyebrow up. Jeff and Mel: wary and tired.",
 5: "Hal: indignant and furious, red faced, then panicked while jumping. Nikki: laughing and mocking. Her friends: giggling. Mel: troubled, eyebrows tilted with worry. Panel 6, Jeff: calm, steady, jaw set, sharp eyes.",
 6: "Jeff: steady and firm, then an amused raised eyebrow in panel 3. Nikki: irritated, then furious in panel 5. Hal: indignant but braver, peeking from behind Jeff. Mel: dry and deadpan.",
 7: "Jeff: calm and cool, the only calm face. Nikki: shocked, eyes wide, mouth open. Hal: huge amazed eyes. Mel: frozen, stunned. The students: gasping and wide eyed.",
 8: "Panel 2, Nikki: embarrassed and annoyed, a little flushed. Panel 4, Jeff: warm and teasing; Hal: relieved. Panel 5, Hal: laughing with wet eyes. Panel 6, Nikki: glancing back, conflicted and a little softer than before.",
 9: "Sir Archie: a calm, cool, teacherly smile. Hal: cheerful and proud. Jeff: polite and attentive. Nikki: glaring, annoyed. The class: sleepy, bored, whispering.",
 10: "Sir Archie: warm and mysterious, storyteller eyes. Hal: curious and whispering. Jeff: eyes sparkling with excitement, whispering back. Nikki: bored, rolling her eyes. The class: laughing. Panel 6, Jeff: quiet, thoughtful, hand closing around his necklace.",
}
PAGE10 = """## Page 10 (6 panels): The lesson
Layout: medium panel, wide illustrated panel, small panel, medium panel, small panel, small panel.

Panel 1 (medium): Sir Archie at the front. Lettering: speech bubble from Sir Archie reads "Before we start, a story. Long ago, our ancestors called these islands the Sangkapuluan."

Panel 2 (wide, illustrated, old ink map style): The islands drawn like an ancient map. Ten small points glow along the map. Lettering: caption box reads "Ten."

Panel 3 (small): Hal whispers to Jeff. Lettering: speech bubble from Hal reads "Ten what?"; speech bubble from Jeff reads "Agimats."

Panel 4 (medium): Sir Archie. Lettering: speech bubble from Sir Archie reads "Every land has its Agimats. Charms with a power of their own. Ten are said to sleep in the Sangkapuluan, our islands."

Panel 5 (small): Nikki, bored. Lettering: speech bubble from Nikki reads "So it's a fairy tale, Sir?"; speech bubble from Sir Archie reads "Every fairy tale begins with someone who stopped listening." The class laughs.

Panel 6 (small): Jeff's hand drifts to his collar and closes around the necklace."""

def prompt_for(n):
    t = open('art/prompts/ch1-pages-all-with-dialogue.md').read()
    if n == 1:
        v = open('art/prompts/ch1-page-01.md').read()
        body = re.search(r'## Version 4.*?```\n(.*?)\n```', v, re.S).group(1).strip()
        body = re.sub(r'Character: Jeff, exactly as in the attached reference sheet.*?Only Jeff appears as a main character on this page\.',
                      'Character: Jeff, exactly as on the attached character sheet (look only, not its pose or expression), in black and white with screentone, with his pendant necklace. Only Jeff appears as a main character on this page.', body, flags=re.S)
        body = body.replace('Tall, lean, effortless, cool, with a faint glow of light behind him.', 'Tall, lean, effortless, with a faint glow of light behind him, his face calm and quietly confident, a faint private smile, eyes on the road ahead.')
        return body, ['jeff']
    pre = re.search(r'## COMMON PREFIX\n(.*?)\n\n## COMMON ENDING\n(.*?)\n\n## Page', t, re.S)
    prefix = re.sub(r'Characters, same designs as the reference image but in black and white:.*?(?=Boys wear)', LOOK, pre.group(1), flags=re.S)
    m = re.search(r'## Page %d .*?(?=\n## Page %d |\Z)' % (n, n + 1), t, re.S)
    block = PAGE10 if n == 10 else m.group(0).strip()
    chars = [c for c in mpb.ORDER if re.search(mpb.NAMES[c], block) or (c in ('jeff', 'hal', 'mel') and re.search(r'\bthe trio\b', block, re.I))]  # 'the trio' means Jeff, Hal and Mel
    return prefix.strip() + '\n\n' + block + '\n\n' + pre.group(2).strip(), chars

if __name__ == '__main__':
    a = argparse.ArgumentParser(); a.add_argument('first', type=int); a.add_argument('last', type=int); a.add_argument('--out', default='.')
    x = a.parse_args()
    name = 'hiraya-ch1-pages-%02d-%02d' % (x.first, x.last)
    os.makedirs(x.out, exist_ok=True); zpath = os.path.join(x.out, name + '.zip')
    needed, files, composites = set(), {}, {}
    for n in range(x.first, x.last + 1):
        p, chars = prompt_for(n)
        if n == 1 or 'FACES:' not in p:
            p = p.replace('\n\nLayout', '\n\nLayout', 1)
        cb = mpb.caption_block(p)
        p = p.rstrip() + '\n\n' + (cb + '\n\n' if cb else '') + mpb.NO_EXTRA_TEXT + intro_block(n, chars) + mpb.VARIED_POSES + mpb.FOCUS_RULE + mpb.crowd_block(p) + CROWD.get(n, '') + PAGE_NOTES.get(n, '') + '\n\n' + EXPR_RULE + EXPR.get(n, '') + mpb.JOINTS + '\n\n' + mpb.FINAL_PASS
        lk = mpb.lock_block(chars)
        if lk: p = lk + '\n\n' + p
        items = mpb.ref_items(chars, [SCHOOL] if n in SCHOOL_PAGES else [])
        p = mpb.ref_note(items) + '\n\n' + p
        needed.update(chars)
        head = ['HIRAYA PAGE PROMPT: Chapter 1, page %d' % n, '', 'ATTACH THIS ONE IMAGE (from the references folder): page-%02d-references.jpg' % n,
                'It combines these labeled panels, with the name written above each one: ' + ', '.join('%s (%s)' % (l, k.lower()) for l, k, _ in items) + '.']
        composites['references/page-%02d-references.jpg' % n] = items
        head += ['', 'Then paste everything under the line PROMPT.',
                 'CHECK THE RESULT: every person has exactly 2 arms, each arm with exactly ONE elbow (two segments, never three), 2 hands, 5 fingers on each hand; faces show the right emotion for the panel; sound effects and captions spelled exactly. If something is wrong, regenerate or ask for a fix on that one thing only.', '', '=== PROMPT ===', '']
        files['prompts/page-%02d.txt' % n] = '\n'.join(head) + p + '\n'
    readme = ('HIRAYA CHAPTER 1, PAGES %d TO %d\n\nprompts/ has one text file per page. references/ has ONE combined image per page, with the character and location names written on it. '
              'Each page file says which combined image to attach for that page. Generate the pages in order and save each result.\n' % (x.first, x.last))
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(name + '/README.txt', readme)
        for k, v in files.items(): z.writestr(name + '/' + k, v)
        for path, its in composites.items():
            saved = mpb.save_combined(its, os.path.basename(path)); z.write(saved, name + '/' + path)
    print(zpath, sorted(needed))
