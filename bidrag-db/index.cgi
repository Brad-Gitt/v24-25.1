#!/bin/sh

DB=../bidrag.db

# start: Public anonym listing og innholdsfiltrering - oppfyller F1 (offentlig tittel og tekst, privat kommentar), F2 (anonym public view) og NF1 (integritet i output) (person 2)
vis_offentlig_liste() {
    sqlite3 -line "$DB" "
        SELECT
            coalesce(trim(tittel), '') AS tittel,
            coalesce(trim(tekst), '') AS tekst
        FROM Bidrag
        WHERE length(trim(coalesce(tittel, ''))) > 0
           OR length(trim(coalesce(tekst, ''))) > 0
        ORDER BY rowid DESC
    "
}
# slutt: Public anonym listing og innholdsfiltrering - oppfyller F1 (offentlig tittel og tekst, privat kommentar), F2 (anonym public view) og NF1 (integritet i output) (person 2)

# start: Redusert logging av innholdsoperasjoner - oppfyller NF1 (dataminimering og konfidensialitet i backend-logikk) (person 2)
logg_innholdsoperasjon() {
    HAR_TITTEL=nei
    HAR_TEKST=nei
    HAR_KOMMENTAR=nei

    if [ -n "$T" ]; then HAR_TITTEL=ja; fi
    if [ -n "$X" ]; then HAR_TEKST=ja; fi
    if [ -n "$K" ]; then HAR_KOMMENTAR=ja; fi

    echo "bidrag-db mottok $REQUEST_METHOD (tittel=$HAR_TITTEL, tekst=$HAR_TEKST, kommentar=$HAR_KOMMENTAR)" >&2
}
# slutt: Redusert logging av innholdsoperasjoner - oppfyller NF1 (dataminimering og konfidensialitet i backend-logikk) (person 2)

# Skriver slutten av HTTP-hodet og en tom linje
cat <<EOF
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET,POST,PUT,DELETE
Access-Control-Allow-Headers: Content-Type
Content-Type:text/plain;charset=utf-8

EOF


# Omgar bug i httpd
CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

if [ "$REQUEST_METHOD" = "GET" ]; then
    vis_offentlig_liste
    exit

elif [ "$REQUEST_METHOD" = "OPTIONS" ]; then
    exit

else
    KR=$(head -c "$CONTENT_LENGTH" )

    N=$( echo "$KR" | xmllint --xpath "/bidrag/navn/text()"             - 2>/dev/null)
    P=$( echo "$KR" | xmllint --xpath "/bidrag/passord/text()"          - 2>/dev/null)
    K=$( echo "$KR" | xmllint --xpath "/bidrag/kommentar/text()"        - 2>/dev/null)
    O=$( echo "$KR" | xmllint --xpath "/bidrag/offentlig_nokkel/text()" - 2>/dev/null)
    T=$( echo "$KR" | xmllint --xpath "/bidrag/tittel/text()"           - 2>/dev/null)
    X=$( echo "$KR" | xmllint --xpath "/bidrag/tekst/text()"            - 2>/dev/null)

    logg_innholdsoperasjon

fi

if [ "$N" = "" ]; then echo Pseudonym mangler!; exit; fi

if [ "$REQUEST_METHOD" = "POST" ]; then

    if [ "$N" != ""  -a  "$P" != "" ]; then

	# Lager et tilfeldig 11-sifret tall som salt
	S=$( for I in $(seq 11);do echo -n $(($RANDOM%9));done )

	# Lager en hashverdi av det skapte saltet og det innsendte passordet
	H=$( mkpasswd -m sha-256 -S $S $P | cut -f4 -d$ )

	# Setter inn ny post i databasen
        sqlite3 $DB "INSERT INTO Bidrag VALUES ('$N','$S','$H','$K','$O','$T','$X')"

    fi
    exit
fi

# Henter lagret saltverdi
S=$( sqlite3 $DB "SELECT salt FROM Bidrag WHERE pseudonym='$N'" )
if [ "$S" = "" ]; then echo Salt mangler ; exit; fi

# Beregner hashverdi av innsendt passord
H1=$( mkpasswd -m sha-256 -S $S $P | cut -f4 -d$ )

# Sammenligner med lagret hashverdi
H2=$( sqlite3 $DB "SELECT passordhash FROM Bidrag WHERE pseudonym='$N'" )

# Avslutter om hashverdiene ikke er like 
if [ "$H1" != "$H2" ]; then echo Feil passord! >&2 ; exit; fi


if [ "$REQUEST_METHOD" = "DELETE" ]; then
    if [ "$N" != "" ]; then
	sqlite3 $DB "DELETE FROM Bidrag WHERE pseudonym='$N'"
    fi

elif [ "$REQUEST_METHOD" = "PUT" ]; then
    sqlite3 $DB                \
       "UPDATE Bidrag SET      \
    	kommentar='$K',        \
    	offentlig_nokkel='$O', \
	tittel='$T',           \
        tekst='$X'             \
        WHERE pseudonym='$N'"
fi
