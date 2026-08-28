# Operation Homeward

A one-page campaign site for talking a friend out of Shanghai and back to Israel.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole site — markup, styles and app in one standalone file. Open it in a browser and it works. |
| `artifact.html` | Generated. `index.html` with the `<!doctype>`/`<head>` wrapper stripped and a base64 copy of itself packed into the `#shell` slot, for publishing as a Claude Artifact. |
| `build-artifact.py` | Regenerates `artifact.html`. Run it after every edit to `index.html`. |

Edit `index.html` only; never `artifact.html` directly.

```
python3 site/build-artifact.py
```

## Sections

Everything is added from inside the page — there is no data file to hand-edit.

- **The fourteen days** — one tab per day of the trip. Each tab holds a date, a
  headline and a timed list of plans. `+ Day` adds more; the pencil on a plan
  edits or deletes it.
- **People he really should meet** — name, Instagram handle, tags, a photo, and
  one line about why they'd get along.
- **Work** — companies, roles, sector, stage, link, and who to call.
- **Soundtrack** — a Spotify link becomes an embedded player, with an
  "Play on Spotify" link behind it for any viewer whose browser blocks the embed.
- **Evidence** — photos, dropped or picked. They are resized to 1400px and stored
  inside the page, so they keep working with no image host.
- **From home** — notes from family and friends, Hebrew or English (each block
  sets its own direction).

## Everyone can edit

Every visitor gets the same add and edit controls; nothing is owner-only. Whether
their changes reach everyone else depends on how the link was shared — from the
artifact's share menu, **edit access** lets a visitor save for everyone, **view
access** does not. The chip in the top bar always says which of the two a visitor
has: *Everyone can edit* / *Saved for everyone*, or *View-only link*.

A view-only visitor still keeps every control. Their edits are kept in their own
browser and a banner explains where they landed, so nothing is silently lost — and
if they are later given an edit link, the queued edits are sent up on their next
visit.

## Where the content is stored

1. **In the page.** Everything lives in the `#state` JSON block inside the page, and
   saving publishes a new version of the page carrying it. When anyone saves, every
   other open copy reloads onto the new version, which is what keeps several editors
   in step.
2. **The browser.** Every change is mirrored to `localStorage`, which is the only
   store when the page is opened as a local file.

Older versions kept the content in a `data/state.json` side file. The page still
reads that file when its own `#state` block is empty, so nothing saved under the
old scheme is lost.

## How the page saves itself

To publish a new version, a page has to hand the host a complete replacement
document — and it must not serialise the live DOM, which by then holds viewer
state and the host's own injected scripts. So the page carries a base64 copy of
its own source in `#shell`, with two placeholders: `%%SHELL%%` and `%%STATE%%`.
Saving fills the first with the shell again and the second with the current
content, which makes every generation able to build the next one.
`build-artifact.py` seeds that copy.

There are two publish forms and the page uses whichever one works:

- **Files form** (`publish({"index.html": doc})`) — leaves the saving view running,
  so it is the one to prefer.
- **Whole document** (`publish(doc)`) — reloads every view including the saver.
  This is the only form available once an artifact is **shared publicly**, where the
  files form is refused with `capability_disabled`.

The page starts on the files form, switches permanently to the whole-document form
the first time it is refused, and remembers the choice. Because the whole-document
form reloads the saver, scroll position and the open day tab are stashed in
`sessionStorage` and restored.

`capability_disabled` therefore does **not** mean read-only — it means "try the
other form". Only `not_writer`, `not_granted`, `not_declared`, `consent_required`
and `capability_removed` mean the viewer cannot write.

## Two people editing at once

Changes are recorded as operations — *add this person*, *change this plan's time*,
*delete this photo* — not as whole-document overwrites. Each operation is queued in
`localStorage` until the shared copy accepts it.

If someone else saves first, the save is rejected as a `conflict` and the platform
reloads this page onto their version. On load the page replays its own queued
operations on top of what it just received, then saves again, and shows a
*Recovered* banner. Both people's work survives; neither overwrites the other.
Adds carry their own id, so replaying one twice cannot duplicate it.

A half-written form survives that reload too — it is kept in `sessionStorage` and
reopened, so a long note is never lost to someone else's save.

Contributors set a name once (the *Adding as…* chip in the top bar). It is stored
in their own browser and stamped on whatever they add.
