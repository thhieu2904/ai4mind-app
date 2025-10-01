FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application
COPY . .

# Build app
RUN npm run build

# Expose port
EXPOSE 3000

# Run application
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
