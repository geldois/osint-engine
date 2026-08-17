#!/bin/bash
set -euo pipefail

# Docker via repositório oficial (não o docker.io do Ubuntu, que atrasa versão) — pin explícito e
# portável entre codenames Ubuntu via o padrão documentado pelo próprio Docker.
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# shellcheck source=/dev/null
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
  >/etc/apt/sources.list.d/docker.list

apt-get update

DOCKER_VERSION_STRING="5:29.5.3-1~ubuntu.${VERSION_ID}~${VERSION_CODENAME}"
apt-get install -y --no-install-recommends \
  docker-ce="${DOCKER_VERSION_STRING}" \
  docker-ce-cli="${DOCKER_VERSION_STRING}" \
  containerd.io \
  docker-compose-plugin \
  unattended-upgrades \
  fail2ban

usermod -aG docker ubuntu
systemctl enable --now docker
systemctl enable --now fail2ban

# unattended-upgrades: só patch de segurança, nunca reboot automático — um reboot inesperado
# perto da demo é pior que um patch de kernel pendente até reboot manual.
echo 'Unattended-Upgrade::Automatic-Reboot "false";' \
  >/etc/apt/apt.conf.d/51unattended-upgrades-osint-engine

# Rotação de log do Docker — sem isso o log dos containers cresce sem limite.
mkdir -p /etc/docker
cat >/etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF
systemctl restart docker

# Clona o repo, gera .env uma única vez — nada aqui é tocado de novo por nenhum deploy futuro.
git clone https://github.com/geldois/osint-engine.git /opt/osint-engine
chown -R ubuntu:ubuntu /opt/osint-engine
cd /opt/osint-engine

POSTGRES_PASSWORD_GENERATED=$(openssl rand -hex 32)
# EXTERNAL_CREDENTIAL_ENCRYPTION_KEY precisa ser uma chave Fernet válida (32 bytes url-safe
# base64), não hex — openssl rand -base64 32 mais a tradução pro alfabeto url-safe é o
# equivalente shell de Fernet.generate_key().
FERNET_KEY_GENERATED=$(openssl rand -base64 32 | tr '+/' '-_')
ADMIN_PASSWORD_GENERATED=$(openssl rand -hex 16)
cat >.env <<EOF
SECRET_KEY=$(openssl rand -hex 32)
EXTERNAL_CREDENTIAL_ENCRYPTION_KEY=${FERNET_KEY_GENERATED}
POSTGRES_USER=osint_engine
POSTGRES_PASSWORD=${POSTGRES_PASSWORD_GENERATED}
POSTGRES_DB=osint_engine
DATABASE_URL=postgresql://osint_engine:${POSTGRES_PASSWORD_GENERATED}@postgres:5432/osint_engine
ADMIN_PASSWORD=${ADMIN_PASSWORD_GENERATED}
CORS_ORIGINS=https://osint.angelitochagas.com
API_DOMAIN=api.osint.angelitochagas.com
IMAGE_TAG=
EOF
chown ubuntu:ubuntu .env
chmod 600 .env

# IMAGE_TAG fica vazio de propósito — o cloud-init não sobe a stack. A primeira subida
# (com a tag real da imagem já publicada no GHCR) é o passo manual seguinte do runbook de
# provisionamento, na mesma sessão SSH em que ADMIN_PASSWORD é revisado.
