# Innhold og visninger for bidrag-db (Person 2)

## Funksjonelle krav

### F1 – offentlig tittel/tekst, privat kommentar
- `GET` uten parametere returnerer bare `tittel` og `tekst`.
- `kommentar` returneres **ikke** i offentlig eller administrativ liste.
- `kommentar` returneres bare i `visning=min`, etter vellykket autentisering med `pseudonym + passord`.
- `visning=min` returnerer også `offentlig_nokkel`-metadata slik at frontend kan dekryptere kommentar for brukeren selv.
- Nye og endrede kommentarer skal lagres som ciphertext når de sendes fra frontend.

### F2 – offentlig visning anonym, admin-visning pseudonym
- Offentlig visning: `GET /cgi-bin/index.cgi`
  - viser bare `tittel` og `tekst`
  - ingen e-post
  - ingen pseudonym
  - ingen kommentar
- Admin-visning: via `Admin`-handling i `app/index.cgi`, eller `GET /cgi-bin/index.cgi?visning=admin&navn=admin&epost=...&passord=...`
  - viser `pseudonym`, `tittel` og `tekst`
  - viser fortsatt **ikke** kommentar
  - krever gyldig admin-bruker fra pseudonym-databasen
- Min visning: `POST handling=Min` via `app/index.cgi`, eller `GET /cgi-bin/index.cgi?visning=min&navn=<pseudonym>&passord=<passord>`
  - returnerer `tittel`, `tekst`, `kommentar` og `offentlig_nokkel`
  - brukes av frontend for å vise brukerens egen private kommentar igjen

## Ikke-funksjonelle krav

### NF1 – lagringsbegrensning og integritet i backend
Backend validerer feltene eksplisitt før lagring:
- `pseudonym <= 200`
- `tittel <= 100`
- `kommentar <= 1000`
- `tekst <= 1000`
- `offentlig_nokkel <= 200`

I tillegg håndheves følgende:
- minst ett av `tittel` eller `tekst` må være satt
- SQL-strenger escapes før de settes inn i SQLite-spørringer
- logging inneholder bare metadata om felter finnes eller ikke, ikke selve innholdet
- kommentar kan ikke lagres uten gyldig krypteringsmetadata i steg 7

## API

### Opprette bidrag
- `POST`
- krever `navn`, `passord`, og minst ett av `tittel` eller `tekst`
- krever at `kommentar` enten er tom, eller sendes som ciphertext med metadata
- oppretter rad for nytt pseudonym

### Endre bidrag
- `PUT`
- autentiserer med `navn + passord`
- oppdaterer `kommentar`, `offentlig_nokkel`, `tittel`, `tekst`
- krever at `kommentar` enten er tom, eller sendes som ciphertext med metadata

### Slette bidrag
- `DELETE`
- autentiserer med `navn + passord`
- sletter bare eget bidrag

### Liste ut bidrag
- `GET` → offentlig anonym liste
- `GET ?visning=admin&navn=admin&epost=...&passord=...` eller `POST handling=Admin` via app → pseudonymisert adminliste for admin
- `GET ?visning=min&navn=...&passord=...` eller `POST handling=Min` via app → brukerens egen visning med metadata for frontend-dekryptering

## Testforslag

### 1. Offentlig anonym liste
Kjør:
```sh
curl -s http://localhost:8082/cgi-bin/index.cgi
```
Forventning:
- ser `tittel` og `tekst`
- ser ikke `kommentar`
- ser ikke `pseudonym`

### 2. Adminliste
Kjør:
```sh
curl -s "http://localhost:8082/cgi-bin/index.cgi?visning=admin&navn=admin&epost=mikke@gmail.com&passord=123"
```
Forventning:
- ser `pseudonym`, `tittel`, `tekst`
- ser ikke `kommentar`

### 3. Egen visning
Kjør:
```sh
curl -s -X POST -d "<bidrag><navn>osiedahs</navn><passord>123</passord><handling>Min</handling></bidrag>" http://localhost:8082/cgi-bin/index.cgi
```
Forventning:
- ser XML med `tittel`, `tekst`, `kommentar` og `offentlig_nokkel`
- frontend kan bruke dette til å dekryptere kommentar

### 4. Integritet / input-validering
Prøv å sende inn kommentar uten `offentlig_nokkel`.
Forventning:
- backend avviser forespørselen
- data lagres ikke
