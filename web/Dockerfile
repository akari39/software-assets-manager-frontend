FROM node:20-alpine AS builder
WORKDIR /app

ARG NEXT_PUBLIC_API_URL_DEV
ENV NEXT_PUBLIC_API_URL_DEV=$NEXT_PUBLIC_API_URL_DEV

COPY package.json package-lock.json ./
RUN npm install --production
COPY next.config.mjs jsconfig.json eslint.config.mjs ./
COPY app ./app
COPY public ./public
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.mjs ./next.config.mjs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules

# ENV NEXTAUTH_SECRET=你的密钥
# ENV DATABASE_URL=你的数据库 URL

EXPOSE 3000

# 启动命令
CMD ["npm", "run", "start", "-H", "0.0.0.0", "-p", "3000"]
