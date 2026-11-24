"""Design tokens and ttk theme for PhotoPilot.

Palette and hierarchy follow a dark "creative tool" direction:
neutral slate surfaces so photography colors read true, one violet accent
for primary actions, cyan only for focus/keyboard affordances.
"""

import tkinter as tk
from tkinter import ttk


class Colors:
    # ---- Surfaces -----------------------------------------------------
    BG = "#0F1522"          # app canvas
    BG_DEEP = "#0A0F19"     # sidebar / chrome behind images
    BG_CARD = "#161F30"     # panels
    BG_INPUT = "#1B2537"    # inputs, chips, troughs
    BG_HOVER = "#232F45"
    BG_ACTIVE = "#2B3A54"
    BG_PREVIEW = "#070B12"  # photo stage (near-black)
    BG_OVERLAY = "#0B111C"

    # Kept for compatibility with older widget code.
    BG_OFF = BG_CARD
    BG_SIDEBAR = BG_DEEP
    BG_SIDEBAR_HOVER = BG_CARD
    BG_SIDEBAR_ACTIVE = BG_HOVER

    # ---- Borders ------------------------------------------------------
    BORDER = "#26324A"
    BORDER_SUBTLE = "#1A2334"
    BORDER_STRONG = "#3A4A66"

    # ---- Text ---------------------------------------------------------
    TEXT = "#E8EEF8"
    TEXT_MUTED = "#9DABC2"
    TEXT_DIM = "#7285A0"
    TEXT_INVERT = "#FFFFFF"
    TEXT_ACCENT = "#C4B5FD"
    TEXT_SIDEBAR = "#9DABC2"
    TEXT_SIDEBAR_ACTIVE = "#FFFFFF"

    # ---- Accent & semantics -------------------------------------------
    ACCENT = "#7C3AED"
    ACCENT_HOVER = "#8B5CF6"
    ACCENT_PRESSED = "#6D28D9"
    ACCENT_SOFT = "#241A44"
    ACCENT_LIGHT = "#2A2050"
    ACCENT_MUTED = "#A78BFA"

    FOCUS = "#22D3EE"
    BORDER_FOCUS = FOCUS

    SUCCESS = "#34D399"
    SUCCESS_SOFT = "#0E2D25"
    WARNING = "#FBBF24"
    WARNING_SOFT = "#2E2512"
    DANGER = "#F87171"
    DANGER_SOFT = "#31181C"

    ACCENT_SUCCESS = SUCCESS
    ACCENT_WARNING = WARNING
    ACCENT_DANGER = DANGER

    # ---- Presets (kept for compatibility) -----------------------------
    PRESET_BTN = BG_INPUT
    PRESET_BTN_HOVER = BG_HOVER
    PRESET_BTN_ACTIVE = ACCENT
    PRESET_TEXT = "#C2CEE3"
    PRESET_TEXT_ACTIVE = "#FFFFFF"


class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24


class Fonts:
    FAMILY = "Segoe UI"
    MONO = "Consolas"

    BRAND = (FAMILY, 15, "bold")
    TITLE = (FAMILY, 15, "bold")
    HEADER = (FAMILY, 11, "bold")
    SUBHEADER = (FAMILY, 9, "bold")
    BODY = (FAMILY, 10)
    SMALL = (FAMILY, 9)
    MICRO = (FAMILY, 8)
    LABEL = (FAMILY, 9)
    BUTTON = (FAMILY, 10)
    BUTTON_SM = (FAMILY, 9)
    VALUE = (MONO, 9, "bold")
    THUMB_NAME = (FAMILY, 8)
    OVERLINE = (FAMILY, 8, "bold")


def _button(style: ttk.Style, name: str, *, bg: str, fg: str,
            border: str, hover_bg: str, hover_fg: str | None,
            pressed_bg: str, padding: tuple[int, int], font,
            disabled_bg: str | None = None,
            disabled_fg: str | None = None,
            disabled_border: str | None = None) -> None:
    style.configure(
        name,
        background=bg,
        foreground=fg,
        bordercolor=border,
        darkcolor=border,
        lightcolor=border,
        focusthickness=1,
        focuscolor=Colors.FOCUS,
        relief="flat",
        padding=padding,
        font=font,
    )
    style.map(
        name,
        background=[
            ("disabled", disabled_bg or bg),
            ("pressed", pressed_bg),
            ("active", hover_bg),
        ],
        foreground=[
            ("disabled", disabled_fg or Colors.TEXT_DIM),
            ("pressed", hover_fg or fg),
            ("active", hover_fg or fg),
        ],
        bordercolor=[
            ("disabled", disabled_border or border),
            ("focus", Colors.FOCUS),
        ],
    )


def setup_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    base = {
        "background": Colors.BG,
        "foreground": Colors.TEXT,
        "font": Fonts.BODY,
        "focuscolor": Colors.FOCUS,
    }
    style.configure(".", **base)

    # ---- Frames -------------------------------------------------------
    style.configure("TFrame", background=Colors.BG)
    style.configure("App.TFrame", background=Colors.BG)
    style.configure("Card.TFrame", background=Colors.BG_CARD)
    style.configure("CardHeader.TFrame", background=Colors.BG_CARD)
    style.configure("Sidebar.TFrame", background=Colors.BG_DEEP)
    style.configure("Preview.TFrame", background=Colors.BG_PREVIEW)
    style.configure("TopBar.TFrame", background=Colors.BG_CARD)
    style.configure("StatusBar.TFrame", background=Colors.BG_CARD)

    style.configure("TLabel", background=Colors.BG, foreground=Colors.TEXT)
    style.configure("Card.TLabel", background=Colors.BG_CARD,
                    foreground=Colors.TEXT)
    style.configure("Muted.TLabel", background=Colors.BG,
                    foreground=Colors.TEXT_MUTED, font=Fonts.SMALL)
    style.configure("Status.TLabel", background=Colors.BG_CARD,
                    foreground=Colors.TEXT_MUTED, font=Fonts.SMALL)
    style.configure("Header.TLabel", background=Colors.BG_CARD,
                    foreground=Colors.TEXT, font=Fonts.SUBHEADER)
    style.configure("SidebarHeader.TLabel", background=Colors.BG_DEEP,
                    foreground=Colors.TEXT, font=Fonts.SUBHEADER)

    # ---- Buttons ------------------------------------------------------
    _button(
        style, "Primary.TButton",
        bg=Colors.ACCENT, fg=Colors.TEXT_INVERT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_HOVER, hover_fg=Colors.TEXT_INVERT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(16, 9),
        font=Fonts.BUTTON, disabled_bg=Colors.BG_INPUT,
        disabled_border=Colors.BG_INPUT,
    )
    _button(
        style, "Secondary.TButton",
        bg=Colors.BG_CARD, fg=Colors.TEXT, border=Colors.BORDER,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(12, 7),
        font=Fonts.BUTTON_SM, disabled_bg=Colors.BG_CARD,
    )
    _button(
        style, "Tool.TButton",
        bg=Colors.BG_INPUT, fg=Colors.TEXT, border=Colors.BORDER_SUBTLE,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(12, 7),
        font=Fonts.BUTTON_SM, disabled_bg=Colors.BG_CARD,
    )
    _button(
        style, "Ghost.TButton",
        bg=Colors.BG_CARD, fg=Colors.TEXT_MUTED, border=Colors.BG_CARD,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(10, 5),
        font=Fonts.BUTTON_SM, disabled_bg=Colors.BG_CARD,
    )
    _button(
        style, "Accent.TButton",
        bg=Colors.ACCENT_SOFT, fg=Colors.TEXT_ACCENT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_LIGHT, hover_fg=Colors.TEXT_ACCENT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(12, 7),
        font=Fonts.BUTTON_SM,
    )
    _button(
        style, "ToggleOn.TButton",
        bg=Colors.ACCENT_SOFT, fg=Colors.TEXT_ACCENT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_LIGHT, hover_fg=Colors.TEXT_INVERT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(12, 8),
        font=Fonts.BUTTON_SM, disabled_bg=Colors.BG_INPUT,
        disabled_border=Colors.BORDER,
    )
    _button(
        style, "ToggleOff.TButton",
        bg=Colors.BG_INPUT, fg=Colors.TEXT_MUTED, border=Colors.BORDER,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(12, 8),
        font=Fonts.BUTTON_SM, disabled_bg=Colors.BG_CARD,
    )

    # ---- Chips (crop platforms / presets) -----------------------------
    _button(
        style, "Chip.TButton",
        bg=Colors.BG_INPUT, fg=Colors.TEXT_MUTED, border=Colors.BORDER,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.BG_CARD,
        disabled_border=Colors.BORDER_SUBTLE,
    )
    _button(
        style, "ChipActive.TButton",
        bg=Colors.ACCENT, fg=Colors.TEXT_INVERT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_HOVER, hover_fg=Colors.TEXT_INVERT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.ACCENT_SOFT,
        disabled_fg=Colors.TEXT_DIM, disabled_border=Colors.BORDER,
    )
    # Legacy aliases
    _button(
        style, "Platform.TButton",
        bg=Colors.BG_INPUT, fg=Colors.TEXT_MUTED, border=Colors.BORDER,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.BG_CARD,
        disabled_border=Colors.BORDER_SUBTLE,
    )
    _button(
        style, "PlatformActive.TButton",
        bg=Colors.ACCENT, fg=Colors.TEXT_INVERT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_HOVER, hover_fg=Colors.TEXT_INVERT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.ACCENT_SOFT,
        disabled_fg=Colors.TEXT_DIM, disabled_border=Colors.BORDER,
    )
    _button(
        style, "Preset.TButton",
        bg=Colors.BG_INPUT, fg=Colors.PRESET_TEXT, border=Colors.BORDER,
        hover_bg=Colors.BG_HOVER, hover_fg=Colors.TEXT,
        pressed_bg=Colors.BG_ACTIVE, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.BG_CARD,
        disabled_border=Colors.BORDER_SUBTLE,
    )
    _button(
        style, "PresetActive.TButton",
        bg=Colors.ACCENT_SOFT, fg=Colors.TEXT_ACCENT, border=Colors.ACCENT,
        hover_bg=Colors.ACCENT_LIGHT, hover_fg=Colors.TEXT_INVERT,
        pressed_bg=Colors.ACCENT_PRESSED, padding=(10, 4),
        font=Fonts.MICRO, disabled_bg=Colors.ACCENT_SOFT,
        disabled_fg=Colors.TEXT_DIM, disabled_border=Colors.BORDER,
    )

    # ---- Inputs / progress / scrollbars -------------------------------
    scale_opts = dict(
        background=Colors.ACCENT,
        troughcolor=Colors.BG_INPUT,
        bordercolor=Colors.BORDER,
        lightcolor=Colors.BORDER,
        darkcolor=Colors.BORDER,
        gripcount=0,
        sliderthickness=14,
        sliderlength=14,
    )
    style.configure("TScale", **scale_opts)
    style.configure("Horizontal.TScale", **scale_opts)
    style.map(
        "Horizontal.TScale",
        background=[("disabled", Colors.BG_INPUT)],
        troughcolor=[("disabled", Colors.BG_CARD)],
        lightcolor=[("disabled", Colors.BORDER_SUBTLE)],
        darkcolor=[("disabled", Colors.BORDER_SUBTLE)],
    )

    style.configure(
        "TProgressbar",
        background=Colors.ACCENT,
        troughcolor=Colors.BG_INPUT,
        bordercolor=Colors.BG_INPUT,
        lightcolor=Colors.ACCENT,
        darkcolor=Colors.ACCENT,
        thickness=6,
    )

    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        arrowsize=10,
        background=Colors.BORDER_STRONG,
        bordercolor=Colors.BG_DEEP,
        lightcolor=Colors.BORDER_STRONG,
        darkcolor=Colors.BORDER_STRONG,
        arrowcolor=Colors.TEXT_DIM,
        troughcolor=Colors.BG_DEEP,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", Colors.BORDER_STRONG)],
        arrowcolor=[("active", Colors.TEXT)],
    )

    # ---- Separators & legacy label frames ----------------------------
    style.configure("TSeparator", background=Colors.BORDER_SUBTLE)
    style.configure(
        "TLabelframe",
        background=Colors.BG_CARD,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        font=Fonts.SUBHEADER,
        foreground=Colors.TEXT,
        background=Colors.BG_CARD,
    )
    style.configure(
        "Preview.TLabelframe",
        background=Colors.BG_CARD,
        bordercolor=Colors.BORDER,
        lightcolor=Colors.BORDER,
        darkcolor=Colors.BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure("PreviewInner.TFrame", background=Colors.BG_PREVIEW)

    # Keyboard focus should be visible on every interactive control.
    style.map(
        "TButton",
        bordercolor=[("focus", Colors.FOCUS)],
        focuscolor=[("focus", Colors.FOCUS)],
    )
