import tkinter as tk
from tkinter import ttk

from config.theme import Colors, Fonts


class ModernSlider(tk.Frame):
    def __init__(self, parent: tk.Widget, label: str, from_: float, to: float,
                 resolution: float, default: float,
                 on_change, **kwargs) -> None:
        super().__init__(parent, bg=Colors.BG_CARD, **kwargs)
        self._on_change = on_change
        self._from = from_
        self._to = to
        self._res = resolution
        self._fine_res = resolution / 10
        self._default = default
        self._value = round(default, 3)
        self._enabled = True
        self._build(label)

    def _format_value(self) -> str:
        value = round(self._value, 3)
        if value == 0:
            value = 0.0
        text = f"{value:.3f}"
        if text.endswith("0"):
            text = f"{value:.2f}"
        return text

    def _build(self, label: str) -> None:
        top = tk.Frame(self, bg=Colors.BG_CARD)
        top.pack(fill=tk.X, padx=2, pady=(1, 0))

        self._label = tk.Label(top, text=label, bg=Colors.BG_CARD,
                               fg=Colors.TEXT_MUTED, font=Fonts.SMALL,
                               anchor="w")
        self._label.pack(side=tk.LEFT)
        self._label.bind("<Double-Button-1>", lambda e: self.reset())

        chip_opts = dict(font=Fonts.MICRO, bg=Colors.BG_INPUT,
                         fg=Colors.TEXT_MUTED, padx=5, pady=1,
                         cursor="hand2", bd=0)
        self._inc_btn = tk.Label(top, text="+", **chip_opts)
        self._inc_btn.pack(side=tk.RIGHT)
        self._value_label = tk.Label(top, text=self._format_value(),
                                     font=Fonts.VALUE, bg=Colors.BG_INPUT,
                                     fg=Colors.TEXT_MUTED, width=7,
                                     anchor="e", padx=4, pady=1)
        self._value_label.pack(side=tk.RIGHT, padx=3)
        self._dec_btn = tk.Label(top, text="\u2212", **chip_opts)
        self._dec_btn.pack(side=tk.RIGHT)

        for btn, direction in ((self._dec_btn, -1), (self._inc_btn, 1)):
            btn.bind("<Button-1>", lambda e, d=direction: self._step(d))
            btn.bind("<Shift-Button-1>",
                     lambda e, d=direction: self._step(d, fine=True))
            btn.bind("<Enter>", lambda e, b=btn: b.configure(
                bg=Colors.ACCENT_LIGHT, fg=Colors.TEXT_ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(
                bg=Colors.BG_INPUT, fg=Colors.TEXT_MUTED))
        self._value_label.bind("<Double-Button-1>", lambda e: self.reset())
        for widget in (self._label, self._value_label, self._dec_btn,
                       self._inc_btn):
            widget.bind("<Button-1>", lambda e: self._scale.focus_set(),
                        add="+")

        self._scale = ttk.Scale(self, from_=self._from, to=self._to,
                                value=self._value, command=self._on_scale,
                                orient=tk.HORIZONTAL, takefocus=True)
        self._scale.pack(fill=tk.X, padx=2, pady=(0, 1))
        self._scale.bind("<Button-1>", lambda e: self._scale.focus_set(),
                         add="+")
        for key, direction, fine in (
            ("<Left>", -1, False), ("<Right>", 1, False),
            ("<Down>", -1, False), ("<Up>", 1, False),
            ("<Shift-Left>", -1, True), ("<Shift-Right>", 1, True),
            ("<Shift-Down>", -1, True), ("<Shift-Up>", 1, True),
        ):
            self._scale.bind(
                key, lambda e, d=direction, f=fine: self._nudge(d, f))
        self._refresh_state()

    def _nudge(self, direction: int, fine: bool = False) -> str:
        self._step(direction, fine)
        return "break"

    def _refresh_state(self) -> None:
        modified = abs(self._value - self._default) > 1e-9
        if not self._enabled:
            self._value_label.config(text=self._format_value(),
                                     fg=Colors.TEXT_DIM)
            self._label.config(fg=Colors.TEXT_DIM, font=Fonts.SMALL)
            return
        self._value_label.config(
            text=self._format_value(),
            fg=Colors.TEXT_ACCENT if modified else Colors.TEXT_MUTED,
        )
        self._label.config(
            fg=Colors.TEXT if modified else Colors.TEXT_MUTED,
            font=(Fonts.FAMILY, 9, "bold") if modified else Fonts.SMALL,
        )

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._scale.state(["!disabled"] if enabled else ["disabled"])
        cursor = "hand2" if enabled else ""
        for widget in (self._dec_btn, self._inc_btn, self._value_label,
                       self._label):
            widget.configure(cursor=cursor)
        self._refresh_state()

    def _step(self, direction: int, fine: bool = False) -> None:
        if not self._enabled:
            return
        step = self._fine_res if fine else self._res
        new_val = round(max(self._from, min(self._to,
                                            self._value + step * direction)), 3)
        if new_val != self._value:
            self._value = new_val
            self._scale.set(new_val)
            self._refresh_state()
            self._on_change(new_val)

    def _on_scale(self, val: str) -> None:
        if not self._enabled:
            return
        self._value = round(float(val), 3)
        self._refresh_state()
        self._on_change(self._value)

    def set(self, value: float) -> None:
        self._value = round(max(self._from, min(self._to, value)), 3)
        self._scale.set(self._value)
        self._refresh_state()

    @property
    def default(self) -> float:
        return self._default

    def reset(self) -> None:
        if not self._enabled or self._value == self._default:
            return
        self._value = self._default
        self._scale.set(self._default)
        self._refresh_state()
        self._on_change(self._default)


class SlidersPanel(ttk.Frame):
    _SECTIONS = (
        ("LUZ", (
            ("brightness", "Brillo", -0.5, 0.5, 0.01, 0.0),
            ("contrast", "Contraste", -0.5, 0.5, 0.01, 0.0),
            ("exposure", "Exposici\u00f3n", -1.0, 1.0, 0.01, 0.0),
            ("shadows", "Sombras", -0.5, 0.5, 0.01, 0.0),
            ("highlights", "Altas luces", -0.5, 0.5, 0.01, 0.0),
            ("gamma", "Gamma", 0.5, 1.5, 0.01, 1.0),
        )),
        ("COLOR", (
            ("saturation", "Saturaci\u00f3n", -0.5, 0.5, 0.01, 0.0),
            ("temperature", "Temperatura", -1.0, 1.0, 0.01, 0.0),
        )),
        ("DETALLE", (
            ("sharpness", "Nitidez", -0.5, 0.5, 0.01, 0.0),
            ("noise_reduction", "Red. ruido", 0.0, 1.0, 0.01, 0.0),
        )),
    )

    def __init__(self, parent: tk.Widget, app, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._app = app
        self._sliders: dict[str, ModernSlider] = {}
        self._build()

    def _build(self) -> None:
        scroll_frame = tk.Frame(self, bg=Colors.BG_CARD)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        scroll_frame.rowconfigure(0, weight=1)
        scroll_frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_frame, highlightthickness=0,
                           bg=Colors.BG_CARD, bd=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL,
                                  command=canvas.yview)
        inner = tk.Frame(canvas, bg=Colors.BG_CARD)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")
        self._canvas = canvas
        self._scrollbar = scrollbar
        self._scroll_visible = True

        def on_inner_configure(_event=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._sync_scrollbar()

        inner.bind("<Configure>", on_inner_configure)
        canvas.bind("<Configure>", lambda e: self._sync_scrollbar())

        canvas.bind("<Enter>", lambda e: canvas.bind_all(
            "<MouseWheel>", lambda ev: canvas.yview_scroll(
                int(-ev.delta / 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for title, specs in self._SECTIONS:
            self._section(inner, title)
            for attr, label, from_, to, res, default in specs:
                slider = ModernSlider(inner, label, from_, to, res, default,
                                      self._make_handler(attr))
                slider.pack(fill=tk.X, padx=8, pady=(0, 0))
                self._sliders[attr] = slider

        tk.Label(inner, text="Flechas o \u00b1: 0.01  \u00b7  May\u00fas: 0.001\n"
                             "Doble clic en el valor: restablecer",
                 bg=Colors.BG_CARD, fg=Colors.TEXT_DIM, font=Fonts.MICRO,
                 anchor="w", justify=tk.LEFT).pack(
                     fill=tk.X, padx=12, pady=(4, 6))

    def _sync_scrollbar(self) -> None:
        bbox = self._canvas.bbox("all")
        if not bbox:
            return
        needed = (bbox[3] - bbox[1]) > self._canvas.winfo_height() + 1
        if needed and not self._scroll_visible:
            self._scrollbar.grid()
            self._scroll_visible = True
        elif not needed and self._scroll_visible:
            self._scrollbar.grid_remove()
            self._scroll_visible = False

    def _section(self, parent: tk.Widget, title: str) -> None:
        row = tk.Frame(parent, bg=Colors.BG_CARD)
        row.pack(fill=tk.X, padx=12, pady=(8, 2))
        tk.Label(row, text=title, bg=Colors.BG_CARD, fg=Colors.TEXT_DIM,
                 font=Fonts.OVERLINE).pack(side=tk.LEFT)
        tk.Frame(row, bg=Colors.BORDER_SUBTLE, height=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))

    def _make_handler(self, attr: str):
        def handler(value: float) -> None:
            setattr(self._app.state.processing, attr, value)
            self._app.on_slider_changed()
        return handler

    def reset(self) -> None:
        for slider in self._sliders.values():
            slider.set(slider.default)

    def set_enabled(self, enabled: bool) -> None:
        for slider in self._sliders.values():
            slider.set_enabled(enabled)

    def load_from_state(self) -> None:
        for attr, slider in self._sliders.items():
            slider.set(getattr(self._app.state.processing, attr))
