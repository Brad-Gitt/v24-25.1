FROM alpine
RUN apk add busybox-extras
COPY index.html var/www/
COPY style.css var/www/
COPY favicon.ico var/www/
COPY skytjenester-logo.png var/www/
COPY crypto.js var/www/
EXPOSE 80
CMD httpd -p 80 -h /var/www -f -vv

