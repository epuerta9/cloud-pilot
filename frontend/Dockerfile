FROM node:22-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --force

# Copy the rest of the application
# COPY . .

# Expose the port
EXPOSE 3000

# Command to run the application with hot reload
CMD ["npm", "start"]