#!/bin/sh
# entrypoint.sh

# Use envsubst to replace placeholders in the template with actual environment variables
envsubst < /usr/share/nginx/html/env-config.js > /usr/share/nginx/html/env-config.js.tmp
mv /usr/share/nginx/html/env-config.js.tmp /usr/share/nginx/html/env-config.js

# Start the web server (e.g., Nginx)
exec "$@"