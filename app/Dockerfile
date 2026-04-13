FROM alpine
RUN apk add busybox-extras curl
COPY index.cgi /var/www/cgi-bin/
RUN chmod +x /var/www/cgi-bin/index.cgi

# start: Høye interne porter for non-root-kjøring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
EXPOSE 8081
CMD httpd -p 8081 -h /var/www -f -vv
# slutt: Høye interne porter for non-root-kjøring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
