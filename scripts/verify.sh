#!/bin/sh

set -eu

# start: Steg 9-verifikasjon av sluttleveransen - oppfyller F1, F2, F3, NF1, NF2, NF3, NF4, NF5, NF6 og NF7 (person 4 og person 5)
for file in \
  app/index.cgi \
  bidrag-db/index.cgi \
  pseudonym-db/index.cgi \
  bidrag-db/init-encrypted-db.sh \
  pseudonym-db/init-encrypted-db.sh \
  podman_til_k8s.sh
do
  sh -n "$file"
done

for manifest in \
  k8s/pvc.yaml \
  k8s/rbac.yaml \
  k8s/networkpolicy.yaml \
  allpodd.yaml
do
  microk8s kubectl apply --dry-run=client -f "$manifest" >/dev/null
done

for doc in \
  docs/rapport.md \
  docs/presentasjon.md \
  docs/threat-model.md \
  docs/cloud-deploy.md \
  docs/testplan.md \
  docs/demo-checklist.md \
  docs/arbeidsfordeling.md \
  docs/demo-status.md
do
  test -f "$doc"
done

grep -q "Steg 9" docs/arbeidsfordeling.md
grep -q "Steg 9" docs/demo-status.md
grep -q "allpodd-storage-secrets" allpodd.yaml
grep -q "allpodd-tls" allpodd.yaml
test -f tls-gateway/Dockerfile
test -f tls-gateway/nginx.conf

echo "Steg 9-verifikasjon ok."
# slutt: Steg 9-verifikasjon av sluttleveransen - oppfyller F1, F2, F3, NF1, NF2, NF3, NF4, NF5, NF6 og NF7 (person 4 og person 5)
