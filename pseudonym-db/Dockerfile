FROM alpine
# start: SQLCipher for kryptert pseudonym-lagring i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)
RUN apk add busybox-extras libxml2-utils sqlcipher
COPY index.cgi /var/www/cgi-bin/
COPY init.sql /var/www/init.sql
COPY init-encrypted-db.sh /var/www/init-encrypted-db.sh
# slutt: SQLCipher for kryptert pseudonym-lagring i steg 9 - oppfyller F3 (persistens) og NF7 (kryptering av data at rest) (person 4 og person 5)

# start: Klargjor CGI og kryptert init-script for pseudonym-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)
RUN chmod +x /var/www/cgi-bin/index.cgi /var/www/init-encrypted-db.sh
EXPOSE 8083
CMD httpd -p 8083 -h /var/www -f -vv
# slutt: Klargjor CGI og kryptert init-script for pseudonym-databasen i steg 9 - oppfyller F3 (persistens) og NF7 (kryptert lagring) (person 4 og person 5)
