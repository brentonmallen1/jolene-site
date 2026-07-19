# Jolene Mallen Designs

Portfolio site for Jolene Mallen — a static [Astro](https://astro.build) site with
content managed through [Sveltia CMS](https://github.com/sveltia/sveltia-cms)
(git-based, no server or database).

- **Two layout themes** (chosen in the CMS): `classic` — faithful continuous-scroll
  rebuild of the original site; `studio` — editorial variant with serif display
  type and a numbered side rail.
- **4 color palettes** (gallery / sage / terracotta / slate) + visitor-facing
  light/dark toggle.
- **Interactive views**: images can be set to **360°** (true look-around sphere —
  the three panoramas from the original site are included, self-hosted, no
  Momento360 watermark) or **wide** (flat drag-to-explore). Both appear in a
  labeled row below their gallery.
- Fully self-hosted assets: fonts, lightbox, and the CMS itself are all bundled — no CDNs.

## Quick start

Requirements: Docker + [just](https://github.com/casey/just). (No local Node needed.)

```sh
cp .env.example .env   # optional — only if the default ports clash
just dev               # dev server with hot reload → http://localhost:4321
```

`just` with no arguments lists every command:

| Command | What it does |
|---|---|
| `just dev` | Dev server w/ hot reload (Ctrl+C stops it cleanly) |
| `just preview` | Production build served by nginx → http://localhost:8080 |
| `just stop` / `just clean` | Stop containers / also wipe volumes & images |
| `just build` / `just check` | Production build / typecheck + build |
| `just cms` | How to edit content locally |
| `just shell` / `just logs` | Debug helpers |
| `just import` | ⚠ Re-runs the original site import — overwrites `content/` |
| `just update-cms` | Update the bundled Sveltia CMS |
| `just fix-files` | Fix Docker "error -35" (see Troubleshooting) |

Ports come from `.env` (`DEV_PORT`, `PREVIEW_PORT`) so you can run this alongside
other projects.

## Editing content

All content lives in `content/` as small YAML/Markdown files; images live in
`src/assets/images/`. The CMS is the friendly way to edit both.

### The CMS, locally (no login needed)

1. `just dev`
2. Open `http://localhost:4321/admin` in **Chrome or Edge** (the local workflow
   uses the File System Access API, which Safari/Firefox don't support)
3. Click **Work with Local Repository** and select this project folder
4. Edits save straight to `content/` and hot-reload the site. Commit + push when happy.

Saving keeps you in the editor (site default). Prefer bouncing back to the list
after each save? Flip **Close the editor after saving** in the CMS settings
(account icon → Settings → Contents).

### The CMS, in production

Same `/admin` on the live site, log in with GitHub (one-time OAuth setup below).
Every save is a commit to `main`, which triggers a rebuild — live in a few minutes.

### How the page is organized

The page is an ordered list of sections. Four are fixed, gallery sections are
whatever exists in `content/galleries/`:

| Order | Section | Source |
|---|---|---|
| 1 | About | `content/about.md` |
| 2 | Portfolio | `content/galleries/portfolio.yml` |
| 3 | Conceptual | `content/conceptual/*.md` (one file per project) |
| 4 | Sketching | `content/galleries/sketching.yml` |
| 5 | Textiles | `content/textiles/*.yml` (one file per pattern) |
| 6 | Resume | `content/resume.yml` |

Section numbers ("01", "02", …) and the nav are generated from this list —
nothing to update by hand when it changes.

### Add or replace images in a gallery

CMS → **Gallery Sections** → pick the section → **Images** → *Add*. Upload the
file, write a short description (alt text — it matters for accessibility and
search), save. Drag entries to reorder; the site shows them in list order.

- Any format works (jpg/png/webp) — Astro generates optimized responsive webp
  at build time, so there's no need to pre-compress. Aim for source images
  ≥ 1600px wide so the lightbox looks sharp.
- CMS uploads land in `src/assets/images/uploads/`; the originally imported
  images sit in per-section folders next to it. Both are fine.

### Create a whole new section

CMS → **Gallery Sections** → **New Gallery Section**. Give it a title, an
**order** number (this is its position: use decimals to slot between the fixed
sections — e.g. `4.5` lands after Sketching and before Textiles), pick a layout,
and add images. Four layouts: **masonry** (flowing columns), **rows** (justified
photo-album rows), **mosaic** (mixed sizes with featured images), **squares**
(uniform grid like Textiles). Existing sections can switch layouts anytime —
it's just a dropdown per section. Nav link and section number appear automatically,
in both themes.

### Interactive views (360° and wide images)

Every gallery image has a **Display** setting:

- **Still image** — a normal tile (default).
- **Wide — drag to explore** — for wide flat images (~2:1): shown below the
  gallery in an "Interactive views" row; visitors drag across the space. Six
  wide interiors ship this way (three spa renderings, three sketching interiors).
- **360° — full look-around** — a real sphere view that slowly rotates, can be
  dragged in any direction, and expands to fullscreen via the corner button. Requires a true equirectangular image (exactly
  2:1, looks bowed when viewed flat — e.g. a SketchUp/V-Ray 360 export). The
  three 360s from the original site (Big House day/night, kitchen concept) ship
  this way at the end of Portfolio, self-hosted with no watermark.

Both interactive kinds appear in the labeled row below their gallery, visually
separated from the stills.

### Conceptual projects & textile patterns

Both are folder collections — CMS → **Conceptual Projects** / **Textile
Patterns** → *New…*. Projects have a kicker ("Project One"), a brief, a
write-up, and a gallery; patterns have a name, inspiration, and square
swatches with colorway names. `order` controls their sequence within the
section.

### Everything else

- **Hero** (big image + name): Site Settings → Hero
- **Bio / headshot / badges**: About
- **Resume PDF**: Resume → upload a new PDF (replaces the embedded viewer + link)
- **Email / LinkedIn** (footer): Site Settings → Footer
- **Theme, palette, light/dark default**: Site Settings

### Hand-editing files instead

Everything the CMS does is plain YAML/Markdown — edit away, it hot-reloads.
One convention to keep: **image paths are relative to the content file**, so
files in `content/` use `../src/assets/images/…` and files one level deeper
(`content/galleries/`, `content/conceptual/`, `content/textiles/`) use
`../../src/assets/images/…`.

⚠ `just import` regenerates all of `content/` from the original site scrape —
it will erase every edit made since. It exists for disaster recovery only.

## Changing the look

- **Theme & palette**: Site Settings in the CMS (no code).
- **Colors**: all palettes live in [src/styles/tokens.css](src/styles/tokens.css)
  as CSS custom properties (OKLCH), each with light + dark variants. Tweak a
  palette or add a fifth — then also add its name to the `palette` options in
  `src/content.config.ts` and `public/admin/config.yml`.
- **Fonts**: self-hosted via Fontsource — Jost everywhere, Fraunces for the
  studio theme's display type. Swap by installing another `@fontsource-*`
  package and updating `--font-*` in `tokens.css`.
- **Layout/markup**: each theme is one file —
  `src/themes/classic/ClassicPage.astro` and `src/themes/studio/StudioPage.astro` —
  plus shared components in `src/components/`.

## Deploying

Two good options. Either way, push the repo to GitHub first, and afterwards do
the one-time **CMS login setup** below so Jolene can edit on the live site.

### Option A — Netlify (recommended)

1. Netlify → **Add new site → Import an existing project** → pick the repo.
   [netlify.toml](netlify.toml) already sets the build command and publish dir.
2. Done — every push (including CMS saves) rebuilds automatically.

### Option B — GitHub Pages

A ready workflow is included at
[.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml):

1. Push the repo to GitHub.
2. Repo **Settings → Pages → Source: GitHub Actions**.
3. Push to `main` (or run the workflow manually) — it builds and deploys.

Caveats worth knowing:

- This site uses root-absolute URLs (`/admin`, `/resume.pdf`, …), so it must be
  served from a **domain root**: either set the custom domain
  (Settings → Pages → Custom domain → `www.jolenemallendesigns.com`) or name the
  repo `<username>.github.io`. A project subpath like
  `username.github.io/jolene-site` would need `base` configured in
  `astro.config.mjs` and link changes — not set up.
- Netlify's cache headers in `netlify.toml` don't apply on Pages (GitHub serves
  its own). Harmless, just Netlify-specific.
- The CMS works the same on Pages — it talks to GitHub, not to the host.

### CMS login on the live site (one-time)

Sveltia needs a tiny OAuth shim so GitHub login works from the browser:

1. Deploy [`sveltia-cms-auth`](https://github.com/sveltia/sveltia-cms-auth) to
   Cloudflare Workers (free; one-click button in that repo's README).
2. Create a GitHub **OAuth App** (Settings → Developer settings) with callback URL
   `https://<your-worker>.workers.dev/callback`; put its client ID/secret in the
   Worker's environment variables, and the site's domain in `ALLOWED_DOMAINS`.
3. In [public/admin/config.yml](public/admin/config.yml): set `backend.repo` to
   `your-user/your-repo` and `backend.base_url` to the Worker URL.

### Custom domain cutover

Add the custom domain on the host (Netlify: Domain settings; Pages: Settings →
Pages), then point the domain's DNS at it per the host's instructions. Keep the
original site untouched until the new one is verified live.

## Self-hosting elsewhere

The site is plain static files. `just build` produces `dist/` — serve it with
any web server. `just preview` runs the exact production bundle in nginx locally
(the same `Dockerfile` `preview` target works on any Docker host).

## Project layout

```
content/            ← CMS-managed content (YAML/Markdown, one file per thing)
  galleries/        ← gallery sections (portfolio, sketching, + any new ones)
  conceptual/       ← one .md per conceptual project
  textiles/         ← one .yml per textile pattern
src/assets/images/  ← site images (imported from the original site media dump + CMS uploads)
src/components/     ← Nav, GalleryGrid (+PhotoSwipe lightbox), PanoramaViewer, …
src/themes/         ← classic/ and studio/ page compositions
src/styles/         ← tokens.css (palettes), base.css
public/admin/       ← Sveltia CMS (bundle is copied from node_modules at build)
scripts/            ← import-content.py (one-time original site import) + helpers
images/             ← original site media dump (gitignored, kept as archive)
```

## Troubleshooting

- **Dev container fails with `Unknown system error -35`** → `just fix-files`.
  This machine background-compresses files (APFS transparent compression) and
  Docker's file sharing can't read compressed files from bind mounts. The same
  fix applies if files in `images/` ever read as empty.
- **`/admin` won't open the local repository** → use Chrome or Edge; the local
  workflow needs the File System Access API.
- **Dev server says "already running"** → a stale `.astro/dev.json` lock;
  `npx astro dev stop`, or just restart `just dev` (the container clears it).
- **A CMS save didn't show up locally** → the dev server watches `content/`;
  if it ever misses a change, restarting `just dev` re-syncs.
- **Want unused original site images?** The dump in `images/` has ~95 images never
  published on the old site (client work, alternates). Add them through the CMS
  like any upload. Regenerate any from the source JPEGs in the original export
  with `scripts/convert-to-webp.sh <src-dir> <dest-dir>`.
