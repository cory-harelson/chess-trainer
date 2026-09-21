# chess-trainer — BUILD LOG

**Read this file before changing anything in this repo.** Multiple Claude threads edit
`index.html` at different times. This log is the only shared memory between them.

Fetch it directly:
`https://raw.githubusercontent.com/cory-harelson/chess-trainer/main/BUILD_LOG.md`

---

## RULES (violating these has cost us real work — twice)

1. **Build from the live raw file, never from `git clone`.**
   Always start from
   `https://raw.githubusercontent.com/cory-harelson/chess-trainer/main/index.html`.
   The Cowork/Claude session git proxy serves a *reconstructed* history — same commit
   messages, different SHAs — so a clone can be silently behind or on a parallel
   lineage. On 2026-08-15 a clone reported HEAD `673f6b5` while GitHub's real HEAD was
   `da08a12`.

2. **Verify against the live URL after pushing, not against your local file.**
   `curl https://cory-harelson.github.io/chess-trainer/`, parse `COURSES_DB`, and check
   the course/variation counts and the specific thing you changed. Pages redeploys in
   about a minute. "I wrote the file" is not "it shipped."

3. **Every commit replaces the whole `index.html`.** There is no merge. If your base is
   stale you will silently revert someone else's work. Diff your output against current
   HEAD before committing and confirm you are only adding.

4. **Append an entry to this log in the same commit as any `index.html` change.**

5. **Validate before shipping.** Replay every non-partial line through chess.js /
   python-chess: zero illegal moves, zero non-canonical SANs. Current baseline is
   1,893 lines, 0 errors (`chess` pip package fails to build in the cloud container —
   extract the embedded chess.js from `index.html` and replay with node instead).

---

## CURRENT STATE — 2026-09-21 (rev 16)

- Live: https://cory-harelson.github.io/chess-trainer/
- HEAD: `<this commit>` · `index.html` = 942,402 bytes (sha256 0bf6ff4e…)
- Validation: 2,110 non-partial lines replayed strictly through the embedded chess.js —
  0 illegal moves, 0 non-canonical SANs; 2,142 chapterId refs, all resolving; 32 partials;
  0 prefix/exact duplicates within the custom course's non-Quickstarter chapters AND
  within the Quickstarter itself; every Quickstarter line = its parent's full move list
  (31/31, `source: "Quickstarter — same line as '<parent>'"`, link identical to parent's).
- Custom course: 221 variations / 11 chapters (Unique Coverage 29), all chapters carry
  `group:"Black Lion"`. The Black Lion course is 332 (its 5 legacy added lines removed).
- **Stockfish in the container: `apt-get install -y stockfish` → `/usr/games/stockfish`
  (SF16); python-chess installs with `pip install chess --break-system-packages
  --only-binary :all:`** (the sdist build fails — the wheel works).

**Courses (6) — ALL use explicit chapter structure:**

| Course | Variations | Chapters |
|---|---|---|
| The Iron English: Botvinnik Variation | 810 | explicit (32) |
| The Black Lion (Simon Williams) | 332 | explicit (29); legacy added lines removed rev 12 |
| Black is Back: Old Benoni | 101 | explicit (12) |
| The Madman's Philidor Defense (James Canty III) | 158 | explicit (10) |
| Lifetime Repertoires: Stonewall Dutch (Simon Williams) | 520 | explicit (27) |
| Cory's Custom Study Lines (all `added:true`, site:"custom") | 222 | explicit (11) |

**Features present in `index.html`:**

- Material-count badge: +N pill on the leading player's side of the board, all views
  (`updateMaterialBadges()` at the end of `renderPosition()`; P1/N3/B3/R5/Q9; hidden when equal)
- Line notes + `flag: "skip"` annotations — 15 notes / 13 skip flags: 11 flagged Black Lion
  lines (10 Risky Lion vs 8.b3 + Tame Lion 6.Bg5 #4, rev 15), 3 Stonewall Dutch move-order
  notes (2b, 8...h6 before ...e5, 2 flagged), 1 unflagged Iron English 4E #10 Alt note
- Explicit chapter support — `course.chapters` + per-variation `chapterId` wins over
  the legacy name-pattern heuristic
- Live-session persistence — `visibilitychange` / `pagehide` snapshot to localStorage,
  restored by `trTryRestore()` (carries each line's `removed` flag)
- Trainer session list (rev 16): course link ↗ sits LEFT of the line name, × far right, both
  32px tap targets; removed lines are parked in a "Removed from this session" section at the
  bottom of the list with a `↩ Restore` button (`trRestoreLine()`)
- Mid-line browsing (rev 16): ◀ ▶ |◀ ▶| and the move strip work during a live trainer line,
  bounded to the moves already played (`moveStack` never holds unplayed moves, so nothing
  leaks). Board is read-only while behind live; any board tap snaps back. `trSyncLive()`
  guards every trainer routine that touches `game`; `setStatus()` parks messages while browsing
- Android back-gesture trap — history sentinel + `overscroll-behavior: none`
- SAN canonicalization + `{sloppy: true}` parse fallback in `trApply()`
- Black Lion move order normalized: 46 transposable lines use `3...Nbd7 4.Nf3 e5`.
  The 34 `3...e5 4.dxe5` queen-trade lines keep Simon's original order (they cannot
  transpose) and remain fully trainable.
- All Sections tab = same collapsible hierarchy as the trainer picker (course ▸ chapter
  ▸ name-family ▸ lines, all default-collapsed, search force-expands)
- ↩ Return button (+ Backspace): restores the explored position after clicking into a
  line from the matches panel or All Sections (jumpStack snapshots, explorer tab only)

## CHANGE LOG (newest first)

### 2026-09-21 (rev 16) — session-list tap targets, restore removed lines, mid-line ◀ ▶ browsing

**Cory's report (mobile):** the ↗ course link and the × remove button sat side by side and
were tiny — a mis-tap on × dropped a line from the session with no way back. Separately, when
he gets interrupted mid-line he loses track of how he got to the position and wanted ◀ ▶ to
work — but only up to the current move, never past it.

**Changes (UI only — `window.COURSES_DB` byte-identical to rev 15, 0 data edits):**

1. **Row layout** (`renderLineList`, CSS `.tr-line .rm` / `.tr-line a.golink.sm`): ↗ moved
   to the LEFT of the line name (after the status icon); × stays far right with `margin-left:
   14px`. Both are now 32×32 flex-centered tap targets. Row padding tightened to
   `2px 9px 2px 6px` so rows don't grow.
2. **Restore removed lines** (`trRestoreLine(i)`): removed lines render in a dashed-rule
   section "Removed from this session (N)" at the bottom of `#tr-linelist`, struck-through,
   with a `↩ Restore` button. Restore clears `L.removed`, pushes an unpassed line onto the end
   of `queue` (unless already in queue/failedNext/on the board), re-calls `trShowOverlay` if
   sitting on a review so "Finish session" flips back to "Next line", and `trSnapSave()`s.
   If `play` is null (deck momentarily empty) it kicks `trAdvance` via `later()` — the token
   guard prevents a double-advance. Removing the LAST active line still finishes the session
   (summary, not restorable) — accepted; the summary already counts removed lines.
   `trRemoveLine`'s status now says the line can be restored from the bottom of the list.
3. **Mid-line browsing** (`goTo`, `setStatus`, new `trBrowseEnd`/`trSyncLive`):
   - `goTo` no longer returns early during a live line; it clamps to `[0, moveStack.length]`
     as before. Because `trApply` only ever pushes moves as they are played, `moveStack.length`
     IS the live position — there is nothing past it to reveal.
   - Leaving live saves the current `#tr-status` into `play.browsing` and shows
     "◀ Looking back at N… — tap the board or ▶| to return to your move" (forced write).
     While browsing, `setStatus()` parks new trainer messages into `play.browsing` instead of
     the DOM; `trBrowseEnd()` delivers the latest one when you return. So an opponent move or
     "Your move" prompt that fires mid-browse is never lost or stale.
   - `trSyncLive()` rebuilds `game` from `moveStack` if `ptr !== moveStack.length` and ends
     browsing. Called at the top of `trApply`, `trRedrillNext`, `trWalkForward.step`,
     `trLineDone`, the hint handler, and `trUserMove` (which returns false there — a tap while
     browsing only snaps back, it never moves). Board `pointerdown` also snaps back before
     selecting a piece so `showLegalTargets` never runs on a stale position.
   - `trPlayLine` initialises `browsing: null`; `trResume` clears it so a parked status can't
     leak across a tab switch.

**Verification:** node `--check` on all 3 inline scripts; jsdom behavioural test (Madman's
Philidor lines, black to move): 24/24 — step back/forward/Home, cannot pass live, board tap
snaps back with no move, status save/park/restore, `trApply` mid-browse syncs first,
remove → queue shrinks → removed section renders → restore → queue restored, removing the
current line advances and is restorable, snapshot carries `removed`. `COURSES_DB` line
diffed byte-equal to rev 15. Shipped from a mobile session (no Chrome) — Cory uploads via
`github.com/cory-harelson/chess-trainer/upload/main`.

### 2026-09-14 (rev 15) — Tame Lion 6.Bg5 #4 flagged SKIP (transposition conflict with #5)

**Cory's report:** Theory #4 and Theory #5 of ch.19 "The Tame Lion (3...e5 4.dxe5 6.Bg5)"
transpose into the *same* position and then recommend different moves — the trainer marks
you wrong depending on which drill you're in.

**Confirmed identical node** (python-chess, ep-stripped):
`r2k1b1r/pppn1ppp/4bn2/4p1B1/4P3/2N2N2/PPP2PPP/2KR1B1R b - - 5 8`, Black to move.
- #4 reaches it via 7.Nf3 Nd7 8.O-O-O, then plays **8...h6**
- #5 reaches it via 7.O-O-O+ Nd7 8.Nf3, then plays **8...Kc8**

**SF16 verdict (depth 26-28, evals from Black):**

| node | course move | engine top | gap |
|---|---|---|---|
| transposition node | 8...h6 (#4) / 8...Kc8 (#5) | **Kc8** | h6 is 0.15-0.23 behind; both playable |
| after 8...Kc8 9.Bh4 | 9...Bb4 (#5) | **Bb4** | 0.00 |
| after 9...Bb4 | 10.Ng5 (course) | **10.Nd5** (0.00) | Ng5 = White's 3rd choice, -0.21 |
| after 10.Ng5 Bxc3 11.Nxe6 | 11...fxe6 (course) | **11...Bxb2+!** | **0.23 — course is imprecise here** |
| #5 end, 19...Re7 | — | Re7 | 0.00; Black a clean pawn up (6v5), ~+0.2 |

10 of #5's 12 Black moves are the engine's #1 choice and 5 are recaptures — it memorizes
like a forced sequence. #4's entire content is three moves (h6, Kc8, Bd6) into a dead-level
quiet ending, and 8...h6 *forecloses* #5 (after ...h6, Ng5 is answered by hxg5).

**Chapter tabulation** — of 14 lines in ch.19, ...h6 appears in 10; the 4 without it are
#6 (White trades on f6 himself), #9/#10 (bishop leaves g5 via Bxf4) and **#5**. So #5 is
the only line that leaves the g5-bishop unchallenged *on purpose* — the tactics are the point.

**Change:** `78e1cf10-9b48-4199-84d4-e348591aed09` (Tame Lion 6.Bg5 #4) gets
`note` + `flag:"skip"`. No move changes anywhere. Deep-equal asserted: exactly one
variation differs across all 6 courses; `moves`/`name`/`id` untouched.

**KNOWN GAP (not created by this change):** neither line covers 9.Bh4 Bb4 **10.Nd5**,
which is White's best (0.00). Black is fine (10...Nxd5 11.exd5 Bg4 12.Bg5 f5 13.Be3, level)
but it's off-book. Offered to Cory as a custom-course addition — pending his call.

### 2026-08-31 (rev 14) — material-count badge + course-wide numbering audit
### (4E #10 Alt, Philidor Qxd4 renames, upstream Alt-suffix sync, 8.h3 #10 reorder)

**Feature: material-count badge on the board (all views).** Two pills inside
`#board-wrap` (`#mat-top`/`#mat-bottom`, `.matbadge` CSS, z-index 10);
`updateMaterialBadges()` sums P1/N3/B3/R5/Q9 from `game.board()` at the end of
`renderPosition()` — the single render choke point, so explorer, trainer, and
every board load update automatically. Only the leading side's pill shows
(+N on that player's side, orientation-aware via `flipped`; hidden when equal;
tooltip spells out who is up how much).

**Cory's Theory 4E report verified — the error is UPSTREAM in Simon's course.**
Re-fetched live course data for all 5 chess.com courses and diffed id-by-id
against our DB (endpoint MOVED since 2026-08-22: now
`/service/courses/rpc/chesscom.courses.v1.CoursesTrainingService/GetCourseLearningSession`,
plain cookie auth from any chess.com page, same request body). Result: ids,
order, chapters, counts, info flags 100% identical in all 5 courses — zero
structural drift. Iron English 4E on chess.com itself has two #7s and no #3.
The second #7 (19 plies, id `e2903123`) is the 8...Qb6 alternative sitting
CORRECTLY between #10 and #11 in the move tree. Local fix: renamed
**"Theory 4E: #10 Alt"** + explanatory `note`; all other 4E numbers still match
chess.com (deliberately did NOT renumber the chapter to close the #3 gap).

**Philidor Ch4 naming bug (also upstream, Canty's):** 8 lines named
"…5.Nf3 / 6.Nxd4 / 7.Be3 #2-#6" and "…6.Nxd4 / 7.e5 #1-#3" actually play
6.**Qxd4** (move 11 verified in-data) → renamed 6.Nxd4→6.Qxd4, moves untouched.
Also fixed the "5.fxe5 # #10" double-# typo → "5.fxe5 #10".

**Upstream rename sync — chess.com dropped suffixes since our scrape (16 renames):**
IE: `1A #28 Alt`→`#28`, `2A #30/#31 Alt`→`#30/#31`. Black Lion: `Tame Lion 6. Bc4
Paused`→`…6. Bc4`, `Theory #22 - 8. b3 Alt`→`…8. b3`, `Be2 Theory #3 - Risky
Alternative Alt`→ sans Alt, `Shirov Theory #5 - 11. Bh3 Alternative Alt`→ sans
Alt, `3. Bd3 and 3. f3: Theory #2 Alt`→`#2`. Old Benoni: `Repertoire Clashes
Ref`→`Repertoire Clashes`, 5× `4.Nc3 Be7 | Alternative #N Alt`→ sans Alt,
`2.e3 #3 | …Nbd7 Alt` and `2.c3 #9 | …cxd4 Alt`→ sans Alt (upstream's double
space collapsed). **NOT synced (upstream noise, ours kept cleaner):** Black
Lion "…5. Be2: Theory #4 - 7. g5" gained a stray leading "/" upstream, plus 6
whitespace-only diffs (trailing/double spaces).

**Custom course:** `8.h3 #10` physically moved from after `8.h3 #1` to after
`8.h3 #9` (it's a 9.Be3-branch line; the picker family rendered 1,10,2…9).
Pure object move — ids, content, stats untouched.

**Known upstream quirks left as-is (course-faithful, for the record):**
IE 2A renders …#29,#32,#33,#30,#31 (Simon's own display order); Stonewall 1c
has two '#9' lines ('#7-#9 (Alternative 9...Nh5)' set and a '#9 (Alternative
10...g5)' after #12); Black Lion Quickstarter has two lines both named "The
Standard Set-up of the Risky Lion: 8. Re1" where the 22-ply one is a strict
prefix of the 32-ply one (candidate for a skip-flag if it bugs Cory in drills).

Validation: 2,110 non-partial strict replay clean (0 illegal, 0 non-canonical);
2,142 chapterId refs resolve; 32 partials; per-id deep diff = exactly the 26
intended name/note changes + 1 reorder, everything else byte-equal; `node
--check` clean; Playwright: badge (+1 correct side in both orientations, clears
on equality, trainer run on mobile viewport clean, 0 page errors), picker shows
4E …#10, #10 Alt, #11…, the Qxd4 renames, and 8.h3 #1-#10 in order.
Base: `543b52d` (clone == live raw, sha256 dd0312e7…).

### 2026-08-24 (rev 13) — study-session audit: Tame rebuilt, Be3-hook & Qe2 recapture fixed,
### c6-order unified, G4/NH2 rules derived (SF16-verified throughout)

Cory drilled the course and fired ~8 questions; every one was resolved with the
tabulate-all-siblings + engine method (SF16 d20-24). 18 objects changed, ids untouched.

**Rules derived (now in the read-me note):**
- **G4 RULE:** after ...g5, push ...g4 only when it forks the hook AND the horse (White
  pawn h3 + knight f3 both standing); if either is missing — or White just set Rd1
  against the d-file with d4/e5 tension on — ...Nf8 first. Verified across all 44
  decision nodes where both moves were legal; the four course ...g4 moves all fit
  (engine gaps 0.8-2.2 vs Nf8); the Nf8 cases fit or are free choices. THREE of our own
  g5-first swap lines (5.Bd3, 5.d5 #1, 5.d5 #3) drill ...Nf8 where the engine now
  prefers ...g4 by 0.3-0.8 — flagged to Cory as optional future refinements, NOT changed.
- **NH4 RULE extended to NH4/NH2:** whenever the knight leaves f3 (Nh4 before ...g5 or
  Nh2 after it), take d4 and jump ...Ne5 — even when Be3 can recapture (engine: exd4
  ~0.55 better than the old regroup in the 6.Be3-hook line).

**Line changes:**
- **Tame lines REBUILT** ('8.b3 - go Tame', '8.Re1 + 9.b3 - go Tame', 24p → 30p, same
  transposed tail, ids kept): Cory flagged a6-first + a Re8/Bf8 wander as "not Simon's
  plan" (Simon: b6, a6, Bb7, b5). Engine verdict: in the early-h6 order an early ...b6
  ALWAYS walks into d5! (~0.7-1.1 worse — Simon's own order has the spare tempo, ours
  spent it on h6), so the regroup is forced — but the expansion works right after it.
  New line: castle, Re8, Bf8, THEN b6 (30cp from best), h3 exd4 Nxd4, a6, Bf1 Bb7 —
  ends -0.12. White's a5 never punishes (checked). QS copy renamed
  "8.b3 — go Tame: regroup, then b6-a6-Bb7". The Nh4/Nf5→Bf8 line untouched (that
  maneuver is correct THERE, as Cory himself noted).
- **6.Be3-hook line FIXED** (24p → 28p): course's ...Nf8 after 10.Nh2 replaced with the
  rule-consistent 10...exd4! 11.Qxd4 Ne5 (engine-walked: Be2 Rg8 Kh1 g4 hxg4 Nfxg4,
  ends -0.22). Canty's Nf8 was 0.55 worse — book imprecision, rule wins.
- **8.Qe2 #1 REBUILT + renamed** '8.Qe2 #1 (dxe5: take with the pawn)' (22p → 28p):
  Simon's Nxe5-and-castle was the ONLY knight-recapture among 9 same-shape dxe5 nodes
  in the whole course (all others take with the pawn); engine says dead equal (0.05
  apart) — switched to the pawn recapture for one-answer-per-position consistency.
  Engine-walked tail: White's best is the immediate Nh4 pest; line teaches Nc5-e6,
  O-O, Ng5! (ends -0.46). QS copy renamed "8.Qe2 + dxe5 — take with the pawn, keep
  attacking".
- **c6 before Be7 unified** (FEN-identical swaps, engine-cleared ≤0.11 apart, zero
  punishes): 5.Nge2 #1-#5, 5.Bd3 (g5 first), 5.Be2 + the QS copies. Canty's Be7-first
  there was arbitrary. NOT swapped: 5.Bg5 (Be7 answers the bishop on g5 — purposeful)
  and the 2.d3 family (different structure).
- **Notes added:** Nfg4-vs-Nh5 in the 8.Nh4 engine lines (Canty's Nh5 needs Re1 spent —
  with White's rook still on f1, f4! refutes Nh5 by a full point; hence Nfg4);
  Be3-regroup QS lines now carry the no-hook rule text.

**Questions answered without changes (engine-verified):**
- 9...a5 in the 4.g3/Nge2 crash lines is the engine's BEST move at that exact moment
  (+0.48, next best hxg3 +0.32): it fixes a4 as the target for ...Nb6 and stops White's
  a5 before the knight needs b6. Not an odd insert — the timing is the point.
- Canty's systematic ...a5 after a4 in the MAIN lines would cost ~0.10-0.15 + a tempo
  (7...a5 -0.68 vs 7...Be7 -0.53) — kept Williams's order; a5 stays only where the
  structure demands it. Flagged as a possible future system conversion, Cory's call.
- "5.dxe5 — keep attacking" plays ...Nh5 (not Nf8/g4) because the kicked bishop sits on
  g3: Nh5! is the engine's best by ~1.2 (Nf8 there is -5.7 — never).

Validation: 2,110 strict replay clean; QS==parent 31/31; 0 dups; only the 20 intended
objects changed (asserted per-id); Playwright boot clean. Base: `cea1615`.

### 2026-08-24 (rev 12) — old 3.Bc4 bolt-ons removed from Black Lion + opening-level grouping

**Data (Cory's call):** the Black Lion course's 5 legacy `added:true` analysis-board
lines ("3. Bc4 Sideline: …", `source:"Own analysis"`, no chapterId) are DELETED —
they drilled the unsound 3...e5 answer that rev 11 replaced with Nxe4!, and kept
surfacing in the This Position tab. Black Lion 337 → 332; its "Added lines" picker
bucket disappears (no added lines remain). These were pre-custom-course bolt-ons, NOT
Williams course content — the never-edit-source-courses rule is intact. Verified: no
remaining references to the 5 ids anywhere in the DB; after 3.Bc4 the explorer now
shows exactly the 5 new custom lines, unanimous on Nxe4.

**UI/data: opening-level grouping in the pickers.** Cory wants the custom course's
chapters grouped by OPENING so future non-Lion lines have a home. Mechanism: chapters
may now carry `group:"<opening>"` — all 11 custom chapters got `group:"Black Lion"`.
Both the trainer picker and All Sections render an extra collapsible level for grouped
chapters: course ▸ **opening** ▸ chapter ▸ family ▸ lines (default collapsed, search/
pos-filter force-expand, tri-state checkbox on the opening row selects the whole
repertoire). Chapter DISPLAY names strip a leading "<group>" prefix ("Black Lion 1:
Main Line Storm" shows as "1: Main Line Storm" under the Black Lion header) — data
names unchanged, collapse keys unchanged. Courses without `group` render exactly as
before (byte-identical data, code path skips the level). New CSS: `.tr-ohdr` +
`.ind` indent modifiers + `.secitem.d4`.

Validation: 2,110 non-partial strict replay clean; 2,142 refs resolve; courses 1-5
untouched except Black Lion (asserted = original minus the 5); custom variations
byte-identical (only chapter objects gained `group`); Playwright pass (opening row
renders in both pickers with stripped chapter names + indentation, checkbox selects
218 trainable, search penetrates the new level, Iron English & friends unchanged,
3.Bc4 explorer matches = the 5 new lines only). Base: `d13ec5d`.

### 2026-08-24 (rev 11) — 3.Bc4 family REPLACED with Cory's Nxe4! analysis + Bxg5-sac note

Cory reviewed the old 3.Bc4 lines (rev 4 imports of the 3...e5-based analysis-collection
lines) and rejected them as unsound: **3.Bc4? simply hangs the e4 pawn — 3...Nxe4! —**
and the e4-knight covers g5, killing the Ng5/f7 ideas the old lines were built around.
He supplied a PGN of his own analysis (3 lines); every node was verified with Stockfish
16 at depth 22-24 in the container (`apt-get install stockfish` works; binary lands at
`/usr/games/stockfish`):
- After 3.Bc4, engine best IS 3...Nxe4 (-0.95); after 4.d3 Nf6 5.Ng5, best IS 5...d5
  (-1.9); at every White branch point the engine's best move is exactly the branch
  Cory's lines cover (7.Nf3 / 7.f3, 8.f4 / 8.O-O).
- His 10...Nxg4! sac vs 7.Nf3 is the engine's top line throughout (final -2.7).
- CRITICAL GAP the PGN didn't cover, engine-checked and added as a 4th line:
  **4.Bxf7+? Kxf7 5.Ng5+ Nxg5! wins a whole piece** (-5.4) — the fork trick fails
  because the e4-knight guards g5.

Changes (226→…→221 variations):
- Unique Coverage: 5 old "3.Bc4 #1-5" lines DELETED (in-slot), replaced by 4 new ones
  (new ids): #1 Nxe4! main 7.f3 (16p) · #2 7.Nf3 Nxg4! (24p) · #3 8.O-O Bxh3! (19p) ·
  #4 4.Bxf7+? Nxg5! (16p, engine-built). Sources: "Cory's analysis 2026-08-24,
  SF16-d24 verified"; links → his chess.com analysis collection (same collection as
  before — he updated it). Notes carry evals + plans. Chapter 30 → 29 lines.
- Quickstarter: "3.Bc4 — the exd3! trap" swapped in-slot for "3.Bc4 — Nxe4! free pawn"
  (new id, full copy of new #1 per the rev 10 convention).
- The old five e5-based lines REMAIN in the Black Lion course's "Added lines" bucket
  (they are pre-custom-course bolt-ons, not Williams course content) — flagged to Cory
  for possible removal, not touched here.
- **Bxg5-sac note upgraded** (QS "dxe5 mid-storm — the Bxg5 sac is fine" + parent
  "8.Qe2 #6"): Cory asked whose sac and why the line ends with his king exposed.
  Engine answer baked into the note: it's WHITE's piece sac (11.Bxg5!? hxg5 12.Nxg5);
  Black takes everything, meets Bxf7+ with 13...Kf8!, trades the attacker with
  14...Nh7!, ends bishop-vs-three-pawns up with the attack spent (SF16 d24: -1.1);
  plan after the line ends: ...Bf7!, ...Kg8 castling by hand, then convert. Moves
  untouched (the line still mirrors course Theory #16 exactly).

Validation: 2,115 non-partial strict replay clean; 2,142 chapter refs resolve; courses
1-5 deep-equal; QS==parent 31/31; 0 dups (QS-internal and non-QS); Playwright boot +
rendered All Sections check (new family renders, 5 lines match the post-Nxe4 position);
only intended objects changed (asserted per-id). Base: built on `5a19bad`.

### 2026-08-24 (rev 10) — Quickstarter lines extended to full length + 3.Bc4 "why" note

Cory's asks: (1) check the Quickstarter itself for the shorter-prefix-duplicate problem;
(2) he likes the whittled-down SELECTION but not the truncation — extend each QS line
back out to its parent custom line's full ending.

- **Within-QS dup scan: 0 before, 0 after** (pairwise SAN-prefix/exact over the 31
  trainable QS lines). The QS was already clean internally.
- **15 QS lines extended to their parents' full move lists** (ids/names/notes/links all
  unchanged — only `moves` grew; stats survive): 8.h3 #2 24→30 · 8.Qe2 #6 26→34 ·
  8.Re1 #1 22→32 · 9.Nh4 #1 26→32 · 9.Nh4 #6 32→44 · 9.Be3 #1 24→30 · 9.Be3 #5 24→40 ·
  5.Bg5 26→40 · 5.Rg1 #2 30→48 · 5.d5 #3 22→34 · 5.Bd3 22→30 · 2.d3 #1 22→30 ·
  6.Qxd4 #17 20→28 · 7.Nxb5/8.Bg2 #1 24→32 · 5.Nge2 #2 22→28. The other 16 were already
  full length. QS ply range now 20–48. **Every QS line is now an exact move-list copy of
  the custom main line named in its `source`** — wording updated from "condensed from 'X'"
  to "same line as 'X'" on all 31 (the quoted parent name is the machine-checked part).
  QS↔main duplication is BY DESIGN (Cory: the QS is the curated selection).
- **3.Bc4 provenance question answered in-app:** Cory flagged the QS "3.Bc4 — the exd3!
  trap" as a weird move order (...e5 before ...Nbd7) with a non-course link. Explanation:
  vs 2.Nf3+3.Bc4 the slow 3...Nbd7 invites 4.Ng5! at f7 — 3...e5! is the antidote and the
  pawns (4...d5!, 6...e4) punish the knight; Nbd7 comes at move 10. All five 3.Bc4 lines
  share this order. They come from the Black Lion course's 5 `added` analysis-board lines
  (`source: "Own analysis"`, links to a chess.com analysis COLLECTION, not a course —
  imported to "Sidelines: Unique Coverage" in rev 4 as the only 2.Nf3/3.Bc4 coverage).
  Added a "why e5 first" note to both the QS line and Unique Coverage's 3.Bc4 #1.

Validation: 2,116 non-partial strict replay clean; 2,143 chapter refs resolve; courses
1–5 deep-equal; only QS `moves`/`source` + two `note` fields changed (asserted); 31/31
QS == parent move-lists; Playwright boot + rendered All Sections check (44-ply squeeze
line renders, note present, no page errors). Base verified: built on `b2c404a` (ls-remote
+ working-tree hash match).

### 2026-08-24 (rev 9) — custom-course dedup + verified links + All Sections reorg + Return button

**Cory's audit ask: check every Cory's-Custom line (esp. Quickstarter) for wrong links /
mixed-up moves, and remove same-line-but-shorter duplicates from the main chapters.**

Audit method (all programmatic, embedded chess.js): strict replay of every line; each
line's moves cross-checked against its LINKED source-course variation (exact / SAN-prefix
/ FEN-transposition-at-same-ply, ep-field normalized); every Quickstarter `source:
"condensed from 'X'"` resolved to parent X and checked for SAN-prefix + identical link;
pairwise prefix/exact dup scan within non-QS chapters.

Findings + fixes:
- **All 226 lines replayed legally; every QS line was a clean prefix of its named parent
  with the parent's exact link** — no moves from one line contaminating another. The two
  content "divergences" (QS 5.Bd3, 5.d5 #1) are the documented g5-first swaps: final FENs
  match the Canty originals modulo the en-passant field.
- **4 true prefix-duplicates REMOVED from main chapters** (kept the longer lines; ids of
  kept lines untouched): BL1 `8.Re1 #1` (22p ⊑ #2/#3/#4) · BL6 `5.fxe5 #1` (18p ⊑ #5/#6)
  · BL6 `6.Qxd4 #1` (20p ⊑ #19/#20) · BL6 `6.Qxd4 #2` (24p ⊑ #27–#34). Their content
  remains as the QS condensations + the longer extensions. The 5.fxe5/6.Qxd4 #1 family
  notes were carried onto the new #1s. 226 → 222 variations.
- **Renumbered to close the gaps** (names only — ids/stats survive): 8.Re1 #2-6 → #1-5,
  5.fxe5 #2-6 → #1-5, 6.Qxd4 #3-34 → #1-32. Root cause of Cory's "link opens the wrong
  line number": the deleted #1/#2 were Williams's unnumbered chapter-OVERVIEW lines, so
  custom `#N` linked course `Theory #(N-1)` / `#(N-2)`. After renumbering, custom
  `5.fxe5 #N` and `6.Qxd4 #N` link course `Theory #N` exactly (offset 0, verified).
  8.Re1 keeps a uniform offset (course numbers Re1 as Theory #33+); other families were
  already offset-consistent. 6.Nxd4 deliberately untouched — its missing #4 is rev 7's
  move-identical dup removal and its −1 offset is uniform.
- **2 QS retargets:** "Storm vs 8.Re1" link → the new `8.Re1 #1` (old link pointed at the
  deleted overview's course line); "4.f4 — exd4!" source+link → `'6.Qxd4 #17'` (the
  longest extension of its stem). QS parent/link consistency now 31/31.

**UI (2 features + 1 tooltip):**
- **All Sections tab reorganized** — was one flat list with a silent 300-per-course cap;
  now the trainer picker's hierarchy (course ▸ chapter ▸ trGkey name-family ▸ lines),
  everything default-collapsed, search force-expands (500-row cap with an explicit
  "+N more" note), scroll position preserved. Reuses tr-chdr/tr-hhdr/tr-ghdr styles and
  trComputeChapters/trGkey; new `.secitem.d2/.d3` indent rules. Line rows unchanged
  (badges, note dots, plies, partial-line external links, click-to-load).
- **↩ Return button + Backspace** — clicking a line in the matches panel or All Sections
  now snapshots {moveStack, ptr, flipped} to a jumpStack (max 40) before the line replaces
  the board; Return/Backspace pops it: forward moves from the opened line are discarded
  and the explored position + its matches list come back. Button lives in #controls,
  visible only on the explorer tab with a non-empty stack; multiple jumps unwind in order.
- Matches-panel ↗ tooltip for added lines now says "Open the source line on chess.com"
  when the link targets a course variation ("analysis board" wording was wrong for most
  custom lines).

Validation: 2,116 non-partial lines strict-replayed, 0 illegal / 0 non-canonical; 2,143
chapterId refs all resolve; courses 1–5 deep-equal pre/post splice; variation order
preserved (subsequence-asserted); Playwright UI pass 20/20 (jump/Return flows incl.
Backspace, collapsed hierarchy counts, search expand, trainer picker unchanged, phone
width). Base verified: built on real `cbbc5b1` (clone HEAD = ls-remote = recorded rev 8
SHA, byte-identical).

### 2026-08-24 (rev 8) — FIX: picker showed custom course as one "Added lines" bucket

**The bug (renderer, not deploy):** `trComputeChapters()`'s explicit-chapters branch
routed EVERY `added:true` variation to "Added lines" unconditionally, ignoring its
`chapterId`. All 226 custom-course lines are `added:true`, so the picker collapsed the
whole course into a single "Added lines" chapter. Revs 1-7 all deployed fine — the
data (11 chapters, renamed lines) was live everywhere; only the chapter RENDERING was
wrong. Reports of "the new organization isn't live" on 08-23 were this bug, not
caching. Lesson recorded: verifying `window.COURSES_DB` proves the DATA shipped, not
that the UI renders it — verify the rendered picker too.

**Fix (one line, DB-semantics identical for courses 1-5):**
`byId[v.chapterId] || (v.added ? 'Added lines' : 'Other')` — an added line whose
chapterId resolves now uses its explicit chapter; only chapterId-less added lines
(Black Lion's 5 legacy analysis-board lines) still fall back to "Added lines".
Verified against all 6 courses: courses 1-5 route identically to before.

**Plus:** custom course variations physically re-sorted into chapter order
(stable sort, IDs & content untouched — training stats unaffected) because the picker
lists chapters by first appearance; without the sort, Black Lion 2 rendered after the
Sidelines chapters. Courses 1-5 byte-identical; custom course deep-equal modulo order.
Validation: 226/226 strict chess.js replay clean, 0 orphan chapterIds.

### 2026-08-23 (rev 7) — coverage complete: 4.f4 (Williams) + 4.g4 & 4.g3 (Canty)

Position-level audit of all 495 source-course lines vs the custom course found exactly
three uncovered White systems; Cory picked sources and all three are now in (verbatim,
no transforms needed — all deviate before the move-5 setup):
- **Black Lion 6: 4.f4 (Williams)** (46): 5.fxe5 #1-6 (Qxd8+ endgame lines), 6.Qxd4
  #1-34 (the main battleground), 6.Nxd4 #1-7. One move-identical dup removed.
- **Black Lion 7: 4.g4 — b5! Counter (Canty)** (10): the 4...h6/5...e5/6...b5! counter-
  gambit (7.Nxb5, 7.a3, 7.Bg2 answers).
- **Black Lion 8: 4.g3 Fianchetto (Canty)** (7): chosen over Williams per engine
  comparison — identical repertoires vs 5.Nf3, Canty's ...h5!-h4 crash vs 5.Nge2.
Plus 3 new Quickstarter lines (one per system). 160 → 226 variations, 8 → 11 chapters;
courses 1-5 deep-equal. Every White system in either source course is now either in the
custom course or deliberately excluded (Williams 3...e5 queen-trade order, full Tame
setup, Canty's 2...e5 vs 2.f4).

### 2026-08-23 (rev 6) — custom course reorganized into 8 chapters + Quickstarter Guide

Restructured per Cory's ask. ALL existing variation ids preserved (training stats survive;
only names + chapterIds changed). New chapter layout: Quickstarter Guide (29 incl. the
read-me info line) · Black Lion 1: Main Line Storm (30) · Black Lion 2: Nh4 Jump — Take
d4 (13) · Black Lion 3: Be3 Regroup & b3 Tame (13) · Black Lion 4: 5th-Move Sidelines
(21) · Black Lion 5: Shirov Gambit (14) · Sidelines: 2.f4 (10) · Sidelines: Unique
Coverage (30). Lines renamed to "<system> #N" style so trGkey groups them into clean
picker subsections (e.g. 8.h3 #1-10, 8.Qe2 #1-6, 9.Nh4 #1-11).

Quickstarter (28 trainable, 20-32 plies, modeled on the Iron English one): one line per
core idea, condensed from full lines (same ids NOT reused — new ids; source field names
the parent), note = the rule. Covers: h3-hook storm, Qe2 lines, dxe5 trades, Bxg5 sac,
Ba2/Nf5 recipe, b3 Tame, Nh4 take-d4 (x3), Be3 regroup (x2), dxe5 Bxf7 trick, 6.Be3
hook, 5th-move sidelines (Bg5/Rg1 mate/d5/dxe5/Bd3), Shirov x2, 2.f4 x2, 2.d3, 3.Bc4
trap, 4.Be3. 132 → 160 variations, 5 → 8 chapters; courses 1-5 deep-equal.

### 2026-08-23 (rev 5) — custom Ch.1: the Nh4 jump + the 9.Be3 regroup (+24 lines)

Filled the two gaps the Canty-vs-custom position scan found. (1) Canty's 9.Nh4 block
(11 lines, setup reordered, FEN-identical) — knight to h4 before ...g5 → 9...exd4! then
...Ne5, queens on. (2) Canty's 9.Be3 block (10 lines) — no h3 hook means the g5/g4 kick
fails (engine: 9...Nf8 +0.64 vs 9...g5 +1.15; Cory's g5-then-exd4/Ne5 idea tested and
rejected, no tactic but ~0.5 worse) — the ONE exception to g5-first. (3) 6.Be3 door:
Canty's #2 imported (h3-hook g5 line); Canty's #1 (9...Nb6 roundabout) NOT imported —
it only works in his interleaving; in Cory's order 8...exd4 is 66cp better, replaced by
an engine-built line (+0.07). (4) Two engine-built 8.Nh4 lines for Cory's exact order
(main stem +0.34, Be3 door +0.07), builder tolerance 35cp, White moves scripted.
Custom course 108 → 132; chapter info line now carries the NH4 and BE3 rules.

### 2026-08-23 (rev 4) — custom course: +chapter "Early Sidelines — Unique Coverage" (30 lines)

Sidelines only ONE course covers, imported verbatim into the custom course so Cory's
whole repertoire lives in one place: Canty's 2.d3 (10 — Williams has none), Williams's
3.Bd3 / 3.f3 (5 + overview deduped), Williams's 2.Nf3/3.Bc4 sideline (5, added-lines with
their own analysis links, preserved), Williams's 4.Be3/f3 setups (10, overview deduped).
Cross-coverage verified programmatically (the other course has 0 lines for each; Canty's
only 2.Nf3 hit is an info model game). Custom course 78 → 108 variations, 4 → 5 chapters;
courses 1-5 deep-equal, only the custom-course span changed.

### 2026-08-23 (rev 3) — custom course: +2 chapters (Canty Shirov, Williams 2.f4)

Ch.3 "Canty Shirov Gambit (5.g4)": all 14 Philidor Ch.3 lines verbatim; one line carries
a QUEEN-FIRST warning note (the bishop-first habit loses ~1.9 in the Shirov — do not
generalize it there). Ch.4 "Williams vs 2.f4 (2...d5!)": Williams's 10 unique 2.f4 lines
verbatim (quickstarter / Theory Overview / Theory #10 were move-identical — deduped to
one). Note: Williams answers 2.f4 with 2...d5 while Canty's Philidor Ch.7 plays 2...e5 —
Cory drills Williams's system. Custom course 54 → 78 variations, 2 → 4 chapters; only
the 6th course's JSON span changed, courses 1-5 deep-equal verified.

### 2026-08-23 (later) — custom course Ch.2: g5-first policy (Cory's h4-bishop rule)

Cory's rule for the Nf8-vs-g5 order in "Canty 5th-Move Sidelines": **if White's dark
bishop was kicked to h4, ...Nf8 comes first; otherwise ...g5 first** (Simon's order —
keeps the knight out of h4), unless g5-first is a blunder. Applied to the custom course
only (Canty originals untouched): 5.Bd3, 5.d5 #1, 5.d5 #3 swapped to g5-first
(engine costs −0.44 i.e. IMPROVEMENT, +0.10, +0.38 — no tactics, all FEN-identical
transpositions, hxg5-hang guard clean); 5.d5 #2 reverted to Canty verbatim (the earlier
Nf8-first fix is superseded by this rule). Bishop-on-h4 lines keep Nf8-first: 5.Be2,
5.Bg5, 5.dxe5 #3. Only the 6th course's JSON span changed — courses 1-5 byte-identical
(deep-equal verified).

### 2026-08-23 — NEW COURSE: "Cory's Custom Study Lines" (54 lines, 2 chapters, purely additive)

Cory's personal drill repertoire — derived lines only, **no original course content
edited**. All 54 variations are `added:true`, `site:"custom"`, each with `source`, a
`link` back to the source variation on chess.com where derived, and `note` explaining
the derivation. Spliced additively before the closing `]}` of `COURSES_DB`
(pre-existing text byte-identical; stripping the 6th course reproduces the old DB).

**Ch.1 "Black Lion Main Line — Early h6" (33):** every Williams Risky Lion standard-setup
line with Black's setup reordered to h6→c6→Be7→Qc7 (26 lines, final positions
FEN-identical to Williams's — engine-verified at every intermediate node, SF16 d18-22;
no White deviation exceeds his normal +0.5, all Bxf7+/Ng5/Bg5 sacs lose). 6 Williams
lines are unreachable in this order (8.Bg5/8.Ng5 hang to hxg5) — deleted by design,
documented in the chapter's info line. The 8 Risky-vs-b3 lines (already flag:"skip" in
the Black Lion course) are replaced by 3 engine-built Tame conversions: castle, ...a6,
...Re8, ...Bf8, then react (immediate ...b6 is 0.5-0.9 worse here — d5!/dxe5 tricks;
final evals 0.00/+0.02/+0.32). Plus 3 verbatim Canty 6.dxe5 guard lines (the one tax
of early h6: 7.Bxf7+ Kxf7 8.Nxe5+ trick).

**Ch.2 "Canty 5th-Move Sidelines — Bishop First" (21):** all of Madman's Philidor Ch.2;
4 lines with consecutive ...Qc7/...Be7 swapped to bishop-first (5.dxe5 #1/#2/#3/#7 —
transpose exactly, swap nodes engine-clean); 5.d5 #2 drilled as 9...Nf8 before ...g5
(engine: +0.65 vs +0.92 — course order gives White 10.a5 free); rest verbatim.
NOTE: bishop-first is Ch.2-only — in the Shirov Gambit chapter ...Be7-first loses
material (-1.9); do not generalize.

Validation: 54/54 strict chess.js replay clean in the live file's own engine; all
chapterIds resolve; courses 1-5 untouched (deep-equal verified pre/post splice).

### 2026-08-22 — real chess.com chapters for the 3 legacy courses + picker starts fully collapsed

Cory's ask (two items): (1) course subsections in the trainer picker must match the real
chess.com course structure — the legacy heuristic lumped e.g. all of Old Benoni's theory
into one "Theory" bucket and merged Iron English's 1A/1B/1C sub-chapters; (2) the picker
should open with EVERYTHING collapsed (it previously default-expanded all course headers).

Changes:
- Fetched real chapter structure for Iron English Botvinnik (32 ch), The Black Lion
  (29 ch), Old Benoni (12 ch) via `GetCourseLearningSession` and spliced
  `"chapters":[…]` + per-variation `"chapterId"` into `COURSES_DB` — purely additive
  (1,246 insertions, +70,066 bytes; stripping them reproduces the previous DB exactly;
  the two code edits below add the other 29 bytes of the 724,466 → 794,561 delta).
  100% of non-added variation ids matched lessonsHeaders ids; info flags agree 100%.
- `trComputeChapters()` explicit branch now routes `v.added` lines to "Added lines"
  (Black Lion's 5 analysis-board lines have no chess.com chapterId).
- Picker course headers now default collapsed: `mkHdr('tr-chdr', …, defOpen)` call
  changed `true` → `false` (~line 2884). Search / position filter still force-expand.
- No moves, names, notes, or flags touched. Old heuristic code left in place (dead for
  these 5 courses, still the fallback for any future course without chapter data).

**Extraction gotcha UPDATE (supersedes the JWT/iframe dance for this endpoint):**
`GetCourseLearningSession` now works with plain cookie auth from any chess.com page —
`fetch(RPC, {method:'POST', credentials:'include', headers:{'content-type':
'application/json','connect-protocol-version':'1'}, body:{contextType:'moveTrainer',
contextId:<courseUuid>}})`. No authorization header needed; a captured-but-stale JWT
actively CAUSES 401 "Invalid JWT Token". The iframe fetch-patch capture may still be
needed for `GetCourseTrainingForLearning` (untested today).

Base verified per rule #1: live raw = 724,466 bytes / sha256 `1189c8cf4c703207…`,
byte-identical to the clone. Validation: 1,894 non-partial lines replayed strictly, 0
illegal, 0 non-canonical; 1,921 chapterId refs all resolve; Playwright UI pass (5
collapsed course rows on load; Old Benoni 12 / Iron English 32 / Black Lion 29+Added
chapters render; search expand + re-collapse; drill smoke test clean).

### 2026-08-21 — Stonewall Dutch 2b move-order notes (3 notes, no move changes)

Cory's ask: one answer per position when drilling. The 2b Bg5 line
(1.d4 f5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Bb4 5.e3 Bxc3+ 6.bxc3 O-O 7.Bd3 d6 8.Ne2) appears
twice in the Quickstarter under the *same title*, diverging only at black's 8th move —
8...e5 vs 8...h6 — from an identical position, which made it unlearnable.
Stockfish 24: 8...h6 −0.03 vs 8...e5 −0.15; 8...e5 allows 9.c5! (+0.24), white's only
good idea, resolving his doubled c-pawns after cxd6 cxd6. The h6 insert
(9.Bxf6 Qxf6) puts the queen on f6 so ...dxc5 / dxe5 is met by Qxe5.

Annotated (no moves touched):
- `9a98b9fb` Quickstarter 2b 8...e5 → note + `flag:"skip"`
- `2bb285e0` chapter "2.c4 e6 3.Nc3 Nf6 4.Bg5 #1" (same 8...e5 order) → note + `flag:"skip"`
- `70704c47` Quickstarter 2b 8...h6 → "PREFERRED move order" note

Base verified by SHA-256 against the live raw file before editing (rule #1): 723,949
bytes / `7300c19aada5ca95aee5…`, matched the clone exactly. The splice is purely
additive — three `,"note":…[,"flag":"skip"]` fragments inserted before the closing brace
of three variation objects; stripping those fragments back out reproduces the previous
file character-for-character. Validation: 1,894 non-partial lines replayed strictly
through the embedded chess.js — 0 illegal, 0 non-canonical, 32 partials, 678 chapterId
refs all resolving, notes 10 → 13. No other field changed.

NOTE for whoever ships the next change: `flag:"skip"` is cosmetic only — it strikes the
line through in the browser/picker lists but the trainer still serves it. Cory wants
flagged lines actually excluded from the training pool by default; that needs a code
change in the pool filters (`trRenderPicker` / the two `tr-include-info` filters around
lines 2716-2880), treating `flag === 'skip'` like `info`. Not done here — flagged as the
next candidate.

### 2026-08-18 — added Lifetime Repertoires: Stonewall Dutch (520 sections)

GM Simon Williams, Black. Extracted via the Connect-RPC protocol in the playbook
(`GetCourseLearningSession` → 520 `lessonsHeaders` + 27 chapters, then
`GetCourseTrainingForLearning` per variation, 6-way concurrency, 0 fetch errors).
Shipped with explicit `chapters` + per-variation `chapterId` — chapter runs are
contiguous and in chess.com display order, all 27 resolve, no "Other" bucket.
`info: true` on the 36 `INFORMATIONAL` sections; the 69 `ALTERNATIVE` sections are
trainable like normal lessons. No partial lines — all 520 start from the initial
position. Validation: every ply replayed through the embedded chess.js and every
resulting FEN compared to chess.com's own per-ply FEN — 13,311 plies, 0 mismatches.
Canonicalized 5 SANs chess.com over-specified: 4× `Nge2`→`Ne2` (2.Nc3 Anti-Dutch lines)
and 1 missing mate suffix `Rh1`→`Rh1#` (Jaskolka–Howell model game).
Base verified against the live raw file by SHA-256 before merging (rule #1); the splice
is purely additive — the pre-existing 416,890-byte `COURSES_DB` text is byte-identical.

### 2026-08-15 · `2d7a2a6` — restore + transpose
Rebuilt from `c66c306` (last good version), ported the line-notes/flag feature forward
from `ef9bc25`, applied the Black Lion move-order transposition (46 lines).
Restored what `ef9bc25` had dropped: the Madman's Philidor course, explicit chapter
support, session persistence, back-gesture trap.
Verified live: 4 courses, 1,374 lines, 0 errors.

### 2026-08-15 · `ef9bc25` — line notes feature ⚠️ REGRESSION
Added the notes/flag UI and 10 flagged Risky Lion lines — good work, but built on a
pre-Aug-14 base. Silently reverted: the Madman's Philidor course (4 courses → 3),
explicit chapters (159 `chapterId` refs → 0), session persistence, back-gesture trap.
Black Lion dropped 337 → 332. **This is rule #1 and #3 in action.** Recovered in
`2d7a2a6`.

### 2026-08-15 · `c66c306` — session persistence + Android back gesture
### 2026-08-14 · `da08a12` — over-disambiguated SAN fix (`Nfd7` → `Nd7`) + sloppy fallback
### 2026-08-14 · `fb23980` — Madman's Philidor real chess.com chapter structure
### 2026-08-14 · `3403744` — added The Madman's Philidor Defense (158 sections)

---

## SHIPPING (the path that works)

`git push` is denied from Claude sessions. The working method:

1. Write the finished file(s) to `/mnt/user-data/outputs/` in the container.
2. Open `https://github.com/cory-harelson/chess-trainer/upload/main` in Claude in Chrome.
3. `find` the "Choose your files" file input, then `file_upload` with the container paths.
   **This works** — `/mnt/user-data/outputs/...` is an allowed path (verified 2026-08-18,
   both `index.html` and `BUILD_LOG.md` in one call). The earlier note that `file_upload`
   rejects container paths was wrong; you do NOT need the in-page `fetch` + `DataTransfer`
   dance. Keep that as a fallback only if the upload tool ever refuses.
4. Fill the commit summary and submit via `find` + ref (coordinate clicks miss — the
   page shifts). **The first submit reliably clears the message field without committing
   while keeping the files attached** — re-enter the message and submit again.
5. Confirm with the commits atom feed
   (`https://github.com/cory-harelson/chess-trainer/commits/main.atom` — no API rate
   limit), then verify the live site. Note: fetching `cory-harelson.github.io` from a
   `github.com` page fails CORS — navigate the tab to the live URL and read
   `window.COURSES_DB` in page context instead.
