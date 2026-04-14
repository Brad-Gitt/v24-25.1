#!/bin/sh

# start: Konfigurerbar databasebane for herdet Kubernetes-drift - oppfyller F3 (persistens), NF1 (minste privilegium) og NF3 (stabil lokal kjÃ¸ring) (person 4)
DB="${PSEUDONYM_DB_PATH:-../pseudonym.db}"

# start: SQLCipher-nokkel fra Kubernetes Secret i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
KEY_FILE="${PSEUDONYM_DB_KEY_FILE:-/run/secrets/storage/pseudonym-db-key}"

les_hemmelighet() {
    FIL="$1"

    if [ ! -s "$FIL" ]; then
        echo "Manglende databasenokkel." >&2
        exit 1
    fi

    tr -d '\r\n' < "$FIL"
}

sqlcipher_escape() {
    printf '%s' "$1" | sed "s/'/''/g"
}

SQLCIPHER_KEY=$(les_hemmelighet "$KEY_FILE")
SQLCIPHER_KEY_SQL=$(sqlcipher_escape "$SQLCIPHER_KEY")

db_query() {
    sqlcipher "$DB" <<EOF
PRAGMA key = '$SQLCIPHER_KEY_SQL';
$1
EOF
}

# start: Renser enkelverdier fra SQLCipher-oppslag i steg 9 - oppfyller F1 (stabil autentisering) og NF1 (integritet i autentiseringsflyt) (person 4 og person 5)
db_scalar() {
    db_query "$1" 2>/dev/null | awk 'NF && $0 != "ok" { print; exit }' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}
# slutt: Renser enkelverdier fra SQLCipher-oppslag i steg 9 - oppfyller F1 (stabil autentisering) og NF1 (integritet i autentiseringsflyt) (person 4 og person 5)
# slutt: SQLCipher-nokkel fra Kubernetes Secret i steg 9 - oppfyller F3 (persistens), NF1 (ingen hardkodede hemmeligheter) og NF7 (kryptering av data at rest og nokkelhandtering) (person 4 og person 5)
# slutt: Konfigurerbar databasebane for herdet Kubernetes-drift - oppfyller F3 (persistens), NF1 (minste privilegium) og NF3 (stabil lokal kjÃ¸ring) (person 4)

echo 'Access-Control-Allow-Origin: https://localhost:8443'
echo 'Access-Control-Allow-Credentials: true'
echo 'Access-Control-Allow-Methods: GET,POST,PUT,DELETE'
echo 'Access-Control-Allow-Headers: Content-Type'

echo "Content-Type:text/plain;charset=utf-8"
echo

# start: Tydeligere steg 4-autentiseringsfeil - oppfyller F1 (identitet og flyt) og NF1 (integritet i tilbakemeldinger) (person 1)
svar_autentiseringsfeil() {
    printf '%s\n' "$1"
    printf '%s\n' "$1" >&2
    exit 0
}
# slutt: Tydeligere steg 4-autentiseringsfeil - oppfyller F1 (identitet og flyt) og NF1 (integritet i tilbakemeldinger) (person 1)

# stopper alt som ikke er POST
if [ "$REQUEST_METHOD" != "POST" ]; then exit; fi

# workaround for content-length bug
CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

KR=$(head -c "$CONTENT_LENGTH" )

# ekstraherer epost fÃ¸r logging sÃ¥ vi kan maskere (endring)
E_TMP=$( echo "$KR" | xmllint --xpath "string(/pseudonym/epost)" - 2>/dev/null )

# masker epost for trygg logging (gdpr = unngÃ¥r lekkasje av persondata)
MASKED_E=$(printf '%s' "$E_TMP" | sed 's/^\(.\).*\(@.*\)$/\1***\2/; t; s/.*/***/') # lagt til masking

# logger uten Ã¥ vise hele body (gdpr = unngÃ¥r passord i logs)
echo "pseudonym-db request mottatt for $MASKED_E" >&2 # endret logging

# henter epost og passord fra XML
E=$( echo "$KR" | xmllint --xpath "string(/pseudonym/epost)"   -  2> /dev/null )
P=$( echo "$KR" | xmllint --xpath "string(/pseudonym/passord)" -  2> /dev/null )

# validerer input fÃ¸r videre bruk (gdpr = dataminimering)
if [ -z "$E" ]; then svar_autentiseringsfeil "Epost mangler!"; fi
if [ -z "$P" ]; then svar_autentiseringsfeil "Passord mangler!"; fi

# enkel escaping for Ã¥ redusere SQL injection risiko (gdpr = beskytter data)
E_SAFE=$(printf "%s" "$E" | sed "s/'/''/g") # lagt til

# henter salt fra databasen
S=$( db_scalar "SELECT salt FROM Pseudonym WHERE epost='$E_SAFE';" ) # endret til SAFE

# stopper hvis bruker ikke finnes
if [ -z "$S" ]; then svar_autentiseringsfeil "Bruker finnes ikke!"; fi

# hasher passord med salt (lagrer ikke klartekst)
H1=$( mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d'$' )

# henter lagret hash
H2=$( db_scalar "SELECT passordhash FROM Pseudonym WHERE epost='$E_SAFE';" ) # bruker SAFE

# sammenligner hash og henter pseudonym
if [ "$H1" != "$H2" ]; then svar_autentiseringsfeil "Feil passord!"; fi
PN=$(db_scalar "SELECT pseudonym FROM Pseudonym WHERE epost='$E_SAFE';") # bruker DB variabel konsekvent

# logger mindre sensitiv info (gdpr = begrenser eksponering)
echo "pseudonym funnet for $MASKED_E" >&2 # endret

# returnerer pseudonym
echo "$PN"

