#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

echo "== Bygger images =="

podman build -t localhost/pseudonym-db:latest pseudonym-db
podman build -t localhost/bidrag-db:latest bidrag-db
podman build -t localhost/app:latest app
podman build -t localhost/web:latest web

echo "== Importerer images til microk8s =="

podman save localhost/pseudonym-db:latest | microk8s ctr image import -
podman save localhost/bidrag-db:latest    | microk8s ctr image import -
podman save localhost/app:latest          | microk8s ctr image import -
podman save localhost/web:latest          | microk8s ctr image import -

echo "== Rydder runtime (uten å slette data) =="

microk8s kubectl delete deployment web -n webrom --ignore-not-found
microk8s kubectl delete deployment app -n approm --ignore-not-found
microk8s kubectl delete deployment bidrag-db -n bidragsrom --ignore-not-found
microk8s kubectl delete deployment pseudonym-db -n pseudonymrom --ignore-not-found
microk8s kubectl delete deployment nginx-https -n webrom --ignore-not-found

microk8s kubectl delete service web -n webrom --ignore-not-found
microk8s kubectl delete service app -n approm --ignore-not-found
microk8s kubectl delete service bidrag-db -n bidragsrom --ignore-not-found
microk8s kubectl delete service pseudonym-db -n pseudonymrom --ignore-not-found
microk8s kubectl delete service nginx-https -n webrom --ignore-not-found

microk8s kubectl delete configmap nginx-conf -n webrom --ignore-not-found
microk8s kubectl delete secret nginx-certs -n webrom --ignore-not-found

microk8s kubectl delete networkpolicy --all -A --ignore-not-found

echo "== Setter opp system =="

# namespaces først
microk8s kubectl apply -f k8s/namespaces.yaml

# storage (bevarer data hvis PVC-ene allerede finnes)
microk8s kubectl apply -f k8s/pvc-bidrag.yaml
microk8s kubectl apply -f k8s/pvc-pseudonym.yaml

# RBAC
microk8s kubectl apply -f k8s/roles.yaml
microk8s kubectl apply -f k8s/rolebindings.yaml

# services før deployments, slik at navnene finnes når nginx starter
microk8s kubectl apply -f k8s/services.yaml

# deployments
microk8s kubectl apply -f k8s/deployments.yaml

echo "== Venter på applikasjons-poddene =="

sleep 5

microk8s kubectl wait --for=condition=available deployment/web -n webrom --timeout=180s
microk8s kubectl wait --for=condition=available deployment/app -n approm --timeout=180s
microk8s kubectl wait --for=condition=available deployment/bidrag-db -n bidragsrom --timeout=180s
microk8s kubectl wait --for=condition=available deployment/pseudonym-db -n pseudonymrom --timeout=180s

echo "== Starter HTTPS-inngangen =="

microk8s kubectl apply -f nginx-https.yaml
microk8s kubectl wait --for=condition=available deployment/nginx-https -n webrom --timeout=180s

# network policies til slutt, når alt annet er oppe
microk8s kubectl apply -f k8s/networkpolicy.yaml

echo
echo "Ferdig."
echo
echo "Normal test går via HTTPS-inngangen:"
echo "  https://localhost:4430"
echo
echo "Start den i en egen terminal:"
echo "  microk8s kubectl port-forward -n webrom service/nginx-https 4430:443"
echo
echo "Hvis du vil feilsøke interne tjenester direkte, kan du bruke:"
echo "  microk8s kubectl port-forward -n webrom service/web 8080:80"
echo "  microk8s kubectl port-forward -n approm service/app 8081:81"
echo
echo "Stopp port-forward med Ctrl-C i terminalen som kjører den."
echo
echo "På gjensyn"