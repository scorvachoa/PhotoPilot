import tkinter as tk
from tkinter import ttk
from typing import Callable

from config.theme import Colors, Fonts
from config.constants import CROP_PRESETS


def _preset_label(platform: str, name: str) -> str:
    return f"{platform} - {name}"


_PLATFORM_TEXT = {
    "Facebook": "Facebook",
    "Instagram": "Instagram",
    "LinkedIn": "LinkedIn",
    "Pinterest": "Pinterest",
    "Twitter / X": "X",
    "YouTube": "YouTube",
    "Personalizado": "Personalizado",
}


class _ChipRow(tk.Frame):
    """A row of chip buttons that wraps when the space is too narrow."""

    def __init__(self, parent: tk.Widget, gap: int = 4) -> None:
        super().__init__(parent, bg=Colors.BG_CARD)
        self._gap = gap
        self._buttons: list[ttk.Button] = []
        self.bind("<Configure>", lambda e: self._relayout())

    def set_buttons(self, buttons: list[ttk.Button]) -> None:
        self._buttons = buttons
        self.after_idle(self._relayout)

    def _relayout(self) -> None:
        width = self.winfo_width()
        if width <= 1:
            return
        if not self._buttons:
            self.configure(height=0)
            return
        x = y = line_h = 0
        for btn in self._buttons:
            w = btn.winfo_reqwidth()
            h = btn.winfo_reqheight()
            if x and x + w > width:
                x = 0
                y += line_h + self._gap
                line_h = 0
            btn.place(x=x, y=y)
            x += w + self._gap
            line_h = max(line_h, h)
        height = y + line_h
        if int(self.cget("height")) != height:
            self.configure(height=height)


class CropPresetBar(ttk.Frame):
    def __init__(self, parent: tk.Widget,
                 on_preset: Callable[[str], None],
                 on_reset_center: Callable[[], None],
                 on_apply_center_all: Callable[[], None],
                 on_apply_preset_all: Callable[[str], None],
                 **kwargs) -> None:
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._on_preset = on_preset
        self._on_reset_center = on_reset_center
        self._on_apply_center_all = on_apply_center_all
        self._on_apply_preset_all = on_apply_preset_all
        self._platforms = list(CROP_PRESETS.keys())
        self._active_platform = "Facebook"
        self._active_preset: str | None = None
        self._platform_btns: list[ttk.Button] = []
        self._preset_btns: list[ttk.Button] = []
        self._action_btns: list[ttk.Button] = []
        self._build()

    def _build(self) -> None:
        head = tk.Frame(self, bg=Colors.BG_CARD)
        head.pack(fill=tk.X, padx=14, pady=(10, 6))
        tk.Label(head, text="RECORTE", bg=Colors.BG_CARD,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(side=tk.LEFT)
        self._size_label = tk.Label(head, text="", bg=Colors.BG_CARD,
                                    fg=Colors.TEXT_MUTED, font=Fonts.MICRO)
        self._size_label.pack(side=tk.RIGHT)

        body = tk.Frame(self, bg=Colors.BG_CARD)
        body.pack(fill=tk.X, padx=12, pady=(0, 10))

        row1 = _ChipRow(body)
        row1.pack(fill=tk.X, pady=(0, 4))

        for plat in self._platforms:
            style = ("PlatformActive.TButton" if plat == self._active_platform
                     else "Platform.TButton")
            btn = ttk.Button(row1, text=_PLATFORM_TEXT.get(plat, plat),
                             style=style, cursor="hand2",
                             command=lambda p=plat: self._select_platform(p))
            self._platform_btns.append(btn)
        row1.set_buttons(self._platform_btns)

        self._row2 = _ChipRow(body)
        self._row2.pack(fill=tk.X, pady=(0, 6))
        self._update_presets()
        self._active_preset = _preset_label("Facebook", "Feed horizontal")

        action_row = tk.Frame(body, bg=Colors.BG_CARD)
        action_row.pack(fill=tk.X)

        tk.Label(action_row, text="ENCUADRE", bg=Colors.BG_CARD,
                 fg=Colors.TEXT_DIM, font=Fonts.OVERLINE).pack(
                     side=tk.LEFT, padx=(0, 8))

        self._add_action(action_row, "Centrar", self._on_reset_center)
        self._add_action(action_row, "Aplicar encuadre a todas",
                         self._on_apply_center_all)
        self._add_action(action_row, "Aplicar preset a todas",
                         lambda: self._on_apply_preset_all(
                             self._active_preset or ""))

        self._update_size_label()

    def _add_action(self, parent: tk.Widget, text: str,
                    command: Callable[[], None]) -> None:
        btn = ttk.Button(parent, text=text, style="Ghost.TButton",
                         cursor="hand2", command=command)
        btn.pack(side=tk.LEFT, padx=(0, 4))
        self._action_btns.append(btn)

    def _update_size_label(self) -> None:
        label = self._active_preset or ""
        platform, _, name = label.partition(" - ")
        size = CROP_PRESETS.get(platform, {}).get(name)
        self._size_label.config(
            text=f"{size[0]} \u00d7 {size[1]} px" if size else "")

    def _select_platform(self, platform: str) -> None:
        if platform == self._active_platform:
            return
        self._active_platform = platform
        for i, plat in enumerate(self._platforms):
            style = ("PlatformActive.TButton" if plat == platform
                     else "Platform.TButton")
            self._platform_btns[i].configure(style=style)
        self._update_presets()
        if self._active_preset:
            self._on_preset(self._active_preset)

    def _update_presets(self) -> None:
        for b in self._preset_btns:
            b.destroy()
        self._preset_btns.clear()

        presets = CROP_PRESETS.get(self._active_platform, {})
        if not presets:
            self._row2.set_buttons([])
            self._active_preset = None
            self._update_size_label()
            return

        for name in presets:
            label = _preset_label(self._active_platform, name)
            btn = ttk.Button(self._row2, text=name, style="Preset.TButton",
                             cursor="hand2",
                             command=lambda l=label: self._select_preset(l))
            btn._preset_label = label
            self._preset_btns.append(btn)
        self._row2.set_buttons(self._preset_btns)

        first_name = next(iter(presets))
        self._select_preset(_preset_label(self._active_platform, first_name),
                            update_preview=False)

    def _select_preset(self, label: str, update_preview: bool = True) -> None:
        self._active_preset = label
        self._highlight_preset(label)
        self._update_size_label()
        if update_preview:
            self._on_preset(label)

    def _highlight_preset(self, label: str) -> None:
        for b in self._preset_btns:
            active = getattr(b, "_preset_label", b.cget("text")) == label
            b.configure(style=("PresetActive.TButton" if active
                               else "Preset.TButton"))

    def set_preset(self, label: str) -> None:
        """Highlight a preset button without firing the callback."""
        self._active_preset = label
        platform = label.split(" - ")[0] if " - " in label else "Facebook"
        if platform in self._platforms and platform != self._active_platform:
            self._active_platform = platform
            for i, plat in enumerate(self._platforms):
                style = ("PlatformActive.TButton" if plat == platform
                         else "Platform.TButton")
                self._platform_btns[i].configure(style=style)
            self._update_presets()
        self._active_preset = label
        self._highlight_preset(label)
        self._update_size_label()

    def reset(self) -> None:
        self._active_platform = "Facebook"
        for i, plat in enumerate(self._platforms):
            style = ("PlatformActive.TButton" if plat == "Facebook"
                     else "Platform.TButton")
            self._platform_btns[i].configure(style=style)
        self._update_presets()
        self._active_preset = _preset_label("Facebook", "Feed horizontal")
        self._highlight_preset(self._active_preset)
        self._update_size_label()

    def set_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (*self._platform_btns, *self._preset_btns,
                    *self._action_btns):
            btn.config(state=state)
        cursor = "hand2" if enabled else ""
        for btn in (*self._platform_btns, *self._preset_btns,
                    *self._action_btns):
            btn.configure(cursor=cursor)

    def current_preset(self) -> str:
        if self._active_preset:
            return self._active_preset
        return _preset_label("Facebook", "Feed horizontal")
