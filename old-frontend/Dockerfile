FROM node:21-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install --loglevel verbose

RUN npm install -g serve

COPY . .

RUN npm run build

EXPOSE 5000

CMD ["serve", "-s", "build", "-l", "5000"]
