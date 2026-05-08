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
    """Export options dialog with improved workflow."""

    def __init__(self, parent, on_export_complete: callable):
        super().__init__(parent)

        self.title("Export Data")
        self.geometry("380x280")
        self.configure(fg_color=Theme.BG_PRIMARY)
        self.on_export_complete = on_export_complete
        self.selected_format = None

        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        """Build dialog UI with format selection and confirm workflow."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)

        header = ctk.CTkLabel(
            main_frame,
            text="Export Capture Data",
            font=Style.get_font("subtitle"),
            text_color=Theme.TEXT_PRIMARY
        )
        header.pack(anchor="w", pady=(0, 5))

        subheader = ctk.CTkLabel(
            main_frame,
            text="Choose export format to continue",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        subheader.pack(anchor="w", pady=(0, 20))

        # Format selection cards
        self.format_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.format_frame.pack(fill="x", pady=10)

        self.format_buttons = {}
        formats = [
            ("JSON", "Machine-readable format with full packet details"),
            ("TXT", "Human-readable log format"),
        ]

        for name, desc in formats:
            btn = self._create_format_card(self.format_frame, name, desc)
            btn.pack(fill="x", pady=5)
            self.format_buttons[name.lower()] = btn

        # Status message
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.status_label.pack(pady=(10, 5))

        # Action buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        self.cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=32,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_SECONDARY,
            font=Style.get_font("normal")
        )
        self.cancel_btn.pack(side="left")

        self.confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Confirm Export",
            command=self._on_confirm,
            width=130,
            height=32,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Style._lighten_color(Theme.ACCENT_PRIMARY, 15),
            text_color="#000000",
            font=Style.get_font("button"),
            state="disabled"
        )
        self.confirm_btn.pack(side="right")

    def _create_format_card(self, parent, name: str, desc: str):
        """Create a selectable format card."""
        card = ctk.CTkFrame(
            parent,
            fg_color=Theme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            cursor="hand2"
        )

        # Click handler
        card.bind("<Button-1>", lambda e, n=name.lower(): self._select_format(n))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)

        # Selection indicator
        indicator = ctk.CTkFrame(
            content,
            width=3,
            height=40,
            fg_color=Theme.BORDER_COLOR,
            corner_radius=2
        )
        indicator.pack(side="left", padx=(0, 12))
        card.indicator = indicator

        # Text content
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        title = ctk.CTkLabel(
            text_frame,
            text=name,
            font=Style.get_font("heading"),
            text_color=Theme.TEXT_PRIMARY,
            anchor="w"
        )
        title.pack(anchor="w")
        card.title_label = title

        subtitle = ctk.CTkLabel(
            text_frame,
            text=desc,
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED,
            anchor="w"
        )
        subtitle.pack(anchor="w")

        # Click binding for all child widgets
        for widget in [content, text_frame, title, subtitle]:
            widget.bind("<Button-1>", lambda e, n=name.lower(): self._select_format(n))

        return card

    def _select_format(self, format_name: str):
        """Handle format selection."""
        self.selected_format = format_name

        # Update UI to show selection
        for fmt, btn in self.format_buttons.items():
            if fmt == format_name:
                btn.configure(border_color=Theme.ACCENT_PRIMARY)
                btn.indicator.configure(fg_color=Theme.ACCENT_PRIMARY)
                btn.title_label.configure(text_color=Theme.ACCENT_PRIMARY)
            else:
                btn.configure(border_color=Theme.BORDER_COLOR)
                btn.indicator.configure(fg_color=Theme.BORDER_COLOR)
                btn.title_label.configure(text_color=Theme.TEXT_PRIMARY)

        # Enable confirm button
        self.confirm_btn.configure(state="normal")
        self.status_label.configure(text=f"Selected: {format_name.upper()}")

    def _on_confirm(self):
        """Proceed to file picker after format selection."""
        if not self.selected_format:
            return

        # Open file picker
        from tkinter import filedialog

        default_name = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.selected_format}"

        file_path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=f".{self.selected_format}",
            initialfile=default_name,
            filetypes=[
                (f"{self.selected_format.upper()} files", f"*.{self.selected_format}"),
                ("All files", "*.*")
            ],
            title=f"Save as {self.selected_format.upper()}"
        )

        if file_path:
            self.on_export_complete(self.selected_format, file_path)
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
