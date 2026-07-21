# Cutting over to the custom domain (www.jolenemallendesigns.com)

Right now the site serves from `https://brentonmallen1.github.io/jolene-site/`
(a project-page subpath), driven by `BASE_PATH` in
[.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml)
defaulting to `/jolene-site`. This doc is the checklist for switching to the
custom domain once DNS is ready. Do the steps **in this order** — setting the
custom domain in GitHub before DNS resolves will make the (currently working)
subpath URL start redirecting to a domain that doesn't answer yet, i.e. the
site goes dark until DNS catches up.

## 1. Point DNS at GitHub Pages first

At your DNS provider for `jolenemallendesigns.com`:

- **`www` subdomain** (the one actually in use — `www.jolenemallendesigns.com`):
  add a `CNAME` record: `www` → `brentonmallen1.github.io`
- **Apex domain** (`jolenemallendesigns.com`, only if you want the bare
  domain to also work / redirect to `www`): add four `A` records at `@` to
  GitHub Pages' IPs (check current values at
  [GitHub's Pages custom-domain docs](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) —
  they occasionally change):
  ```
  185.199.108.153
  185.199.109.153
  185.199.110.153
  185.199.111.153
  ```

Wait for DNS to actually propagate before continuing — check with:
```
dig www.jolenemallendesigns.com CNAME
```

## 2. Add the CNAME file to the repo

Create `public/CNAME` (no extension) containing exactly:
```
www.jolenemallendesigns.com
```
This ships into `dist/CNAME` on every build so GitHub Pages picks up the
custom domain from the deployed artifact.

## 3. Set the custom domain in repo settings

Either via the UI (Settings → Pages → Custom domain → enter
`www.jolenemallendesigns.com` → Save), or via the API:
```
gh api -X PUT repos/brentonmallen1/jolene-site/pages \
  -f cname=www.jolenemallendesigns.com
```
Once GitHub verifies DNS, tick **Enforce HTTPS** in the same settings page
(it can take a few minutes to become available after the domain verifies).

## 4. Flip BASE_PATH back to root

The site no longer lives under a subpath once the custom domain is live, so
set the repo variable that overrides the workflow's default:
```
gh variable set BASE_PATH --body "/" --repo brentonmallen1/jolene-site
```
Then re-run the deploy workflow (push a commit, or `gh workflow run deploy-pages.yml --repo brentonmallen1/jolene-site`).

## 5. Verify

```
curl -sI https://www.jolenemallendesigns.com/ | head -1        # 200
curl -sI https://www.jolenemallendesigns.com/favicon.svg       # 200
curl -sI https://www.jolenemallendesigns.com/admin             # 404 — the CMS is local-only, stripped from builds
curl -sI https://www.jolenemallendesigns.com/resume.pdf        # 200
```

If something 404s, it's almost certainly a stale `BASE_PATH` (still
`/jolene-site` — re-check step 4) or the CNAME file missing from the build
(step 2).
