#!/bin/bash
# Video para Estados V2.0 - Script de instalación AUDITADO
# Para Zorin OS 18 / Ubuntu 24.04

set -e

echo "╔══════════════════════════════════════════╗"
echo "║ Video para Estados V2.0 - Instalación    ║"
echo "║         (Versión Auditada)               ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Instalar dependencias de sistema (SOLO apt, sin pip)
echo -e "${BLUE}[1/4]${NC} Instalando dependencias de sistema..."
sudo apt update
sudo apt install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    gir1.2-adw-1 \
    ffmpeg \
    vainfo

# V2.0: NO crear venv ni usar pip
# PyGObject viene de apt (python3-gi), no de pip
# Esto evita conflictos con paquetes del sistema
echo -e "${YELLOW}[INFO]${NC} Usando PyGObject del sistema (sin venv)"

# 2. Hacer ejecutable el script principal
echo -e "${BLUE}[2/4]${NC} Configurando permisos..."
chmod +x videoparaestados.py

# 3. Instalar ícono
echo -e "${BLUE}[3/4]${NC} Instalando ícono..."
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$ICON_DIR"
cp videoparaestados.svg "$ICON_DIR/com.videoparaestados.app.svg"

# Crear index.theme si no existe (V2.0: fix para gtk-update-icon-cache)
HICOLOR_DIR="$HOME/.local/share/icons/hicolor"
if [ ! -f "$HICOLOR_DIR/index.theme" ]; then
    cat > "$HICOLOR_DIR/index.theme" << EOF
[Icon Theme]
Name=Hicolor
Comment=Fallback icon theme
Directories=scalable/apps

[scalable/apps]
Size=64
Type=Scalable
MinSize=16
MaxSize=512
EOF
fi

gtk-update-icon-cache -f -t "$HICOLOR_DIR" 2>/dev/null || true

# 4. Instalar archivo .desktop (V2.0: portable)
echo -e "${BLUE}[4/4]${NC} Instalando acceso directo..."
mkdir -p ~/.local/share/applications

# V2.0: Generar .desktop con path correcto dinámicamente
cat > ~/.local/share/applications/com.videoparaestados.app.desktop << EOF
[Desktop Entry]
Name=Video para Estados
Comment=Convierte videos de Instagram para Estados de WhatsApp
Exec=python3 $SCRIPT_DIR/videoparaestados.py
Icon=com.videoparaestados.app
Terminal=false
Type=Application
Categories=AudioVideo;Video;GTK;
Keywords=video;converter;whatsapp;instagram;estados;
StartupNotify=true
EOF

update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ Instalación V2.0 completada${NC}"
echo ""
echo "Para ejecutar Video para Estados:"
echo "  1. Busca 'Video para Estados' en el menú de aplicaciones"
echo "  2. O ejecuta: python3 $SCRIPT_DIR/videoparaestados.py"
echo ""
echo -e "${YELLOW}Nota:${NC} Esta versión ha sido auditada para seguridad."
echo ""
