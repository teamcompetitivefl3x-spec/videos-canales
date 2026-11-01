#!/bin/sh
# Prepara el entorno de producción (ejecutar desde la raíz del repo clonado en /home/claude/videos-canales)
set -e
pip install --break-system-packages -q kokoro-onnx soundfile scipy >/dev/null 2>&1 || true
mkdir -p /home/claude/models /home/claude/piloto
cd /home/claude/models
[ -f kokoro-v1.0.onnx ] || curl -sSL -o kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f voices-v1.0.bin ] || curl -sSL -o voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# Los scripts usan estas rutas fijas
mkdir -p /home/claude/build /home/claude/kids
cp -n /home/claude/videos-canales/pulso/*.py /home/claude/build/
cp -n /home/claude/videos-canales/infantil/*.py /home/claude/kids/
echo "OK: entorno listo"
