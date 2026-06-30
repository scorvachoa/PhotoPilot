import tkinter as tk
from tkinter import ttk

from config.theme import Colors, Fonts


class ModernSlider(ttk.Frame):
    def __init__(self, parent: tk.Widget, label: str, from_: float, to: float,
                 resolution: float, default: float,
                 on_change, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_change = on_change
        self._from = from_
        self._to = to
        self._res = resolution
        self._default = default
        self._value = default
        self._build(label)

    def _build(self, label: str) -> None:
        self.columnconfigure(2, weight=1)

        self._label = ttk.Label(self, text=label, style="Muted.TLabel")
        self._label.grid(row=0, column=0, sticky="w", padx=(8, 4))

        btn_style = {"font": ("Segoe UI", 9, "bold"), "fg": Colors.TEXT_MUTED,
                     "bg": Colors.BG_INPUT, "cursor": "hand2",
                     "width": 2, "relief": tk.FLAT, "bd": 0}
        self._dec_btn = tk.Label(self, text="\u2212", **btn_style)
        self._dec_btn.grid(row=0, column=1, padx=(0, 1), pady=0, sticky="e")
        self._dec_btn.bind("<Button-1>", lambda e: self._step(-1))
        self._dec_btn.bind("<Enter>", lambda e: self._dec_btn.configure(
            fg=Colors.ACCENT, bg=Colors.ACCENT_LIGHT))
        self._dec_btn.bind("<Leave>", lambda e: self._dec_btn.configure(
            fg=Colors.TEXT_MUTED, bg=Colors.BG_INPUT))

        self._value_label = tk.Label(self, text=f"{self._value:.2f}",
                                     font=("Segoe UI", 8, "bold"),
                                     fg=Colors.ACCENT, bg=Colors.BG,
                                     width=6, anchor="e")
        self._value_label.grid(row=0, column=2, sticky="e", padx=(1, 1))

        self._inc_btn = tk.Label(self, text="+", **btn_style)
        self._inc_btn.grid(row=0, column=3, padx=(1, 8), pady=0, sticky="w")
        self._inc_btn.bind("<Button-1>", lambda e: self._step(1))
        self._inc_btn.bind("<Enter>", lambda e: self._inc_btn.configure(
            fg=Colors.ACCENT, bg=Colors.ACCENT_LIGHT))
        self._inc_btn.bind("<Leave>", lambda e: self._inc_btn.configure(
            fg=Colors.TEXT_MUTED, bg=Colors.BG_INPUT))

        self._scale = ttk.Scale(self, from_=self._from, to=self._to,
                                value=self._value, command=self._on_scale,
                                orient=tk.HORIZONTAL)
        self._scale.grid(row=1, column=0, columnspan=4, sticky="ew",
                         padx=8, pady=(2, 6))

    def _step(self, direction: int) -> None:
        step = self._res * direction
        new_val = round(max(self._from, min(self._to, self._value + step)), 2)
        if new_val != self._value:
            self._value = new_val
            self._scale.set(new_val)
            self._value_label.config(text=f"{new_val:.2f}")
            self._on_change(new_val)

    def _on_scale(self, val: str) -> None:
        self._value = round(float(val), 2)
        self._value_label.config(text=f"{self._value:.2f}")
        self._on_change(self._value)

    def set(self, value: float) -> None:
        self._value = round(max(self._from, min(self._to, value)), 2)
        self._scale.set(self._value)
        self._value_label.config(text=f"{self._value:.2f}")

    def reset(self) -> None:
        self.set(self._default)


class SlidersPanel(ttk.Frame):
    def __init__(self, parent: tk.Widget, app, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._app = app
        self._build()

    def _build(self) -> None:
        self._sliders: list[ModernSlider] = []
        specs = [
            ("Brillo", -0.5, 0.5, 0.01, 0.0),
            ("Contraste", -0.5, 0.5, 0.01, 0.0),
            ("Saturacion", -0.5, 0.5, 0.01, 0.0),
            ("Exposicion", -1.0, 1.0, 0.01, 0.0),
            ("Nitidez", -0.5, 0.5, 0.01, 0.0),
            ("Temperatura", -1.0, 1.0, 0.01, 0.0),
            ("Sombras", -0.5, 0.5, 0.01, 0.0),
            ("Altas luces", -0.5, 0.5, 0.01, 0.0),
            ("Gamma", 0.5, 1.5, 0.01, 1.0),
            ("Red. ruido", 0.0, 1.0, 0.01, 0.0),
        ]
        self._attr_map = [
            "brightness", "contrast", "saturation", "exposure",
            "sharpness", "temperature", "shadows", "highlights",
            "gamma", "noise_reduction",
        ]

        scroll_frame = ttk.Frame(self)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scroll_frame, highlightthickness=0, bg=Colors.BG, bd=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL,
                                  command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for spec, attr in zip(specs, self._attr_map):
            s = ModernSlider(inner, *spec, self._make_handler(attr))
            s.pack(fill=tk.X, padx=2, pady=1)
            self._sliders.append(s)

    def _make_handler(self, attr: str):
        def handler(value: float) -> None:
            setattr(self._app.state.processing, attr, value)
            self._app.on_slider_changed()
        return handler

    def reset(self) -> None:
        defaults = {"gamma": 1.0}
        for attr in self._attr_map:
            setattr(self._app.state.processing, attr, defaults.get(attr, 0.0))
        for s in self._sliders:
            s.reset()

    def load_from_state(self) -> None:
        for s, attr in zip(self._sliders, self._attr_map):
            val = getattr(self._app.state.processing, attr)
            s.set(val)
