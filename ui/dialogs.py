"""
Dialog windows for packet details and export.
"""

import customtkinter as ctk
from typing import Dict, Any
from ui.styles import Theme, Style


class PacketDetailsDialog(ctk.CTkToplevel):
    """Detailed packet information dialog."""
    
    def __init__(self, parent, packet_details: Dict[str, Any]):
        super().__init__(parent)
        
        self.title("Packet Details")
        self.geometry("600x700")
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        self.transient(parent)
        self.grab_set()
        
        self._build_ui(packet_details)
        self._center_on_parent(parent)
        
    def _build_ui(self, details: Dict[str, Any]):
        """Build dialog UI."""
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Theme.BG_PRIMARY,
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        header = ctk.CTkLabel(
            main_frame,
            text="Packet Details",
            font=Style.get_font("subtitle"),
            text_color=Theme.ACCENT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 20))
        
        for section_name, section_data in details.items():
            if not section_data:
                continue
                
            section_frame = ctk.CTkFrame(
                main_frame,
                fg_color=Theme.BG_CARD,
                corner_radius=10,
                border_width=1,
                border_color=Theme.BORDER_COLOR
            )
            section_frame.pack(fill="x", pady=10)
            
            title = section_name.replace("_", " ").title()
            section_label = ctk.CTkLabel(
                section_frame,
                text=title,
                font=Style.get_font("heading"),
                text_color=Theme.TEXT_PRIMARY
            )
            section_label.pack(anchor="w", padx=15, pady=(15, 10))
            
            for key, value in section_data.items():
                row = ctk.CTkFrame(section_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=3)
                
                key_label = ctk.CTkLabel(
                    row,
                    text=f"{key}:",
                    font=Style.get_font("small"),
                    text_color=Theme.TEXT_MUTED,
                    width=150,
                    anchor="w"
                )
                key_label.pack(side="left")
                
                value_label = ctk.CTkLabel(
                    row,
                    text=str(value),
                    font=Style.get_font("mono"),
                    text_color=Theme.TEXT_SECONDARY,
                    anchor="w"
                )
                value_label.pack(side="left", fill="x", expand=True)
                
        close_btn = ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.destroy,
            width=120,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Style._lighten_color(Theme.ACCENT_PRIMARY, 15),
            text_color=Theme.BG_PRIMARY,
            font=Style.get_font("button")
        )
        close_btn.pack(pady=20)
        
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")


class ExportDialog(ctk.CTkToplevel):
    """Export options dialog."""
    
    def __init__(self, parent, on_export: callable):
        super().__init__(parent)
        
        self.title("Export Packets")
        self.geometry("400x250")
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.on_export = on_export
        
        self.transient(parent)
        self.grab_set()
        
        self.format_var = ctk.StringVar(value="json")
        
        self._build_ui()
        self._center_on_parent(parent)
        
    def _build_ui(self):
        """Build dialog UI."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        header = ctk.CTkLabel(
            main_frame,
            text="Export Packet Data",
            font=Style.get_font("subtitle"),
            text_color=Theme.TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 20))
        
        format_label = ctk.CTkLabel(
            main_frame,
            text="Select Format:",
            font=Style.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY
        )
        format_label.pack(anchor="w", pady=(0, 10))
        
        formats_frame = ctk.CTkFrame(main_frame, fg_color=Theme.BG_CARD, corner_radius=8)
        formats_frame.pack(fill="x", pady=10)
        
        formats = [
            ("JSON", "json", "Machine-readable format"),
            ("Text", "txt", "Human-readable log"),
            ("CSV", "csv", "Spreadsheet format"),
        ]
        
        for name, value, desc in formats:
            radio = ctk.CTkRadioButton(
                formats_frame,
                text=f"{name} - {desc}",
                variable=self.format_var,
                value=value,
                font=Style.get_font("normal"),
                text_color=Theme.TEXT_SECONDARY,
                fg_color=Theme.ACCENT_PRIMARY,
                border_color=Theme.BORDER_COLOR
            )
            radio.pack(anchor="w", padx=15, pady=8)
            
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BG_CARD,
            text_color=Theme.TEXT_SECONDARY
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        export_btn = ctk.CTkButton(
            btn_frame,
            text="Export",
            command=self._do_export,
            width=100,
            fg_color=Theme.ACCENT_SUCCESS,
            hover_color=Style._lighten_color(Theme.ACCENT_SUCCESS, 15),
            text_color=Theme.BG_PRIMARY
        )
        export_btn.pack(side="right")
        
    def _do_export(self):
        """Trigger export callback."""
        self.on_export(self.format_var.get())
        self.destroy()
        
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")


class ErrorDialog(ctk.CTkToplevel):
    """Error message dialog."""
    
    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("450x200")
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        self.transient(parent)
        self.grab_set()
        
        self._build_ui(message)
        self._center_on_parent(parent)
        
    def _build_ui(self, message: str):
        """Build dialog UI."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        icon_label = ctk.CTkLabel(
            frame,
            text="⚠",
            font=("Segoe UI", 48),
            text_color=Theme.ACCENT_DANGER
        )
        icon_label.pack(pady=(0, 15))
        
        msg_label = ctk.CTkLabel(
            frame,
            text=message,
            font=Style.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY,
            wraplength=350
        )
        msg_label.pack(pady=10)
        
        ok_btn = ctk.CTkButton(
            frame,
            text="OK",
            command=self.destroy,
            width=100,
            fg_color=Theme.ACCENT_DANGER,
            hover_color=Style._lighten_color(Theme.ACCENT_DANGER, 15),
            text_color=Theme.TEXT_PRIMARY
        )
        ok_btn.pack(pady=15)
        
    def _center_on_parent(self, parent):
        """Center dialog on parent window."""
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
