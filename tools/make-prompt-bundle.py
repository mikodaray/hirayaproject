#!/usr/bin/env python3
"""Makes a prompt bundle: a zip with prompt.txt plus the character reference images that the prompt needs.
Run from the repo root:
  python3 tools/make-prompt-bundle.py --page 2 --out /path/to/out
  python3 tools/make-prompt-bundle.py --cover --out /path/to/out
  python3 tools/make-prompt-bundle.py --name X --prompt-md art/prompts/FILE.md --chars jeff,hal --out /path/to/out   (takes the block under ## Prompt)
  python3 tools/make-prompt-bundle.py --name my-image --prompt-file prompt.txt --chars jeff,hal --out /path/to/out
Characters: jeff, hal, mel, nikki, archie, totet. The current sheet for each is listed in SHEETS.
"""
import argparse, re, zipfile, os

SHEETS = {
 'jeff':  ('Jeff',       'art/characters/01-jeff-sheet-v1.png'),
 'hal':   ('Hal',        'art/characters/02-hal-sheet-v3.png'),
 'mel':   ('Mel',        'art/characters/03-mel-sheet-v1.png'),
 'nikki': ('Nikki',      'art/characters/04-nikki-sheet-v1.png'),
 'archie':('Sir Archie', 'art/characters/05-sir-archie-sheet-v1.png'),
 'totet': ('Totet',      'art/characters/06-totet-sheet-v1.png'),
}
NAMES = {'jeff':r'\bJeff\b','hal':r'\bHal\b','mel':r'\bMel\b','nikki':r'\bNikki\b','archie':r'\b(Sir Archie|Archie)\b','totet':r'\bTotet\b'}
ORDER = ['jeff','hal','mel','nikki','archie','totet']

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

def build(name, prompt, chars, out):
    os.makedirs(out, exist_ok=True)
    zpath = os.path.join(out, name + '.zip')
    lines = ['HIRAYA PROMPT BUNDLE: ' + name, '', 'HOW TO USE', '1. Attach the images in this bundle to your image generator, in this order:']
    for i, c in enumerate(chars, 1):
        lines.append('   %d. %s  (%s)' % (i, os.path.basename(SHEETS[c][1]), SHEETS[c][0]))
    lines += ['2. Paste everything under the line PROMPT below.', '3. CHECK THE RESULT: every person must have exactly 2 arms, 2 hands, and 5 fingers on each hand. If not, regenerate, or attach the result and ask: Keep everything the same, only fix the anatomy so every person has exactly two arms and two hands with five fingers each.', '4. If a face drifts, attach that character sheet again with the result and ask for a fix on that character only.', '', '=== PROMPT ===', '', prompt, '']
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(name + '/prompt.txt', '\n'.join(lines))
        for i, c in enumerate(chars, 1):
            z.write(SHEETS[c][1], '%s/%d-%s' % (name, i, os.path.basename(SHEETS[c][1])))
    return zpath, chars

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--page', type=int); a.add_argument('--cover', action='store_true')
    a.add_argument('--name'); a.add_argument('--prompt-file'); a.add_argument('--prompt-md'); a.add_argument('--chars')
    a.add_argument('--out', default='.')
    x = a.parse_args()
    if x.page: p, ch = page_prompt(x.page); name = 'hiraya-ch1-page-%02d' % x.page
    elif x.cover: p, ch = cover_prompt(); name = 'hiraya-ch1-cover-warriors'
    elif x.prompt_md:
        p = re.search(r'## Prompt\n```\n(.*?)\n```', open(x.prompt_md).read(), re.S).group(1).strip(); ch = [c.strip() for c in x.chars.split(',')]; name = x.name
    else: p = open(x.prompt_file).read().strip(); ch = [c.strip() for c in x.chars.split(',')]; name = x.name
    print(build(name, p, ch, x.out))
