#!/usr/bin/env bash
# Instala Blender (LTS) y librerías de sistema necesarias para renderizar sin pantalla.
set -euo pipefail
BLENDER_VERSION="${BLENDER_VERSION:-4.2.3}"
BLENDER_DIR="${BLENDER_DIR:-/opt/blender}"
if [ ! -x "$BLENDER_DIR/blender" ]; then
  mkdir -p "$BLENDER_DIR"
  major="${BLENDER_VERSION%.*}"
  curl -fL -o /tmp/blender.tar.xz \
    "https://download.blender.org/release/Blender${major}/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
  tar -xf /tmp/blender.tar.xz -C "$BLENDER_DIR" --strip-components=1
  rm -f /tmp/blender.tar.xz
fi
if ! ldconfig -p | grep -q libEGL.so.1; then
  apt-get update -q && apt-get install -y -q libegl1 libgl1 libxi6 libxkbcommon0 libsm6
fi
pip3 install -q pillow numpy pyyaml 2>/dev/null || true
"$BLENDER_DIR/blender" --version | head -1
