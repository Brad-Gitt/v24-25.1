# Frontend-kryptering av kommentar (Person 3)

Dette dokumentet beskriver steg 6 og steg 7 for klientside-kryptering av `kommentar`.

## Hva som er implementert

- `web/index.html` laster `crypto.js`.
- `web/crypto.js` krypterer `kommentar` i nettleseren ved handlingene `Ny` og `Endre`.
- Krypteringen bruker `AES-GCM`.
- Krypteringsnøkkelen avledes i nettleseren med `PBKDF2` fra `e-post + passord`.
- Tilfeldig `salt` og `iv` genereres per innsending.
- Selve ciphertext lagres i feltet `kommentar`.
- Krypteringsmetadata lagres i feltet `offentlig_nokkel`.
- Frontend sender ciphertext til backend med `fetch`, uten å erstatte det synlige kommentarfeltet med ciphertext.
- `Min` henter brukerens egen kommentar tilbake fra backend.
- Hvis kommentaren er kryptert, dekrypterer frontend den i nettleseren og fyller inn lesbar kommentar i skjemaet igjen.
- Hvis kommentaren er eldre klartekst uten metadata, vises den fortsatt som klartekst for bakoverkompatibilitet.

## Hvorfor dette hjelper

- Backend mottar ikke lenger kommentar i klartekst for nye og endrede bidrag.
- Offentlig liste og admin-visning viser fortsatt ikke `kommentar`.
- Brukeren selv kan nå hente og lese sin egen private kommentar igjen via `Min`.
- Kommentar-konfidensialitet er derfor gjennomført i den normale applikasjonsflyten.

## Begrensninger

- Kommentarfeltet er fortsatt begrenset til omtrent `700` byte i frontend, slik at ciphertext får plass i dagens backend-felt.
- Transportlaget bruker fortsatt vanlig HTTP i lokal demo. TLS hører til senere steg i prosjektet.

## Testforslag

1. Åpne nettsiden.
2. Fyll inn `e-post`, `passord`, `tittel`, `tekst` og `kommentar`.
3. Trykk `Ny`.
4. Bekreft at kommentarfeltet fortsatt viser lesbar tekst i skjemaet etter innsending.
5. Trykk `Min`.
6. Bekreft at `kommentar` fylles inn igjen som lesbar tekst for brukeren.
7. Bekreft at offentlig liste og admin-visning fortsatt ikke viser `kommentar`.
