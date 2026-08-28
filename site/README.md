# Operation Homeward

A one-page campaign site for talking a friend out of Shanghai and back to Israel.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole site — markup, styles and app in one standalone file. Open it in a browser and it works. |
| `artifact.html` | Generated. `index.html` with the `<!doctype>`/`<head>` wrapper stripped, for publishing as a Claude Artifact. |
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

1. **The artifact itself.** The page saves to `data/state.json` alongside it, so
   everyone opening the link sees the same content. When anyone saves, every other
   open copy of the page reloads onto the new version, which is what keeps several
   editors in step.
2. **The browser.** Every change is mirrored to `localStorage`, which is the only
   store when the page is opened as a local file.

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
