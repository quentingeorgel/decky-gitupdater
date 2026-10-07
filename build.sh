#!/bin/bash
set -e

PLUGIN_NAME="decky-gitupdater"
BUILD_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${BUILD_DIR}/dist-zip"

cd "$BUILD_DIR"

echo "▶ Installation des dépendances..."
pnpm install

echo "▶ Build frontend..."
pnpm run build

echo "▶ Préparation du ZIP..."
STAGE="/tmp/${PLUGIN_NAME}-stage"
rm -rf "$STAGE"
mkdir -p "$STAGE"
mkdir -p "$OUTPUT_DIR"

cp plugin.json "$STAGE/"
cp main.py "$STAGE/"
mkdir -p "$STAGE/dist"
cp -r dist/* "$STAGE/dist/"

ZIP_PATH="$OUTPUT_DIR/${PLUGIN_NAME}.zip"
rm -f "$ZIP_PATH"
cd "$STAGE"
zip -r "$ZIP_PATH" . > /dev/null

echo ""
echo "✅ ZIP créé : $ZIP_PATH"
