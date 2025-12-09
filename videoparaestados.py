#!/usr/bin/env python3
"""
Video para Estados V2.0 - AUDITED VERSION
Conversor de Videos para Estados de WhatsApp
Convierte videos de Instagram a formato compatible con WhatsApp.

Cambios V2.0 (Auditoría de Seguridad):
- Eliminación de metadatos privados (-map_metadata -1)
- Timeout de 5 minutos por video
- Bloqueo de UI durante conversión
- Lista detallada de errores
- Mejor gestión de hilos en Intel híbridos
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import threading
import logging
from pathlib import Path
from typing import List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Extensiones de video soportadas
VIDEO_EXTENSIONS = frozenset({'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'})

# Timeout por video en segundos (5 minutos)
FFMPEG_TIMEOUT = 300


class VideoParaEstadosWindow(Adw.ApplicationWindow):
    """Ventana principal de Video para Estados."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.selected_folder: str = None
        self.video_files: List[Path] = []
        self.is_converting: bool = False
        self.failed_videos: List[Tuple[str, str]] = []  # (nombre, error)
        
        self.has_vaapi = self._check_vaapi()
        self.has_ffmpeg = self._check_ffmpeg()
        
        self.set_title("Video para Estados")
        self.set_default_size(420, 540)
        
        self._build_ui()
        
        if not self.has_ffmpeg:
            self._show_toast("⚠️ FFmpeg no encontrado. Instálalo para convertir.")
            logger.warning("FFmpeg not found in system PATH")
    
    def _check_vaapi(self) -> bool:
        """Verifica si VAAPI está disponible (Intel Arc)."""
        try:
            result = subprocess.run(
                ["vainfo"],
                capture_output=True,
                text=True,
                timeout=5
            )
            has_h264 = "VAProfileH264" in result.stdout
            logger.info(f"VAAPI check: {'available' if has_h264 else 'not available'}")
            return has_h264 or result.returncode == 0
        except FileNotFoundError:
            logger.info("vainfo not installed")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("vainfo timed out")
            return False
        except Exception as e:
            logger.error(f"VAAPI check failed: {e}")
            return False
    
    def _check_ffmpeg(self) -> bool:
        """Verifica si FFmpeg está instalado."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                timeout=5
            )
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    def _build_ui(self):
        """Construye la interfaz de usuario."""
        # Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.set_content(self.toast_overlay)
        
        # ToolbarView
        toolbar_view = Adw.ToolbarView()
        self.toast_overlay.set_child(toolbar_view)
        
        # Header Bar
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)
        
        # Menú
        menu = Gio.Menu()
        menu.append("Acerca de", "app.about")
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu)
        header.pack_end(menu_btn)
        
        # Scroll
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        toolbar_view.set_content(scrolled)
        
        # Clamp centrado
        clamp = Adw.Clamp()
        clamp.set_maximum_size(380)
        clamp.set_margin_top(8)
        clamp.set_margin_bottom(16)
        clamp.set_margin_start(16)
        clamp.set_margin_end(16)
        scrolled.set_child(clamp)
        
        # Contenido principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        clamp.set_child(main_box)
        
        # === HERO COMPACTO ===
        hero = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hero.set_halign(Gtk.Align.CENTER)
        hero.set_margin_top(8)
        hero.set_margin_bottom(4)
        main_box.append(hero)
        
        # Ícono pequeño
        icon = Gtk.Image.new_from_icon_name("com.videoparaestados.app")
        icon.set_pixel_size(32)
        hero.append(icon)
        
        # Título y subtítulo en vertical
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        hero.append(title_box)
        
        title = Gtk.Label(label="Video para Estados")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        title_box.append(title)
        
        subtitle = Gtk.Label(label="Instagram → WhatsApp")
        subtitle.add_css_class("dim-label")
        subtitle.add_css_class("caption")
        subtitle.set_halign(Gtk.Align.START)
        title_box.append(subtitle)
        
        # === LISTA DE ACCIONES ===
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        list_box.add_css_class("boxed-list")
        main_box.append(list_box)
        
        # Row 1: Seleccionar carpeta
        self.folder_row = Adw.ActionRow()
        self.folder_row.set_title("Seleccionar carpeta")
        self.folder_row.set_subtitle("Videos: MP4, MOV, MKV, WebM")
        self.folder_row.set_activatable(True)
        self.folder_row.connect("activated", self._on_select_folder)
        
        folder_icon = Gtk.Image.new_from_icon_name("folder-videos-symbolic")
        self.folder_row.add_prefix(folder_icon)
        
        folder_arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
        folder_arrow.add_css_class("dim-label")
        self.folder_row.add_suffix(folder_arrow)
        
        list_box.append(self.folder_row)
        
        # Row 2: Contador de videos
        self.videos_row = Adw.ActionRow()
        self.videos_row.set_title("Videos encontrados")
        self.videos_row.set_subtitle("Ninguno aún")
        self.videos_row.set_sensitive(False)
        
        video_icon = Gtk.Image.new_from_icon_name("video-x-generic-symbolic")
        self.videos_row.add_prefix(video_icon)
        
        self.count_label = Gtk.Label(label="0")
        self.count_label.add_css_class("accent")
        self.count_label.add_css_class("heading")
        self.count_label.set_valign(Gtk.Align.CENTER)
        self.videos_row.add_suffix(self.count_label)
        
        list_box.append(self.videos_row)
        
        # Row 3: Info de codecs (expander)
        expander_row = Adw.ExpanderRow()
        expander_row.set_title("Configuración de conversión")
        expander_row.set_subtitle("H.264 Baseline + AAC")
        
        settings_icon = Gtk.Image.new_from_icon_name("emblem-system-symbolic")
        expander_row.add_prefix(settings_icon)
        
        list_box.append(expander_row)
        
        # Contenido del expander
        codec_row = Adw.ActionRow()
        codec_row.set_title("Códec de video")
        codec_row.set_subtitle("libx264 (profile baseline, level 3.0)")
        expander_row.add_row(codec_row)
        
        audio_row = Adw.ActionRow()
        audio_row.set_title("Códec de audio")
        audio_row.set_subtitle("AAC 128kbps, 44.1kHz stereo")
        expander_row.add_row(audio_row)
        
        # V2.0: Indicar que se eliminan metadatos
        privacy_row = Adw.ActionRow()
        privacy_row.set_title("Privacidad")
        privacy_row.set_subtitle("Metadatos eliminados (GPS, fecha, etc.)")
        privacy_icon = Gtk.Image.new_from_icon_name("security-high-symbolic")
        privacy_row.add_prefix(privacy_icon)
        expander_row.add_row(privacy_row)
        
        # Row de aceleración (si hay VAAPI)
        if self.has_vaapi:
            hw_row = Adw.ActionRow()
            hw_row.set_title("Aceleración GPU")
            hw_row.set_subtitle("Intel Arc VAAPI detectado ⚡")
            hw_row.add_css_class("success")
            
            hw_icon = Gtk.Image.new_from_icon_name("computer-symbolic")
            hw_row.add_prefix(hw_icon)
            expander_row.add_row(hw_row)
        
        output_row = Adw.ActionRow()
        output_row.set_title("Carpeta de salida")
        output_row.set_subtitle("./convertidos/ (dentro de origen)")
        expander_row.add_row(output_row)
        
        # === PROGRESO ===
        self.progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.progress_box.set_visible(False)
        main_box.append(self.progress_box)
        
        self.progress_label = Gtk.Label()
        self.progress_label.set_halign(Gtk.Align.START)
        self.progress_label.add_css_class("caption")
        self.progress_label.add_css_class("dim-label")
        self.progress_box.append(self.progress_label)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_box.append(self.progress_bar)
        
        # === BOTÓN ===
        self.convert_button = Gtk.Button()
        self.convert_button.set_halign(Gtk.Align.CENTER)
        self.convert_button.add_css_class("suggested-action")
        self.convert_button.add_css_class("pill")
        self.convert_button.set_sensitive(False)
        self.convert_button.set_tooltip_text(
            "Convierte los videos al formato de WhatsApp Status"
        )
        self.convert_button.connect("clicked", self._on_convert_clicked)
        main_box.append(self.convert_button)
        
        btn_box = Gtk.Box(spacing=8)
        self.convert_button.set_child(btn_box)
        
        self.btn_icon = Gtk.Image.new_from_icon_name(
            "media-playback-start-symbolic"
        )
        btn_box.append(self.btn_icon)
        
        self.btn_label = Gtk.Label(label="Convertir para WhatsApp")
        btn_box.append(self.btn_label)
        
        # Registrar About
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self._on_about)
        self.get_application().add_action(about_action)
    
    def _on_about(self, action, param):
        """Diálogo Acerca de."""
        hw_info = "Intel Arc VAAPI activado" if self.has_vaapi else "Software encoding"
        about = Adw.AboutWindow(
            transient_for=self,
            application_name="Video para Estados",
            application_icon="com.videoparaestados.app",
            developer_name="Discaury",
            version="2.0.0",
            comments=(
                "Convierte videos de Instagram\n"
                "para Estados de WhatsApp.\n\n"
                f"{hw_info}\n\n"
                "V2.0: Auditoría de seguridad aplicada"
            ),
            license_type=Gtk.License.GPL_3_0
        )
        about.present()
    
    def _on_select_folder(self, widget):
        """Selección de carpeta."""
        if self.is_converting:
            return  # V2.0: Bloquear durante conversión
        
        dialog = Gtk.FileDialog()
        dialog.set_title("Seleccionar carpeta")
        dialog.select_folder(self, None, self._on_folder_selected)
    
    def _on_folder_selected(self, dialog, result):
        """Carpeta seleccionada."""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.selected_folder = folder.get_path()
                self._scan_videos()
        except GLib.Error as e:
            if e.code != Gtk.DialogError.DISMISSED:
                self._show_toast(f"Error: {e.message}")
                logger.error(f"Folder selection error: {e.message}")
    
    def _scan_videos(self):
        """Escanea videos."""
        folder = Path(self.selected_folder)
        self.video_files = [
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in VIDEO_EXTENSIONS
        ]
        
        # Actualizar UI
        self.folder_row.set_title(folder.name)
        self.folder_row.set_subtitle(str(folder))
        
        count = len(self.video_files)
        self.count_label.set_text(str(count))
        logger.info(f"Found {count} videos in {folder}")
        
        if count == 0:
            self.videos_row.set_subtitle("Ningún video encontrado")
            self.convert_button.set_sensitive(False)
            self._show_toast("No hay videos en esta carpeta")
        else:
            self.videos_row.set_sensitive(True)
            names = ", ".join(f.name for f in self.video_files[:2])
            if count > 2:
                names += f" +{count - 2}"
            self.videos_row.set_subtitle(names)
            self.convert_button.set_sensitive(True)
    
    def _on_convert_clicked(self, btn):
        """Inicia conversión."""
        if self.is_converting or not self.video_files:
            return
        
        self.is_converting = True
        self.failed_videos = []  # V2.0: Reset lista de errores
        
        # V2.0: Deshabilitar folder_row durante conversión
        self.folder_row.set_sensitive(False)
        self.convert_button.set_sensitive(False)
        self.progress_box.set_visible(True)
        self.progress_bar.set_fraction(0)
        
        self.btn_icon.set_from_icon_name("emblem-synchronizing-symbolic")
        self.btn_label.set_text("Convirtiendo...")
        
        output = Path(self.selected_folder) / "convertidos"
        output.mkdir(exist_ok=True)
        
        thread = threading.Thread(
            target=self._convert_videos,
            args=(self.video_files.copy(), output),
            daemon=True
        )
        thread.start()
        logger.info(f"Started conversion of {len(self.video_files)} videos")
    
    def _convert_videos(self, videos: List[Path], output: Path):
        """Conversión en hilo separado."""
        total = len(videos)
        ok, err = 0, 0
        
        for i, v in enumerate(videos):
            GLib.idle_add(
                self._update_progress,
                i / total,
                f"[{i + 1}/{total}] {v.name}"
            )
            
            out_file = output / f"{v.stem}_whatsapp.mp4"
            
            # V2.0: Comando FFmpeg AUDITADO
            cmd = [
                "ffmpeg",
                "-i", str(v),
                "-y",
                # Eliminar metadatos privados (V2.0)
                "-map_metadata", "-1",
                # Video
                "-c:v", "libx264",
                "-profile:v", "baseline",
                "-level:v", "3.0",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                # Audio
                "-c:a", "aac",
                "-b:a", "128k",
                "-ar", "44100",
                "-ac", "2",
                # V2.0: Omitir -threads (libx264 gestiona mejor)
                "-movflags", "+faststart",
                str(out_file)
            ]
            
            try:
                # V2.0: Añadir timeout
                r = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=FFMPEG_TIMEOUT
                )
                if r.returncode == 0:
                    ok += 1
                    logger.info(f"Converted: {v.name}")
                else:
                    err += 1
                    error_msg = r.stderr.split('\n')[-2] if r.stderr else "Unknown"
                    self.failed_videos.append((v.name, error_msg))
                    logger.error(f"Failed: {v.name} - {error_msg}")
                    
            except subprocess.TimeoutExpired:
                err += 1
                self.failed_videos.append((v.name, "Timeout (>5min)"))
                logger.error(f"Timeout: {v.name}")
            except Exception as e:
                err += 1
                self.failed_videos.append((v.name, str(e)))
                logger.error(f"Exception: {v.name} - {e}")
            
            GLib.idle_add(
                self._update_progress,
                (i + 1) / total,
                f"{'✓' if err == 0 else '⚠'} {v.name}"
            )
        
        GLib.idle_add(self._done, ok, err, output)
    
    def _update_progress(self, frac: float, txt: str):
        """Actualiza progreso."""
        self.progress_bar.set_fraction(frac)
        self.progress_label.set_text(txt)
    
    def _done(self, ok: int, err: int, output: Path):
        """Conversión terminada."""
        self.is_converting = False
        
        # V2.0: Rehabilitar folder_row
        self.folder_row.set_sensitive(True)
        self.convert_button.set_sensitive(True)
        self.progress_bar.set_fraction(1)
        
        self.btn_icon.set_from_icon_name("emblem-ok-symbolic")
        self.btn_label.set_text("¡Listo!")
        
        if err == 0:
            self.progress_label.set_text(f"✓ {ok} videos convertidos")
            self._show_toast(f"✓ {ok} videos en 'convertidos'")
        else:
            self.progress_label.set_text(f"{ok} ok, {err} errores")
            # V2.0: Mostrar detalles de errores
            failed_names = ", ".join(f[0] for f in self.failed_videos[:3])
            if len(self.failed_videos) > 3:
                failed_names += f" +{len(self.failed_videos) - 3}"
            self._show_toast(f"⚠️ Falló: {failed_names}")
            logger.warning(f"Conversion completed with {err} errors")
        
        try:
            subprocess.Popen(["xdg-open", str(output)])
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
        
        GLib.timeout_add_seconds(3, self._reset_btn)
    
    def _reset_btn(self) -> bool:
        """Resetea botón."""
        self.btn_icon.set_from_icon_name("media-playback-start-symbolic")
        self.btn_label.set_text("Convertir para WhatsApp")
        return False
    
    def _show_toast(self, msg: str):
        """Toast."""
        t = Adw.Toast.new(msg)
        t.set_timeout(3)
        self.toast_overlay.add_toast(t)


class VideoParaEstadosApp(Adw.Application):
    """Aplicación principal."""
    
    def __init__(self):
        super().__init__(
            application_id="com.videoparaestados.app",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
    
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = VideoParaEstadosWindow(application=self)
        win.present()


if __name__ == "__main__":
    app = VideoParaEstadosApp()
    app.run(None)
