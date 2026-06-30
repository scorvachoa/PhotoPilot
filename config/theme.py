import tkinter as tk
from tkinter import ttk


class Colors:
    BG = "#1a1a2e"
    BG_OFF = "#1e1e36"
    BG_CARD = "#16213e"
    BG_INPUT = "#252542"
    BG_HOVER = "#2a2a4a"
    BG_ACTIVE = "#35355a"

    BG_SIDEBAR = "#0f0f23"
    BG_SIDEBAR_HOVER = "#16162a"
    BG_SIDEBAR_ACTIVE = "#1e1e36"

    BG_PREVIEW = "#0a0a18"

    BORDER = "#2a2a4a"
    BORDER_FOCUS = "#6C63FF"

    TEXT = "#e0e0e0"
    TEXT_MUTED = "#8a8aaa"
    TEXT_DIM = "#6a6a8a"
    TEXT_INVERT = "#ffffff"
    TEXT_SIDEBAR = "#8a8aaa"
    TEXT_SIDEBAR_ACTIVE = "#ffffff"

    ACCENT = "#6C63FF"
    ACCENT_HOVER = "#7b73ff"
    ACCENT_LIGHT = "#2a2a5a"
    ACCENT_MUTED = "#a8a2ff"
    SECONDARY = "#4A4A8A"
    SECONDARY_HOVER = "#3d3d75"
    ACCENT_SUCCESS = "#12b886"
    ACCENT_WARNING = "#fab005"
    ACCENT_DANGER = "#fa5252"

    PRESET_BTN = "#252542"
    PRESET_BTN_HOVER = "#2a2a4a"
    PRESET_BTN_ACTIVE = "#6C63FF"
    PRESET_TEXT = "#c0c0d0"
    PRESET_TEXT_ACTIVE = "#ffffff"


class Fonts:
    FAMILY = "Segoe UI"
    MONO = "Consolas"
    TITLE = (FAMILY, 16, "bold")
    HEADER = (FAMILY, 12, "bold")
    SUBHEADER = (FAMILY, 10, "bold")
    BODY = (FAMILY, 10)
    SMALL = (FAMILY, 8)
    LABEL = (FAMILY, 9)
    BUTTON = (FAMILY, 10)
    BUTTON_SM = (FAMILY, 9)
    THUMB_NAME = (FAMILY, 7)


def setup_theme(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")

    base = {
        "background": Colors.BG,
        "foreground": Colors.TEXT,
        "font": Fonts.BODY,
    }
    style.configure(".", **base)

    style.configure("TFrame", background=Colors.BG)
    style.configure("TLabel", background=Colors.BG, foreground=Colors.TEXT)
    style.configure(
        "TLabelframe",
        background=Colors.BG,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        font=Fonts.SUBHEADER,
        foreground=Colors.TEXT,
        background=Colors.BG,
    )

    style.configure("Card.TFrame", background=Colors.BG_CARD)
    style.configure("Sidebar.TFrame", background=Colors.BG_SIDEBAR)
    style.configure("Preview.TFrame", background=Colors.BG_PREVIEW)
    style.configure("TopBar.TFrame", background=Colors.BG)

    style.configure(
        "Primary.TButton",
        font=Fonts.BUTTON,
        background=Colors.ACCENT,
        foreground=Colors.TEXT_INVERT,
        bordercolor=Colors.ACCENT,
        borderwidth=0,
        focusthickness=0,
        padding=(16, 9),
    )
    style.map(
        "Primary.TButton",
        background=[("active", Colors.ACCENT_HOVER), ("disabled", Colors.BG_INPUT)],
        foreground=[("disabled", Colors.TEXT_DIM)],
    )

    style.configure(
        "Secondary.TButton",
        font=Fonts.BUTTON,
        background=Colors.BG_OFF,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        borderwidth=1,
        focusthickness=0,
        padding=(16, 9),
    )
    style.map(
        "Secondary.TButton",
        background=[("active", Colors.BG_HOVER), ("disabled", Colors.BG_OFF)],
        foreground=[("disabled", Colors.TEXT_DIM)],
    )

    style.configure(
        "Tool.TButton",
        font=Fonts.BUTTON_SM,
        background=Colors.BG_INPUT,
        foreground=Colors.TEXT,
        bordercolor=Colors.BORDER,
        borderwidth=1,
        focusthickness=0,
        padding=(12, 6),
    )
    style.map(
        "Tool.TButton",
        background=[("active", Colors.ACCENT_LIGHT)],
        foreground=[("active", Colors.ACCENT)],
    )

    style.configure(
        "Accent.TButton",
        font=Fonts.BUTTON_SM,
        background=Colors.ACCENT,
        foreground=Colors.TEXT_INVERT,
        bordercolor=Colors.ACCENT,
        borderwidth=1,
        focusthickness=0,
        padding=(12, 6),
    )
    style.map(
        "Accent.TButton",
        background=[("active", Colors.ACCENT_HOVER)],
    )

    style.configure(
        "Preset.TButton",
        font=Fonts.BUTTON_SM,
        background=Colors.PRESET_BTN,
        foreground=Colors.PRESET_TEXT,
        bordercolor=Colors.BORDER,
        borderwidth=1,
        focusthickness=0,
        padding=(10, 4),
    )
    style.map(
        "Preset.TButton",
        background=[("active", Colors.PRESET_BTN_HOVER)],
    )

    style.configure(
        "PresetActive.TButton",
        font=Fonts.BUTTON_SM,
        background=Colors.PRESET_BTN_ACTIVE,
        foreground=Colors.PRESET_TEXT_ACTIVE,
        bordercolor=Colors.PRESET_BTN_ACTIVE,
        borderwidth=1,
        focusthickness=0,
        padding=(10, 4),
    )

    style.configure(
        "Platform.TButton",
        font=("Segoe UI", 8, "bold"),
        background=Colors.BG_OFF,
        foreground=Colors.TEXT_MUTED,
        bordercolor=Colors.BORDER,
        borderwidth=1,
        focusthickness=0,
        padding=(8, 4),
    )
    style.map(
        "Platform.TButton",
        background=[("active", Colors.ACCENT_LIGHT)],
        foreground=[("active", Colors.ACCENT)],
    )

    style.configure(
        "PlatformActive.TButton",
        font=("Segoe UI", 8, "bold"),
        background=Colors.ACCENT,
        foreground=Colors.TEXT_INVERT,
        bordercolor=Colors.ACCENT,
        borderwidth=1,
        focusthickness=0,
        padding=(8, 4),
    )

    style.configure(
        "TScale",
        background=Colors.BG,
        troughcolor=Colors.BG_INPUT,
        bordercolor=Colors.BG,
        lightcolor=Colors.ACCENT,
        darkcolor=Colors.ACCENT,
        relief="flat",
        sliderthickness=14,
        sliderlength=14,
    )
    style.configure(
        "Horizontal.TScale",
        background=Colors.BG,
        troughcolor=Colors.BG_INPUT,
        lightcolor=Colors.ACCENT,
        darkcolor=Colors.ACCENT,
        relief="flat",
        sliderthickness=14,
        sliderlength=14,
    )

    style.configure(
        "TProgressbar",
        background=Colors.ACCENT,
        troughcolor=Colors.BG_INPUT,
        bordercolor=Colors.BORDER,
        thickness=5,
    )

    style.configure(
        "Vertical.TScrollbar",
        gripcount=0,
        background=Colors.BORDER,
        bordercolor=Colors.BORDER,
        arrowcolor=Colors.TEXT_MUTED,
        troughcolor=Colors.BG,
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", Colors.TEXT_DIM)],
    )

    style.configure(
        "Header.TLabel",
        font=Fonts.HEADER,
        background=Colors.BG,
        foreground=Colors.TEXT,
    )
    style.configure(
        "Muted.TLabel",
        font=Fonts.SMALL,
        background=Colors.BG,
        foreground=Colors.TEXT_MUTED,
    )
    style.configure(
        "Status.TLabel",
        font=Fonts.SMALL,
        background=Colors.BG,
        foreground=Colors.TEXT_MUTED,
    )

    style.configure(
        "SidebarHeader.TLabel",
        font=Fonts.SUBHEADER,
        background=Colors.BG_SIDEBAR,
        foreground=Colors.TEXT_SIDEBAR,
    )

    style.configure(
        "TSeparator",
        background=Colors.BORDER,
    )

    style.configure(
        "Preview.TLabelframe",
        background=Colors.BG,
        bordercolor=Colors.BORDER,
        lightcolor=Colors.BORDER,
        darkcolor=Colors.BORDER,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "PreviewInner.TFrame",
        background=Colors.BG_PREVIEW,
        relief="sunken",
        borderwidth=1,
    )
