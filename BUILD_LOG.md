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

## CURRENT STATE — 2026-08-18

- Live: https://cory-harelson.github.io/chess-trainer/
- HEAD: `<this commit>` · `index.html` = 723,949 bytes
- Validation: 1,893 lines replayed, 0 illegal moves, 0 non-canonical SANs, 0 unresolved
  chapter refs. (The 1,374 figure in the 2026-08-15 log counted one 1-move line that the
  trainer itself skips; under the current script the pre-merge baseline is 1,373.)

**Courses (5):**

| Course | Variations | Chapters |
|---|---|---|
| The Iron English: Botvinnik Variation | 810 | heuristic |
| The Black Lion (Simon Williams) | 337 | heuristic |
| Black is Back: Old Benoni | 101 | heuristic |
| The Madman's Philidor Defense (James Canty III) | 158 | explicit (10) |
| Lifetime Repertoires: Stonewall Dutch (Simon Williams) | 520 | explicit (27) |

**Features present in `index.html`:**

- Line notes + `flag: "skip"` annotations (10 flagged Risky Lion lines vs 8.b3)
- Explicit chapter support — `course.chapters` + per-variation `chapterId` wins over
  the legacy name-pattern heuristic
- Live-session persistence — `visibilitychange` / `pagehide` snapshot to localStorage,
  restored by `trTryRestore()`
- Android back-gesture trap — history sentinel + `overscroll-behavior: none`
- SAN canonicalization + `{sloppy: true}` parse fallback in `trApply()`
- Black Lion move order normalized: 46 transposable lines use `3...Nbd7 4.Nf3 e5`.
  The 34 `3...e5 4.dxe5` queen-trade lines keep Simon's original order (they cannot
  transpose) and remain fully trainable.

## CHANGE LOG (newest first)

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

`git push` is denied from Claude sessions and `file_upload` no longer accepts container
paths. The working method:

1. Open `https://github.com/cory-harelson/chess-trainer/upload/main` in Claude in Chrome
2. Have the *page* build the file — `fetch()` the raw base from
   `raw.githubusercontent.com`, apply changes in page context, `new File([out], ...)`
3. Attach via `DataTransfer` → `input.files` → dispatch `change`
4. Fill the commit summary and submit via `find` + ref (coordinate clicks miss — the
   page shifts). If the form reappears empty, re-enter the message and submit again.
5. Confirm with the commits atom feed
   (`https://github.com/cory-harelson/chess-trainer/commits/main.atom` — no API rate
   limit) and then curl the live site.
