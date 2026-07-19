// Copies the Sveltia CMS bundle into public/admin so the site is fully
// self-hosted (no CDN). Runs automatically before `npm run dev` and `build`.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const src = join(root, "node_modules/@sveltia/cms/dist/sveltia-cms.js");
const dest = join(root, "public/admin/sveltia-cms.js");

mkdirSync(dirname(dest), { recursive: true });
copyFileSync(src, dest);
console.log("[copy-cms] public/admin/sveltia-cms.js updated");
