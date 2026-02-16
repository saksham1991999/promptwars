FROM node:20-alpine AS build
WORKDIR /app

# Build arguments for environment-specific builds
ARG VITE_API_BASE_URL
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_PUBLISHABLE_KEY
ARG VITE_POSTHOG_API_KEY
ARG VITE_POSTHOG_HOST=https://app.posthog.com
ARG VITE_SENTRY_DSN

# ENV variables are picked up from .env.production by Vite during build

COPY package*.json ./
RUN npm ci --production=false
COPY . .
RUN npm run build

FROM nginx:alpine

LABEL cloud.google.com/service="chess-alive-frontend"
LABEL maintainer="Chess Alive Team"

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
