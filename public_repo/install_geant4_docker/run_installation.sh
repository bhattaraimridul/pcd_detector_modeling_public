#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /absolute/host/path/to/install/geant4"
  exit 1
fi

PREFIX="$1"

if [[ "${PREFIX:0:1}" != "/" ]]; then
  echo "ERROR: Please provide an absolute path (starts with /). Got: ${PREFIX}"
  exit 1
fi

IMAGE="geant4-installer:10.7.3"

echo "==> Building installer image: ${IMAGE}"
docker build -t "${IMAGE}" -f ./Dockerfile.geant4_installer .

echo "==> Installing Geant4 into host path: ${PREFIX}"
# Mount the *parent* (or the exact prefix) so container can write there.
# Mounting exact prefix is simplest.
mkdir -p "${PREFIX}"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -e GEANT4_PREFIX="${PREFIX}" \
  -v "${PREFIX}:${PREFIX}" \
  "${IMAGE}" \
  "/install_geant4.sh"

echo "Geant4 Installation Done!!!"
