#!/usr/bin/env python3
"""Makes a prompt bundle: a zip with prompt.txt plus the character reference images that the prompt needs.
Run from the repo root:
  python3 tools/make-prompt-bundle.py --page 2 --out /path/to/out
  python3 tools/make-prompt-bundle.py --cover --out /path/to/out   (adds the logo automatically)
  add --extra file1,file2 to attach any other reference images
  python3 tools/make-prompt-bundle.py --name X --prompt-md art/prompts/FILE.md --chars jeff,hal --out /path/to/out   (takes the block under ## Prompt)
  python3 tools/make-prompt-bundle.py --name my-image --prompt-file prompt.txt --chars jeff,hal --out /path/to/out
Characters: jeff, hal, mel, nikki, archie, totet, procopio. The current sheet for each is listed in SHEETS.
"""
import argparse, re, zipfile, os

SHEETS = {
 'jeff':  ('Jeff',       'art/characters/01-jeff-sheet-v1.png'),
 'hal':   ('Hal',        'art/characters/02-hal-sheet-v3.png'),
 'mel':   ('Mel',        'art/characters/03-mel-sheet-v1.png'),
 'nikki': ('Nikki',      'art/characters/04-nikki-sheet-v1.png'),
 'archie':('Sir Archie', 'art/characters/05-sir-archie-sheet-v1.png'),
 'totet': ('Totet',      'art/characters/06-totet-sheet-v1.png'),
 'procopio': ('Tandang Procopio', 'art/characters/07-tandang-procopio-sheet-v1.png'),
}
NAMES = {'jeff':r'\bJeff\b','hal':r'\bHal\b','mel':r'\bMel\b','nikki':r'\bNikki\b','archie':r'\b(Sir Archie|Archie)\b','totet':r'\bTotet\b','procopio':r'\b(Tandang Procopio|Procopio)\b'}
ORDER = ['jeff','hal','mel','nikki','archie','totet','procopio']

def page_prompt(n):
    t = open('art/prompts/ch1-pages-all-with-dialogue.md').read()
    if n == 1:
        v = open('art/prompts/ch1-page-01.md').read()
        m = re.search(r'## Version 4.*?```\n(.*?)\n```', v, re.S)
        return m.group(1).strip(), ['jeff']
    pre = re.search(r'## COMMON PREFIX\n(.*?)\n\n## COMMON ENDING\n(.*?)\n\n## Page', t, re.S)
    m = re.search(r'## Page %d .*?(?=\n## Page %d |\Z)' % (n, n + 1), t, re.S)
    block = m.group(0).strip()
    chars = [c for c in ORDER if re.search(NAMES[c], block)]
    return pre.group(1).strip() + '\n\n' + block + '\n\n' + pre.group(2).strip(), chars

def cover_prompt():
    t = open('art/prompts/03-chapter-1-cover-warriors.md').read()
    return re.search(r'## Prompt\n```\n(.*?)\n```', t, re.S).group(1).strip(), ['jeff','hal','mel','nikki']

JOINTS = (" Joints must be correct: every arm has exactly two segments, an upper arm and a forearm, joined at exactly ONE elbow, from a shoulder that sits right next to the neck and torso to the wrist, "
          "with no extra bend, no second elbow, no third segment, and every leg has exactly one knee. Check every arm of every person, including folded arms, arms resting on desks and hands held to the face. "
          "Avoid arms with three segments, two elbows, extra joints, extra bends, rubbery or too long arms, and arms attached in the wrong place.")

# Added 2026-11-08 at the creator's request: goes at the very end of EVERY image generation prompt.
FINAL_PASS = "Final anatomy pass before rendering: inspect every visible character and remove any extra limbs, extra fingers, duplicate hands, merged hands, phantom hands, or malformed joints."

# ---- Character lock and exact caption copy (added 2026-11-08 after the page 2 generation problems) ----
# Goes at the very START of every prompt, before the page description. Only decided facts from story-bible/characters/.
# No numeric heights here on purpose, so the generator never letters them on the page.
LOCKS = {
 'jeff':  ('JEFF', 'male', 'messy ube purple hair falling over one eye, narrow calm eyes, relaxed expression, small pendant necklace, tall and lean, calm demeanor. NEVER wears glasses.', 'boys'),
 'hal':   ('HAL BAUTISTA', 'male', 'neat combed chestnut brown hair, big round thin black framed glasses, loud and expressive, very short but with an 18 year old body, not childlike. ALWAYS wears round glasses.', 'boys'),
 'mel':   ('MEL', 'male', 'long wavy golden blonde hair, big, tall and gentle looking, carries a brown wooden violin. Never wears glasses.', 'boys'),
 'nikki': ('NIKKI', 'female', 'long wavy chestnut brown hair with a side part and a white hair clip, curvy fuller figure drawn naturally and modestly, playful smirk. Never wears glasses.', 'girls'),
 'archie':('SIR ARCHIE', 'male', 'messy short pure white hair, thin dark rectangle glasses, tall, muscular and athletic, cream fitted buttoned shirt with a long brown cardigan, ID lanyard, black coffee thermos. ALWAYS wears rectangle glasses.', None),
 'totet': ('TOTET', 'female', 'glossy black bob cut with straight bangs, freckles on both cheeks and nose, short and petite. Never wears glasses.', 'girls'),
 'procopio': ('TANDANG PROCOPIO', 'male', 'very old, short silver white hair, short white goatee and mustache, scar across the left eye, dense tattoos on the whole right arm, beige cloth vest or robe over a dark wrap skirt, barefoot, layered beaded necklaces. Never wears glasses.', None),
}
GLASSES = ('hal', 'archie')

def _join(names):
    return names[0] if len(names) == 1 else ', '.join(names[:-1]) + ' and ' + names[-1]

def lock_block(chars):
    cs = [c for c in ORDER if c in chars and c in LOCKS]
    if not cs: return ''
    out = ['CHARACTER LOCK. CHARACTER CONSISTENCY IS MORE IMPORTANT THAN STYLE.',
           'These are recurring characters. Draw each one identically in every panel, exactly as on their attached character sheet. '
           'Do not redesign faces, hair, clothing, proportions, or accessories between panels, including in close ups and when characters overlap or stand close together.']
    for c in cs:
        n, g, d, _ = LOCKS[c]; out.append('%s: %s. %s' % (n, g, d))
    gl = [SHEETS[c][0] for c in cs if c in GLASSES]
    if gl:
        out.append('ACCESSORY RULES: Only %s %s glasses on this page. Everyone else never wears glasses.' % (_join(gl), 'wears' if len(gl) == 1 else 'wear'))
    else:
        out.append('ACCESSORY RULES: No named character wears glasses on this page.')
    out.append('Do not transfer accessories, hair, or clothing from one character to another.')
    boys = [SHEETS[c][0] for c in cs if LOCKS[c][3] == 'boys']
    girls = [SHEETS[c][0] for c in cs if LOCKS[c][3] == 'girls']
    u = []
    if boys: u.append('%s %s male and %s the boys school uniform (blue short sleeved buttoned shirt, khaki pants, black shoes) in every panel. Never draw %s in a skirt, blouse, dress, or any female uniform.' % (_join(boys), 'is' if len(boys) == 1 else 'are', 'wears' if len(boys) == 1 else 'wear', _join(boys)))
    if girls: u.append('%s %s female and %s the girls school uniform (white short sleeved blouse and white skirt) in every panel.' % (_join(girls), 'is' if len(girls) == 1 else 'are', 'wears' if len(girls) == 1 else 'wear'))
    if u: out.append('UNIFORM RULES: ' + ' '.join(u))
    return '\n'.join(out)

def caption_block(prompt):
    caps = re.findall(r'caption box reads "([^"]+)"', prompt)
    if not caps: return ''
    return ('CAPTIONS MUST READ EXACTLY as written here, nothing added and nothing removed. No extra lines, no extra facts, no ages, no heights, no relationships, and no leftover wording from earlier versions:\n'
            + '\n'.join('- "%s"' % c for c in caps))

def build(name, prompt, chars, out, extra=()):
    os.makedirs(out, exist_ok=True)
    zpath = os.path.join(out, name + '.zip')
    if 'CHARACTER LOCK' not in prompt and lock_block(chars): prompt = lock_block(chars) + '\n\n' + prompt
    if 'CAPTIONS MUST READ EXACTLY' not in prompt and caption_block(prompt): prompt = prompt.rstrip() + '\n\n' + caption_block(prompt)
    if 'ONE elbow' not in prompt: prompt = prompt.rstrip() + JOINTS
    if FINAL_PASS not in prompt: prompt = prompt.rstrip() + '\n\n' + FINAL_PASS
    lines = ['HIRAYA PROMPT BUNDLE: ' + name, '', 'HOW TO USE', '1. Attach the images in this bundle to your image generator, in this order:']
    for k, f in enumerate(extra, 1):
        lines.append('   %d. %s  (extra reference)' % (k, os.path.basename(f)))
    for i, c in enumerate(chars, 1):
        lines.append('   %d. %s  (%s)' % (i + len(extra), os.path.basename(SHEETS[c][1]), SHEETS[c][0]))
    lines += ['2. Paste everything under the line PROMPT below.', '3. CHECK THE RESULT: every person must have exactly 2 arms, each arm with exactly ONE elbow (two segments, never three), 2 hands, and 5 fingers on each hand. If not, regenerate, or attach the result and ask: Keep everything the same, only fix the anatomy so every person has exactly two arms and two hands with five fingers each.', '4. If a face drifts, attach that character sheet again with the result and ask for a fix on that character only.', '5. Faces must match the scene: animated, clear emotion, not the same resting face as the character sheet. If a face looks flat or copied, ask: Keep everything the same, only redraw the face of NAME with an expression that fits the scene (describe the emotion), animated and clearly showing emotion.', '', '=== PROMPT ===', '', prompt, '']
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(name + '/prompt.txt', '\n'.join(lines))
        for k, f in enumerate(extra, 1):
            z.write(f, '%s/%d-%s' % (name, k, os.path.basename(f)))
        for i, c in enumerate(chars, 1):
            z.write(SHEETS[c][1], '%s/%d-%s' % (name, i + len(extra), os.path.basename(SHEETS[c][1])))
    return zpath, chars

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--page', type=int); a.add_argument('--cover', action='store_true')
    a.add_argument('--name'); a.add_argument('--prompt-file'); a.add_argument('--prompt-md'); a.add_argument('--chars')
    a.add_argument('--out', default='.'); a.add_argument('--extra', default='')
    x = a.parse_args()
    if x.page: p, ch = page_prompt(x.page); name = 'hiraya-ch1-page-%02d' % x.page
    elif x.cover: p, ch = cover_prompt(); name = 'hiraya-ch1-cover-1-v3'
    elif x.prompt_md:
        p = re.search(r'## Prompt\n```\n(.*?)\n```', open(x.prompt_md).read(), re.S).group(1).strip(); ch = [c.strip() for c in x.chars.split(',')]; name = x.name
    else: p = open(x.prompt_file).read().strip(); ch = [c.strip() for c in x.chars.split(',')]; name = x.name
    ex = [e for e in x.extra.split(',') if e]
    if x.cover and not ex: ex = ['art/logo/hiraya-logo.png']
    print(build(name, p, ch, x.out, ex))
