## Development

Day-to-day tasks run through the justfile (`just` lists them): `just dev` (Docker dev
server), `just preview` (prod build in nginx), `just check`, `just cms`. Ports come
from `.env` (see `.env.example`).

When starting the dev server directly on the host, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Project gotchas

- **Docker "Unknown system error -35"**: this machine APFS-compresses files in the
  background; Docker's VirtioFS can't read them from bind mounts. Run `just fix-files`
  (scripts/fix-apfs-compression.py). Detection needs `st_flags & 0x20` — the decmpfs
  xattr is invisible to `xattr`. Use `shutil.copyfile` (not `copy2`) in scripts.
- **Stale dev-server lock**: Astro writes `.astro/dev.json`; the Docker dev CMD removes
  it on start. If a host daemon is stuck: `npx astro dev stop`.
- **Content model**: `content/` is CMS-managed (Sveltia at `/admin`, config in
  `public/admin/config.yml`). Gallery image paths are entry-relative
  (`../src/assets/...` or `../../src/assets/...`) — keep CMS `public_folder` and
  `content.config.ts` in sync if moving things.
- **Pannellum** (360 sphere viewer): config `type` must be `equirectangular`
  (not `equirect`); only feed it true 2:1 equirect sources or it warps.
- Gallery items have `view: still | wide | "360"` (quoted in YAML).
- `scripts/import-content.py` regenerates all of `content/` from the original Wix
  scrape — running it destroys CMS edits.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
