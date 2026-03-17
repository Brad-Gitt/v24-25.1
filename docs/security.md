# Kryptering, Nøkkelhåndtering og Sikkerhet (NF7)

## Kryptering
- **I transit**: Bruk TLS 1.3 for all kommunikasjon (web ↔ app ↔ db).
- **At rest**: Krypter SQLite-databaser med SQLCipher eller lignende. Bruk Kubernetes secrets for krypteringsnøkler.
- **Passord**: SHA-256 med salt, lagret som hash.

## Nøkkelhåndtering
- **Generering**: Bruk Kubernetes Certificate Manager for TLS-sertifikater.
- **Lagring**: Secrets i K8s for private nøkler, aldri i kode.
- **Rotasjon**: Automatisk rotasjon av nøkler hvert 90 dager.
- **Backup**: Encrypted backups av nøkler i secure vault.

## Inventar over Sårbarheter
- **SQLite**: Ingen SQL injection – bruk prepared statements (implisitt i xmllint).
- **CGI**: Begrenset input, ingen shell injection.
- **Container**: Alpine-basert, oppdaterte pakker, ingen root-tilgang.
- **K8s**: RBAC, network policies for isolasjon.

## Deteksjon og Recovery
- **Logging**: Alle forespørsler logges til stderr, send til ELK-stack.
- **Overvåking**: Prometheus for metrics, alerting på unormal aktivitet.
- **Intrusion Detection**: Bruk Falco for runtime-sikkerhet.
- **Recovery**: Automatiske backups av PVC-er, disaster recovery-plan med RTO/RPO.

## Implementasjon i Kode/K8s
- Kode: Legg til TLS i httpd, krypter db-filer.
- K8s: Ingress med TLS, secrets for nøkler, network policies.

# start: dokumentasjon lagt til (person 5)
# slutt: dokumentasjon lagt til (person 5)