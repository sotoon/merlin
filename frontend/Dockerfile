FROM node:21-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --loglevel verbose

COPY . .

RUN npm run build

RUN npm install -g serve

EXPOSE 5000

CMD ["serve", "-s", "build", "-l", "5000"]
