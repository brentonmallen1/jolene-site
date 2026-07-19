# syntax=docker/dockerfile:1

FROM node:22-alpine AS base
WORKDIR /app

FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# --- dev: source code is bind-mounted by docker-compose ---------------------
FROM deps AS dev
EXPOSE 4321
# clear any stale dev-server lock left in the bind mount by a previous run
CMD ["sh", "-c", "rm -f .astro/dev.json && npm run dev -- --host 0.0.0.0 --port 4321"]

# --- build -------------------------------------------------------------------
FROM deps AS build
COPY . .
RUN npm run build

# --- preview: production build served by nginx --------------------------------
FROM nginx:alpine AS preview
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
