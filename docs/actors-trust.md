# Aktører, Verdier og Tillitsgrenser (NF5)

## Aktører
- **Bruker**: Sender inn bidrag via web-skjema. Identifiseres via e-post, bruker pseudonym for anonymitet.
- **Admin**: Har tilgang til pseudonymer og kan se alle bidrag (unntatt kommentarer).
- **Utvikler**: Tilgang til kode og infrastruktur for vedlikehold.
- **Cloud Provider**: Tilgang til underliggende infrastruktur.

## Verdier
- **Konfidensialitet**: Kommentarer er private, kun for bruker. Offentlig nøkkel for kryptering.
- **Integritet**: Data hashes for passord, ingen uautorisert endring.
- **Tilgjengelighet**: Systemet må være oppe, med persistens for data.

## Tillitsgrenser
- **Bruker ↔ Web/App**: HTTPS/TLS for kryptering i transit.
- **App ↔ DB-er**: Intern kommunikasjon i Pod, ingen ekstern tilgang.
- **DB-er**: SQLite med fil-tilgang, begrenset til container.
- **Admin-tilgang**: Krever autentisering, separate grensesnitt.

## Trusselmodell
- **Eksterne trusler**: SQL injection, XSS – mitigert med input-validering.
- **Interne trusler**: Insider-angrep – least privilege, logging.
- **Datalekkasje**: Kryptering av sensitive data.

# start: dokumentasjon lagt til (person 5)
# slutt: dokumentasjon lagt til (person 5)