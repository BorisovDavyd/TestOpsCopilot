FROM node:20-alpine
WORKDIR /app
COPY frontend/package.json frontend/tsconfig.json frontend/tsconfig.node.json frontend/vite.config.ts ./
COPY frontend/src ./src
COPY frontend/index.html ./
RUN npm install
RUN npm run build
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
