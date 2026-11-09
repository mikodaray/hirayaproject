#!/usr/bin/env python3
"""Builds wiki-data.js (the wiki glossary) from the mythology files.
Reads story-bible/mythology/08-bestiary-by-lineage.md and 09-folk-deities-by-lineage.md, adds the gods and concepts defined below.
Run from the repo root: python3 tools/build-wiki-data.py
"""
import re, json

LINES = ['Sicalac and Sicabay', 'Maguayan', 'Captan', 'Lidagat', 'Lihangin', 'Licalibutan', 'Liadlao', 'Libulan', 'Lisuga']

GODS = [
 dict(name='Maguayan', lines=['Maguayan'], rank=1, domain='The sea, the deep, renewal, growth',
  desc='God of the sea and one of the two first gods. He ruled the water when there was only sea beneath the sky. After the rebellion and the lightning, he planted a seed in the broken land, and from its bamboo came the first people. His answer to loss was hope, not revenge. That first hope is hiraya.',
  agimat='Holds the strongest Agimat of the sea. Its hope is that what is broken can live again.', nature='Patient. Friendly, but the most powerful of all.'),
 dict(name='Captan', lines=['Captan'], rank=1, domain='The sky, lightning, judgment, order',
  desc='God of the sky and one of the two first gods. When his grandchildren attacked the sky he struck them with lightning, and what was left became the sun, the moon, the stars, and the land. He is a guardian and a judge. He is not cruel, but he will defend the order of the sky at any cost.',
  agimat='Holds the strongest Agimat of the sky. Its hope is a promise that the sky will be defended.', nature='A judge. Neither kind nor cruel, and dangerous in the wrong hands.'),
 dict(name='Lidagat', lines=['Lidagat'], rank=2, domain='Tides, shores, rivers, travel',
  desc='The sea itself, child of Maguayan and Captan, married to Lihangin. Mother or father of the four who rebelled. The tides answer to Lidagat, and the tides are pulled by the moon, which ties Lidagat to Libulan.',
  agimat='Holds a rank 2 Agimat. Its hope is a way home for the lost.', nature='Friendly.'),
 dict(name='Lihangin', lines=['Lihangin'], rank=2, domain='The wind, voice, words that carry',
  desc='The wind, child of Maguayan and Captan, married to Lidagat. The wind carries voices and spoken words, which is why reading the old script aloud matters. Unseen spirits of the air are among the wind\'s children.',
  agimat='Holds a rank 2 Agimat. Its hope is a word that is heard.', nature='Friendly.'),
 dict(name='Licalibutan', lines=['Licalibutan'], rank=3, domain='The land, stone, strength, pride',
  desc='The strongest and proudest of the four grandchildren. He persuaded his brothers to attack the sky. Captan\'s lightning broke his body apart, and the pieces became the land and the islands. The land remembers his pride, and the dark kin, the beings that prey on people, follow his line.',
  agimat='Holds a rank 3 Agimat. Its hope is the wish to stand on one\'s own and above. It is the Agimat that can corrupt its bearer.', nature='Dangerous, born from pride.'),
 dict(name='Liadlao', lines=['Liadlao'], rank=3, domain='The sun, light, warmth, dawn',
  desc='One of the four grandchildren, warm and bright, who followed his brother into the rebellion. The lightning made him the sun. His Agimat has already awoken in the story. Dawn and the first glimmer of light, banaag, belong to him.',
  agimat='Holds a rank 3 Agimat. Its hope is the light that begins again. It has awoken in the hands of a young bearer.', nature='Friendly.'),
 dict(name='Libulan', lines=['Libulan'], rank=3, domain='The moon, night, dreams, quiet',
  desc='One of the four grandchildren, quiet and watchful. He saw where the rebellion was going and went with his brothers out of loyalty. The lightning made him the moon. The moon swallowing beings hunger for him, and his line has the night fliers.',
  agimat='Holds a rank 3 Agimat. Its hope is the watch kept for those asleep.', nature='Friendly, but moody.'),
 dict(name='Lisuga', lines=['Lisuga'], rank=3, domain='The stars, silver, beauty, guidance',
  desc='The silver one, the youngest of the four, who did not want war and was swept up in it. Her silver body scattered across the sky as the stars. Her line has the fair and the fallen, the engkanto and their dark kin.',
  agimat='Holds a rank 3 Agimat. Its hope is a light to find the way.', nature='Friendly.'),
 dict(name='Sicalac', lines=['Sicalac and Sicabay'], rank=4, domain='Life, bonds, people, bamboo',
  desc='The first man, who came out of the bamboo that grew from Maguayan\'s seed. With Sicabay, the first of all people. Their line includes Libo, Saman, Pandaguan, and Arion.',
  agimat='Shares the rank 4 Agimat of the first people with Sicabay. Its hope is the wish to belong.', nature='Friendly.'),
 dict(name='Sicabay', lines=['Sicalac and Sicabay'], rank=4, domain='Life, bonds, people, bamboo',
  desc='The first woman, who came out of the bamboo that grew from Maguayan\'s seed. With Sicalac, the first of all people.',
  agimat='Shares the rank 4 Agimat of the first people with Sicalac. Its hope is the wish to belong.', nature='Friendly.'),
]

CONCEPTS = [
 ('Agimat', 'A wish made real. An Agimat holds one hope, and its power is the shape of that hope. There are ten in the Sangkapuluan, patroned by the gods of the family of Maguayan and Captan. Agimats exist in other lands as well.'),
 ('Hiraya', 'A Filipino word for imagination, dream, and hope. In this mythos it is the name of Maguayan\'s first wish, the seed that grew into the first people.'),
 ('Hiraya manawari', 'The wish that your dreams come true. The first words of the First Wish.'),
 ('The First Wish', 'The seed Maguayan planted on the broken land after the lightning, a hope that the broken world would live again. The bamboo that grew from it gave the first people.'),
 ('Banaag', 'A faint light, a glimmer, a first hint of light, and a glimmer of hope. The faint gold glow of an Agimat waking is called the banaag. (Meaning to be checked with a Tagalog source before print.)'),
 ('Baybayin', 'The old Filipino script. In this mythos it is the language the spirits listen to. Words read aloud in it with real intent are heard. Writing alone does nothing.'),
 ('Sangkapuluan', 'The old name of the islands of the Philippines. In this mythos the islands are the broken pieces of Licalibutan, and the ten Agimats rest in them.'),
 ('Lineage', 'A god\'s family line. Each of the nine lines (Maguayan, Captan, Lidagat, Lihangin, Licalibutan, Liadlao, Libulan, Lisuga, and Sicalac and Sicabay) holds the beings and demigods that descend from that god.'),
 ('Demigod', 'A child or descendant of the gods who grew so strong it has powers of its own. Demigods do not carry one of the ten Agimats.'),
 ('Dark kin', 'The children of pride, the beings that turned on people, such as the aswang. Their line is Licalibutan\'s pride, with the night fliers belonging to Libulan.'),
 ('The Swallowers', 'The beings that hunger for the sun and the moon: Bakunawa, Sawa, Olimaw, Arimaonga, Samal Naga, and Minokawa. A possible story wide threat.'),
 ('Anito', 'In folklore, ancestor spirits, nature spirits, and deities. The belief system is called Anitism. A mainly Luzon term. Visayan peoples often say diwata.'),
 ('Diwata', 'In folklore, a non human spirit tied to a place, object, plant, animal, or natural event. Most are kind or neutral and may harm if angered. In this mythos each lineage has its own bound diwata.'),
 ('Tabi po', 'A phrase people said to ask a spirit\'s permission when passing its place. Possible rule of the mythos: Agimats must be asked, not taken.'),
 ('Babaylan', 'A Visayan shaman and spirit medium, mostly women, who a diwata chooses as a guide. The Tagalog word is katalonan.'),
]

def clean(s): return re.sub(r'\s+', ' ', s).strip()

def parse(path, mode):
    t = open(path, encoding='utf-8').read()
    out = []; line = None; sec = ''
    for raw in t.split('\n'):
        if raw.startswith('## '):
            h = raw[3:]
            line = next((l for l in LINES if h.startswith(l)), None); sec = h; sub = ''
            continue
        if raw.startswith('### '): sub = raw[4:]; continue
        if not line or not raw.startswith('|') or raw.startswith('|---'): continue
        cols = [c.strip() for c in raw.strip().strip('|').split('|')]
        if cols[0] in ('Name', 'Rank', 'Line'): hdr = cols; continue
        out.append((line, sub, cols))
    return out

def build():
    entries = {}
    def add(name, **kw):
        key = name.lower()
        if key in entries:
            e = entries[key]
            for l in kw.get('lines', []):
                if l not in e['lines']: e['lines'].append(l)
            return
        entries[key] = dict(name=name, aliases=[], lines=[], group='', type='', desc='', why='', source='', **{})
        entries[key].update(kw)

    # gods and concepts
    for g in GODS:
        add(g['name'], type='God', lines=g['lines'], group='The family of Maguayan and Captan', desc=g['desc'], why='Domain: ' + g['domain'] + '. ' + g['agimat'] + ' ' + g['nature'], source='core', rank=g['rank'])
    for n, d in CONCEPTS:
        add(n, type='Concept', desc=d, source='core')

    # bestiary
    for line, sub, cols in parse('story-bible/mythology/08-bestiary-by-lineage.md', 'b'):
        if len(cols) < 5: continue
        name, group, what, why, role = cols[:5]
        if not role or role not in ('C', 'B', 'D', 'B, D', 'C, D'): continue
        typ = 'Demigod candidate' if 'D' in role else ('Being' if 'B' in role else 'Creature')
        add(name, type=typ, lines=[line], group=group if group != 'Not stated' else '', desc=what, why=why, source='bestiary')

    # folk deities
    aliases = {}
    for line, sub, cols in parse('story-bible/mythology/09-folk-deities-by-lineage.md', 'd'):
        if len(cols) == 3:
            name, group, folk = cols
            for n in [x.strip() for x in name.split(', ')] if '(' not in name else [name]:
                add(n, type='Another name', lines=[line], group=group, desc=folk, why='Another name for ' + line, source='deities')
                aliases.setdefault(line, []).append(n)
            continue
        if len(cols) < 4: continue
        name, group, folk, role = cols[:4]
        if re.search(r'see 08|^See |Cross reference|The god (him|her)self', role) or role.startswith('Dark kin') or role.startswith('Beings') or role.startswith('Ancestors'):
            continue
        if role.startswith('Another name'):
            names = [x.strip() for x in name.split(', ')] if '(' not in name else [name]
            for n in names:
                add(n, type='Another name', lines=[line], group=group, desc=folk, why='Another name for ' + line + (' or a child of the line' if 'child' in role else ''), source='deities')
                if 'child' not in role: aliases.setdefault(line, []).append(n)
            continue
        typ = 'Demigod' if 'Demigod' in role or 'mortal who rose' in role.lower() else ('Messenger' if role.startswith('Messenger') else 'Divine child')
        add(name, type=typ, lines=[line], group=group, desc=folk, why=role, source='deities')

    # attach aliases to god entries
    for g in GODS:
        a = aliases.get(g['lines'][0], [])
        if g['name'] in ('Sicalac', 'Sicabay'): a = aliases.get('Sicalac and Sicabay', [])
        entries[g['name'].lower()]['aliases'] = [x for x in dict.fromkeys(a) if x.lower() != g['name'].lower()]

    lst = sorted(entries.values(), key=lambda e: e['name'].lower())
    return lst

if __name__ == '__main__':
    lst = build()
    open('wiki-data.js', 'w', encoding='utf-8').write('// Built by tools/build-wiki-data.py from the mythology files. Do not edit by hand.\nvar WIKI_GLOSSARY = ' + json.dumps(lst, ensure_ascii=False, separators=(',', ':')) + ';\n')
    from collections import Counter
    print(len(lst), 'entries', dict(Counter(e['type'] for e in lst)))
