#!/usr/bin/env bash
set -euo pipefail

# User sets these
: "${GEANT4_PREFIX:?Set GEANT4_PREFIX (install location)}"
: "${GEANT4_VERSION:=10.07.p03}"  # Geant4 10.7.3 patch-03
: "${GEANT4_SRC_NAME:=geant4.10.07.p03}"
: "${GEANT4_TARBALL:=geant4.10.07.p03.tar.gz}"

# If already installed, do nothing
if [[ -f "${GEANT4_PREFIX}/bin/geant4.sh" ]]; then
  echo "Geant4 already present at: ${GEANT4_PREFIX}"
  echo "Found: ${GEANT4_PREFIX}/bin/geant4.sh"
  exit 0
fi

echo "Installing Geant4 into: ${GEANT4_PREFIX}"
mkdir -p "${GEANT4_PREFIX}"

# Build in /tmp
WORKDIR=/tmp/geant4_build
SRCROOT=/tmp/geant4_src
rm -rf "${WORKDIR}" "${SRCROOT}"
mkdir -p "${WORKDIR}" "${SRCROOT}"

cd "${SRCROOT}"
echo "Downloading ${GEANT4_TARBALL} ..."
wget -q "https://geant4-data.web.cern.ch/releases/${GEANT4_TARBALL}"
tar -xzf "${GEANT4_TARBALL}"

cd "${WORKDIR}"
cmake -DCMAKE_INSTALL_PREFIX="${GEANT4_PREFIX}" \
      -DGEANT4_INSTALL_DATA=ON \
      -DGEANT4_USE_SYSTEM_EXPAT=ON \
      -DGEANT4_USE_SYSTEM_ZLIB=ON \
      -DGEANT4_BUILD_MULTITHREADED=ON \
      "${SRCROOT}/${GEANT4_SRC_NAME}"

make -j"$(nproc)"
make install

echo "Installed Geant4 into ${GEANT4_PREFIX}"
echo "Check: ${GEANT4_PREFIX}/bin/geant4.sh"
