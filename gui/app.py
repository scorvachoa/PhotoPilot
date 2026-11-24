import os
import tkinter as tk
from tkinter import ttk, filedialog

from tkinterdnd2 import TkinterDnD

from config.constants import APP_NAME
from config.theme import Colors, Fonts, Spacing, setup_theme
from core.state import AppState
from core.pipeline import ProcessingPipeline
from core.batch_processor import BatchProcessor
from gui.widgets import TopBar, SidePanel, PreviewPanel, ControlPanel
from gui.sliders import SlidersPanel
from gui.crop_presets import CropPresetBar
from utils.aspect_ratio import (clamp_crop_center, detect_best_preset,
                                get_preset_size)
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
        self._root.minsize(1120, 700)
        self._root.configure(bg=Colors.BG)

        setup_theme(self._root)
        self._build_ui()
        self._bind_shortcuts()
        self._update_button_states()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, bg=Colors.BG_CARD, bd=0,
                        highlightthickness=1,
                        highlightbackground=Colors.BORDER,
                        highlightcolor=Colors.BORDER)

    def _build_ui(self) -> None:
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=1)

        self._top = TopBar(self._root, on_open=self._on_select_files)
        self._top.grid(row=0, column=0, sticky="ew")

        main = ttk.Frame(self._root, style="App.TFrame")
        main.grid(row=1, column=0, sticky="nsew")
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._side = SidePanel(main, self._on_select_image,
                               self._on_select_input, self._on_select_output)
        self._side.grid(row=0, column=0, sticky="ns")

        center = ttk.Frame(main, style="App.TFrame")
        center.grid(row=0, column=1, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(0, weight=1)

        # ---- Preview card --------------------------------------------
        preview_card = self._card(center)
        preview_card.grid(row=0, column=0, sticky="nsew",
                          padx=Spacing.MD, pady=(Spacing.MD, 0))
        preview_card.columnconfigure(0, weight=1)
        preview_card.rowconfigure(1, weight=1)

        preview_head = tk.Frame(preview_card, bg=Colors.BG_CARD)
        preview_head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 8))
        tk.Label(preview_head, text="VISTA PREVIA", bg=Colors.BG_CARD,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(side=tk.LEFT)
        self._preview_meta = tk.Label(preview_head, text="", bg=Colors.BG_CARD,
                                      fg=Colors.TEXT_MUTED, font=Fonts.MICRO)
        self._preview_meta.pack(side=tk.RIGHT)

        preview_stage = tk.Frame(preview_card, bg=Colors.BG_PREVIEW)
        preview_stage.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        preview_stage.columnconfigure(0, weight=1)
        preview_stage.rowconfigure(0, weight=1)

        self._preview = PreviewPanel(preview_stage)
        self._preview.grid(row=0, column=0, sticky="nsew")
        self._preview.set_drag_callbacks(self._on_preview_drag,
                                         self._on_preview_drag_end)

        # ---- Crop presets --------------------------------------------
        self._crop_bar = CropPresetBar(
            center, self.on_crop_preset,
            self._on_reset_center, self._on_apply_center_to_all,
            self._on_apply_preset_to_all,
        )
        self._crop_bar.grid(row=1, column=0, sticky="ew",
                            padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))

        # ---- Right column --------------------------------------------
        right = ttk.Frame(main, style="App.TFrame", width=274)
        right.grid(row=0, column=2, sticky="ns")
        right.grid_propagate(False)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        tools_card = self._card(right)
        tools_card.grid(row=0, column=0, sticky="ew",
                        padx=Spacing.MD, pady=(Spacing.MD, 0))
        self._controls = ControlPanel(tools_card, self)
        self._controls.pack(fill=tk.X)
        self._controls.set_enhance_active(True)

        sliders_card = self._card(right)
        sliders_card.grid(row=1, column=0, sticky="nsew",
                          padx=Spacing.MD, pady=(Spacing.SM, Spacing.MD))
        sliders_card.columnconfigure(0, weight=1)
        sliders_card.rowconfigure(1, weight=1)

        sliders_head = tk.Frame(sliders_card, bg=Colors.BG_CARD)
        sliders_head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
        tk.Label(sliders_head, text="AJUSTES", bg=Colors.BG_CARD,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(side=tk.LEFT)

        self._sliders = SlidersPanel(sliders_card, self)
        self._sliders.grid(row=1, column=0, sticky="nsew")

        # ---- Status bar ----------------------------------------------
        self._build_status_bar()

        self._root.drop_target_register("*")
        self._root.dnd_bind("<<Drop>>", self._on_drop)

    def _build_status_bar(self) -> None:
        bar = tk.Frame(self._root, bg=Colors.BG_CARD)
        bar.grid(row=2, column=0, sticky="ew")
        tk.Frame(bar, bg=Colors.BORDER, height=1).pack(fill=tk.X)

        inner = tk.Frame(bar, bg=Colors.BG_CARD)
        inner.pack(fill=tk.X, padx=Spacing.LG, pady=6)

        self._status_dot = tk.Canvas(inner, width=10, height=10,
                                     bg=Colors.BG_CARD, highlightthickness=0,
                                     bd=0)
        self._status_dot.pack(side=tk.LEFT, pady=1)
        self._status_dot_id = self._status_dot.create_oval(
            2, 2, 8, 8, fill=Colors.TEXT_DIM, outline="")

        self._status_label = tk.Label(inner, text="Listo", bg=Colors.BG_CARD,
                                      fg=Colors.TEXT_MUTED, font=Fonts.SMALL)
        self._status_label.pack(side=tk.LEFT, padx=(8, 0))

        self._progress_label = tk.Label(inner, text="", bg=Colors.BG_CARD,
                                        fg=Colors.TEXT_MUTED, font=Fonts.MICRO)
        self._progress_bar = ttk.Progressbar(inner, mode="determinate",
                                             style="TProgressbar", length=180)

    def _show_progress(self, visible: bool) -> None:
        if visible:
            self._progress_bar.pack(side=tk.RIGHT)
            self._progress_label.pack(side=tk.RIGHT, padx=(0, 10))
        else:
            self._progress_bar.pack_forget()
            self._progress_label.pack_forget()

    def _set_status(self, text: str, kind: str = "info") -> None:
        palette = {
            "info": Colors.TEXT_MUTED,
            "success": Colors.SUCCESS,
            "warning": Colors.WARNING,
            "error": Colors.DANGER,
        }
        color = palette.get(kind, Colors.TEXT_MUTED)
        self._status_label.config(text=text, fg=color)
        self._status_dot.itemconfigure(self._status_dot_id, fill=color)

    def _bind_shortcuts(self) -> None:
        self._root.bind("<Control-o>", self._shortcut(self._on_select_files))
        self._root.bind("<Control-O>", self._shortcut(self._on_select_input))
        self._root.bind("<Control-e>", self._shortcut(self.on_export_one))
        self._root.bind("<Control-Return>",
                        self._shortcut(self.on_process_folder))

    @staticmethod
    def _shortcut(callback):
        def handler(event):
            callback()
            return "break"
        return handler

    def _sync_paths(self) -> None:
        self._side.set_input_path(self.state.input_dir)
        self._side.set_output_path(self.state.output_dir)
        self._top.set_output(self.state.output_dir)
        self._top.set_counts(len(self.state.images))

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
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
        self._sync_paths()
        self._update_button_states()
        self._set_status(f"{len(images)} im\u00e1genes cargadas", "success")

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
            title="Seleccionar im\u00e1genes",
            filetypes=[("Im\u00e1genes", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                       ("Todos los archivos", "*.*")],
        )
        if not paths:
            return
        images = self.state.load_files(list(paths))
        self._side.load(images)
        if images:
            self._open_image(0)
        self._sync_paths()
        self._update_button_states()
        self._set_status(f"{len(images)} im\u00e1genes cargadas", "success")

    def _on_select_input(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta de im\u00e1genes")
        if not path:
            return
        images = self.state.load_directory(path)
        self._side.load(images)
        if images:
            self._open_image(0)
        self._sync_paths()
        self._update_button_states()
        self._set_status(f"{len(images)} im\u00e1genes cargadas de la carpeta",
                         "success" if images else "warning")

    def _on_select_output(self) -> None:
        path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if path:
            self.state.output_dir = path
            self._sync_paths()
            self._set_status("Carpeta destino actualizada", "success")

    def _on_select_image(self, index: int) -> None:
        self._open_image(index)

    def _open_image(self, index: int) -> None:
        img = self.state.open_image(index)
        if img:
            self._side.select(index)
            self._sliders.load_from_state()
            self._crop_bar.set_preset(self.state.crop_preset)
            self._auto_detect_crop_preset()
            self._suggest_initial_center(img)
            self._refresh_preview()
            name = os.path.basename(self.state.images[index])
            self._preview_meta.config(
                text=f"{name}  \u00b7  {img.width} \u00d7 {img.height} px")

    def _suggest_initial_center(self, img) -> None:
        """Use face detection once, only for photos the user has not framed."""
        if self.state.has_crop_center(self.state.current_index):
            return
        cx, cy = self.pipeline.suggest_center(img)
        tw, th = get_preset_size(self.state.crop_preset)
        cx, cy = clamp_crop_center(img.width, img.height, tw, th, cx, cy)
        self.state.set_crop_center(self.state.current_index, cx, cy)

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
        result = self.pipeline.process(self.state, max_size=1800)
        if result:
            self._preview.show_result(result)
        if self.state.crop_enabled:
            tw, th = get_preset_size(self.state.crop_preset)
            cx, cy = clamp_crop_center(
                orig.width, orig.height, tw, th,
                self.state.crop_center_x, self.state.crop_center_y,
            )
            self.state.set_crop_center(self.state.current_index, cx, cy)
            self._preview.prepare_drag(orig, tw, th, cx, cy)
            self._preview.enable_drag()
        else:
            self._preview.disable_drag()

    def _update_button_states(self) -> None:
        has_images = len(self.state.images) > 0
        self._controls.set_buttons_enabled(has_images)
        self._crop_bar.set_enabled(has_images)
        self._side.set_enabled(has_images)
        self._sliders.set_enabled(has_images)
        self._top.set_counts(len(self.state.images))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def on_slider_changed(self) -> None:
        if self._preview_timer_id:
            self._root.after_cancel(self._preview_timer_id)
        self._preview_timer_id = self._root.after(80, self._refresh_preview)

    def on_crop_preset(self, preset: str) -> None:
        self.state.crop_preset = preset
        if self.state.crop_enabled:
            self._refresh_preview()

    def _on_preview_drag(self, cx: float, cy: float) -> None:
        self.state.set_crop_center(self.state.current_index, cx, cy)

    def _on_preview_drag_end(self) -> None:
        self._refresh_preview()

    def _on_reset_center(self) -> None:
        self.state.set_crop_center(self.state.current_index, 0.5, 0.5)
        self._refresh_preview()
        self._set_status("Encuadre centrado")

    def _on_apply_center_to_all(self) -> None:
        cx = self.state.crop_center_x
        cy = self.state.crop_center_y
        self.state.apply_center_to_all(cx, cy)
        self._set_status("Encuadre aplicado a todas las fotos", "success")

    def _on_apply_preset_to_all(self, preset: str) -> None:
        self.state.apply_preset_to_all(preset)
        self.state.crop_preset = preset
        self._crop_bar.set_preset(preset)
        self._refresh_preview()
        self._set_status("Preset aplicado a todas las fotos", "success")

    def on_auto_enhance(self) -> None:
        self.state.enhance_enabled = not self.state.enhance_enabled
        self._controls.set_enhance_active(self.state.enhance_enabled)
        self._refresh_preview()
        estado = "activada" if self.state.enhance_enabled else "desactivada"
        self._set_status(f"Mejora autom\u00e1tica {estado}")

    def on_reset(self) -> None:
        self.state.reset()
        self._sliders.reset()
        self._crop_bar.reset()
        self._refresh_preview()
        self._set_status("Ajustes restablecidos")

    def on_export_one(self) -> None:
        if self.state.original_image is None:
            return
        if not self.state.output_dir:
            self._set_status("Selecciona una carpeta destino para exportar",
                             "warning")
            return
        result = self.pipeline.process(self.state)
        if result is None:
            return
        exporter = Exporter(self.state.export)
        exporter.save(
            result,
            self.state.images[self.state.current_index],
            self.state.output_dir,
        )
        self._set_status("Foto exportada", "success")

    def on_export_all(self) -> None:
        if not self.state.images:
            self._set_status("Abre im\u00e1genes antes de exportar", "warning")
            return
        if not self.state.output_dir:
            self._set_status("Selecciona una carpeta destino para exportar",
                             "warning")
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
        self._set_status(f"{saved} fotos exportadas", "success")

    def on_process_folder(self) -> None:
        if not self.state.images:
            self._set_status("Abre im\u00e1genes antes de procesar", "warning")
            return
        if not self.state.output_dir:
            self._set_status("Selecciona una carpeta destino", "warning")
            return
        self._progress_bar["value"] = 0
        self._progress_label.config(text="")
        self._show_progress(True)
        self._set_status("Procesando carpeta...", "info")
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
            text=f"{progress.current}/{progress.total}  \u00b7  "
            f"errores: {progress.errors}  \u00b7  ETA: {eta:.0f}s"
        )

    def _on_batch_complete_ui(self) -> None:
        self._progress_bar["value"] = 100
        self._progress_label.config(text="")
        self._set_status("Procesamiento completado", "success")
        self._controls.enable_after_batch()
        self._root.after(2500, self._hide_progress)

    def _hide_progress(self) -> None:
        if self._progress_bar["value"] >= 100:
            self._show_progress(False)

    def run(self) -> None:
        self._root.mainloop()
