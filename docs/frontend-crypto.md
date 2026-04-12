# Frontend-kryptering av kommentar (Person 3)

Dette dokumentet beskriver steg 6: klientside-kryptering av `kommentar` i frontend før data sendes til backend.

## Hva som er implementert

- `web/index.html` laster `crypto.js`.
- `web/crypto.js` krypterer `kommentar` i nettleseren ved handlingene `Ny` og `Endre`.
- Krypteringen bruker `AES-GCM`.
- Krypteringsnøkkelen avledes i nettleseren med `PBKDF2` fra `e-post + passord`.
- Tilfeldig `salt` og `iv` genereres per innsending.
- Selve ciphertext lagres i feltet `kommentar`.
- Krypteringsmetadata lagres i feltet `offentlig_nokkel`.

## Hvorfor dette hjelper

- Backend mottar ikke lenger kommentar i klartekst for nye og endrede bidrag.
- Offentlig liste og admin-visning viser fortsatt ikke `kommentar`.
- Kommentar-konfidensialitet er derfor styrket allerede i steg 6.

## Begrensninger i denne fasen

- `Min`-visningen er ikke tilpasset dekryptering ennå.
- En bruker vil derfor foreløpig se lagret ciphertext for nye eller endrede kommentarer.
- Dette er forventet frem til steg 7, der flyt og lagring skal tilpasses ciphertext fullt ut.
- Kommentar er midlertidig begrenset til omtrent `700` byte i frontend, slik at ciphertext fortsatt får plass i dagens backend-felt.

## Testforslag

1. Åpne nettsiden.
2. Fyll inn `e-post`, `passord`, `tittel`, `tekst` og `kommentar`.
3. Trykk `Ny`.
4. Bekreft i nettleseren at ingen krypteringsfeil vises.
5. Hent data via `Min`.
6. Bekreft at `kommentar` ikke lenger er lesbar klartekst, men lagret ciphertext.
