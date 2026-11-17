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
                  "FOCUS: panels 1, 2 and 3 Jeff, panel 4 Hal, panel 5 Nikki. Darken the others and the background in those panels. Nikki's throw in panel 5 is showy and playful, an arm swing with the glasses flying high, not an attack. "),
               7: ("PAGE 7 NOTES. GLASSES EXCEPTION: Hal has no glasses on this page, squinting. The glasses are the ones Jeff catches between two fingers. FOCUS: Jeff, the splash image. Nikki's friends gather near him with hearts in their eyes, and the rest of the crowd is darker. "),
               8: ("PAGE 8 NOTES. GLASSES EXCEPTION: Hal has no glasses in panels 1 to 3, squinting, and Jeff puts them back on him in panel 4, so Hal wears them in panels 4 to 6. In panel 2 the focus is Jeff. "),
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
 6: "Jeff: steady and firm, then an amused raised eyebrow in panel 3. Nikki: irritated, then smug and annoyed in panel 5, a showy playful throw, not violent. Hal: indignant but braver, peeking from behind Jeff. Mel: dry and deadpan.",
 7: "Jeff: calm and cool, the only calm face. Nikki: shocked, eyes wide, mouth open. Nikki's friends: starry eyed and swooning, hearts in their eyes, hands over their mouths. Hal: huge amazed eyes. Mel: frozen, stunned. The students: gasping and wide eyed.",
 8: "Panel 1, Nikki's friends: dreamy sighs. Panel 2, friends: starry eyed and giddy. Panel 3, Nikki: jaw tight, a stiff forced smile, annoyed. Panel 4, Jeff: warm and teasing; Hal: relieved. Panel 5, Hal: laughing with wet eyes. Panel 6, Nikki: glancing back, conflicted and a little softer than before; her friends dreamy, still looking at Jeff.",
 9: "Sir Archie: a calm, cool, teacherly smile. Hal: cheerful and proud. Jeff: polite and attentive. Nikki: glaring, annoyed. The class: sleepy, bored, whispering.",
 10: "Sir Archie: warm and mysterious, storyteller eyes. Hal: curious and whispering. Jeff: eyes sparkling with excitement, whispering back. Nikki: bored, rolling her eyes. The class: laughing. Panel 6, Jeff: quiet, thoughtful, hand closing around his necklace.",
}
# ---- Pages 11 and up: the new arc (added 2026-11-17). The page blocks come from tools/build-page-prompts.py. ----
HOME = 'art/places/jeff-family-home-color-v1.png'
SCHOOL_PAGES |= {11, 12, 13}
HOME_PAGES = set(range(16, 23))
# Who is on each page. Sheet characters get their sheet. New characters have NO sheet yet, so they get a written look (NEWCAST).
PAGE_CAST = {11: ['jeff','hal','mel','jared','dan'], 12: ['jared','dan'], 13: ['jared','dan'], 14: ['jared'], 15: ['jared','agta'],
             16: ['jeff','twins'], 17: ['jeff','twins'], 18: ['jeff','mama','twins'], 19: ['jeff','mama','twins'], 20: ['jeff','papa'],
             21: ['jeff','papa'], 22: ['jeff','papa'], 23: ['jared'], 24: ['jared'], 25: ['jared','agta'], 26: ['jared'], 27: ['jared','agta'], 28: ['jared']}
NEWCAST = {
 'jared': "JARED CALLAO: male student, tall and slender, long straight black emo hair that falls over one eye, a small nose ring, tattoos down his whole RIGHT arm only, a spiked belt and stacks of bracelets on both wrists. He wears the boys school uniform (short sleeved buttoned shirt, khaki pants) in a punk way, untucked. Quiet, guarded face. Never wears glasses.",
 'dan': "DAN MACABEBE: male student, very big, tall and heavy, much bigger and wider than Jared, short cropped hair, thick neck, a mean grin. He wears the boys school uniform (short sleeved buttoned shirt, khaki pants). Never wears glasses.",
 'agta': "THE AGTA: a spirit, not a person. A long, thin, shadowy black figure with long limbs, a crooked grin full of teeth, and two glowing eyes. The page is black and white, so draw the eyes as two bright white glowing shapes with a dark halo, the brightest thing in the panel. Keep the body a dark shape with soft smoky edges.",
 'twins': "GAIL AND JANELLE: Jeff's twin sisters, five years old, small children with round faces, the same face and dark hair. Gail wears two pigtails and a plain house dress. Janelle wears one side ponytail and a striped house dress. Keep the hair and the dress of each twin the same in every panel.",
 'mama': "MAMA: Jeff's mother, a woman in her forties, average build, dark hair tied back in a low bun, warm sharp eyes, a house dress with an apron, and a ladle in her hand in the kitchen.",
 'papa': "PAPA: Jeff's father, a tall man in his late forties, lean and strong, short dark hair with a little gray, tired kind eyes, grease smudges on his cheek and hands, a plain work shirt, a grease stained towel over one shoulder, and a small carved wooden charm on a cord around his neck. Never wears glasses.",
}
SETTING = {
 11: "the front gate and the outside wall of Durian City High School in the golden late afternoon",
 12: "a path along the outside wall of Durian City High School, late afternoon",
 13: "a path along the outside wall of Durian City High School, late afternoon, almost empty",
 14: "a quiet road lined with old trees at dusk, in a neighborhood of Durian City, a modern Philippine city",
 15: "the same quiet road at dusk, under a huge old balete tree with hanging roots",
 16: "Jeff's family home at evening, outside and then inside the front door and hall. Draw the house exactly like the attached home reference",
 17: "inside Jeff's family home, the hall and living room, evening. Warm, simple, wood and woven bamboo walls, like the attached home reference",
 18: "the kitchen and dining table of Jeff's family home, evening, wood and woven bamboo walls",
 19: "the dining table of Jeff's family home, evening",
 20: "the kitchen back door, then the carport of Jeff's family home at night, with the jeepney from the attached home reference",
 21: "the carport of Jeff's family home at night, lit by one hanging work lamp, with the jeepney from the attached home reference",
 22: "the carport of Jeff's family home at night, with the jeepney from the attached home reference",
 23: "a small, narrow, worn house at night, and Jared's small upstairs bedroom",
 24: "Jared's small bedroom at night, lit by one desk lamp",
 25: "outside Jared's narrow house at night, with a huge old tree beside it",
 26: "Jared's small bedroom at night",
 27: "Jared's bedroom at night, in the dark, with moonlight from the window. Use a lot of solid black",
 28: "Jared's bedroom at night, in moonlight, then pure black",
}
HOME_NOTE = ("HOME REFERENCE: the attached home image is in color. Draw the house, the carport and the jeepney with the same shapes and materials in black and white with screentone. "
             "Do not copy the flag, the signs or any words from it unless a panel lists them. ")
NOSHEET = ("NEW CHARACTERS WITHOUT A SHEET. These characters have no reference image yet, so draw them from this written look and keep each one identical in every panel:\n")

EXPR.update({
 11: "Jeff: relaxed, a small goodbye smile. Mel: gentle and calm. Hal: bright and boasting about his robot. Panels 3 and 4, Jared: closed off, eyes down, tired. Panel 5, Dan: a wide mean grin, looking down; Jared: wary, looking up with one eye through his hair.",
 12: "Dan: sneering, enjoying it, teeth showing. Jared: cold, flat, jaw set, holding everything in, a flash of pain when he hits the ground. Passing students: awkward, eyes turned away.",
 13: "Dan: laughing with his head back. Jared: blank and still in panel 2, then in panel 4 hurt and shaking, eyes wet but not crying, mouth pressed shut.",
 14: "Jared: numb in panel 2, then heavy and dreading in panel 3, then in panel 5 his whole face breaks into rage, mouth wide open in a shout, eyes shut tight.",
 15: "Jared: empty and let down, staring at his hand. The Agta: delighted and hungry, a crooked grin, eyes wide.",
 16: "Jeff: tired but soft when he walks in, then a flat annoyed stare with red ears in panel 5. Gail and Janelle: huge open mouthed joy, then stubborn and smug.",
 17: "Jeff: deadpan in panel 1, confused in panel 3, and in panel 5 trying to frown while a small smile wins. Janelle: proud of her drawing. Gail: sneaky and focused.",
 18: "Mama: brisk and warm, then narrow suspicious eyes in panel 5. Jeff: chewing, dry and teasing. The twins: busy eating, cheeks full.",
 19: "Mama: caring, then a sly teasing smile in panel 4. Janelle: sneaky, then shocked. Gail: impressed. Jeff: cool and smug in panel 3, then in panel 5 choking, red faced and flustered. The twins: laughing hard.",
 20: "Papa: tired eyes with a faint smile, calm. Jeff: alert and glad to be asked. Panel 4, both: the same thinking frown. Panel 5, Papa: dry and stubborn; Jeff: flat disbelief.",
 21: "Papa: focused, then one eyebrow up and teasing in panel 3, a sly half smile in panel 5. Jeff: shy and modest in panel 2, then eyes sparkling in panel 4.",
 22: "Jeff: eager, hopeful. Papa: chuckling, then fond and proud. Panel 4, both: the same wide grin lit by the headlights.",
 23: "Jared: trying to focus in panel 2, then in panel 4 eyes squeezed shut and teeth clenched, then in panel 5 a face of helpless anger.",
 24: "Jared: ashamed and bitter, eyes down, then jaw tight, then in panel 4 shaking with hate and close to tears.",
 25: "The Agta: curious, head tilted, then a wide hungry grin, eyes glowing. Jared, tiny in the window: slumped and small.",
 26: "Jared: worn out and flat, then younger and softer without his spikes, then in panel 4 quiet and sad, eyes on the floor.",
 27: "Jared: tired, blank, noticing nothing. The Agta: gleeful, mouth wide, arms open as it dives.",
 28: "Jared: heavy eyed, confused by how tired he is, then peaceful and asleep.",
})
PAGE_NOTES.update({
 12: "PAGE 12 NOTES. Show shoving and cruelty but nothing graphic, no blood. Jared only gets a slight scrape. ",
 13: "PAGE 13 NOTES. No blood. Jared has one small scrape on his cheek and one small bruise on his forearm, and he keeps them on later pages. ",
 14: "PAGE 14 NOTES. Jared keeps the small scrape on his cheek and the small bruise on his forearm. Panel 4 is a memory: show NO violence and no faces, only the bottles, the man's shadow on the wall and the woman's hands. ",
 15: "PAGE 15 NOTES. Jared keeps the small scrape on his cheek. ",
 16: "PAGE 16 NOTES. The only sign that may be read is PILIPINAS above the jeepney windshield in panel 1. ",
 23: "PAGE 23 NOTES. Jared keeps the small scrape on his cheek. Show NO violence. The parents are never seen, only heard. ",
 24: "PAGE 24 NOTES. Jared keeps the small scrape on his cheek. ",
 26: "PAGE 26 NOTES. In panels 3 and 4 Jared has taken off his spiked belt and bracelets. He keeps his nose ring and his arm tattoos. ",
 27: "PAGE 27 NOTES. Jared has no spiked belt and no bracelets. The window glass does not break. ",
 28: "PAGE 28 NOTES. Jared has no spiked belt and no bracelets. Panel 5 is solid black with one tiny point of light in the center. ",
})
# ---- Pages 29 to 50: draft by Claude (2026-11-17) ----
SCHOOL_PAGES |= {34, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50}
HOME_PAGES |= {33}
PAGE_CAST.update({29: ['jared'], 30: ['jared','agta'], 31: ['jared','agta'], 32: ['jared'], 33: ['jeff','papa','twins'], 34: ['jeff','hal','mel','nikki','jared'],
 35: ['jeff','nikki','archie','jared'], 36: ['hal','archie','jared'], 37: ['jared','dan'], 38: ['jared','dan','agta'], 39: ['jeff','hal','mel','jared','dan','agta'],
 40: ['jeff','hal','mel','nikki','jared','dan','agta'], 41: ['jeff','nikki','jared','dan','agta'], 42: ['jeff','agta'], 43: ['jeff','hal','mel','jared','agta'],
 44: ['jeff','hal','mel','nikki','jared','agta'], 45: ['jeff','hal','mel','nikki','jared','agta'], 46: ['jeff','hal','mel','nikki'], 47: ['jeff','hal','mel','nikki'],
 48: ['jeff','hal','mel','nikki'], 49: ['jeff','hal','mel','nikki'], 50: ['jeff','archie','papa','jared','agta']})
_path = "the path along the outside wall of Durian City High School, after class, bright afternoon sun"
SETTING.update({29: "a nightmare version of Jared's kitchen, gray, stretched and too big, with heavy black shadows",
 30: "the same nightmare kitchen, with a black crack in the floor", 31: "the nightmare, almost all solid black",
 32: "Jared's bedroom in the morning light, then the small kitchen downstairs", 33: "Jeff's family home in the morning, the carport and the front gate, like the attached home reference",
 34: "the road to school and the front gate of Durian City High School in the morning", 35: "the homeroom classroom of Durian City High School, with ceiling fans, a blackboard and open windows",
 36: "the homeroom classroom of Durian City High School", 37: _path, 38: _path, 39: _path, 40: _path, 41: _path, 42: _path, 43: _path,
 44: _path + ", with a pool of black shadow spreading over the ground", 45: _path + ", with a pool of black shadow on the ground",
 46: "an endless black void with giant roots, firefly lanterns and one huge eye drifting past", 47: "the black void, then a ceiling of giant leaves, lit by one soft light",
 48: "a forest floor of thick glowing moss and giant roots in the spirit world", 49: "the spirit world: a balete tree as big as a mountain under a sky with two low suns and stars",
 50: "three places: the empty path by the school wall, the carport of Jeff's family home, and a giant root in the spirit world"})
PAGE_NOTES.update({29: "PAGE 29 NOTES. In panels 2 to 4 Jared is a seven year old boy in pajamas, with the same long black hair but no nose ring, no tattoos and no spikes. The father is ONLY a shadow on the wall. Show no violence. ",
 30: "PAGE 30 NOTES. Jared is the seven year old boy from the dream, with no nose ring, no tattoos and no spikes. ",
 32: "PAGE 32 NOTES. Jared's mother is seen only from behind. The father is never seen. ",
 38: "PAGE 38 NOTES. No blood and no injury. Dan is scared, not hurt. ", 39: "PAGE 39 NOTES. No blood and no injury. ",
 46: "PAGE 46 NOTES. Hal's scream is one long speech bubble. ", 50: "PAGE 50 NOTES. The uniform rule does not apply to Sir Archie or Papa. "})
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
    if n >= 11:
        block = block.split('\n<!--')[0].strip()
        prefix = re.sub(r'Setting: Durian City High School in Durian City, a modern Makati like Philippine city\.', 'Setting for this page: ' + SETTING[n] + '.', prefix)
        cast = PAGE_CAST[n]; new = [c for c in cast if c in NEWCAST]
        extra = NOSHEET + '\n'.join('- ' + NEWCAST[c] for c in new) if new else ''
        if n in HOME_PAGES: extra = HOME_NOTE + ('\n\n' + extra if extra else '')
        return prefix.strip() + ('\n\n' + extra if extra else '') + '\n\n' + block + '\n\n' + pre.group(2).strip(), [c for c in cast if c in mpb.SHEETS]
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
        p = p.rstrip() + '\n\n' + (cb + '\n\n' if cb else '') + mpb.NO_EXTRA_TEXT + intro_block(n, chars) + mpb.VARIED_POSES + mpb.FOCUS_RULE + mpb.crowd_block(p) + CROWD.get(n, '') + PAGE_NOTES.get(n, '') + '\n\n' + EXPR_RULE + EXPR.get(n, 'Take the emotion of each face from its panel description and its dialogue.') + mpb.JOINTS + '\n\n' + mpb.FINAL_PASS
        lk = mpb.lock_block(chars)
        if lk: p = lk + '\n\n' + p
        items = mpb.ref_items(chars, [SCHOOL] if n in SCHOOL_PAGES else [HOME] if n in HOME_PAGES else [])
        if items: p = mpb.ref_note(items) + '\n\n' + p
        needed.update(chars)
        if items:
            head = ['HIRAYA PAGE PROMPT: Chapter 1, page %d' % n, '', 'ATTACH THIS ONE IMAGE (from the references folder): page-%02d-references.jpg' % n,
                    'It combines these labeled panels, with the name written above each one: ' + ', '.join('%s (%s)' % (l, k.lower()) for l, k, _ in items) + '.']
            composites['references/page-%02d-references.jpg' % n] = items
        else:
            head = ['HIRAYA PAGE PROMPT: Chapter 1, page %d' % n, '', 'NO REFERENCE IMAGE for this page yet (the characters on it have no sheet). To keep them consistent, attach your best earlier page that shows them.']
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
