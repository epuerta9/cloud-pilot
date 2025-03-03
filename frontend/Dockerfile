FROM node:14-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Set environment variables for the backend connection
ENV REACT_APP_BACKEND_HOST=localhost
ENV REACT_APP_BACKEND_PORT=8000

# Build the React app
RUN npm run build

# Production environment
FROM nginx:alpine

# Copy built files from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
RUN echo 'server { \
  listen 3000; \
  location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
  } \
}' > /etc/nginx/conf.d/default.conf

# Expose the port
EXPOSE 3000

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]