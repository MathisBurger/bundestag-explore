# Stage 1: Build the React Application
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
# Copy the built files from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Install envsubst (via gettext) to inject env vars at runtime
RUN apk add --no-cache gettext

# Copy an entrypoint script to handle variable injection
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]