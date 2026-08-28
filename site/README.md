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

## Where the content is stored

Two places, in this order:

1. **The artifact itself.** When the page runs as a published Artifact it saves to
   `data/state.json` alongside the page, so everyone who opens the link sees the
   same content. The chip in the top bar reads *Saved for everyone*.
2. **The browser.** Every change is also mirrored to `localStorage`, which is the
   only store when the page is opened as a local file. The chip then reads
   *Saved on this device* — that copy does not reach anyone else.

A viewer without write access sees the content with every add and edit button
hidden, and the chip reads *Read-only view*.
