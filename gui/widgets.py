import os
import tkinter as tk
from tkinter import ttk
from typing import Callable

from PIL import Image, ImageTk

from config.theme import Colors, Fonts, Spacing
from utils.aspect_ratio import clamp_crop_center, get_crop_box


def _short_path(path: str, limit: int = 26) -> str:
    if not path:
        return ""
    name = os.path.basename(path.rstrip("\\/")) or path
    if len(name) <= limit:
        return name
    return name[: limit - 1] + "\u2026"


class TopBar(ttk.Frame):
    def __init__(self, parent: tk.Widget,
                 on_open: Callable[[], None] | None = None, **kwargs) -> None:
        super().__init__(parent, style="TopBar.TFrame", **kwargs)
        self._on_open = on_open
        self._build()

    def _build(self) -> None:
        self.columnconfigure(2, weight=1)
        bg = Colors.BG_CARD

        brand = ttk.Frame(self, style="TopBar.TFrame")
        brand.grid(row=0, column=0, padx=(Spacing.LG, Spacing.SM),
                   pady=10, sticky="w")

        mark = tk.Canvas(brand, width=30, height=30, bg=bg,
                         highlightthickness=0, bd=0)
        mark.pack(side=tk.LEFT)
        mark.create_polygon(
            7, 1, 23, 1, 29, 7, 29, 23, 23, 29, 7, 29, 1, 23, 1, 7,
            smooth=True, splinesteps=24, fill=Colors.ACCENT, outline="",
        )
        mark.create_text(15, 15, text="P", fill=Colors.TEXT_INVERT,
                         font=(Fonts.FAMILY, 12, "bold"))

        brand_text = ttk.Frame(brand, style="TopBar.TFrame")
        brand_text.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(brand_text, text="PhotoPilot", bg=bg, fg=Colors.TEXT,
                 font=Fonts.BRAND).pack(anchor="w")
        tk.Label(brand_text, text="Editor por lotes", bg=bg,
                 fg=Colors.TEXT_DIM, font=Fonts.MICRO).pack(anchor="w")

        meta = ttk.Frame(self, style="TopBar.TFrame")
        meta.grid(row=0, column=2, sticky="e", padx=Spacing.SM)
        self._count_label = tk.Label(meta, text="Sin imagenes", bg=bg,
                                     fg=Colors.TEXT, font=Fonts.SMALL)
        self._count_label.pack(anchor="e")
        self._folder_label = tk.Label(meta, text="Sin carpeta destino", bg=bg,
                                      fg=Colors.TEXT_DIM, font=Fonts.MICRO)
        self._folder_label.pack(anchor="e")

        actions = ttk.Frame(self, style="TopBar.TFrame")
        actions.grid(row=0, column=3, sticky="e", padx=(Spacing.SM, Spacing.LG),
                     pady=10)
        self._open_btn = ttk.Button(actions, text="Abrir im\u00e1genes",
                                    style="Primary.TButton",
                                    command=self._on_open)
        self._open_btn.pack(side=tk.LEFT)
        tk.Label(actions, text="Ctrl+O", bg=bg, fg=Colors.TEXT_DIM,
                 font=Fonts.MICRO).pack(side=tk.LEFT, padx=(8, 0))

        tk.Frame(self, bg=Colors.BORDER_SUBTLE, height=1).grid(
            row=1, column=0, columnspan=4, sticky="ew")

    def set_counts(self, count: int) -> None:
        if count == 0:
            text = "Sin im\u00e1genes"
        elif count == 1:
            text = "1 imagen"
        else:
            text = f"{count} im\u00e1genes"
        self._count_label.config(text=text)

    def set_output(self, path: str) -> None:
        text = f"Destino: {_short_path(path, 30)}" if path else "Sin carpeta destino"
        self._folder_label.config(
            text=text,
            fg=Colors.TEXT_MUTED if path else Colors.TEXT_DIM,
        )


class SidePanel(ttk.Frame):
    _THUMB_SIZE = 96
    _PAD = 6
    _RING = 2

    def __init__(self, parent: tk.Widget,
                 on_select: Callable[[int], None],
                 on_input: Callable[[], None],
                 on_output: Callable[[], None], **kwargs) -> None:
        super().__init__(parent, style="Sidebar.TFrame", width=300, **kwargs)
        self.grid_propagate(False)
        self.pack_propagate(False)
        self._on_select = on_select
        self._on_input = on_input
        self._on_output = on_output
        self._paths: list[str] = []
        self._thumb_refs: list[ImageTk.PhotoImage] = []
        self._items: list[dict] = []
        self._selected_index: int = -1
        self._cols: int = 1
        self._build()

    def _build(self) -> None:
        header = tk.Frame(self, bg=Colors.BG_DEEP)
        header.pack(fill=tk.X, padx=Spacing.LG, pady=(Spacing.LG, Spacing.SM))
        tk.Label(header, text="Fotograf\u00edas", bg=Colors.BG_DEEP,
                 fg=Colors.TEXT, font=Fonts.SUBHEADER).pack(side=tk.LEFT)
        self._count_chip = tk.Label(header, text="0", bg=Colors.BG_INPUT,
                                    fg=Colors.TEXT_MUTED, font=Fonts.MICRO,
                                    padx=8, pady=1)
        self._count_chip.pack(side=tk.RIGHT)

        container = tk.Frame(self, bg=Colors.BG_DEEP)
        container.pack(fill=tk.BOTH, expand=True, padx=(10, 2), pady=(0, 4))

        self._canvas = tk.Canvas(container, highlightthickness=0, bd=0,
                                 bg=Colors.BG_DEEP, takefocus=True)
        self._scroll = ttk.Scrollbar(container, orient=tk.VERTICAL,
                                     command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scroll.set)
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self._scroll.grid(row=0, column=1, sticky="ns")
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._scroll_visible = True

        self._grid_frame = tk.Frame(self._canvas, bg=Colors.BG_DEEP)
        self._window_id = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw")
        self._grid_frame.bind(
            "<Configure>", self._on_grid_configure)

        self._empty_title = self._canvas.create_text(
            0, 0, text="Sin fotos", fill=Colors.TEXT_MUTED,
            font=Fonts.SMALL, tags="empty", anchor="center")
        self._empty_hint = self._canvas.create_text(
            0, 0, text="Arrastra im\u00e1genes o abre\nuna carpeta", fill=Colors.TEXT_DIM,
            font=Fonts.MICRO, tags="empty", anchor="center", justify="center")

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind("<Enter>", self._bind_wheel)
        self._canvas.bind("<Leave>", self._unbind_wheel)
        self._canvas.bind("<Button-1>", lambda e: self._canvas.focus_set())
        for key, delta in (("<Left>", -1), ("<Right>", 1)):
            self._canvas.bind(key, lambda e, d=delta: self._move_selection(d))
        self._canvas.bind("<Up>", lambda e: self._move_selection(-self._cols))
        self._canvas.bind("<Down>", lambda e: self._move_selection(self._cols))
        self._canvas.bind("<Home>", lambda e: self._move_selection(-10 ** 6))
        self._canvas.bind("<End>", lambda e: self._move_selection(10 ** 6))

        tk.Frame(self, bg=Colors.BORDER_SUBTLE, height=1).pack(
            fill=tk.X, padx=Spacing.LG, pady=(2, Spacing.SM))

        folders = tk.Frame(self, bg=Colors.BG_DEEP)
        folders.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Label(folders, text="CARPETAS", bg=Colors.BG_DEEP,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(
                     anchor="w", padx=2, pady=(0, 4))

        self._input_btn = ttk.Button(folders, text="Carpeta origen",
                                     style="Secondary.TButton",
                                     command=self._on_input)
        self._input_btn.pack(fill=tk.X, pady=(0, 4))
        self._input_hint = tk.Label(folders, text="Sin carpeta", bg=Colors.BG_DEEP,
                                    fg=Colors.TEXT_DIM, font=Fonts.MICRO,
                                    anchor="w")
        self._input_hint.pack(fill=tk.X, padx=2, pady=(0, 6))

        self._output_btn = ttk.Button(folders, text="Carpeta destino",
                                      style="Secondary.TButton",
                                      command=self._on_output)
        self._output_btn.pack(fill=tk.X, pady=(0, 4))
        self._output_hint = tk.Label(folders, text="Sin carpeta",
                                     bg=Colors.BG_DEEP, fg=Colors.TEXT_DIM,
                                     font=Fonts.MICRO, anchor="w")
        self._output_hint.pack(fill=tk.X, padx=2)

    def _bind_wheel(self, _event=None) -> None:
        self._canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _on_grid_configure(self, _event=None) -> None:
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._sync_scrollbar()

    def _sync_scrollbar(self) -> None:
        bbox = self._canvas.bbox("all")
        if not bbox:
            return
        needed = (bbox[3] - bbox[1]) > self._canvas.winfo_height() + 1
        if needed and not self._scroll_visible:
            self._scroll.grid()
            self._scroll_visible = True
        elif not needed and self._scroll_visible:
            self._scroll.grid_remove()
            self._scroll_visible = False

    def _unbind_wheel(self, _event=None) -> None:
        self._canvas.unbind_all("<MouseWheel>")

    def _on_wheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_canvas_configure(self, event: tk.Event) -> None:
        cw = event.width
        self._canvas.itemconfigure(self._window_id, width=cw)
        cx, cy = cw // 2, max(80, event.height // 2)
        self._canvas.coords(self._empty_title, cx, cy - 10)
        self._canvas.coords(self._empty_hint, cx, cy + 14)
        if self._layout_items(cw) and self._selected_index >= 0:
            self._highlight_item(self._selected_index)
        self._sync_scrollbar()

    def load(self, paths: list[str]) -> None:
        self._paths = paths
        self._selected_index = -1
        self._thumb_refs.clear()
        for item in self._items:
            item["frame"].destroy()
        self._items.clear()

        for idx, path in enumerate(paths):
            self._items.append(self._create_item(idx, path))

        self._cols = 0
        self._layout_items(self._canvas.winfo_width() or 220)
        self._canvas.after(50, lambda: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._count_chip.config(text=str(len(paths)))
        state = "hidden" if paths else "normal"
        self._canvas.itemconfigure(self._empty_title, state=state)
        self._canvas.itemconfigure(self._empty_hint, state=state)
        self._canvas.after_idle(self._sync_scrollbar)

    def _layout_items(self, width: int) -> bool:
        cols = max(1, width // (self._THUMB_SIZE + self._PAD * 2))
        if cols == self._cols:
            return False
        for old_col in range(self._cols):
            self._grid_frame.grid_columnconfigure(old_col, weight=0)
        self._cols = cols
        for col in range(cols):
            self._grid_frame.grid_columnconfigure(col, weight=1)
        for idx, item in enumerate(self._items):
            item["frame"].grid(
                row=idx // cols, column=idx % cols,
                padx=self._PAD, pady=self._PAD, sticky="n")
        return True

    def _create_item(self, idx: int, path: str) -> dict:
        frame = tk.Frame(self._grid_frame, bg=Colors.BG_DEEP, bd=0,
                         highlightthickness=self._RING,
                         highlightbackground=Colors.BG_DEEP,
                         highlightcolor=Colors.BG_DEEP, cursor="hand2")
        thumb = self._make_thumb(path)
        self._thumb_refs.append(thumb)

        img_label = tk.Label(frame, image=thumb, bg=Colors.BG_DEEP,
                             bd=0, highlightthickness=0)
        img_label.pack(padx=4, pady=(4, 2))

        name = os.path.basename(path)
        if len(name) > 15:
            name = name[:14] + "\u2026"
        name_label = tk.Label(frame, text=name, font=Fonts.THUMB_NAME,
                              bg=Colors.BG_DEEP, fg=Colors.TEXT_SIDEBAR)
        name_label.pack(pady=(0, 4))

        widgets = (frame, img_label, name_label)
        for widget in widgets:
            widget.bind("<Button-1>", lambda e, i=idx: self._on_thumb_click(i))
            widget.bind("<Enter>", lambda e, i=idx: self._hover_item(i, True))
            widget.bind("<Leave>", lambda e, i=idx: self._hover_item(i, False))
        return {"frame": frame, "image": img_label, "name": name_label}

    def _make_thumb(self, path: str) -> ImageTk.PhotoImage:
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((self._THUMB_SIZE, self._THUMB_SIZE), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            placeholder = Image.new("RGB", (self._THUMB_SIZE, self._THUMB_SIZE),
                                    color=Colors.BG_SIDEBAR_HOVER)
            return ImageTk.PhotoImage(placeholder)

    def _paint_item(self, index: int, bg: str, ring: str) -> None:
        item = self._items[index]
        item["frame"].configure(bg=bg, highlightbackground=ring,
                                highlightcolor=ring)
        item["image"].configure(bg=bg)
        item["name"].configure(
            bg=bg,
            fg=Colors.TEXT if index == self._selected_index else Colors.TEXT_SIDEBAR,
        )

    def _hover_item(self, index: int, hovered: bool) -> None:
        if index == self._selected_index or index >= len(self._items):
            return
        if hovered:
            self._paint_item(index, Colors.BG_CARD, Colors.BG_CARD)
        else:
            self._paint_item(index, Colors.BG_DEEP, Colors.BG_DEEP)

    def _on_thumb_click(self, index: int) -> None:
        self._canvas.focus_set()
        self._highlight_item(index)
        self._on_select(index)

    def _highlight_item(self, index: int) -> None:
        if index >= len(self._items):
            return
        previous = self._selected_index
        self._selected_index = index
        if previous >= 0 and previous < len(self._items) and previous != index:
            self._paint_item(previous, Colors.BG_DEEP, Colors.BG_DEEP)
        self._paint_item(index, Colors.BG_HOVER, Colors.ACCENT)

    def _move_selection(self, delta: int) -> str:
        if not self._items:
            return "break"
        base = self._selected_index if self._selected_index >= 0 else 0
        index = max(0, min(len(self._items) - 1, base + delta))
        self._on_thumb_click(index)
        item = self._items[index]["frame"]
        total = max(1, self._grid_frame.winfo_height())
        self._canvas.yview_moveto(max(0.0, (item.winfo_y() - 40) / total))
        return "break"

    def select(self, index: int) -> None:
        self._highlight_item(index)

    def set_enabled(self, enabled: bool) -> None:
        self._output_btn.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def set_input_path(self, path: str) -> None:
        if path:
            self._input_hint.config(text=_short_path(path), fg=Colors.TEXT_MUTED)
        else:
            self._input_hint.config(text="Sin carpeta", fg=Colors.TEXT_DIM)

    def set_output_path(self, path: str) -> None:
        if path:
            self._output_hint.config(text=_short_path(path), fg=Colors.TEXT_MUTED)
        else:
            self._output_hint.config(text="Sin carpeta", fg=Colors.TEXT_DIM)


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
        self._drag_origin_pos = None
        self._drag_origin_center = (0.5, 0.5)
        self._drag_active = False
        self._disp_offset = (0, 0)
        self._disp_scale = 1.0
        self._overlay_items: list[int] = []
        self._has_image = False
        self._hint_text: str | None = None
        self._hint_items: list[int] = []
        self._render_source: Image.Image | None = None
        self._resize_job: str | None = None
        self._build()

    def _build(self) -> None:
        self._canvas = tk.Canvas(
            self, bg=Colors.BG_PREVIEW, highlightthickness=0,
            relief="flat", bd=0,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._image_id: int | None = None
        self._canvas.bind("<Configure>", self._on_resize)
        self._draw_empty()

    def _on_resize(self, event: tk.Event = None) -> None:
        if self._drag_active:
            return
        if self._resize_job:
            self._canvas.after_cancel(self._resize_job)
        self._resize_job = self._canvas.after(60, self._rerender)

    def _rerender(self) -> None:
        self._resize_job = None
        if self._render_source is not None:
            self._display(self._render_source)
        else:
            self._draw_empty()
        self._draw_hint()

    def _draw_empty(self) -> None:
        self._canvas.delete("empty")
        if self._has_image:
            return
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        cx, cy = cw // 2, ch // 2

        w, h = 132, 96
        x0, y0 = cx - w // 2, cy - h // 2 - 26
        self._canvas.create_rectangle(
            x0, y0, x0 + w, y0 + h, outline=Colors.BORDER, width=1,
            dash=(4, 4), tags="empty")
        # Minimal aperture/photo glyph drawn with primitives.
        self._canvas.create_oval(
            x0 + 20, y0 + 24, x0 + 46, y0 + 50,
            outline=Colors.TEXT_DIM, width=2, tags="empty")
        self._canvas.create_line(
            x0 + 22, y0 + 72, x0 + 50, y0 + 44, x0 + 72, y0 + 66,
            x0 + 92, y0 + 42, x0 + 112, y0 + 68,
            fill=Colors.TEXT_DIM, width=2, joinstyle="round", tags="empty")

        self._canvas.create_text(
            cx, y0 + h + 34, text="Sin imagen seleccionada",
            fill=Colors.TEXT_MUTED, font=Fonts.SUBHEADER, tags="empty")
        self._canvas.create_text(
            cx, y0 + h + 56, text="Abre una carpeta o arrastra fotos aqu\u00ed",
            fill=Colors.TEXT_DIM, font=Fonts.SMALL, tags="empty")
        self._canvas.create_text(
            cx, y0 + h + 82, text="Ctrl+O  Abrir im\u00e1genes",
            fill=Colors.TEXT_DIM, font=Fonts.MICRO, tags="empty")

    def _draw_hint(self) -> None:
        for item in self._hint_items:
            self._canvas.delete(item)
        self._hint_items.clear()
        if not self._hint_text or not self._has_image:
            return
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        text_id = self._canvas.create_text(
            cw // 2, ch - 30, text=self._hint_text, fill=Colors.TEXT_MUTED,
            font=Fonts.MICRO, tags="hint")
        bbox = self._canvas.bbox(text_id)
        if bbox:
            pad_x, pad_y = 10, 5
            bg_id = self._canvas.create_rectangle(
                bbox[0] - pad_x, bbox[1] - pad_y,
                bbox[2] + pad_x, bbox[3] + pad_y,
                fill=Colors.BG_OVERLAY, outline=Colors.BORDER,
                tags="hint")
            self._canvas.tag_lower(bg_id, text_id)
            self._hint_items.extend([bg_id, text_id])
        else:
            self._hint_items.append(text_id)

    def set_hint(self, text: str | None) -> None:
        self._hint_text = text
        self._draw_hint()

    def set_drag_callbacks(self, on_move, on_release=None) -> None:
        self._drag_move_cb = on_move
        self._drag_end_cb = on_release

    def show_original(self, image: Image.Image) -> None:
        self._orig_img = None
        self._render_source = image
        self._display(image)

    def show_result(self, image: Image.Image) -> None:
        self._orig_img = None
        self._render_source = image
        self._display(image)

    def prepare_drag(self, orig_img: Image.Image,
                     target_w: int, target_h: int,
                     cx: float = 0.5, cy: float = 0.5) -> tuple[float, float]:
        self._orig_img = orig_img
        self._orig_size = (orig_img.width, orig_img.height)
        self._crop_target = (target_w, target_h)
        self._crop_cx, self._crop_cy = clamp_crop_center(
            orig_img.width, orig_img.height, target_w, target_h, cx, cy)
        return self._crop_cx, self._crop_cy

    def update_overlay(self, cx: float, cy: float) -> None:
        self._crop_cx, self._crop_cy = self._clamp_center(cx, cy)
        if self._orig_size and self._crop_target:
            self._draw_overlay(self._crop_cx, self._crop_cy)

    def _clamp_center(self, cx: float, cy: float) -> tuple[float, float]:
        if not self._orig_size or not self._crop_target:
            return (max(0.0, min(1.0, cx)), max(0.0, min(1.0, cy)))
        w, h = self._orig_size
        tw, th = self._crop_target
        return clamp_crop_center(w, h, tw, th, cx, cy)

    def _draw_overlay(self, cx: float, cy: float) -> None:
        self._clear_overlay()
        if not self._orig_size or not self._crop_target or not self._photo:
            return
        img_w, img_h = self._orig_size
        tw, th = self._crop_target
        cw = self._canvas.winfo_width() or 800
        ch = self._canvas.winfo_height() or 540
        crop_w, crop_h = get_crop_box(img_w, img_h, tw, th)
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
        for box in (
            (0, 0, cw, r[1]),
            (0, r[3], cw, ch),
            (0, r[1], r[0], r[3]),
            (r[2], r[1], cw, r[3]),
        ):
            self._overlay_items.append(
                self._canvas.create_rectangle(*box, fill=Colors.BG_PREVIEW,
                                              stipple="gray50", outline="",
                                              tags="overlay"))
        self._draw_thirds(r)
        self._draw_corners(r)

    def _draw_thirds(self, r: tuple[float, float, float, float]) -> None:
        x0, y0, x1, y1 = r
        for i in (1, 2):
            x = x0 + (x1 - x0) * i / 3
            y = y0 + (y1 - y0) * i / 3
            self._overlay_items.append(self._canvas.create_line(
                x, y0, x, y1, fill=Colors.TEXT_INVERT, width=1,
                stipple="gray50", tags="overlay"))
            self._overlay_items.append(self._canvas.create_line(
                x0, y, x1, y, fill=Colors.TEXT_INVERT, width=1,
                stipple="gray50", tags="overlay"))

    def _draw_corners(self, r: tuple[float, float, float, float]) -> None:
        x0, y0, x1, y1 = r
        length = 18
        for (sx, sy, dx, dy) in (
            (x0, y0, 1, 1), (x1, y0, -1, 1),
            (x0, y1, 1, -1), (x1, y1, -1, -1),
        ):
            self._overlay_items.append(self._canvas.create_line(
                sx, sy, sx + length * dx, sy, fill=Colors.TEXT_INVERT,
                width=3, tags="overlay"))
            self._overlay_items.append(self._canvas.create_line(
                sx, sy, sx, sy + length * dy, fill=Colors.TEXT_INVERT,
                width=3, tags="overlay"))

    def _clear_overlay(self) -> None:
        for item in self._overlay_items:
            self._canvas.delete(item)
        self._overlay_items.clear()

    def enable_drag(self) -> None:
        self._canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self._canvas.bind("<B1-Motion>", self._on_drag_move)
        self._canvas.bind("<ButtonRelease-1>", self._on_drag_release)
        self._canvas.configure(cursor="fleur")
        self.set_hint("Arrastra para encuadrar \u00b7 gu\u00edas de tercios")

    def disable_drag(self) -> None:
        self._drag_active = False
        self._drag_origin_pos = None
        self._canvas.unbind("<ButtonPress-1>")
        self._canvas.unbind("<B1-Motion>")
        self._canvas.unbind("<ButtonRelease-1>")
        self._canvas.configure(cursor="")
        self.set_hint(None)

    def _on_drag_start(self, event: tk.Event) -> None:
        if not self._orig_img or not self._crop_target:
            return
        self._drag_active = True
        self._drag_origin_pos = (event.x, event.y)
        self._drag_origin_center = self._clamp_center(self._crop_cx,
                                                      self._crop_cy)
        self._crop_cx, self._crop_cy = self._drag_origin_center
        self.set_hint(None)
        self._display(self._orig_img)
        self._draw_overlay(self._crop_cx, self._crop_cy)
        self._canvas.focus_set()

    def _on_drag_move(self, event: tk.Event) -> None:
        if (not self._drag_active or not self._drag_origin_pos
                or not self._orig_size):
            return
        ow, oh = self._orig_size
        s = self._disp_scale
        if s <= 0:
            return
        dx = (event.x - self._drag_origin_pos[0]) / (s * ow)
        dy = (event.y - self._drag_origin_pos[1]) / (s * oh)
        cx, cy = self._clamp_center(
            self._drag_origin_center[0] + dx,
            self._drag_origin_center[1] + dy,
        )
        self._crop_cx, self._crop_cy = cx, cy
        self._draw_overlay(cx, cy)
        if self._drag_move_cb:
            self._drag_move_cb(cx, cy)

    def _on_drag_release(self, event: tk.Event) -> None:
        self._drag_active = False
        self._drag_origin_pos = None
        self._clear_overlay()
        if self._drag_end_cb:
            self._drag_end_cb()

    def _display(self, image: Image.Image) -> None:
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw < 80 or ch < 80:
            return
        margin = 40
        img = image.copy()
        img.thumbnail((max(1, cw - margin * 2), max(1, ch - margin * 2)),
                      Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)
        self._show_image(self._photo)

    def _show_image(self, photo: ImageTk.PhotoImage) -> None:
        self._has_image = True
        self._canvas.delete("empty")
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
        self._canvas.tag_lower(self._image_id)
        self._draw_hint()

    def clear(self) -> None:
        self._has_image = False
        self._photo = None
        self._orig_size = None
        self._render_source = None
        self._canvas.delete("all")
        self._draw_empty()


class ControlPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, app, **kwargs) -> None:
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._app = app
        self._build()

    def _build(self) -> None:
        head = tk.Frame(self, bg=Colors.BG_CARD)
        head.pack(fill=tk.X, padx=14, pady=(10, 6))
        tk.Label(head, text="HERRAMIENTAS", bg=Colors.BG_CARD,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(side=tk.LEFT)

        body = tk.Frame(self, bg=Colors.BG_CARD)
        body.pack(fill=tk.X, padx=12, pady=(0, 10))

        self._enhance_btn = ttk.Button(
            body, text="Mejorar autom\u00e1ticamente", style="ToggleOn.TButton",
            command=self._app.on_auto_enhance)
        self._enhance_btn.pack(fill=tk.X, pady=(0, 6))

        self._reset_btn = ttk.Button(body, text="Restablecer ajustes",
                                     style="Tool.TButton",
                                     command=self._app.on_reset)
        self._reset_btn.pack(fill=tk.X)

        self._section(body, "EXPORTAR", top=10)

        self._export_one_btn = ttk.Button(body, text="Exportar esta foto",
                                          style="Tool.TButton",
                                          command=self._app.on_export_one)
        self._export_one_btn.pack(fill=tk.X, pady=(0, 6))

        self._export_all_btn = ttk.Button(body, text="Exportar todas",
                                          style="Tool.TButton",
                                          command=self._app.on_export_all)
        self._export_all_btn.pack(fill=tk.X)

        self._section(body, "LOTE", top=10)

        self._process_btn = ttk.Button(body, text="Procesar carpeta",
                                       style="Primary.TButton",
                                       command=self._app.on_process_folder)
        self._process_btn.pack(fill=tk.X)

    def _section(self, parent: tk.Widget, text: str, top: int = 8) -> None:
        row = tk.Frame(parent, bg=Colors.BG_CARD)
        row.pack(fill=tk.X, pady=(top, 6))
        tk.Label(row, text=text, bg=Colors.BG_CARD, fg=Colors.TEXT_DIM,
                 font=Fonts.OVERLINE).pack(side=tk.LEFT)
        tk.Frame(row, bg=Colors.BORDER_SUBTLE, height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

    def set_enhance_active(self, active: bool) -> None:
        if active:
            self._enhance_btn.configure(style="ToggleOn.TButton",
                                        text="\u2713  Mejorar autom\u00e1ticamente")
        else:
            self._enhance_btn.configure(style="ToggleOff.TButton",
                                        text="Mejorar autom\u00e1ticamente")

    def _all_buttons(self) -> tuple:
        return (self._enhance_btn, self._reset_btn,
                self._export_one_btn, self._export_all_btn,
                self._process_btn)

    def set_buttons_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self._all_buttons():
            btn.config(state=state)

    def disable_during_batch(self) -> None:
        for btn in self._all_buttons():
            btn.config(state=tk.DISABLED)

    def enable_after_batch(self) -> None:
        for btn in self._all_buttons():
            btn.config(state=tk.NORMAL)
