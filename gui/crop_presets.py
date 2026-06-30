import tkinter as tk
from tkinter import ttk
from typing import Callable

from config.theme import Colors, Fonts
from config.constants import CROP_PRESETS


def _preset_label(platform: str, name: str) -> str:
    return f"{platform} - {name}"


_SHORT = {
    "Facebook": "FB", "Instagram": "IG", "LinkedIn": "In",
    "Pinterest": "Pin", "Twitter / X": "X", "YouTube": "YT",
    "Personalizado": "...",
}


class CropPresetBar(ttk.Frame):
    def __init__(self, parent: tk.Widget,
                 on_preset: Callable[[str], None],
                 on_reset_center: Callable[[], None],
                 on_apply_center_all: Callable[[], None],
                 on_apply_preset_all: Callable[[str], None],
                 **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_preset = on_preset
        self._platforms = list(CROP_PRESETS.keys())
        self._active_platform = "Facebook"
        self._active_preset: str | None = None
        self._platform_btns: list[ttk.Button] = []
        self._preset_btns: list[ttk.Button] = []
        self._action_btns: list[tk.Label] = []
        self._build(on_reset_center, on_apply_center_all, on_apply_preset_all)

    def _build(self, on_reset_center, on_apply_center_all, on_apply_preset_all) -> None:
        row1 = ttk.Frame(self, style="TFrame")
        row1.pack(fill=tk.X, padx=10, pady=(4, 2))

        for plat in self._platforms:
            style = "PlatformActive.TButton" if plat == self._active_platform else "Platform.TButton"
            text = _SHORT.get(plat, plat)
            btn = ttk.Button(row1, text=text, style=style,
                             command=lambda p=plat: self._select_platform(p))
            btn.pack(side=tk.LEFT, padx=2)
            self._platform_btns.append(btn)

        self._row2 = ttk.Frame(self, style="TFrame")
        self._row2.pack(fill=tk.X, padx=10, pady=(2, 2))
        self._update_presets()
        self._active_preset = _preset_label("Facebook", "Feed horizontal")

        action_row = ttk.Frame(self, style="TFrame")
        action_row.pack(fill=tk.X, padx=10, pady=(2, 4))

        ttk.Label(action_row, text="Encuadre:",
                  font=Fonts.SMALL, foreground=Colors.TEXT_MUTED).pack(
                      side=tk.LEFT, padx=(0, 6))

        self._make_btn(action_row, "Centrar", Colors.ACCENT, Colors.ACCENT_LIGHT,
                       lambda: on_reset_center())

        self._make_btn(action_row, "Aplicar encuadre a todas",
                       Colors.TEXT_INVERT, Colors.ACCENT,
                       lambda: on_apply_center_all())

        ttk.Label(action_row, text="   Preset:",
                  font=Fonts.SMALL, foreground=Colors.TEXT_MUTED).pack(
                      side=tk.LEFT, padx=(6, 6))

        self._make_btn(action_row, "Aplicar preset a todas",
                       Colors.TEXT_INVERT, Colors.SECONDARY,
                       lambda: on_apply_preset_all(self._active_preset or ""))

    def _make_btn(self, parent, text, fg, bg, cmd) -> tk.Label:
        btn = tk.Label(parent, text=text, font=("Segoe UI", 8),
                       fg=fg, bg=bg, cursor="hand2", padx=8, pady=2)
        btn.pack(side=tk.LEFT, padx=2)
        btn.bind("<Button-1>", lambda e: cmd())
        self._bind_hover(btn, fg, bg)
        self._action_btns.append(btn)
        return btn

    def _bind_hover(self, btn, fg, bg) -> None:
        def on_enter(e):
            if bg == Colors.ACCENT:
                btn.configure(bg=Colors.ACCENT_HOVER)
            elif bg == Colors.SECONDARY:
                btn.configure(bg=Colors.SECONDARY_HOVER)
        def on_leave(e):
            btn.configure(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def _select_platform(self, platform: str) -> None:
        self._active_platform = platform
        for i, plat in enumerate(self._platforms):
            style = "PlatformActive.TButton" if plat == platform else "Platform.TButton"
            self._platform_btns[i].configure(style=style)
        self._update_presets()

    def _update_presets(self) -> None:
        for b in self._preset_btns:
            b.destroy()
        self._preset_btns.clear()

        presets = CROP_PRESETS.get(self._active_platform, {})
        if not presets:
            return

        for name in presets:
            label = _preset_label(self._active_platform, name)
            btn = ttk.Button(self._row2, text=name, style="Preset.TButton",
                             command=lambda l=label: self._select_preset(l))
            btn.pack(side=tk.LEFT, padx=2)
            self._preset_btns.append(btn)

        first_name = list(presets.keys())[0]
        self._select_preset(_preset_label(self._active_platform, first_name),
                            update_preview=False)

    def _select_preset(self, label: str, update_preview: bool = True) -> None:
        self._active_preset = label
        self._highlight_preset(label)
        if update_preview:
            self._on_preset(label)

    def _highlight_preset(self, label: str) -> None:
        for b in self._preset_btns:
            b.configure(style="Preset.TButton")
        for b in self._preset_btns:
            if b.cget("text") in label:
                b.configure(style="PresetActive.TButton")
                break

    def set_preset(self, label: str) -> None:
        """Highlight a preset button without firing the callback."""
        self._active_preset = label
        platform = label.split(" - ")[0] if " - " in label else "Facebook"
        if platform in self._platforms and platform != self._active_platform:
            self._active_platform = platform
            for i, plat in enumerate(self._platforms):
                style = "PlatformActive.TButton" if plat == platform else "Platform.TButton"
                self._platform_btns[i].configure(style=style)
            self._update_presets()
        self._highlight_preset(label)

    def reset(self) -> None:
        self._active_platform = "Facebook"
        for i, plat in enumerate(self._platforms):
            self._platform_btns[i].configure(style="Platform.TButton")
        self._update_presets()

    def set_enabled(self, enabled: bool) -> None:
        state = "!disabled" if enabled else "disabled"
        for btn in self._platform_btns:
            btn.state([state])
        for btn in self._preset_btns:
            btn.state([state])
        cursor = "hand2" if enabled else ""
        for btn in self._action_btns:
            btn.configure(cursor=cursor)

    def current_preset(self) -> str:
        if self._active_preset:
            return self._active_preset
        return _preset_label("Facebook", "Feed horizontal")
