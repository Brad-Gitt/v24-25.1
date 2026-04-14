# Cloud Deploy-Plan og Ansvar (NF4)

<!-- start: Operativ status etter steg 8 - oppfyller NF4 og støtter NF1/NF2 i drift (person 4) -->
## Operativ status etter steg 8
- Kubernetes-manifestene i repoet er nå kuraterte og herdede, og brukes direkte av `podman_til_k8s.sh`.
- Persistens, servicekonto uten API-token, RBAC uten privilegier, health probes, requests/limits og network policy er lagt inn i manifestene.
- Dette gjør at cloud-deploy-planen ikke lenger bare er teoretisk; grunnoppsettet er nå nærmere det som faktisk bør flyttes til en sky-klynge.
<!-- slutt: Operativ status etter steg 8 - oppfyller NF4 og støtter NF1/NF2 i drift (person 4) -->

## Oversikt
Dette dokumentet beskriver planen for cloud-deployment av Allpodd-systemet, inkludert shared responsibility-modellen og roller som controller/processor i henhold til GDPR.

## Shared Responsibility Model
- **Cloud Provider (f.eks. AWS/Azure)**: Ansvarlig for infrastruktur-sikkerhet, nettverk, fysiske servere, hypervisor.
- **Utvikler/Operatør (Controller)**: Ansvarlig for applikasjonskode, konfigurasjon, datahåndtering, tilgangskontroll, kryptering av data i transit/rest.
- **Bruker**: Ansvarlig for sine egne data, passord, tilgang.

## Controller/Processor Roller (GDPR Art. 4)
- **Controller**: Eieren av data (brukere som sender inn bidrag). Ansvarlig for formål, samtykke, rettigheter.
- **Processor**: Systemet (Allpodd) som behandler data på vegne av controller. Ansvarlig for sikker behandling, dataminimering.

## Deploy-Plan
1. **Lokal utvikling**: Bruk Podman/microk8s for testing.
2. **Cloud miljø**: Deploy til Kubernetes-cluster (f.eks. EKS/GKE) med PVC for persistens.
3. **CI/CD**: Bruk GitHub Actions eller lignende for automatisert bygg/deploy.
4. **Sikkerhet**: Implementer secrets for passord, TLS for kommunikasjon, RBAC for tilgang.
5. **Overvåking**: Bruk Prometheus/Grafana for logging og alerting.
6. **Backup/Recovery**: Automatiske snapshots av PVC-er.

## Risikoer og Tiltak
- **Data lekkasje**: Kryptering, tilgangskontroll.
- **Nedetid**: Multi-AZ deployment, load balancing.
- **GDPR-brudd**: Audit logs, dataportabilitet.

# start: dokumentasjon lagt til (person 5)
# slutt: dokumentasjon lagt til (person 5)
