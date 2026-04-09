#!/bin/sh

DB=../pseudonym.db

echo 'Access-Control-Allow-Origin: http://localhost:8080'
echo 'Access-Control-Allow-Credentials: true'
echo 'Access-Control-Allow-Methods: GET,POST,PUT,DELETE'
echo 'Access-Control-Allow-Headers: Content-Type'

echo "Content-Type:text/plain;charset=utf-8"
echo

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
if [ -z "$E" ]; then echo "Epost mangler!" >&2; exit; fi # lagt til
if [ -z "$P" ]; then echo "Passord mangler!" >&2; exit; fi # lagt til

# enkel escaping for å redusere SQL injection risiko (gdpr = beskytter data)
E_SAFE=$(printf "%s" "$E" | sed "s/'/''/g") # lagt til

# henter salt fra databasen
S=$( sqlite3 "$DB" "SELECT salt FROM Pseudonym WHERE epost='$E_SAFE'" ) # endret til SAFE

# stopper hvis bruker ikke finnes
if [ -z "$S" ]; then echo "Bruker finnes ikke!" >&2 ; exit; fi # forbedret sjekk

# hasher passord med salt (lagrer ikke klartekst)
H1=$( mkpasswd -m sha-256 -S "$S" "$P" | cut -f4 -d'$' )

# henter lagret hash
H2=$( sqlite3 "$DB" "SELECT passordhash FROM Pseudonym WHERE epost='$E_SAFE'" ) # bruker SAFE

# sammenligner hash og henter pseudonym
if [ "$H1" != "$H2" ]; then echo "Feil passord!" >&2 ; exit; fi
PN=$(sqlite3 "$DB" "SELECT pseudonym FROM Pseudonym WHERE epost='$E_SAFE'") # bruker DB variabel konsekvent

# logger mindre sensitiv info (gdpr = begrenser eksponering)
echo "pseudonym funnet for $MASKED_E" >&2 # endret

# returnerer pseudonym
echo "$PN"
