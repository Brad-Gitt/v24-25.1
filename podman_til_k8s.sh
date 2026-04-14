#!/bin/sh

set -eu

# start: Gjenbrukbare hemmeligheter og lokalt TLS-sertifikat i steg 9 - oppfyller NF1 (ingen hemmeligheter i repoet) og NF7 (TLS, nokkelhandtering og kryptering av data at rest) (person 4 og person 5)
TMPDIR=$(mktemp -d)

cleanup() {
  rm -rf "$TMPDIR"
}

trap cleanup EXIT
# slutt: Gjenbrukbare hemmeligheter og lokalt TLS-sertifikat i steg 9 - oppfyller NF1 (ingen hemmeligheter i repoet) og NF7 (TLS, nokkelhandtering og kryptering av data at rest) (person 4 og person 5)

# start: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)
podman build pseudonym-db -t localhost/pseudonym-db:latest
podman build bidrag-db    -t localhost/bidrag-db:latest
podman build app          -t localhost/app:latest
podman build web          -t localhost/web:latest
podman build tls-gateway  -t localhost/tls-gateway:latest

podman save localhost/pseudonym-db:latest | microk8s ctr image import -
podman save localhost/bidrag-db:latest    | microk8s ctr image import -
podman save localhost/app:latest          | microk8s ctr image import -
podman save localhost/web:latest          | microk8s ctr image import -
podman save localhost/tls-gateway:latest  | microk8s ctr image import -
# slutt: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)

# start: Aktiverer RBAC for manifester i steg 9 - oppfyller NF1 (least privilege) og NF2 (Kubernetes) (person 4 og person 5)
microk8s enable rbac
# slutt: Aktiverer RBAC for manifester i steg 9 - oppfyller NF1 (least privilege) og NF2 (Kubernetes) (person 4 og person 5)

# start: Oppretter og gjenbruker TLS- og lagringshemmeligheter i steg 9 - oppfyller NF1 (ingen hardkodede hemmeligheter) og NF7 (TLS, nokkelhandtering og kryptert lagring) (person 4 og person 5)
if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl mangler. Installer openssl og prov igjen."
  exit 1
fi

if ! microk8s kubectl get secret allpodd-storage-secrets >/dev/null 2>&1; then
  BIDRAG_DB_KEY=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 48)
  PSEUDONYM_DB_KEY=$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 48)

  microk8s kubectl create secret generic allpodd-storage-secrets \
    --from-literal=bidrag-db-key="$BIDRAG_DB_KEY" \
    --from-literal=pseudonym-db-key="$PSEUDONYM_DB_KEY"
fi

if ! microk8s kubectl get secret allpodd-tls >/dev/null 2>&1; then
  openssl req -x509 -nodes -newkey rsa:2048 \
    -keyout "$TMPDIR/tls.key" \
    -out "$TMPDIR/tls.crt" \
    -days 365 \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" >/dev/null 2>&1

  microk8s kubectl create secret tls allpodd-tls \
    --cert="$TMPDIR/tls.crt" \
    --key="$TMPDIR/tls.key"
fi
# slutt: Oppretter og gjenbruker TLS- og lagringshemmeligheter i steg 9 - oppfyller NF1 (ingen hardkodede hemmeligheter) og NF7 (TLS, nokkelhandtering og kryptert lagring) (person 4 og person 5)

# start: Bruker kuraterte manifestfiler i stedet for podman generate kube - oppfyller NF1 (kontrollert konfigurasjon), NF2 (Kubernetes) og deler av NF7 (recovery) (person 4)
microk8s kubectl apply -f k8s/pvc.yaml
microk8s kubectl apply -f k8s/rbac.yaml
microk8s kubectl apply -f k8s/networkpolicy.yaml

microk8s kubectl delete service/allpodd --ignore-not-found
microk8s kubectl delete pod/allpodd --ignore-not-found

microk8s kubectl apply -f allpodd.yaml
microk8s kubectl wait --for=condition=Ready pod/allpodd --timeout=180s
# slutt: Bruker kuraterte manifestfiler i stedet for podman generate kube - oppfyller NF1 (kontrollert konfigurasjon), NF2 (Kubernetes) og deler av NF7 (recovery) (person 4)

echo
echo "Gjor HTTPS-gatewayen tilgjengelig pa localhost:"
echo
echo "microk8s kubectl port-forward service/allpodd 8443:443"
echo
echo "For a se i nettleser, ga til https://localhost:8443"
