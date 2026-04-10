#!/bin/sh

# litt oppgradert CGI-script med bedre sikkerhet og logging (gdpr = mindre lekkasje av persondata)

# sender riktig header tilbake så nettleser skjønner responsen
echo "Content-Type: text/plain; charset=utf-8"
echo

# støtter nå både GET og POST, før var det bare POST
if [ "$REQUEST_METHOD" != "POST" ] && [ "$REQUEST_METHOD" != "GET" ]; then
  echo "Feil metode: $REQUEST_METHOD" >&2
  exit 0
fi

# workaround for kjent bug med content-length fra server
CONTENT_LENGTH=$HTTP_CONTENT_LENGTH$CONTENT_LENGTH

# leser body kun hvis det faktisk er POST
if [ "$REQUEST_METHOD" = "POST" ]; then
  KROPP=$(head -c "$CONTENT_LENGTH")
else
  KROPP=""
fi

# enkel decoding av URL-data (litt bedre enn originalen) (gdpr = korrekt behandling av inputdata)
urldecode() {
  printf '%s' "$1" | sed 's/+/ /g; s/%40/@/g'
}

# escaper spesialtegn så vi unngår XML injection (gdpr = hindrer manipulering av lagret data)
xml_escape() {
  printf '%s' "$1" | sed \
    -e 's/&/\&amp;/g' \
    -e 's/</\&lt;/g' \
    -e 's/>/\&gt;/g' \
    -e 's/"/\&quot;/g' \
    -e "s/'/\&apos;/g"
}

# masker epost før logging så vi ikke lekker data (gdpr = anonymisering i logger)
mask_email() {
  printf '%s' "$1" | sed 's/^\(.\).*\(@.*\)$/\1***\2/; t; s/.*/***/'
}

# parser input på en tryggere måte enn før (ikke cut/for loop) (gdpr = mindre risiko for feil håndtering)
TMP="/tmp/body.$$"
printf '%s\n' "$KROPP" | tr '&' '\n' > "$TMP"

E="" P="" K="" O="" T="" X="" H=""

while IFS= read -r pair; do
  [ -z "$pair" ] && continue

  key=${pair%%=*}
  val=${pair#*=}
  val=$(urldecode "$val")

  case "$key" in
    epost) E="$val" ;;
    passord) P="$val" ;;
    kommentar) K="$val" ;;
    offentlig_nokkel) O="$val" ;;
    tittel) T="$val" ;;
    tekst) X="$val" ;;
    handling) H="$val" ;;
  esac
done < "$TMP"

# rydder opp temp-fil etter bruk (gdpr = unngår lagring av sensitiv data)
rm -f "$TMP"

# basic validering så vi ikke sender tom data videre (gdpr = dataminimering)
if [ -z "$E" ]; then
  echo "Epost mangler"
  exit 0
fi

# krever passord med mindre man bare lister
if [ "$H" != "Liste" ] && [ -z "$P" ]; then
  echo "Passord mangler"
  exit 0
fi

# logger request, men uten sensitiv info som før (gdpr = begrenser eksponering i logger)
MASKED_EMAIL=$(mask_email "$E")
echo "app: request mottatt - epost=$MASKED_EMAIL handling=$H" >&2

# escaper alt før vi sender det videre (nytt i min versjon) (gdpr = beskytter data før lagring/overføring)
E_ESC=$(xml_escape "$E")
P_ESC=$(xml_escape "$P")
K_ESC=$(xml_escape "$K")
O_ESC=$(xml_escape "$O")
T_ESC=$(xml_escape "$T")
X_ESC=$(xml_escape "$X")

# bygger XML til pseudonym-tjenesten med trygg data
XML_PN="<pseudonym>
<epost>${E_ESC}</epost>
<passord>${P_ESC}</passord>
</pseudonym>"

URL_PN="http://allpodd:83/cgi-bin/index.cgi"

# logger hva vi kaller, men fortsatt anonymisert (gdpr = skjuler identitet i logs)
echo "PN kall til: $URL_PN (masked=$MASKED_EMAIL)" >&2

# henter pseudonym basert på input
N=$(curl -s -d "$XML_PN" "$URL_PN") 


# stopper hvis vi ikke får noe tilbake
if [ -z "$N" ]; then
  echo "Pseudonym mangler!"
  exit 0
fi

# lager XML for bidrag-databasen med sanitert input (gdpr = trygg behandling av brukerdata)
XML_B="<bidrag>
<navn>$(xml_escape "$N")</navn>
<passord>${P_ESC}</passord>
<kommentar>${K_ESC}</kommentar>
<offentlig_nokkel>${O_ESC}</offentlig_nokkel>
<tittel>${T_ESC}</tittel>
<tekst>${X_ESC}</tekst>
<handling>${H}</handling>
</bidrag>"

URL_B="http://allpodd:82/cgi-bin/index.cgi"

# logger hvilken handling som kjøres
echo "BIDRAG kall til: $URL_B - handling=$H" >&2

# mye ryddigere enn originalen med if-if-if
case "$H" in

  Ny)
    curl -s -X POST -d "$XML_B" "$URL_B"
    ;;

  Endre)
    curl -s -X PUT -d "$XML_B" "$URL_B"
    ;;

  Slett)
    curl -s -X DELETE -d "$XML_B" "$URL_B"
    ;;

  Liste)
    curl -s "$URL_B"
    ;;

  Min)
    curl -s -X POST -d "$XML_B" "$URL_B" # Person 1 bruker POST fordi GET gir 404 i dette oppsettet
    ;;
  *)
    echo "Ukjent handling" >&2
    ;;
esac

exit 0
