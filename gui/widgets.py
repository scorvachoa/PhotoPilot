import os
import tkinter as tk
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageTk

from config.theme import Colors, Fonts


class TopBar(ttk.Frame):
    def __init__(self, parent: tk.Widget,
                 on_open: Callable[[], None] | None = None, **kwargs) -> None:
        super().__init__(parent, style="TopBar.TFrame", **kwargs)
        self._on_open = on_open
        self._build()

    def _build(self) -> None:
        logo_frame = ttk.Frame(self, style="TopBar.TFrame")
        logo_frame.grid(row=0, column=0, padx=(16, 8), pady=12)
        ttk.Label(logo_frame, text="PhotoPilot", font=Fonts.TITLE,
                  foreground=Colors.ACCENT,
                  style="TopBar.TFrame").pack(side=tk.LEFT)

        ttk.Button(self, text="Abrir imagenes", style="Primary.TButton",
                   command=self._on_open).grid(row=0, column=1, padx=16)


class SidePanel(ttk.Frame):
    _THUMB_SIZE = 85
    _PAD = 4

    def __init__(self, parent: tk.Widget,
                 on_select: Callable[[int], None],
                 on_input: Callable[[], None],
                 on_output: Callable[[], None], **kwargs) -> None:
        super().__init__(parent, style="Sidebar.TFrame", width=220, **kwargs)
        self._on_select = on_select
        self._on_input = on_input
        self._on_output = on_output
        self._paths: list[str] = []
        self._thumb_refs: list[ImageTk.PhotoImage] = []
        self._item_frames: list[tk.Frame] = []
        self._selected_index: int = -1
        self._build()

    def _build(self) -> None:
        header = ttk.Frame(self, style="Sidebar.TFrame")
        header.pack(fill=tk.X, padx=14, pady=(14, 8))
        ttk.Label(header, text="Fotografias",
                  style="SidebarHeader.TLabel").pack(side=tk.LEFT)
        self._count_label = ttk.Label(header, text="",
                                      style="Sidebar.TFrame",
                                      foreground=Colors.TEXT_SIDEBAR,
                                      font=Fonts.SMALL)
        self._count_label.pack(side=tk.RIGHT)

        container = tk.Frame(self, bg=Colors.BG_SIDEBAR)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 4))

        self._canvas = tk.Canvas(container, highlightthickness=0, bd=0,
                                 bg=Colors.BG_SIDEBAR)
        scroll = ttk.Scrollbar(container, orient=tk.VERTICAL,
                               command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=Colors.BG_SIDEBAR)
        self._canvas.create_window((0, 0), window=self._grid_frame,
                                   anchor="nw")
        self._grid_frame.bind("<Configure>",
                              lambda e: self._canvas.configure(
                                  scrollregion=self._canvas.bbox("all")))

        sep_line = tk.Frame(self, bg=Colors.BG_SIDEBAR_HOVER, height=1)
        sep_line.pack(fill=tk.X, padx=10, pady=(2, 6))

        btn_frame = tk.Frame(self, bg=Colors.BG_SIDEBAR)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._input_btn = ttk.Button(btn_frame, text="Carpeta origen",
                                     style="Secondary.TButton",
                                     command=self._on_input)
        self._input_btn.pack(fill=tk.X, pady=2)

        self._output_btn = ttk.Button(btn_frame, text="Carpeta destino",
                                      style="Secondary.TButton",
                                      command=self._on_output)
        self._output_btn.pack(fill=tk.X, pady=2)

    def load(self, paths: list[str]) -> None:
        self._paths = paths
        self._selected_index = -1
        self._thumb_refs.clear()
        for f in self._item_frames:
            f.destroy()
        self._item_frames.clear()

        cw = self._canvas.winfo_width() or 200
        cols = max(1, cw // (self._THUMB_SIZE + self._PAD * 2))

        for idx, path in enumerate(paths):
            row = idx // cols
            col = idx % cols
            item = self._create_item(idx, path)
            item.grid(row=row, column=col, padx=self._PAD, pady=self._PAD,
                      sticky="n")
            self._item_frames.append(item)
        self._canvas.after(50, lambda: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._count_label.config(text=str(len(paths)))

    def _create_item(self, idx: int, path: str) -> tk.Frame:
        frame = tk.Frame(self._grid_frame, bg=Colors.BG_SIDEBAR,
                         cursor="hand2", bd=0)
        thumb = self._make_thumb(path)
        self._thumb_refs.append(thumb)

        img_label = tk.Label(frame, image=thumb, bg=Colors.BG_SIDEBAR,
                             bd=0, highlightthickness=0)
        img_label.pack(padx=4, pady=(4, 1))

        name = os.path.basename(path)
        if len(name) > 14:
            name = name[:12] + ".."
        name_label = tk.Label(frame, text=name, font=Fonts.THUMB_NAME,
                              bg=Colors.BG_SIDEBAR, fg=Colors.TEXT_SIDEBAR)
        name_label.pack(pady=(0, 4))

        frame.bind("<Button-1>", lambda e, i=idx: self._on_thumb_click(i))
        img_label.bind("<Button-1>", lambda e, i=idx: self._on_thumb_click(i))
        name_label.bind("<Button-1>", lambda e, i=idx: self._on_thumb_click(i))
        return frame

    def _make_thumb(self, path: str) -> ImageTk.PhotoImage:
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((self._THUMB_SIZE, self._THUMB_SIZE), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            placeholder = Image.new("RGB", (self._THUMB_SIZE, self._THUMB_SIZE),
                                    color=Colors.BG_SIDEBAR_HOVER)
            return ImageTk.PhotoImage(placeholder)

    def _on_thumb_click(self, index: int) -> None:
        self._highlight_item(index)
        self._on_select(index)

    def _highlight_item(self, index: int) -> None:
        for i, f in enumerate(self._item_frames):
            bg = Colors.ACCENT if i == index else Colors.BG_SIDEBAR
            f.configure(bg=bg)
            for child in f.winfo_children():
                try:
                    child.configure(bg=bg)
                except Exception:
                    pass
        self._selected_index = index

    def select(self, index: int) -> None:
        self._highlight_item(index)

    def set_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        self._output_btn.config(state=state)


class PreviewPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, style="Preview.TFrame", **kwargs)
        self._photo: ImageTk.PhotoImage | None = None
        self._drag_move_cb = None
        self._drag_end_cb = None
        self._orig_img: Image.Image | None = None
        self._orig_size = None
        self._crop_target = None
        self._crop_cx = 0.5
        self._crop_cy = 0.5
        self._drag_start_pos = None
        self._drag_active = False
        self._disp_offset = (0, 0)
        self._disp_scale = 1.0
        self._overlay_items: list[int] = []
        self._build()

    def _build(self) -> None:
        self._canvas = tk.Canvas(
            self, bg=Colors.BG_PREVIEW, highlightthickness=0,
            relief="flat", bd=0,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._overlay_text = self._canvas.create_text(
            400, 270, text="Selecciona una carpeta de imagenes",
            fill=Colors.TEXT_DIM, font=("Segoe UI", 14), tags="text",
        )
        self._sub_text = self._canvas.create_text(
            400, 310, text="Usa el boton superior para comenzar",
            fill=Colors.TEXT_DIM, font=("Segoe UI", 10), tags="text",
        )
        self._image_id: int | None = None
        self._canvas.bind("<Configure>", self._on_resize)

    def set_drag_callbacks(self, on_move, on_release=None) -> None:
        self._drag_move_cb = on_move
        self._drag_end_cb = on_release

    def _on_resize(self, event: tk.Event = None) -> None:
        if self._photo:
            self._show_image(self._photo)

    def show_original(self, image: Image.Image) -> None:
        self._orig_img = None
        self._display(image)

    def show_result(self, image: Image.Image) -> None:
        self._orig_img = None
        self._display(image)

    def prepare_drag(self, orig_img: Image.Image,
                     target_w: int, target_h: int,
                     cx: float = 0.5, cy: float = 0.5) -> None:
        self._orig_img = orig_img
        self._orig_size = (orig_img.width, orig_img.height)
        self._crop_target = (target_w, target_h)
        self._crop_cx = cx
        self._crop_cy = cy

    def update_overlay(self, cx: float, cy: float) -> None:
        self._crop_cx = cx
        self._crop_cy = cy
        if self._orig_size and self._crop_target:
            self._draw_overlay(cx, cy)

    def _draw_overlay(self, cx: float, cy: float) -> None:
        self._clear_overlay()
        if not self._orig_size or not self._crop_target or not self._photo:
            return
        img_w, img_h = self._orig_size
        tw, th = self._crop_target
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        aspect = tw / th
        if img_w / img_h > aspect:
            crop_h = img_h
            crop_w = img_h * aspect
        else:
            crop_w = img_w
            crop_h = img_w / aspect
        crop_x = cx * img_w - crop_w / 2
        crop_y = cy * img_h - crop_h / 2
        crop_x = max(0, min(crop_x, img_w - crop_w))
        crop_y = max(0, min(crop_y, img_h - crop_h))
        ox, oy = self._disp_offset
        s = self._disp_scale
        r = (
            ox + crop_x * s, oy + crop_y * s,
            ox + (crop_x + crop_w) * s, oy + (crop_y + crop_h) * s,
        )
        self._overlay_items.append(
            self._canvas.create_rectangle(*r, outline=Colors.ACCENT,
                                          width=2, tags="overlay"))
        self._overlay_items.append(
            self._canvas.create_rectangle(0, 0, cw, r[1],
                fill="#0d0d1a", stipple="gray25", outline="", tags="overlay"))
        self._overlay_items.append(
            self._canvas.create_rectangle(0, r[3], cw, ch,
                fill="#0d0d1a", stipple="gray25", outline="", tags="overlay"))
        self._overlay_items.append(
            self._canvas.create_rectangle(0, r[1], r[0], r[3],
                fill="#0d0d1a", stipple="gray25", outline="", tags="overlay"))
        self._overlay_items.append(
            self._canvas.create_rectangle(r[2], r[1], cw, r[3],
                fill="#0d0d1a", stipple="gray25", outline="", tags="overlay"))

    def _clear_overlay(self) -> None:
        for item in self._overlay_items:
            self._canvas.delete(item)
        self._overlay_items.clear()

    def enable_drag(self) -> None:
        self._canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self._canvas.bind("<B1-Motion>", self._on_drag_move)
        self._canvas.bind("<ButtonRelease-1>", self._on_drag_release)
        self._canvas.configure(cursor="fleur")

    def disable_drag(self) -> None:
        self._drag_active = False
        self._drag_start_pos = None
        self._canvas.unbind("<ButtonPress-1>")
        self._canvas.unbind("<B1-Motion>")
        self._canvas.unbind("<ButtonRelease-1>")
        self._canvas.configure(cursor="")

    def _on_drag_start(self, event: tk.Event) -> None:
        if not self._orig_img or not self._crop_target:
            return
        self._drag_start_pos = (event.x, event.y)
        self._drag_active = True
        self._display(self._orig_img)
        self._draw_overlay(self._crop_cx, self._crop_cy)

    def _on_drag_move(self, event: tk.Event) -> None:
        if not self._drag_active or not self._drag_start_pos or not self._orig_size:
            return
        ow, oh = self._orig_size
        dx = event.x - self._drag_start_pos[0]
        dy = event.y - self._drag_start_pos[1]
        s = self._disp_scale
        if s == 0:
            return
        self._drag_start_pos = (event.x, event.y)
        if self._drag_move_cb:
            self._drag_move_cb(dx / (s * ow), dy / (s * oh))

    def _on_drag_release(self, event: tk.Event) -> None:
        self._drag_active = False
        self._drag_start_pos = None
        self._clear_overlay()
        if self._drag_end_cb:
            self._drag_end_cb()

    def _display(self, image: Image.Image) -> None:
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        margin = 40
        img = image.copy()
        img.thumbnail((cw - margin * 2, ch - margin * 2), Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)
        self._show_image(self._photo)

    def _show_image(self, photo: ImageTk.PhotoImage) -> None:
        self._canvas.delete("text")
        if self._image_id:
            self._canvas.delete(self._image_id)
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        x = max(0, (cw - photo.width()) // 2)
        y = max(0, (ch - photo.height()) // 2)
        self._disp_offset = (x, y)
        if self._orig_size:
            self._disp_scale = photo.width() / self._orig_size[0]
        else:
            self._disp_scale = 1.0
        self._image_id = self._canvas.create_image(
            x, y, anchor=tk.NW, image=photo,
        )


class ControlPanel(ttk.LabelFrame):
    def __init__(self, parent: tk.Widget, app, **kwargs) -> None:
        super().__init__(parent, text=" Herramientas ", width=210, **kwargs)
        self._app = app
        self._build()

    def _build(self) -> None:
        self._enhance_btn = ttk.Button(self, text="Mejorar automaticamente",
                                       style="Tool.TButton",
                                       command=self._app.on_auto_enhance)
        self._enhance_btn.pack(fill=tk.X, padx=10, pady=3)

        self._reset_btn = ttk.Button(self, text="Restablecer",
                                     style="Tool.TButton",
                                     command=self._app.on_reset)
        self._reset_btn.pack(fill=tk.X, padx=10, pady=3)

        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=10, pady=6)

        self._export_one_btn = ttk.Button(self, text="Exportar esta foto",
                                          style="Tool.TButton",
                                          command=self._app.on_export_one)
        self._export_one_btn.pack(fill=tk.X, padx=10, pady=3)

        self._export_all_btn = ttk.Button(self, text="Exportar todas",
                                          style="Tool.TButton",
                                          command=self._app.on_export_all)
        self._export_all_btn.pack(fill=tk.X, padx=10, pady=3)

        sep2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep2.pack(fill=tk.X, padx=10, pady=6)

        self._process_btn = ttk.Button(self, text="Procesar carpeta",
                                       style="Primary.TButton",
                                       command=self._app.on_process_folder)
        self._process_btn.pack(fill=tk.X, padx=10, pady=(4, 12))

    def set_enhance_active(self, active: bool) -> None:
        style = "Accent.TButton" if active else "Tool.TButton"
        self._enhance_btn.configure(style=style, text="Mejorar automaticamente")

    def set_buttons_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self._enhance_btn, self._reset_btn,
                    self._export_one_btn, self._export_all_btn,
                    self._process_btn):
            btn.config(state=state)

    def disable_during_batch(self) -> None:
        for btn in (self._enhance_btn, self._reset_btn,
                    self._export_one_btn, self._export_all_btn,
                    self._process_btn):
            btn.config(state=tk.DISABLED)

    def enable_after_batch(self) -> None:
        for btn in (self._enhance_btn, self._reset_btn,
                    self._export_one_btn, self._export_all_btn,
                    self._process_btn):
            btn.config(state=tk.NORMAL)
