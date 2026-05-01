# syntax=docker/dockerfile:1.6
###############################################################################
# Stage 1 — build avec Node + Vite
###############################################################################
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

###############################################################################
# Stage 2 — runtime nginx, image minimale
###############################################################################
FROM nginx:1.27-alpine AS runtime

# Conf nginx adaptée au SPA React (fallback vers index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie du build statique
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx tourne déjà en non-root sur les ports >= 80 dans cette image
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
