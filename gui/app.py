import os
import tkinter as tk
from tkinter import ttk, filedialog

from tkinterdnd2 import TkinterDnD

from config.constants import APP_NAME
from config.theme import Colors, Fonts, setup_theme
from core.state import AppState
from core.pipeline import ProcessingPipeline
from core.batch_processor import BatchProcessor
from gui.widgets import TopBar, SidePanel, PreviewPanel, ControlPanel
from gui.sliders import SlidersPanel
from gui.crop_presets import CropPresetBar
from utils.aspect_ratio import get_preset_size, detect_best_preset
from core.exporter import Exporter


class PhotoPilotApp:
    def __init__(self) -> None:
        self.state = AppState()
        self.pipeline = ProcessingPipeline()
        self.batch = BatchProcessor()
        self._preview_timer_id: str | None = None

        self._root = TkinterDnD.Tk()
        self._root.title(APP_NAME)
        self._root.state("zoomed")
        self._root.minsize(1200, 700)
        self._root.configure(bg=Colors.BG)

        setup_theme(self._root)
        self._build_ui()
        self._update_button_states()

    def _build_ui(self) -> None:
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=1)

        top = TopBar(self._root, on_open=self._on_select_files)
        top.grid(row=0, column=0, sticky="ew")

        main = ttk.Frame(self._root, style="TFrame")
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._side = SidePanel(main, self._on_select_image,
                                self._on_select_input, self._on_select_output)
        self._side.grid(row=0, column=0, sticky="ns")

        center_container = ttk.Frame(main, style="TFrame")
        center_container.grid(row=0, column=1, sticky="nsew")
        center_container.columnconfigure(0, weight=1)
        center_container.rowconfigure(0, weight=1)

        preview_frame = ttk.LabelFrame(
            center_container, text=" Vista previa ",
            style="Preview.TLabelframe",
        )
        preview_frame.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        preview_container = ttk.Frame(preview_frame, style="PreviewInner.TFrame")
        preview_container.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        preview_container.columnconfigure(0, weight=1)
        preview_container.rowconfigure(0, weight=1)

        self._preview = PreviewPanel(preview_container)
        self._preview.grid(row=0, column=0, sticky="nsew")
        self._preview.set_drag_callbacks(self._on_preview_drag,
                                         self._on_preview_drag_end)

        self._crop_bar = CropPresetBar(
            center_container, self.on_crop_preset,
            self._on_reset_center, self._on_apply_center_to_all,
            self._on_apply_preset_to_all,
        )
        self._crop_bar.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 0))

        progress_frame = ttk.Frame(center_container, style="TFrame")
        progress_frame.grid(row=2, column=0, sticky="ew",
                            padx=12, pady=(8, 8))
        progress_frame.columnconfigure(0, weight=1)

        progress_inner = ttk.Frame(progress_frame, style="TFrame")
        progress_inner.pack(fill=tk.X)
        progress_inner.columnconfigure(0, weight=1)

        self._progress_bar = ttk.Progressbar(
            progress_inner, mode="determinate", style="TProgressbar",
        )
        self._progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._progress_label = ttk.Label(
            progress_inner, text="", style="Status.TLabel",
        )
        self._progress_label.grid(row=0, column=1)

        right_outer = ttk.Frame(main, style="TFrame", width=230)
        right_outer.grid(row=0, column=2, sticky="ns")
        right_outer.grid_propagate(False)
        right_outer.columnconfigure(0, weight=1)
        right_outer.rowconfigure(1, weight=1)

        self._controls = ControlPanel(right_outer, self)
        self._controls.grid(row=0, column=0, sticky="ew", pady=(8, 0))
        self._controls.set_enhance_active(True)

        sliders_outer = ttk.LabelFrame(
            right_outer, text="  Ajustes  ", style="TLabelframe",
        )
        sliders_outer.grid(row=1, column=0, sticky="nsew", padx=0,
                           pady=(8, 8))
        sliders_outer.columnconfigure(0, weight=1)
        sliders_outer.rowconfigure(0, weight=1)

        self._sliders = SlidersPanel(sliders_outer, self)
        self._sliders.grid(row=0, column=0, sticky="nsew")

        self._root.drop_target_register("*")
        self._root.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event) -> None:
        raw = event.data
        if not raw:
            return
        paths = self._parse_drop_data(raw)
        if not paths:
            return
        if len(paths) == 1 and os.path.isdir(paths[0]):
            images = self.state.load_directory(paths[0])
        else:
            images = self.state.load_files(paths)
        self._side.load(images)
        if images:
            self._open_image(0)
        self._update_button_states()

    def _parse_drop_data(self, raw: str) -> list[str]:
        parts = raw.strip().split()
        paths = []
        i = 0
        while i < len(parts):
            p = parts[i]
            if p.startswith("{") and not p.endswith("}"):
                buf = p
                i += 1
                while i < len(parts):
                    buf += " " + parts[i]
                    if parts[i].endswith("}"):
                        break
                    i += 1
                p = buf
            paths.append(p.strip("{}").strip())
            i += 1
        return [p for p in paths if os.path.exists(p)]

    def _on_select_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Seleccionar imagenes",
            filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                       ("Todos los archivos", "*.*")],
        )
        if not paths:
            return
        images = self.state.load_files(list(paths))
        self._side.load(images)
        if images:
            self._open_image(0)
        self._update_button_states()

    def _on_select_input(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta de imagenes")
        if not path:
            return
        images = self.state.load_directory(path)
        self._side.load(images)
        if images:
            self._open_image(0)
        self._update_button_states()

    def _on_select_output(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if path:
            self.state.output_dir = path

    def _on_select_image(self, index: int) -> None:
        self._open_image(index)

    def _open_image(self, index: int) -> None:
        img = self.state.open_image(index)
        if img:
            self._side.select(index)
            self._sliders.load_from_state()
            self._crop_bar.set_preset(self.state.crop_preset)
            self._auto_detect_crop_preset()
            self._refresh_preview()

    def _auto_detect_crop_preset(self) -> None:
        if not self.state.original_image or not self.state.crop_enabled:
            return
        if self.state.current_index in self.state._crop_presets:
            return
        w, h = self.state.original_image.size
        preset = detect_best_preset(w, h)
        if preset:
            self.state.crop_preset = preset
            self._crop_bar.set_preset(preset)

    def _refresh_preview(self) -> None:
        orig = self.state.original_image
        if orig is None:
            return
        result = self.pipeline.process(self.state)
        if result:
            self._preview.show_result(result)
        if self.state.crop_enabled:
            tw, th = get_preset_size(self.state.crop_preset)
            self._preview.prepare_drag(orig, tw, th,
                                       self.state.crop_center_x,
                                       self.state.crop_center_y)
            self._preview.enable_drag()
        else:
            self._preview.disable_drag()

    def _update_button_states(self) -> None:
        has_images = len(self.state.images) > 0
        self._controls.set_buttons_enabled(has_images)
        self._crop_bar.set_enabled(has_images)
        self._side.set_enabled(has_images)

    def on_slider_changed(self) -> None:
        if self._preview_timer_id:
            self._root.after_cancel(self._preview_timer_id)
        self._preview_timer_id = self._root.after(80, self._refresh_preview)

    def on_crop_preset(self, preset: str) -> None:
        self.state.crop_preset = preset
        if self.state.crop_enabled:
            self._refresh_preview()

    def _on_preview_drag(self, dx: float, dy: float) -> None:
        cx = max(0.0, min(1.0, self.state.crop_center_x + dx))
        cy = max(0.0, min(1.0, self.state.crop_center_y + dy))
        self.state.set_crop_center(self.state.current_index, cx, cy)
        self._preview.update_overlay(cx, cy)

    def _on_preview_drag_end(self) -> None:
        self._refresh_preview()

    def _on_reset_center(self) -> None:
        self.state.set_crop_center(self.state.current_index, 0.5, 0.5)
        self._refresh_preview()

    def _on_apply_center_to_all(self) -> None:
        cx = self.state.crop_center_x
        cy = self.state.crop_center_y
        self.state.apply_center_to_all(cx, cy)

    def _on_apply_preset_to_all(self, preset: str) -> None:
        self.state.apply_preset_to_all(preset)
        self.state.crop_preset = preset

    def on_auto_enhance(self) -> None:
        self.state.enhance_enabled = not self.state.enhance_enabled
        self._controls.set_enhance_active(self.state.enhance_enabled)
        self._refresh_preview()

    def on_reset(self) -> None:
        self.state.reset()
        self._sliders.reset()
        self._crop_bar.reset()
        self._refresh_preview()

    def on_export_one(self) -> None:
        if not self.state.processed_image:
            return
        if not self.state.output_dir:
            return
        exporter = Exporter(self.state.export)
        exporter.save(
            self.state.processed_image,
            self.state.images[self.state.current_index],
            self.state.output_dir,
        )

    def on_export_all(self) -> None:
        if not self.state.output_dir:
            return
        exporter = Exporter(self.state.export)
        saved = 0
        for i, path in enumerate(self.state.images):
            self.state.open_image(i)
            result = self.pipeline.process(self.state)
            if result:
                exporter.save(result, path, self.state.output_dir, i)
                saved += 1
        self.state.open_image(self.state.current_index)
        self._refresh_preview()

    def on_process_folder(self) -> None:
        if not self.state.images:
            return
        if not self.state.output_dir:
            return
        self._progress_bar["value"] = 0
        self._progress_label.config(text="Iniciando...")
        self._controls.disable_during_batch()
        self.batch.process(
            self.state,
            on_progress=self._on_batch_progress,
            on_complete=self._on_batch_complete,
        )

    def _on_batch_progress(self, progress) -> None:
        self._root.after_idle(self._update_progress_ui, progress)

    def _on_batch_complete(self) -> None:
        self._root.after_idle(self._on_batch_complete_ui)

    def _update_progress_ui(self, progress) -> None:
        pct = (progress.current / progress.total * 100) if progress.total else 0
        self._progress_bar["value"] = pct
        eta = progress.elapsed / max(progress.current, 1) * (
            progress.total - progress.current
        )
        self._progress_label.config(
            text=f"{progress.current}/{progress.total}  "
            f"errores: {progress.errors}  "
            f"ETA: {eta:.0f}s"
        )

    def _on_batch_complete_ui(self) -> None:
        self._progress_label.config(text="Completado")
        self._controls.enable_after_batch()

    def run(self) -> None:
        self._root.mainloop()
