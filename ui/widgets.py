"""
Custom UI widgets for the network sniffer.
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any
from ui.styles import Theme, Style


class StatCard(ctk.CTkFrame):
    """Animated statistics card widget."""
    
    def __init__(self, parent, title: str, value: str = "0", 
                 color: str = Theme.ACCENT_PRIMARY, **kwargs):
        super().__init__(
            parent,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            **kwargs
        )
        
        self.color = color
        self.current_value = 0
        self.target_value = 0
        
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=Style.get_font("counter"),
            text_color=color
        )
        self.value_label.pack(pady=(15, 5))
        
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.title_label.pack(pady=(0, 15))
        
    def set_value(self, value: int, animate: bool = True):
        """Update the displayed value with optional animation."""
        self.target_value = value
        if animate:
            self._animate_value()
        else:
            self.current_value = value
            self.value_label.configure(text=str(value))
            
    def _animate_value(self, steps: int = 10):
        """Animate value transition."""
        step_size = (self.target_value - self.current_value) / steps
        
        def step_animation(remaining_steps):
            if remaining_steps <= 0:
                self.current_value = self.target_value
                self.value_label.configure(text=str(int(self.target_value)))
                return
                
            self.current_value += step_size
            self.value_label.configure(text=str(int(self.current_value)))
            self.after(30, lambda: step_animation(remaining_steps - 1))
            
        step_animation(steps)
        
    def set_color(self, color: str):
        """Change the value color."""
        self.value_label.configure(text_color=color)


class AnimatedButton(ctk.CTkButton):
    """Button with hover animation effects."""
    
    def __init__(self, parent, text: str, command: Callable,
                 width: int = 120, height: int = 40,
                 style: str = "primary", **kwargs):
        
        colors = {
            "primary": Theme.ACCENT_PRIMARY,
            "success": Theme.ACCENT_SUCCESS,
            "danger": Theme.ACCENT_DANGER,
            "warning": Theme.ACCENT_WARNING,
            "secondary": Theme.BG_TERTIARY,
        }
        
        self.base_color = colors.get(style, Theme.ACCENT_PRIMARY)
        self.hover_color = Style._lighten_color(self.base_color, 15)

        text_color = "#000000" if style != "secondary" else Theme.TEXT_PRIMARY
        
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=self.base_color,
            hover_color=self.hover_color,
            text_color=text_color,
            font=Style.get_font("button"),
            corner_radius=10,
            **kwargs
        )


class StatusIndicator(ctk.CTkFrame):
    """Status indicator with pulsing animation."""
    
    def __init__(self, parent, text: str = "Ready", **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )
        
        self.status_colors = {
            "idle": Theme.TEXT_MUTED,
            "capturing": Theme.ACCENT_SUCCESS,
            "error": Theme.ACCENT_DANGER,
            "warning": Theme.ACCENT_WARNING,
        }
        
        self.dot = ctk.CTkLabel(
            self,
            text="●",
            font=("Segoe UI", 14),
            text_color=self.status_colors["idle"]
        )
        self.dot.pack(side="left", padx=(0, 8))
        
        self.label = ctk.CTkLabel(
            self,
            text=text,
            font=Style.get_font("small"),
            text_color=Theme.TEXT_SECONDARY
        )
        self.label.pack(side="left")
        
        self._pulse_active = False
        
    def set_status(self, status: str, text: Optional[str] = None):
        """Update status indicator."""
        color = self.status_colors.get(status, Theme.TEXT_MUTED)
        self.dot.configure(text_color=color)
        
        if text:
            self.label.configure(text=text)
            
        if status == "capturing":
            self._start_pulse()
        else:
            self._stop_pulse()
            
    def _start_pulse(self):
        """Start pulsing animation."""
        if self._pulse_active:
            return
        self._pulse_active = True
        self._pulse_animation()
        
    def _stop_pulse(self):
        """Stop pulsing animation."""
        self._pulse_active = False
        self.dot.configure(text_color=self.status_colors.get("idle"))
        
    def _pulse_animation(self, bright: bool = True):
        """Pulse the status dot."""
        if not self._pulse_active:
            return
            
        current_color = self.dot.cget("text_color")
        base_color = self.status_colors["capturing"]
        
        if bright:
            dim_color = Theme._lighten_color(base_color, -30)
            self.dot.configure(text_color=dim_color)
            self.after(600, lambda: self._pulse_animation(False))
        else:
            self.dot.configure(text_color=base_color)
            self.after(600, lambda: self._pulse_animation(True))


class SearchBar(ctk.CTkFrame):
    """Search input with integrated button."""
    
    def __init__(self, parent, placeholder: str = "Search...",
                 on_search: Optional[Callable] = None, **kwargs):
        super().__init__(
            parent,
            fg_color=Theme.BG_TERTIARY,
            corner_radius=8,
            **kwargs
        )
        
        self.on_search = on_search
        
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=Style.get_font("normal"),
            fg_color="transparent",
            border_width=0,
            text_color=Theme.TEXT_PRIMARY,
            height=35
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=10)
        self.entry.bind("<Return>", lambda e: self._trigger_search())
        
        self.search_btn = ctk.CTkButton(
            self,
            text="Search",
            width=80,
            height=30,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme._lighten_color(Theme.ACCENT_PRIMARY, 15),
            text_color=Theme.BG_PRIMARY,
            font=Style.get_font("small"),
            command=self._trigger_search,
            corner_radius=6
        )
        self.search_btn.pack(side="right", padx=5, pady=3)
        
        self.clear_btn = ctk.CTkButton(
            self,
            text="Clear",
            width=60,
            height=30,
            fg_color=Theme.BG_SECONDARY,
            hover_color=Theme.BG_CARD,
            text_color=Theme.TEXT_SECONDARY,
            font=Style.get_font("small"),
            command=self._clear,
            corner_radius=6
        )
        self.clear_btn.pack(side="right", padx=(5, 0), pady=3)
        
    def _trigger_search(self):
        """Trigger search callback."""
        if self.on_search:
            self.on_search(self.entry.get())
            
    def _clear(self):
        """Clear search field."""
        self.entry.delete(0, "end")
        if self.on_search:
            self.on_search("")
            
    def get_value(self) -> str:
        """Get current search value."""
        return self.entry.get()
        
    def set_value(self, value: str):
        """Set search value."""
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class ProtocolBadge(ctk.CTkLabel):
    """Colored badge for protocol display."""
    
    def __init__(self, parent, protocol: str, **kwargs):
        color = Theme.get_protocol_color(protocol)
        
        super().__init__(
            parent,
            text=protocol,
            font=Style.get_font("small"),
            text_color=Theme.BG_PRIMARY,
            fg_color=color,
            corner_radius=4,
            width=60,
            **kwargs
        )
