// @ts-check
import { defineConfig } from 'astro/config';
import { rm } from 'node:fs/promises';

// The CMS is a local editing tool (dev server in the Docker container); the
// deployed site is read-only. Strip /admin — the page shell plus the Sveltia
// bundle and config from public/admin/ — from every build output.
const stripAdmin = {
  name: 'strip-admin',
  hooks: {
    'astro:build:done': async ({ dir, logger }) => {
      await rm(new URL('admin/', dir), { recursive: true, force: true });
      logger.info('removed /admin from the build output');
    },
  },
};

// https://astro.build/config
export default defineConfig({
  integrations: [stripAdmin],
  site: process.env.SITE_URL ?? "https://www.jolenemallendesigns.com",
  // Set to e.g. "/jolene-site" when serving from a GitHub Pages project
  // subpath instead of the custom domain root.
  base: process.env.BASE_PATH || "/",
  vite: {
    server: {
      // Inside Docker, file events from the host (especially the atomic
      // temp-file + rename writes the CMS does) don't reliably cross the
      // bind mount — poll instead. Set via docker-compose; off on the host.
      watch: process.env.WATCH_POLLING
        ? { usePolling: true, interval: 700 }
        : undefined,
    },
  },
});
