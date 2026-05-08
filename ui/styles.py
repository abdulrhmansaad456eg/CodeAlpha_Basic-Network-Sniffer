"""
UI styling and theme configuration for the network sniffer.
Dark cybersecurity theme with modern aesthetics.
"""

import customtkinter as ctk


class Theme:
    """Color scheme and styling constants."""
    
    BG_PRIMARY = "#0a0a0f"
    BG_SECONDARY = "#12121a"
    BG_TERTIARY = "#1a1a24"
    BG_CARD = "#1e1e2e"
    
    ACCENT_PRIMARY = "#00d4ff"
    ACCENT_SECONDARY = "#7b2cbf"
    ACCENT_SUCCESS = "#00ff88"
    ACCENT_WARNING = "#ffaa00"
    ACCENT_DANGER = "#ff4757"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0b0"
    TEXT_MUTED = "#6a6a7a"
    
    BORDER_COLOR = "#2a2a3a"
    
    TCP_COLOR = "#00d4ff"
    UDP_COLOR = "#ffaa00"
    ICMP_COLOR = "#ff4757"
    HTTP_COLOR = "#00ff88"
    OTHER_COLOR = "#a0a0b0"
    
    @classmethod
    def get_protocol_color(cls, protocol: str) -> str:
        """Get color for protocol type."""
        protocol = protocol.upper()
        colors = {
            "TCP": cls.TCP_COLOR,
            "UDP": cls.UDP_COLOR,
            "ICMP": cls.ICMP_COLOR,
            "HTTP": cls.HTTP_COLOR,
        }
        return colors.get(protocol, cls.OTHER_COLOR)


class Style:
    """UI component styling helpers."""
    
    @staticmethod
    def configure_ctk():
        """Configure CustomTkinter global settings."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
    @staticmethod
    def create_button(parent, text, command, width=120, height=35, 
                      style="primary"):
        """Create a styled button."""
        colors = {
            "primary": Theme.ACCENT_PRIMARY,
            "success": Theme.ACCENT_SUCCESS,
            "danger": Theme.ACCENT_DANGER,
            "warning": Theme.ACCENT_WARNING,
        }
        color = colors.get(style, Theme.ACCENT_PRIMARY)
        
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=color,
            hover_color=Style._lighten_color(color, 20),
            text_color=Theme.BG_PRIMARY,
            font=Style.get_font("button"),
            corner_radius=8
        )
        
    @staticmethod
    def create_card(parent, **kwargs):
        """Create a styled card frame."""
        return ctk.CTkFrame(
            parent,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            **kwargs
        )
        
    @staticmethod
    def create_entry(parent, placeholder="", width=200, **kwargs):
        """Create a styled entry field."""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            width=width,
            height=35,
            font=Style.get_font("normal"),
            fg_color=Theme.BG_TERTIARY,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=8,
            **kwargs
        )
        
    @staticmethod
    def create_label(parent, text, style="normal", **kwargs):
        """Create a styled label."""
        fonts = {
            "title": ("Segoe UI", 24, "bold"),
            "subtitle": ("Segoe UI", 16, "bold"),
            "normal": ("Segoe UI", 12),
            "small": ("Segoe UI", 10),
            "mono": ("Consolas", 11),
        }
        
        colors = {
            "title": Theme.TEXT_PRIMARY,
            "subtitle": Theme.TEXT_PRIMARY,
            "normal": Theme.TEXT_SECONDARY,
            "small": Theme.TEXT_MUTED,
            "mono": Theme.TEXT_SECONDARY,
        }
        
        font = fonts.get(style, fonts["normal"])
        color = colors.get(style, Theme.TEXT_SECONDARY)
        
        return ctk.CTkLabel(
            parent,
            text=text,
            font=font,
            text_color=color,
            **kwargs
        )
        
    @staticmethod
    def create_combobox(parent, values, width=150, **kwargs):
        """Create a styled combobox."""
        return ctk.CTkComboBox(
            parent,
            values=values,
            width=width,
            height=35,
            font=Style.get_font("normal"),
            fg_color=Theme.BG_TERTIARY,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            dropdown_text_color=Theme.TEXT_PRIMARY,
            button_color=Theme.ACCENT_PRIMARY,
            corner_radius=8,
            **kwargs
        )
        
    @staticmethod
    def get_font(style="normal"):
        """Get font configuration."""
        fonts = {
            "title": ("Segoe UI", 24, "bold"),
            "subtitle": ("Segoe UI", 18, "bold"),
            "heading": ("Segoe UI", 14, "bold"),
            "button": ("Segoe UI", 12, "bold"),
            "normal": ("Segoe UI", 12),
            "small": ("Segoe UI", 10),
            "mono": ("Consolas", 11),
            "counter": ("Segoe UI", 32, "bold"),
        }
        return fonts.get(style, fonts["normal"])
        
    @staticmethod
    def _lighten_color(hex_color: str, percent: int) -> str:
        """Lighten or darken a hex color by percentage."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        new_rgb = tuple(
            max(0, min(255, int(c + (255 - c) * percent / 100)))
            for c in rgb
        )
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'
