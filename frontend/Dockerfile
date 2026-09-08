FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ARG BACKEND_URL

ENV BACKEND_URL=${BACKEND_URL}

RUN npm run build

CMD ["npm", "run", "start"]
