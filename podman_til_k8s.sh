#!/bin/sh

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR"

# start: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)
podman build -t localhost/pseudonym-db:latest pseudonym-db
podman build -t localhost/bidrag-db:latest bidrag-db
podman build -t localhost/app:latest app
podman build -t localhost/web:latest web

podman save localhost/pseudonym-db:latest | microk8s ctr image import -
podman save localhost/bidrag-db:latest | microk8s ctr image import -
podman save localhost/app:latest | microk8s ctr image import -
podman save localhost/web:latest | microk8s ctr image import -
# slutt: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)

# start: Rydder gamle runtime-objekter uten å røre databasedata - oppfyller NF7 (recovery) og bevarer PVC-er (person 4)
microk8s kubectl delete pod web app bidrag-db pseudonym-db --ignore-not-found
microk8s kubectl delete service web app bidrag-db pseudonym-db --ignore-not-found
microk8s kubectl delete networkpolicy --all --ignore-not-found
# slutt: Rydder gamle runtime-objekter uten å røre databasedata - oppfyller NF7 (recovery) og bevarer PVC-er (person 4)

# start: Bruker kuraterte manifestfiler - oppfyller NF1 (kontrollert konfigurasjon), NF2 (Kubernetes) og deler av NF7 (recovery) (person 4)
microk8s kubectl apply -f k8s/pvc.yaml
microk8s kubectl apply -f k8s/rbac.yaml

microk8s kubectl apply -f allpodd.yaml

microk8s kubectl wait --for=condition=Ready pod/web --timeout=180s
microk8s kubectl wait --for=condition=Ready pod/app --timeout=180s
microk8s kubectl wait --for=condition=Ready pod/bidrag-db --timeout=180s
microk8s kubectl wait --for=condition=Ready pod/pseudonym-db --timeout=180s

microk8s kubectl apply -f k8s/networkpolicy.yaml
# slutt: Bruker kuraterte manifestfiler - oppfyller NF1 (kontrollert konfigurasjon), NF2 (Kubernetes) og deler av NF7 (recovery) (person 4)

echo
echo "Ferdig."
echo "Web: http://localhost:8080"
echo "App: http://localhost:8081"

echo
echo "Start port-forward i to egne terminaler:"
echo "microk8s kubectl port-forward service/web 8080:80"
echo "microk8s kubectl port-forward service/app 8081:81"