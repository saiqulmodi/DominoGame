# Domino Game: pending upgrades

Read this at the start of every upgrade of this game and solve what is still open. Tick an item only when it is built and tested.
Written 05-Nov-2026 at the owner's request.

## Rule: the game should be in 3D only

The town, the journeys and picture tracing are already 3D (`town_web/town.js`, `town_web/trace3d.js`). These screens are still 2D (pygame):

- [ ] **Maths Play** (`mathsgame.py`: 50 drawing screens, `maths_bank.py`: 80 question generators, 79 chapters, Classes 1-7). Two ways, not yet chosen:
  - 3D classroom: answer blocks and dominoes in 3D, each question's drawing shown as a picture on the board, from a ready-made set of questions. Much quicker, but questions eventually repeat.
  - Full rebuild in 3D: every drawing true 3D, questions stay endless. Several times more work.
- [ ] **Rhymes sing-along** (`singalong.py`; Classic Rhymes and Desi Rhymes)
- [ ] **Draw my own** (free drawing; must never be dropped)
- [ ] **Cross the Road** (`roadsafety.py`)
- [ ] **Stories** (`stories.py`, `schoolday.py`)
- [ ] **Menus and panels**: Games menu, players, stickers, parents report
- [ ] **Sparkle button extras on a picture**: video, real photo, Hear it, Draw it. They open the 2D screen today (`&item=<n>`).
- [ ] **Stickers from 3D tracing**: 3D tracing saves the picture as done, but stickers are only given the next time a picture is finished on a 2D screen. Give them in 3D.

## Content gap

- [ ] **English and Hindi for Classes 2-7**: the game only has the alphabet (`ABC`, `abc`, `Swar`, `Vyanjan`, all in Class 1), so Classes 2-7 show no English or Hindi. When content is added, list it in `ncert.SYLLABUS`.

## To check on a real phone

- [ ] Sound: the 7 notes, the voice, no crackle
- [ ] Smoothness of the town, journeys and tracing, with no shaking
- [ ] Bigger name letters and lower camera angle on the tracing table (only checked at desktop size)

## When publishing

- Build with `tools/build_web.py` only, never raw pygbag: the 4-Nov commit (69e9c60) used raw pygbag and lost the line that opens the 3D town.
- Keep `town/pics3d` and `town/js` out of the Stratos box (the stage fetches pictures from GitHub Pages there), and keep the box's no-saving rule.
- Stratos form: one `dominowonderdash.zip` made from `docs/dominowonderdash.tar.gz`, with `load` and `save` in `fun.py` emptied; no `dg.town.visited` save in the box's `town.js`. `tools/make_stratos_box.py` still makes the old form, so do not run it as it is.
