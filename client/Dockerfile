# build stage
FROM node:20-slim as build-stage
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install
COPY . .

RUN pnpm build
RUN find ./.output -name '*.map' -delete

# run stage
FROM node:20-slim as run-stage
ENV NITRO_CLUSTER_WORKERS=5

COPY --from=build-stage /app/.output .

CMD PORT=5000 node ./server/index.mjs

EXPOSE 5000
