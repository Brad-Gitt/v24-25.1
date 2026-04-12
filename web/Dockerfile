FROM alpine
RUN apk add busybox-extras 
COPY index.html var/www/
COPY style.css var/www/
# start: Pakk med klientside-kryptering i web-containeren - oppfyller F1 (privat kommentar) og NF7 (kryptering i klient) (person 3)
COPY crypto.js var/www/
# slutt: Pakk med klientside-kryptering i web-containeren - oppfyller F1 (privat kommentar) og NF7 (kryptering i klient) (person 3)
EXPOSE 80
CMD httpd -p 80 -h /var/www -f -vv
