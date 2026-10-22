#!/usr/bin/env bash
set -Eeuo pipefail
cd "$HOME/cloud-team-project"
mkdir -p "$HOME/cloud-lab7-evidence"
exec > >(tee "$HOME/cloud-lab7-evidence/07-docker-checks.txt") 2>&1
printf '\nLab 7 started: %s\n' "$(date -Is)"
echo '=== Git commit ==='
git rev-parse HEAD
echo '=== Install and check Docker ==='
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker --version
sudo docker run --rm hello-world
echo '=== Build ==='
sudo docker build --progress=plain -t cloud-catalog:v1 .
sudo docker images cloud-catalog
echo '=== Run ==='
if sudo docker container inspect cloud-catalog-docker >/dev/null 2>&1; then
  sudo docker rm -f cloud-catalog-docker
fi
sudo docker run -d --name cloud-catalog-docker --restart unless-stopped --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges:true -p 8080:5000 -e APP_TITLE='Cloud Service Catalog Docker' cloud-catalog:v1
sudo docker ps --filter name=cloud-catalog-docker
echo '=== HTTP checks from VM ==='
curl --retry 10 --retry-all-errors --retry-delay 1 -fsS -i http://127.0.0.1:8080/
curl -fsS -i http://127.0.0.1:8080/health
curl -fsS -i http://127.0.0.1:8080/api/services
python3 - <<'PYTHON'
import json, urllib.request
with urllib.request.urlopen('http://127.0.0.1:8080/api/services', timeout=10) as response:
    catalog = json.load(response)
assert {s['model'] for s in catalog['services']} == {'IaaS','PaaS','SaaS'}
print('PASS: all three cloud models returned')
PYTHON
echo '=== Docker logs and user ==='
sudo docker logs cloud-catalog-docker
sudo docker inspect --format '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' cloud-catalog-docker
sudo docker exec cloud-catalog-docker id
echo '=== Stop and restart ==='
sudo docker stop cloud-catalog-docker
sudo docker start cloud-catalog-docker
curl --retry 10 --retry-all-errors --retry-delay 1 -fsS http://127.0.0.1:8080/health
sudo docker ps --filter name=cloud-catalog-docker
echo 'LAB 7 SUCCESS: image built; container started, checked, stopped and restarted.'
