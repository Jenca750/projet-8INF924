FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Vite default port
EXPOSE 3000

# for production, use "npm run build" and "npm run serve" instead
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
