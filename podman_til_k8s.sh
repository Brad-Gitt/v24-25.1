#!/bin/sh

set -eu

# start: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)
podman build pseudonym-db -t localhost/pseudonym-db:latest
podman build bidrag-db    -t localhost/bidrag-db:latest
podman build app          -t localhost/app:latest
podman build web          -t localhost/web:latest

podman save localhost/pseudonym-db:latest | microk8s ctr image import -
podman save localhost/bidrag-db:latest    | microk8s ctr image import -
podman save localhost/app:latest          | microk8s ctr image import -
podman save localhost/web:latest          | microk8s ctr image import -
# slutt: Bygger og importerer lokale bilder for herdede Kubernetes-manifester - oppfyller NF2 (Kubernetes) og NF3 (lokal utvikling med Podman og microk8s) (person 4)

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
echo "Gjør web (80) og app (81) tilgjengelig på localhost:"
echo
echo "microk8s kubectl port-forward service/allpodd 8080:80 8081:81"
echo
echo "For å se i nettleser, gå til http://localhost:8080"
