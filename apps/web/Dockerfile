# syntax=docker/dockerfile:1.7
FROM node:22.22.0-alpine3.23 AS dependencies
WORKDIR /app
COPY apps/web/package.json apps/web/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM node:22.22.0-alpine3.23 AS builder
ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app
COPY --from=dependencies /app/node_modules ./node_modules
COPY apps/web ./
RUN npm run build

FROM node:22.22.0-alpine3.23 AS runtime
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 HOSTNAME=0.0.0.0 PORT=3000 HOME=/tmp
WORKDIR /app
RUN addgroup --system --gid 10001 app && adduser --system --uid 10001 --ingroup app app
COPY --from=builder --chown=10001:10001 /app/.next/standalone ./
COPY --from=builder --chown=10001:10001 /app/.next/static ./.next/static
USER 10001:10001
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
  CMD ["wget", "--quiet", "--spider", "http://127.0.0.1:3000/"]
CMD ["node", "server.js"]
