#!/usr/bin/env bash
set -euo pipefail

# default install location: <current_dir>/geant4
DEFAULT_PREFIX="$(pwd)/geant4"

# --- parse input ---
if [[ $# -eq 0 ]]; then
  PREFIX="${DEFAULT_PREFIX}"
  echo "No install path provided."
  echo "Using default: ${PREFIX}"
elif [[ $# -eq 1 ]]; then
  PREFIX="$1"
else
  echo "Usage: $0 [/absolute/host/path/to/install/geant4]"
  exit 1
fi

# --- ensure absolute path ---
if [[ "${PREFIX:0:1}" != "/" ]]; then
  echo "ERROR: Install path must be absolute."
  echo "Got: ${PREFIX}"
  exit 1
fi

IMAGE="geant4-installer:10.7.3"

echo "==> Building installer image: ${IMAGE}"
docker build -t "${IMAGE}" -f ./Dockerfile.geant4_installer .

echo "==> Installing Geant4 into host path: ${PREFIX}"
mkdir -p "${PREFIX}"

docker run --rm \
  --user "$(id -u):$(id -g)" \
  -e GEANT4_PREFIX="${PREFIX}" \
  -v "${PREFIX}:${PREFIX}" \
  "${IMAGE}" \
  "/install_geant4.sh"

echo
echo "Geant4 installation complete!"
echo "Installed at: ${PREFIX}"

