FROM alpine
# start: SQLCipher og intern adminverifisering for steg 9 - oppfyller F2 (tilgangsbegrenset admin-visning) og NF7 (kryptering av data at rest) (person 4 og person 5)
RUN apk add busybox-extras libxml2-utils sqlcipher mkpasswd curl
# slutt: SQLCipher og intern adminverifisering for steg 9 - oppfyller F2 (tilgangsbegrenset admin-visning) og NF7 (kryptering av data at rest) (person 4 og person 5)
COPY index.cgi /var/www/cgi-bin/
COPY init.sql /var/www/init.sql
COPY init-encrypted-db.sh /var/www/init-encrypted-db.sh
# start: Klargjor CGI og kryptert init-script for bidrag-tjenesten i steg 9 - oppfyller F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)
RUN chmod +x /var/www/cgi-bin/index.cgi /var/www/init-encrypted-db.sh
# slutt: Klargjor CGI og kryptert init-script for bidrag-tjenesten i steg 9 - oppfyller F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)

# start: Hoye interne porter for non-root-kjoring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
EXPOSE 8082
CMD httpd -p 8082 -h /var/www -f -vv
# slutt: Hoye interne porter for non-root-kjoring i Kubernetes - oppfyller NF1 (minste privilegium) og NF3 (stabil lokal drift) (person 4)
