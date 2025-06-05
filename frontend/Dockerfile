FROM node:16

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the port the frontend dev server runs on
EXPOSE 3000

# Set host to 0.0.0.0 to allow external connections
ENV HOST=0.0.0.0

# Command to run the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
