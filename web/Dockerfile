FROM alpine
RUN apk add busybox-extras
COPY index.html /var/www/
COPY style.css /var/www/
COPY favicon.ico /var/www/
COPY skytjenester-logo.png /var/www/
COPY crypto.js /var/www/

# start: Høy intern port for non-root-kjøring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
EXPOSE 8080
CMD httpd -p 8080 -h /var/www -f -vv
# slutt: Høy intern port for non-root-kjøring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
