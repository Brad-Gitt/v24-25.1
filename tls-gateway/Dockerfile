FROM alpine
# start: Nginx-basert TLS-gateway i steg 9 - oppfyller NF7 (TLS/HTTPS) og NF1 (forsvar i dybden) (person 4 og person 5)
RUN apk add nginx
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8443
CMD ["nginx", "-e", "/dev/stderr", "-g", "daemon off;"]
# slutt: Nginx-basert TLS-gateway i steg 9 - oppfyller NF7 (TLS/HTTPS) og NF1 (forsvar i dybden) (person 4 og person 5)
