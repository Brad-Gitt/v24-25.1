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
podman save localhost/bidrag-db:latest | microk8s ctr image import -
podman save localhost/app:latest | microk8s ctr image import -
podman save localhost/web:latest | microk8s ctr image import -

echo "== Rydder runtime (uten å slette data) =="

microk8s kubectl delete deployment web -n webrom --ignore-not-found
microk8s kubectl delete deployment app -n approm --ignore-not-found
microk8s kubectl delete deployment bidrag-db -n bidragsrom --ignore-not-found
microk8s kubectl delete deployment pseudonym-db -n pseudonymrom --ignore-not-found

microk8s kubectl delete service web -n webrom --ignore-not-found
microk8s kubectl delete service app -n approm --ignore-not-found
microk8s kubectl delete service bidrag-db -n bidragsrom --ignore-not-found
microk8s kubectl delete service pseudonym-db -n pseudonymrom --ignore-not-found

microk8s kubectl delete networkpolicy --all -A --ignore-not-found

echo "== Setter opp system =="

# viktig: namespaces først
microk8s kubectl apply -f k8s/namespaces.yaml

# storage (bevarer data hvis finnes)
microk8s kubectl apply -f k8s/pvc-bidrag.yaml
microk8s kubectl apply -f k8s/pvc-pseudonym.yaml
# RBAC
microk8s kubectl apply -f k8s/roles.yaml
microk8s kubectl apply -f k8s/rolebindings.yaml

# deployments
microk8s kubectl apply -f k8s/deployments.yaml

# vent på pods
echo "== Venter på pods =="

sleep 5

microk8s kubectl wait --for=condition=available deployment/web -n webrom --timeout=180s
microk8s kubectl wait --for=condition=available deployment/app -n approm --timeout=180s
microk8s kubectl wait --for=condition=available deployment/bidrag-db -n bidragsrom --timeout=180s
microk8s kubectl wait --for=condition=available deployment/pseudonym-db -n pseudonymrom --timeout=180s

# services
microk8s kubectl apply -f k8s/services.yaml

# network policies til slutt
microk8s kubectl apply -f k8s/networkpolicy.yaml

echo
echo "Ferdig."
echo

echo "Test:"
echo "Web: http://localhost:32199"
echo "App: http://localhost:30921"
echo
echo
echo
echo "kjør det vet å bruke"
echo
echo "terminal 1"
echo "kubectl port-forward -n webrom service/web 8080:80"
echo
echo "terminal 2"
echo "kubectl port-forward -n approm service/app 8081:81"
echo
echo "Avslutt med"
echo
echo "kill %1 %2 2>/dev/null"
echo "pkill -f port-forward"
echo 
echo "På gjensyn"
echo
