# 使用官方Node.js镜像作为基础镜像  
FROM node:20  AS builder
  
# 设置工作目录  
WORKDIR /app  
  
# 复制整个项目目录到工作目录  
COPY . .  
  
# 切换到rtclient目录并运行npm link  
WORKDIR /app/rtclient  
RUN npm install  
RUN npm run build
RUN npm link  
  
# 切换到web目录并运行npm link rtclient  
WORKDIR /app/web  
RUN npm install  
RUN npm link rt-client  
  
# 构建web项目  
RUN npm run build  
  
# 使用官方Nginx镜像作为基础镜像  
FROM nginx:alpine  
  
# 复制构建的文件到Nginx的html目录  
COPY --from=builder /app/web/dist /usr/share/nginx/html  
  
# 复制自定义的Nginx配置文件  
COPY nginx.conf /etc/nginx/nginx.conf  
  
# 暴露应用程序端口  
EXPOSE 8080

  
# 启动Nginx  
CMD ["nginx", "-g", "daemon off;"] 