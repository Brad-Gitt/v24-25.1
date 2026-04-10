# Innhold og visninger for bidrag-db (Person 2)

## Funksjonelle krav

### F1 – offentlig tittel/tekst, privat kommentar
- `GET` uten parametere returnerer bare `tittel` og `tekst`.
- `kommentar` returneres **ikke** i offentlig eller administrativ liste.
- `kommentar` returneres bare i `visning=min`, etter vellykket autentisering med `pseudonym + passord`.

### F2 – offentlig visning anonym, admin-visning pseudonym
- Offentlig visning: `GET /cgi-bin/index.cgi`
  - viser bare `tittel` og `tekst`
  - ingen e-post
  - ingen pseudonym
  - ingen kommentar
- Admin-visning: `GET /cgi-bin/index.cgi?visning=admin`
  - viser `pseudonym`, `tittel` og `tekst`
  - viser fortsatt **ikke** kommentar
- Min visning: `GET /cgi-bin/index.cgi?visning=min&navn=<pseudonym>&passord=<passord>`
  - viser eget `pseudonym`, `tittel`, `tekst` og `kommentar`
  - brukes for å oppfylle kravet om at brukerens egen kommentar skal være tilgjengelig for brukeren selv

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

## API

### Opprette bidrag
- `POST`
- krever `navn`, `passord`, og minst ett av `tittel` eller `tekst`
- oppretter rad for nytt pseudonym

### Endre bidrag
- `PUT`
- autentiserer med `navn + passord`
- oppdaterer `kommentar`, `offentlig_nokkel`, `tittel`, `tekst`

### Slette bidrag
- `DELETE`
- autentiserer med `navn + passord`
- sletter bare eget bidrag

### Liste ut bidrag
- `GET` → offentlig anonym liste
- `GET ?visning=admin` → pseudonymisert adminliste
- `GET ?visning=min&navn=...&passord=...` → brukerens egen visning

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
curl -s "http://localhost:8082/cgi-bin/index.cgi?visning=admin"
```
Forventning:
- ser `pseudonym`, `tittel`, `tekst`
- ser ikke `kommentar`

### 3. Egen visning
Kjør:
```sh
curl -s "http://localhost:8082/cgi-bin/index.cgi?visning=min&navn=osiedahs&passord=123"
```
Forventning:
- ser eget `pseudonym`
- ser `tittel`, `tekst`, `kommentar`

### 4. Integritet / input-validering
Prøv å sende inn for lang `tittel` eller `tekst`.
Forventning:
- backend avviser forespørselen
- data lagres ikke

