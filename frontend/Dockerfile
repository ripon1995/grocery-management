# standard Node.js image version
FROM node:24-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the files ot /app directory first to leverage Docler caching
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
Copy . .

# Expose the port
EXPOSE 3000

# Run the server
CMD ["npm", "run", "dev-public"]