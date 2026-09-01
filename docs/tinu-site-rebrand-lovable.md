# Tinu site rebrand — brief for Lovable

Paste everything inside the fence into Lovable as a single prompt.

**Before it goes live:** the GB300 NVL72 specs are unverified (FY27 risk R10).
The prompt below deliberately tells Lovable to leave every spec number as a
visible placeholder. Get Ken to confirm the numbers, then fill them in.

---

```
Build a single-page marketing site for Tinu (tinu.ai). Dark, restrained,
engineering-led. This is a stealth-stage company — the site should read as
confident and deliberately under-explained, not as a startup trying to be found.

## What Tinu actually is

Tinu buys, builds and resells GPU compute. Three things, in one business:

1. Procurement — NVIDIA GB300 / DGX B300 systems, secured at allocation scale.
2. Buildout — a data centre in northern Israel, with power already approved and
   a path to significantly more.
3. Deployment — putting that compute to work for customers who do serious
   scientific and technical computing, with engineers who understand the science,
   not just the hardware.

The differentiator is the third one. Anyone can resell GPUs. Very few can staff
a deployment with people who can read the customer's actual research problem.

## Sections, in order

**1. Hero.** No tagline cliché. One short, declarative line about compute that is
hard to get, and a second line no longer than a sentence. A single quiet CTA:
"Talk to us" → mailto:nadav.d@tinu.ai. No signup form, no newsletter, no chat
widget.

**2. The hardware.** GB300 NVL72 and DGX B300. State what generation this is and
why access matters right now, but IMPORTANT: put every numeric spec — GPU count,
memory, interconnect bandwidth, rack power — as a visibly marked placeholder like
[SPEC: GPUs per rack]. Do not invent, estimate or look up any figure. I will fill
them in myself.

**3. Vera Rubin.** Next-generation NVIDIA silicon, arriving Q1 2027. Frame it as
the reason to have the relationship in place now rather than then. Short — three
or four lines. No specs at all here.

**4. Orchestration.** Software out of Princeton that schedules and manages the
fleet. Keep it deliberately thin on detail — say what it does for the customer
(their job runs, they don't manage infrastructure), not how it works.

**5. The engineers.** The real section. Forward-deployed engineers with Ivy League
scientific backgrounds — Princeton among them — who deploy GPUs on-prem for
companies doing computationally heavy science. Explain that this is the part
nobody else offers: the person who shows up understands the domain, so the
cluster gets used properly from week one rather than after six months of
misconfiguration. No names, no photos, no headcount.

**6. Footprint.** Princeton as the primary data centre, additional US colocation,
and a facility being built in northern Israel. For Israel say only that initial
power is approved and further capacity is in progress — no megawatt figures, no
site name, no town.

**7. Contact.** Just nadav.d@tinu.ai, large and plain. Nothing else.

## What must NOT appear

No team page, no photos, no customer logos, no testimonials, no case studies,
no funding announcements, no press section, no social links, no cookie banner,
no pricing, no "trusted by", no counters that animate up. No invented numbers
anywhere — if a figure isn't in this brief, it doesn't go on the page.

## Design direction

Dark, single-theme, committed. Do not build a light mode.

Palette: cold graphite as the ground (#0E1113 to #1A1F23 range), with a warm
sodium-ember accent (around #E8843C) used sparingly — one accent moment per
viewport at most. The contrast between cold ground and warm accent is the whole
visual idea: it should read like something running hot in a cold room. Do not
add a second accent colour.

Type: a grotesque with real character for headings — Archivo, weights 600–800,
tightened tracking on the large sizes. IBM Plex Mono for labels, specs, section
eyebrows and the placeholder markers. Body text in Archivo at normal weight.
Load from Google Fonts and declare real fallback stacks.

Layout: generous vertical space, a narrow measure for reading text (around 65
characters), and section transitions marked by a thin hairline rule rather than
a colour change. Left-aligned throughout — do not centre body content.

One ambient effect, and only one: a slow, subtle thermal bloom behind the hero,
rendered on canvas — dark field with warm colour welling up and dissipating, like
heat off a rack. Very low contrast, very slow. Respect prefers-reduced-motion and
drop it entirely to a static gradient when reduced motion is set. No other
animation on the page: no scroll reveals, no hover lifts, no parallax.

Fully responsive. Nothing scrolls horizontally.

## Tone of the copy

Short sentences. Technical and unhurried. Never say "revolutionary",
"cutting-edge", "empowering", "unlock", "seamless", "game-changing", or
"the future of". Assume the reader knows what a GPU cluster is and would be
insulted by an explanation. Fewer words is better — if a section can be three
lines instead of a paragraph, make it three lines.
```

---

## After Lovable returns it

- Replace every `[SPEC: ...]` placeholder with figures Ken has confirmed.
- Check `nadav.d@tinu.ai` is live before the site is — see the Google Workspace
  task. A contact address that bounces is worse than no site.
- Decide whether stealth still serves you. If the Israeli buildout needs inbound
  from 20–40 early-stage tenants, a site with nothing findable on it works
  against that. Positioning call, not a design one.
