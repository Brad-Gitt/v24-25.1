#!/bin/sh

# start: Konfigurerbar databasebane for herdet Kubernetes-drift - oppfyller F3 (persistens), NF1 (minste privilegium) og NF3 (stabil lokal kjøring) (person 4)
DB="${PSEUDONYM_DB_PATH:-../pseudonym.db}"
# slutt: Konfigurerbar databasebane for herdet Kubernetes-drift - oppfyller F3 (persistens), NF1 (minste privilegium) og NF3 (stabil lokal kjøring) (person 4)

echo 'Access-Control-Allow-Origin: http://localhost:8080'
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

# ekstraherer epost før logging så vi kan maskere (endring)
E_TMP=$( echo "$KR" | xmllint --xpath "string(/pseudonym/epost)" - 2>/dev/null )

# masker epost for trygg logging (gdpr = unngår lekkasje av persondata)
MASKED_E=$(printf '%s' "$E_TMP" | sed 's/^\(.\).*\(@.*\)$/\1***\2/; t; s/.*/***/') # lagt til masking

# logger uten å vise hele body (gdpr = unngår passord i logs)
echo "pseudonym-db request mottatt for $MASKED_E" >&2 # endret logging

# henter epost og passord fra XML
E=$( echo "$KR" | xmllint --xpath "string(/pseudonym/epost)"   -  2> /dev/null )
P=$( echo "$KR" | xmllint --xpath "string(/pseudonym/passord)" -  2> /dev/null )

# validerer input før videre bruk (gdpr = dataminimering)
if [ -z "$E" ]; then svar_autentiseringsfeil "Epost mangler!"; fi
if [ -z "$P" ]; then svar_autentiseringsfeil "Passord mangler!"; fi

# enkel escaping for å redusere SQL injection risiko (gdpr = beskytter data)
E_SAFE=$(printf "%s" "$E" | sed "s/'/''/g") # lagt til

# henter salt fra databasen
S=$( sqlite3 "$DB" "SELECT salt FROM Pseudonym WHERE epost='$E_SAFE'" ) # endret til SAFE

# stopper hvis bruker ikke finnes
if [ -z "$S" ]; then svar_autentiseringsfeil "Bruker finnes ikke!"; fi

# hasher passord med salt (lagrer ikke klartekst)
H1=$( mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d'$' )

# henter lagret hash
H2=$( sqlite3 "$DB" "SELECT passordhash FROM Pseudonym WHERE epost='$E_SAFE'" ) # bruker SAFE

# sammenligner hash og henter pseudonym
if [ "$H1" != "$H2" ]; then svar_autentiseringsfeil "Feil passord!"; fi
PN=$(sqlite3 "$DB" "SELECT pseudonym FROM Pseudonym WHERE epost='$E_SAFE'") # bruker DB variabel konsekvent

# logger mindre sensitiv info (gdpr = begrenser eksponering)
echo "pseudonym funnet for $MASKED_E" >&2 # endret

# returnerer pseudonym
echo "$PN"
