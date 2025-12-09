# Video para Estados

![Video para Estados](videoparaestados.svg)

> 📹 **Convierte videos de Instagram para Estados de WhatsApp**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![GTK4](https://img.shields.io/badge/GTK4-Libadwaita-4a86cf.svg)](https://gtk.org/)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)]()

---

## 📖 Descripción

**Video para Estados** es una aplicación de escritorio para Linux que convierte videos descargados de Instagram al formato exacto requerido por WhatsApp Status. Soluciona el problema común de "códec no soportado" al intentar subir videos a los Estados.



---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 🔄 **Conversión por lotes** | Convierte múltiples videos a la vez |
| 📱 **100% compatible WhatsApp** | H.264 Baseline + AAC (la receta exacta) |
| 🔒 **Privacidad** | Elimina metadatos GPS/EXIF antes de subir |
| 🖥️ **Detección Intel Arc** | Muestra si tienes aceleración VAAPI |
| 🌙 **Tema del sistema** | Se adapta al tema claro/oscuro |
| 📁 **Carpeta automática** | Crea `./convertidos/` dentro de origen |
| ⚡ **Optimizado** | Usa todos los núcleos de tu CPU |
| 📊 **Progreso en tiempo real** | Barra de progreso y contador |

---

## 📋 Requisitos

- **Sistema operativo:** Linux (Ubuntu 22.04+, Zorin OS 17+, Fedora 38+)
- **Python** 3.8 o superior
- **FFmpeg** instalado
- **GTK4 + Libadwaita**

---

## 🚀 Instalación

### Linux (Ubuntu/Zorin OS/Fedora) ⭐ Recomendado

```bash
# Clonar el repositorio
git clone https://github.com/discodiski/vidconverter.git
cd vidconverter

# Ejecutar instalador automático
chmod +x install.sh
./install.sh
```

El instalador automáticamente:
- ✅ Instala GTK4 y Libadwaita (look nativo)
- ✅ Instala FFmpeg y vainfo
- ✅ Instala el ícono en el sistema
- ✅ Crea acceso directo en el menú de aplicaciones

---

## 🎯 Uso

### Desde el menú de aplicaciones (Linux)
1. Busca **"Video para Estados"** en tu menú
2. Haz clic en el ícono de WhatsApp

### Desde terminal
```bash
python3 videoparaestados.py
```

### Flujo de trabajo
1. **Selecciona carpeta** → Elige la carpeta con videos de Instagram
2. **Revisa el contador** → Verás cuántos videos se detectaron
3. **Haz clic en Convertir** → Espera a que termine
4. **¡Listo!** → Se abre la carpeta `convertidos/` automáticamente

---

## 🔧 Parámetros de Conversión

La aplicación usa FFmpeg con estos parámetros optimizados para WhatsApp:

| Parámetro | Valor | Propósito |
|-----------|-------|-----------|
| `-c:v libx264` | H.264 | Códec de video universal |
| `-profile:v baseline` | Baseline | Máxima compatibilidad |
| `-level:v 3.0` | Level 3.0 | Dispositivos antiguos |
| `-pix_fmt yuv420p` | YUV 4:2:0 | Formato de color estándar |
| `-c:a aac` | AAC | Códec de audio |
| `-b:a 128k` | 128 kbps | Calidad de audio |
| `-map_metadata -1` | - | Elimina GPS/EXIF |
| `-movflags +faststart` | - | Streaming optimizado |

---

## 📁 Estructura del proyecto

```
vidconverter/
├── videoparaestados.py      # Aplicación principal (GTK4)
├── videoparaestados.svg     # Ícono de la aplicación
├── install.sh               # Script de instalación
├── requirements.txt         # Documentación de dependencias
├── com.videoparaestados.app.desktop  # Acceso directo
├── LICENSE                  # Licencia GPL-3.0
└── README.md               # Este archivo
```

---

## 🛠️ Desarrollo

### Ejecutar desde código fuente
```bash
# Instalar dependencias de sistema
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 ffmpeg

# Ejecutar
python3 videoparaestados.py
```

### Formatos de video soportados
- MP4, MOV, MKV, WebM, AVI, M4V

---

## 📄 Licencia

Este proyecto está bajo la licencia **GNU General Public License v3.0**.
Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Discaury Salas**
- GitHub: [@discodiski](https://github.com/discodiski)

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:
1. Haz fork del repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Haz commit (`git commit -m 'Añade nueva función'`)
4. Push (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## ⭐ Tecnologías

| Tecnología | Uso |
|------------|-----|
| ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) | Lenguaje principal |
| ![GTK4](https://img.shields.io/badge/GTK4-4a86cf?logo=gtk&logoColor=white) | Interfaz gráfica |
| ![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?logo=ffmpeg&logoColor=white) | Conversión de video |

---

## 📝 Changelog

### V2.0.0 (2024-12-09) - Versión Auditada
- ✅ Eliminación automática de metadatos (privacidad)
- ✅ Timeout de 5 minutos por video
- ✅ Bloqueo de UI durante conversión
- ✅ Lista detallada de errores
- ✅ Sistema de logging
- ✅ Instalador mejorado sin pip/venv

### V1.0.0 (2024-12-09)
- 🎉 Lanzamiento inicial
- Conversión de videos para WhatsApp
- Interfaz GTK4 + Libadwaita
- Detección de Intel Arc VAAPI
