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
    """Export options dialog with clean compact design."""

    def __init__(self, parent, on_export_complete: callable):
        super().__init__(parent)

        self.title("Export Data")
        self.geometry("500x300")
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.on_export_complete = on_export_complete
        self.selected_format = ctk.StringVar(value="")

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        """Build compact export dialog with radio buttons."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Export Format",
            font=Style.get_font("heading"),
            text_color=Theme.TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 15))

        # Radio button frame
        radio_frame = ctk.CTkFrame(main_frame, fg_color=Theme.BG_CARD, corner_radius=10)
        radio_frame.pack(fill="x", pady=10)

        # JSON option
        self.json_radio = ctk.CTkRadioButton(
            radio_frame,
            text="JSON  -  Machine-readable format",
            variable=self.selected_format,
            value="json",
            font=Style.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.ACCENT_PRIMARY,
            border_color=Theme.BORDER_COLOR,
            command=self._on_selection_change
        )
        self.json_radio.pack(anchor="w", padx=20, pady=(20, 10))

        # TXT option
        self.txt_radio = ctk.CTkRadioButton(
            radio_frame,
            text="TXT   -  Human-readable log",
            variable=self.selected_format,
            value="txt",
            font=Style.get_font("normal"),
            text_color=Theme.TEXT_SECONDARY,
            fg_color=Theme.ACCENT_PRIMARY,
            border_color=Theme.BORDER_COLOR,
            command=self._on_selection_change
        )
        self.txt_radio.pack(anchor="w", padx=20, pady=(10, 20))

        # Button frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))

        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=35,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_SECONDARY,
            font=Style.get_font("button")
        )
        cancel_btn.pack(side="left")

        # Export button - text changes based on selection
        self.export_btn = ctk.CTkButton(
            btn_frame,
            text="Export",
            command=self._on_export,
            width=140,
            height=35,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Style._lighten_color(Theme.ACCENT_PRIMARY, 15),
            text_color="#000000",
            font=Style.get_font("button"),
            state="disabled"
        )
        self.export_btn.pack(side="right")

    def _on_selection_change(self):
        """Update button when format is selected."""
        selected = self.selected_format.get()
        if selected:
            self.export_btn.configure(
                state="normal",
                text=f"Save as {selected.upper()}"
            )

    def _on_export(self):
        """Open file picker and export."""
        selected = self.selected_format.get()
        if not selected:
            return

        from tkinter import filedialog

        default_name = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{selected}"

        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=f".{selected}",
            initialfile=default_name,
            filetypes=[
                (f"{selected.upper()} files", f"*.{selected}"),
                ("All files", "*.*")
            ],
            title=f"Save as {selected.upper()}"
        )

        if file_path:
            self.on_export_complete(selected, file_path)
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
