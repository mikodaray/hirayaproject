# Art Style

DECIDED by creator: the art style for Hiraya should be close to how the Naruto manga looks.

## What that means for us
- Bold, confident ink linework with varied line weight
- Dynamic poses and dramatic camera angles, like low angle wide lens shots
- Expressive faces, with exaggerated comedy reactions mixed with serious moments
- Heavy hatching and screentone shading in black and white pages, rich flat color on covers
- Strong foreground and background depth in group shots

## Black and white rule
DECIDED by creator: the chapter pages are black and white like a real manga, with black ink, white paper, and gray screentone. No color on interior pages. Covers can stay in color unless the creator says otherwise.
Colors that matter in the story (Jeff's ube hair, blue uniforms) are shown with screentone shades. Keep a color note in the character docs so a colorist knows the real colors.

## Reading direction
DECIDED by creator (changed 2026-11-08): the panels inside each page read from left to right, then top to bottom, so the first panel of a row is the one on the left. The pages also go left to right in the web viewer (page 1, then page 2 to the right). This replaces the earlier right to left rule. Page images made before this date (cover aside, pages 1 to 10) were drawn right to left and need to be regenerated.

## Hand drawn rule
DECIDED by creator: every image must look hand drawn, not realistic. Use ink pen linework, hatching, and flat cel style coloring. No photographic, 3D, or realistic rendering. If a generator gives a realistic or painted look, convert it to a drawing.
Note: the first cover concept and the first cast scene were made before this rule and may look more rendered than drawn.

## Sound effects (onomatopoeia)
DECIDED by creator: every page includes onomatopoeia (SFX). UPDATED 2026-11-07: use Filipino words for the sound effects instead of the Japanese manga sounds. Plain English is fine for real world sounds that have no common Filipino word (HONK, THUD, SWISH). Use all three kinds:
- Giongo, real world sounds: crashes, thunder, footsteps, traffic (HONK, THUD, CLACK)
- Giseigo, voices and living creatures: laughter, gasps, animal noises (HAHAHA, GASP, MEOW)
- Gitaigo, feelings and atmosphere with no literal sound: sparkle, awkward silence, a racing heartbeat, gloom (KINANG, KISLAP, TIBOK, ...)
Draw them big and hand lettered, part of the art, often curving with the action. For gitaigo use Filipino words: KINANG or KISLAP for sparkle, KINTAB for a glossy shine, TIBOK for a heartbeat, BULONG BULONG for whispers, DALDAL for chatter. Do not use Japanese manga sounds like KIRA KIRA, DOKI, ZAWA ZAWA, or HISO HISO.

## Expressions rule (faces match the scene)

Every prompt must give each character an expression that fits what is happening in that scene: animated, clear emotion, readable at a glance (shock, laughing, fear, determination, embarrassment, awe, and so on). Say where the head is turned and where the eyes look. Do not reuse the same resting face in every image (Jeff's smirk is only his default look). Tell the generator to use the character sheet for hair, face shape, clothes and build, but not to copy the sheet's pose or expression; the sheet's expression row shows the range.

## Anatomy rule (limbs and fingers)
DECIDED by creator (2026-11-06): every person in every image must have exactly two arms and two hands, five fingers on each hand (four fingers and one thumb), and two legs. No extra, missing, merged, or duplicated limbs or fingers, also for people in the background and when hands overlap. This rule is written into every prompt, both as a positive instruction and in the avoid list. Always check the result, and if a hand or arm is wrong, regenerate or use the fix prompt below.
Final pass line (DECIDED by creator 2026-11-08): every image generation prompt ends with this exact line, and both bundle scripts add it automatically: "Final anatomy pass before rendering: inspect every visible character and remove any extra limbs, extra fingers, duplicate hands, merged hands, phantom hands, or malformed joints." If you write a prompt by hand or paste one from art/prompts/ without a bundle, add this line at the very end.
Fix prompt: "Keep everything exactly the same. Only fix the anatomy: every person must have exactly two arms and two hands with five fingers on each hand, and remove any extra arms, hands, or fingers."

### Joints rule (added 2026-11-07 after the cover 2 mistake)
Mistake to never repeat: in cover 2, Nikki's arm had three segments and two elbows. Every arm must have exactly two segments, an upper arm and a forearm, joined at exactly ONE elbow, from the shoulder to the wrist, with no extra bend, joint or segment. Every leg has exactly one knee. The upper arm and forearm are about the same length, and the shoulder sits right next to the neck and torso. When a character has an arm folded (elbow on a desk, hand on the face, hand on the hip), the prompt must describe that arm in plain steps: where the shoulder is, where the single elbow rests, where the hand ends up, and where the other arm is. Prefer simple arm poses in crowded foreground shots. The prompt bundle script now adds this joints paragraph to every prompt automatically, in the instructions and in the avoid list.
Joints fix prompt: "Keep everything exactly the same. Only fix the arm of NAME: redraw it as a normal human arm with exactly two segments and one elbow, a upper arm from the shoulder to a single elbow and one forearm from the elbow to the hand, no extra bends or joints."

## School setting
DECIDED by creator (2026-11-06): all the students are in high school (Durian City High School), not college. Keep the looks from the approved character sheets. Some of them are 18 or 19, so draw them as older high school students in school uniforms.

## Limits
- The style is a direction only. Do not copy any existing character, costume, or design. Hiraya has its own cast, setting, and look.
- Keep the Filipino setting, uniforms, and Butuan details accurate to our own story bible, not to the style reference.

## Reference
- Group scene composition reference: low angle, one character close to the camera, others arranged behind on a diagonal (see art/prompts/01-cast-group-scene.md)
