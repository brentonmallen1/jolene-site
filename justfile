# Jolene Mallen Designs — common tasks. Run `just` to see this list.
# Ports & settings come from .env (see .env.example); defaults work out of the box.

set dotenv-load

dev_port := env_var_or_default("DEV_PORT", "4321")
preview_port := env_var_or_default("PREVIEW_PORT", "8080")

# List available commands
default:
    @just --list --unsorted

# Start the dev server with hot reload (Ctrl+C stops it) → http://localhost:$DEV_PORT
dev:
    docker compose up --build dev

# Build the production site and serve it with nginx → http://localhost:$PREVIEW_PORT
preview:
    docker compose --profile preview up --build preview

# Stop and remove all containers for this project
stop:
    docker compose --profile preview down --remove-orphans

# Stop everything and also remove volumes + built images (fresh-slate reset)
clean:
    docker compose --profile preview down --remove-orphans --volumes --rmi local

# Production build inside Docker (output in ./dist)
build:
    docker compose run --rm --no-deps dev npm run build

# Type-check the Astro project and run a production build
check:
    docker compose run --rm --no-deps dev sh -c "NODE_OPTIONS=--max-old-space-size=4096 npx astro check && npm run build"

# Commit all changes and push to trigger the Pages deploy (new images auto-LFS via .gitattributes)
publish message="content: site update":
    git add -A
    git diff --cached --quiet || git commit -m "{{message}}"
    git push -u origin main
    @echo "Pushed. Watch the deploy: $(git remote get-url origin | sed -e 's#^git@github.com:#https://github.com/#' -e 's#\.git$##')/actions"

# Re-run the one-time Wix content import (overwrites content/ — CMS edits are lost!)
import:
    python3 scripts/import-content.py

# How to edit content locally with the CMS
cms:
    @echo "1. just dev"
    @echo "2. Open http://localhost:{{dev_port}}/admin in Chrome or Edge"
    @echo "3. Click 'Work with Local Repository' and select this project folder"
    @echo "   → edits write straight to content/ and hot-reload the site."
    @echo "   (Commit and push the changes yourself when happy.)"

# Follow dev server logs (when dev is running detached or from another terminal)
logs:
    docker compose logs -f dev

# Open a shell inside the dev container
shell:
    docker compose run --rm dev sh

# Update the self-hosted Sveltia CMS bundle to the latest release
update-cms:
    docker compose run --rm --no-deps dev sh -c "npm update @sveltia/cms && node scripts/copy-cms.mjs"

# Fix "Unknown system error -35" in the dev container (macOS APFS compression vs Docker)
fix-files:
    python3 scripts/fix-apfs-compression.py
