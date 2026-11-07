// Lettering for the Hiraya reader. Text is drawn on top of the art, so it stays sharp and editable.
// Each entry: [kind, x, y, w, text]  (x, y = top left corner, w = width, all in % of the page)
// kind: "s" speech bubble, "w" whisper or small bubble, "c" caption box, "x" sound effect, "t" tiny caption
// Positions are first pass guesses against the generated art. Nudge the numbers to move a bubble.
// Reading order is left to right, so the first lines of a row sit on the left. NOTE (2026-11-08): the positions below were guessed for the old right to left art, so mirror x (100 - x - w) or redo them after the pages are redrawn.
var LETTERING = {
  // Page 1 has its lettering drawn into the art (v4), so no overlay is needed.
  // Page 2 has its lettering drawn into the art (v2), so no overlay is needed.
  // Page 3 has its lettering drawn into the art (v2), so no overlay is needed.
  4: [
    ["w", 36, 28, 22, "...No."],
    ["c", 6, 56, 44, "Nikki Sharon Legazpi. The most popular girl in school."],
    ["s", 38, 90, 58, "Look. The nerd, the giant, and the pocket edition."]
  ],
  5: [
    ["s", 55, 4, 40, "I am NOT a pocket edition!"],
    ["s", 55, 52, 40, "Aww. He can't even jump."],
    ["s", 18, 66, 40, "Nikki, please. Those are his."]
  ],
  6: [
    ["s", 55, 22, 40, "Give them back."],
    ["s", 8, 22, 40, "Make me."],
    ["s", 55, 46, 40, "Do you ever get tired of being this predictable?"],
    ["s", 8, 46, 40, "Do you ever get tired of reading about ghosts?"],
    ["s", 8, 60, 44, "They're not ghosts. It's folklore!"],
    ["w", 50, 60, 42, "It's technically mythology."],
    ["x", 8, 90, 36, "WHIP"]
  ],
  7: [
    ["s", 54, 6, 40, "Not him."],
    ["t", 4, 94, 60, "Jeff Victorio never starts a fight. He just never lets his friends stand alone."]
  ],
  8: [
    ["x", 8, 4, 40, "KRIIIIING"],
    ["s", 54, 24, 42, "Whatever. Come on, girls."],
    ["s", 54, 60, 42, "Thanks, Jeff."],
    ["s", 8, 60, 44, "Don't mention it. Actually, mention it. I want credit."],
    ["w", 8, 86, 22, "Nik?"],
    ["w", 40, 91, 30, "Nothing."]
  ],
  9: [
    ["c", 6, 20, 42, "Mr. Archibald Oronies. Everyone calls him Sir Archie."],
    ["s", 54, 38, 40, "Victorio?"],
    ["s", 54, 45, 40, "Present, sir."],
    ["s", 8, 38, 40, "Bautista?"],
    ["s", 8, 45, 40, "Here, Sir! Alive!"],
    ["s", 30, 52, 30, "Abaldado? ... Present."],
    ["s", 30, 58, 36, "Legazpi? ... ...Present."]
  ],
  10: [
    ["s", 6, 36, 44, "Before we start, a story. Long ago, our ancestors called these islands the Sangkapuluan."],
    ["c", 30, 20, 20, "Ten."],
    ["w", 55, 52, 40, "Ten what?"],
    ["w", 8, 52, 40, "Agimats."],
    ["s", 5, 70, 52, "Every land has its Agimats. Charms with a power of their own. Ten are said to sleep in the Sangkapuluan, our islands."],
    ["s", 54, 84, 40, "So it's a fairy tale, Sir?"],
    ["s", 8, 92, 56, "Every fairy tale begins with someone who stopped listening."]
  ]
};
