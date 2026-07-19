// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
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
