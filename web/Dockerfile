FROM node:20-alpine

WORKDIR /app

# Same caching trick: manifests first, then install, then the source.
COPY package*.json ./

# The flags are all about surviving a slow or flaky network: npm's
# default timeout is short enough that a busy registry aborts the
# build with ETIMEDOUT halfway through. --no-audit/--no-fund just
# skip two extra round-trips we do not need.
RUN npm install --no-audit --no-fund \
      --fetch-retries=5 \
      --fetch-retry-maxtimeout=120000 \
      --fetch-timeout=600000

COPY . .

# Dev server, because this is a teaching project. A production build
# would run `npm run build` and then `npm start`.
#
# The dev script passes -H 0.0.0.0 for the same reason uvicorn does:
# a server bound to 127.0.0.1 inside a container is reachable only
# from that container, so the published port would go nowhere.
CMD ["npm", "run", "dev"]