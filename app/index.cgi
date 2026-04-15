#!/bin/sh

# litt oppgradert CGI-script med bedre sikkerhet og logging (gdpr = mindre lekkasje av persondata)

# start: CORS-støtte for steg 7-klientflyt - oppfyller F1 (egen visning av privat kommentar) og NF1 (sikker og kontrollert frontend-flyt) (person 5)
echo "Access-Control-Allow-Origin: http://localhost:8080"
echo "Access-Control-Allow-Credentials: true"
echo "Access-Control-Allow-Methods: GET,POST,OPTIONS"
echo "Access-Control-Allow-Headers: Content-Type"
# slutt: CORS-støtte for steg 7-klientflyt - oppfyller F1 (egen visning av privat kommentar) og NF1 (sikker og kontrollert frontend-flyt) (person 5)

# sender riktig header tilbake så nettleser skjønner responsen
echo "Content-Type: text/plain; charset=utf-8"
echo

if [ "$REQUEST_METHOD" = "OPTIONS" ]; then
  exit 0
fi

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
  DATA=$(printf '%s' "$1" | sed 's/+/ /g; s/%/\\x/g')
  printf '%b' "$DATA"
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

# start: Bedre steg 4-brukerflyt og tilbakemeldinger - oppfyller F1 (identitet og flyt) og NF1 (dataminimering i flyt) (person 1 og person 3)
er_pseudonymfeil() {
  case "$1" in
    "Epost mangler!"|"Passord mangler!"|"Bruker finnes ikke!"|"Feil passord!")
      return 0
      ;;
  esac

  return 1
}

skriv_svar_eller_standardmelding() {
  SVAR="$1"
  STANDARDMELDING="$2"

  if [ -n "$SVAR" ]; then
    printf '%s\n' "$SVAR"
  else
    printf '%s\n' "$STANDARDMELDING"
  fi
}
# slutt: Bedre steg 4-brukerflyt og tilbakemeldinger - oppfyller F1 (identitet og flyt) og NF1 (dataminimering i flyt) (person 1 og person 3)

# start: Admin-routing med tilgangsbegrensning - oppfyller F2 (admin-visning med pseudonym) og NF1 (forsvar i dybden) (person 3 og person 5)
er_adminpseudonym() {
  [ "$1" = "admin" ]
}
# slutt: Admin-routing med tilgangsbegrensning - oppfyller F2 (admin-visning med pseudonym) og NF1 (forsvar i dybden) (person 3 og person 5)

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

# grunnleggende validering av handling før videre ruting
if [ -z "$H" ]; then
  echo "Handling mangler"
  exit 0
fi

# start: Intern ruting mellom separate pods via Kubernetes-service-navn - oppfyller NF1 (minste privilegium og redusert nettverksoverflate) og NF3 (stabil lokal kjøring i Kubernetes) (person 4)
URL_B_INTERNAL="${URL_B_INTERNAL:-http://bidrag-db.bidragsrom.svc.cluster.local:8082/cgi-bin/index.cgi}"
URL_PN_INTERNAL="${URL_PN_INTERNAL:-http://pseudonym-db.pseudonymrom.svc.cluster.local:8083/cgi-bin/index.cgi}"
# slutt: Intern ruting mellom separate pods via Kubernetes-service-navn - oppfyller NF1 (minste privilegium og redusert nettverksoverflate) og NF3 (stabil lokal kjøring i Kubernetes) (person 4)

# offentlig liste skal ikke kreve epost eller passord
if [ "$H" = "Liste" ]; then
  URL_B="$URL_B_INTERNAL"
  echo "BIDRAG kall til: $URL_B - handling=$H" >&2
  SVAR=$(curl -fsS "$URL_B" || true)
  skriv_svar_eller_standardmelding "$SVAR" "Ingen bidrag å vise."
  exit 0
fi

# basic validering så vi ikke sender tom data videre (gdpr = dataminimering)
if [ -z "$E" ]; then
  echo "Epost mangler"
  exit 0
fi

# krever passord for alle gjenværende steg 4-handlinger
if [ -z "$P" ]; then
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

URL_PN="$URL_PN_INTERNAL"

# logger hva vi kaller, men fortsatt anonymisert (gdpr = skjuler identitet i logs)
echo "PN kall til: $URL_PN (masked=$MASKED_EMAIL)" >&2

# henter pseudonym basert på input
if ! N=$(curl -fsS --max-time 10 -d "$XML_PN" "$URL_PN"); then
  echo "Kunne ikke nå pseudonym-tjenesten."
  exit 0
fi

if er_pseudonymfeil "$N"; then
  echo "$N"
  exit 0
fi

# stopper hvis vi ikke får noe tilbake
if [ -z "$N" ]; then
  echo "Pseudonym mangler!"
  exit 0
fi

if [ "$H" = "Admin" ] && ! er_adminpseudonym "$N"; then
  echo "Ingen tilgang til admin."
  exit 0
fi

# lager XML for bidrag-databasen med sanitert input (gdpr = trygg behandling av brukerdata)
XML_B="<bidrag>
<navn>$(xml_escape "$N")</navn>
<epost>${E_ESC}</epost>
<passord>${P_ESC}</passord>
<kommentar>${K_ESC}</kommentar>
<offentlig_nokkel>${O_ESC}</offentlig_nokkel>
<tittel>${T_ESC}</tittel>
<tekst>${X_ESC}</tekst>
<handling>${H}</handling>
</bidrag>"

URL_B="$URL_B_INTERNAL"

# logger hvilken handling som kjøres
echo "BIDRAG kall til: $URL_B - handling=$H" >&2

# mye ryddigere enn originalen med if-if-if
case "$H" in

  Ny)
    SVAR=$(curl -fsS -X POST -d "$XML_B" "$URL_B" || true)
    skriv_svar_eller_standardmelding "$SVAR" "Bidrag lagret."
    ;;

  Endre)
    SVAR=$(curl -fsS -X PUT -d "$XML_B" "$URL_B" || true)
    skriv_svar_eller_standardmelding "$SVAR" "Bidrag oppdatert."
    ;;

  Slett)
    SVAR=$(curl -fsS -X DELETE -d "$XML_B" "$URL_B" || true)
    skriv_svar_eller_standardmelding "$SVAR" "Bidrag slettet."
    ;;

  Min)
    SVAR=$(curl -fsS -X POST -d "$XML_B" "$URL_B" || true) # Person 1 bruker POST fordi GET gir 404 i dette oppsettet
    skriv_svar_eller_standardmelding "$SVAR" "Ingen data funnet for brukeren."
    ;;

  Admin)
    SVAR=$(curl -fsS -X POST -d "$XML_B" "$URL_B" || true)
    skriv_svar_eller_standardmelding "$SVAR" "Ingen bidrag å vise."
    ;;
  *)
    echo "Ukjent handling"
    ;;
esac

exit 0
