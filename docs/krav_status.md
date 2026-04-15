# Kravstatus mot dagens kodebase

Oppdatert: 2026-04-15

Denne vurderingen er basert på den faktiske kodebasen i WSL-repoet slik den ser ut nå. Ved konflikt mellom kode og eldre dokumentasjon er kode og manifester vurdert som fasit.

## Markering
- Fullført: kravet er dekket i dagens kode, manifester eller dokumentasjon.
- Delvis: deler av kravet er dekket, men det finnes tydelige mangler.
- Ikke fullført: kravet er ikke reelt implementert eller dokumentert godt nok.

## Funksjonelle krav

| Krav | Status | Vurdering | Grunnlag |
| --- | --- | --- | --- |
| FK-01 | Fullført | Tittel og tekst er offentlige. Kommentar vises ikke i offentlig eller admin-visning. Kommentar krypteres i nettleseren og dekrypteres bare i Min-visning for riktig bruker. | web/crypto.js, app/index.cgi, bidrag-db/index.cgi |
| FK-02 | Fullført | Offentlig visning skjuler e-post og pseudonym. Admin-visning viser pseudonym, men ikke e-post. E-post og pseudonym holdes atskilt i egne databaser. | web/crypto.js, app/index.cgi, bidrag-db/index.cgi, pseudonym-db/index.cgi |
| FK-03 | Fullført | Persistens er satt opp med PVC-er for bidrag.db og pseudonym.db, og data seedes inn igjen bare når volumet er tomt. | k8s/pvc.yaml, allpodd.yaml |

## Ikke-funksjonelle krav

| Krav | Status | Vurdering | Grunnlag |
| --- | --- | --- | --- |
| IFK-01 | Delvis | Least privilege og defense in depth er godt dekket i Kubernetes-oppsettet. Zero trust og GDPR-prinsippene er bare delvis dekket: intern kommunikasjon i samme pod stoler fortsatt mye på loopback, og lagringsbegrensning er ikke implementert som reell mekanisme. | allpodd.yaml, k8s/rbac.yaml, k8s/networkpolicy.yaml, app/index.cgi, docs/infra.md |
| IFK-02 | Fullført | Løsningen er orkestrert med Kubernetes-manifester for service, pod, PVC, RBAC og network policy. | allpodd.yaml, k8s/*.yaml |
| IFK-03 | Fullført | Lokal utvikling med MicroK8s og Podman er tydelig støttet gjennom bygg og deploy-script og verify-script. | podman_til_k8s.sh, scripts/verify.sh |
| IFK-04 | Fullført | Det finnes cloud deploy-plan og beskrivelse av ansvar mellom aktører. Dette er dokumentasjonskravet, ikke full skyimplementasjon. | docs/cloud-deploy.md, docs/deploy-plan.md |
| IFK-05 | Delvis | Aktører, verdier og tillitsgrenser er beskrevet, men inventaret er ikke like eksplisitt og komplett for compute-, storage- og network-assets som kravet legger opp til. | docs/actors-trust.md, docs/threat-model.md |
| IFK-06 | Delvis | Labels er implementert bredt i Kubernetes-manifestene, men det finnes ikke en tydelig egen label-policy som forklarer format, regler og bruk samlet. | allpodd.yaml, k8s/pvc.yaml, k8s/rbac.yaml, k8s/networkpolicy.yaml |
| IFK-07 | Delvis | Kommentar krypteres i klient og passord hashes med salt. Men TLS, kryptering av databaser at rest, moden nøkkelhåndtering, full asset inventory, reell deteksjonsovervåking og backup og restore er ikke fullt implementert i dagens branch. | web/crypto.js, bidrag-db/index.cgi, pseudonym-db/index.cgi, docs/security.md, docs/frontend-crypto.md, docs/infra.md |

## Detaljer for delvise krav

### IFK-01
- IFK-01.1 minste privilegium: stort sett fullført med runAsNonRoot, readOnlyRootFilesystem, droppede capabilities og servicekonto uten API-token.
- IFK-01.2 forsvar i dybden: stort sett fullført med flere lag i frontend, app, databaser og Kubernetes.
- IFK-01.3 zero trust: delvis. Appen autentiserer brukere og admin, men interne komponenter i samme pod er fortsatt tett koblet og har ikke sterk gjensidig verifikasjon.
- IFK-01.4 dataminimering: delvis til godt dekket. Offentlig visning lekker ikke e-post, og logger maskerer e-post. Samtidig lagres fortsatt nødvendige persondata lokalt uten egen retention-mekanisme.
- IFK-01.5 langtidsbegrensning: ikke reelt implementert. Det finnes ingen automatisk sletting, TTL eller dokumentert retention-policy i kode eller manifester.
- IFK-01.6 integritet og konfidensialitet: delvis. Hashing, klientkryptering og tilgangskontroll finnes, men dagens branch mangler TLS og databasekryptering at rest.

### IFK-05
- Det finnes beskrivelser av aktører, verdier og trust boundaries.
- Det mangler en mer systematisk oversikt som eksplisitt dekker compute-, storage- og network-assets samlet.

### IFK-06
- Labeling er brukt i praksis.
- En samlet policy-fil som sier hvilke label-nøkler som skal brukes, hvorfor, og på hvilke asset-typer, mangler.

### IFK-07
- IFK-07.1 kryptering av data: delvis. Kommentar krypteres i frontend, men ikke hele datalageret.
- IFK-07.2 nøkkelhåndtering: delvis. Nøkkelen avledes i nettleseren fra e-post og passord, men det finnes ikke en full modell for opprettelse, rotasjon, backup og beskyttelse av nøkler.
- IFK-07.3 inventarføring av skyverdier: delvis. Dokumentasjon finnes, men ikke som komplett asset inventory.
- IFK-07.4 håndtering av sårbarheter: delvis. Herding er gjort, men ingen tydelig scanning- eller patch-rutine er implementert.
- IFK-07.5 deteksjon av brudd: delvis. Det finnes logging til stderr, men ikke full monitorering eller alerting i praksis.
- IFK-07.6 gjenopprettelse etter brudd: delvis. PVC og kontrollert oppstart finnes, men dokumentert og testet backup- og restore-løp mangler.

## Kort oppsummering

### Fullført nå
- FK-01
- FK-02
- FK-03
- IFK-02
- IFK-03
- IFK-04

### Delvis fullført nå
- IFK-01
- IFK-05
- IFK-06
- IFK-07

### Ikke fullført som egen hovedkategori
- Ingen hovedkrav er vurdert som helt fraværende, men flere ikke-funksjonelle krav er bare delvis dekket.
