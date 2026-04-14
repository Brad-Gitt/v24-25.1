# Kryptering, Nøkkelhåndtering og Sikkerhet (NF7)

<!-- start: Status etter steg 8 for Kubernetes-hardening - oppfyller NF1, NF2 og deler av NF7 (person 4) -->
## Status etter steg 8
- `allpodd.yaml` er nå herdet med `securityContext`, `readOnlyRootFilesystem`, `capabilities.drop`, `seccompProfile`, `requests`, `limits` og health probes.
- `k8s/rbac.yaml` oppretter dedikert `ServiceAccount` uten API-token og binder den til en rolle uten API-privilegier.
- `k8s/networkpolicy.yaml` begrenser den ytre angrepsflaten til bare web- og app-portene.
- `k8s/pvc.yaml` brukes sammen med `initContainers` for å seed-e og bevare databasene på persistente volum, og SQLite får egne skrivbare PVC-mapper selv om root-filsystemet er read-only.
- Containerne bruker høye interne porter for å kunne kjøre som non-root i Kubernetes.
- Intern trafikk mellom `app`, `bidrag-db` og `pseudonym-db` går over loopback i samme pod for å redusere avhengighet til tjeneste-DNS inne i podden.
<!-- slutt: Status etter steg 8 for Kubernetes-hardening - oppfyller NF1, NF2 og deler av NF7 (person 4) -->

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
