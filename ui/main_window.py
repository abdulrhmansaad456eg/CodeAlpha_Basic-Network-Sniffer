"""
Main application window for the Network Sniffer.
Complete UI with packet table, stats, controls, and search.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import queue
import threading
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from core.sniffer import PacketSniffer
from core.packet_parser import PacketParser
from core.filters import PacketFilter
from core.exporter import PacketExporter
from ui.styles import Theme, Style
from ui.widgets import StatCard, AnimatedButton, StatusIndicator, SearchBar, ProtocolBadge
from ui.dialogs import PacketDetailsDialog, ExportDialog, ErrorDialog


class MainWindow(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        Style.configure_ctk()
        
        self.title("Network Sniffer")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        self.configure(fg_color=Theme.BG_PRIMARY)
        
        self.packet_queue: queue.Queue = queue.Queue()
        self.sniffer = PacketSniffer(self.packet_queue)
        self.packet_store: List[Dict[str, Any]] = []
        self.displayed_packets: List[Dict[str, Any]] = []
        
        self.filter_protocol = "ALL"
        self.search_query = ""
        self.is_capturing = False
        
        self._build_ui()
        self._start_update_loop()
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
    def _build_ui(self):
        """Build the complete user interface."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._build_sidebar()
        self._build_main_content()
        
    def _build_sidebar(self):
        """Build left sidebar with controls."""
        sidebar = ctk.CTkFrame(
            self,
            fg_color=Theme.BG_SECONDARY,
            width=250,
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=20)
        
        logo = ctk.CTkLabel(
            logo_frame,
            text="Network Sniffer",
            font=("Segoe UI", 20, "bold"),
            text_color=Theme.ACCENT_PRIMARY
        )
        logo.pack(anchor="w")
        
        sep = ctk.CTkFrame(sidebar, height=2, fg_color=Theme.BORDER_COLOR)
        sep.pack(fill="x", padx=20, pady=10)
        
        controls_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        capture_label = ctk.CTkLabel(
            controls_frame,
            text="CAPTURE",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        capture_label.pack(anchor="w", pady=(0, 10))
        
        self.start_btn = AnimatedButton(
            controls_frame,
            text="Start Capture",
            command=self._start_capture,
            style="success",
            width=210
        )
        self.start_btn.pack(pady=5)
        
        self.stop_btn = AnimatedButton(
            controls_frame,
            text="Stop Capture",
            command=self._stop_capture,
            style="danger",
            width=210
        )
        self.stop_btn.pack(pady=5)
        self.stop_btn.configure(state="disabled")
        
        sep2 = ctk.CTkFrame(sidebar, height=2, fg_color=Theme.BORDER_COLOR)
        sep2.pack(fill="x", padx=20, pady=15)
        
        filter_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="PROTOCOL FILTER",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        filter_label.pack(anchor="w", pady=(0, 10))
        
        self.protocol_filter = ctk.CTkComboBox(
            filter_frame,
            values=["ALL", "TCP", "UDP", "ICMP"],
            command=self._on_protocol_change,
            width=210,
            font=Style.get_font("normal"),
            fg_color=Theme.BG_TERTIARY,
            border_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_PRIMARY,
            dropdown_fg_color=Theme.BG_CARD,
            button_color=Theme.ACCENT_PRIMARY
        )
        self.protocol_filter.pack(pady=5)
        self.protocol_filter.set("ALL")
        
        sep3 = ctk.CTkFrame(sidebar, height=2, fg_color=Theme.BORDER_COLOR)
        sep3.pack(fill="x", padx=20, pady=15)
        
        export_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=10)
        
        export_label = ctk.CTkLabel(
            export_frame,
            text="EXPORT",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        export_label.pack(anchor="w", pady=(0, 10))
        
        export_btn = AnimatedButton(
            export_frame,
            text="Export Data",
            command=self._show_export_dialog,
            style="primary",
            width=210
        )
        export_btn.pack(pady=5)
        
        clear_btn = ctk.CTkButton(
            export_frame,
            text="Clear All Data",
            command=self._clear_packets,
            width=210,
            height=35,
            fg_color=Theme.BG_TERTIARY,
            hover_color=Theme.ACCENT_DANGER,
            text_color=Theme.TEXT_SECONDARY,
            font=Style.get_font("button")
        )
        clear_btn.pack(pady=5)
        
        self.status_indicator = StatusIndicator(sidebar, text="Ready")
        self.status_indicator.pack(side="bottom", pady=20, padx=20)
        
    def _build_main_content(self):
        """Build main content area."""
        main = ctk.CTkFrame(self, fg_color=Theme.BG_PRIMARY, corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)
        
        self._build_stats_bar(main)
        self._build_packet_table(main)
        self._build_bottom_bar(main)
        
    def _build_stats_bar(self, parent):
        """Build statistics cards bar."""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.total_card = StatCard(
            stats_frame,
            title="Total Packets",
            value="0",
            color=Theme.TEXT_PRIMARY
        )
        self.total_card.grid(row=0, column=0, padx=5, sticky="nsew")
        
        self.tcp_card = StatCard(
            stats_frame,
            title="TCP Packets",
            value="0",
            color=Theme.TCP_COLOR
        )
        self.tcp_card.grid(row=0, column=1, padx=5, sticky="nsew")
        
        self.udp_card = StatCard(
            stats_frame,
            title="UDP Packets",
            value="0",
            color=Theme.UDP_COLOR
        )
        self.udp_card.grid(row=0, column=2, padx=5, sticky="nsew")
        
        self.icmp_card = StatCard(
            stats_frame,
            title="ICMP Packets",
            value="0",
            color=Theme.ICMP_COLOR
        )
        self.icmp_card.grid(row=0, column=3, padx=5, sticky="nsew")
        
        self.duration_card = StatCard(
            stats_frame,
            title="Duration (s)",
            value="0",
            color=Theme.ACCENT_WARNING
        )
        self.duration_card.grid(row=0, column=4, padx=5, sticky="nsew")
        
    def _build_packet_table(self, parent):
        """Build packet table with treeview."""
        table_frame = ctk.CTkFrame(
            parent,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)
        
        search_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        search_frame.grid_columnconfigure(0, weight=1)
        
        table_header_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        table_header_frame.pack(side="left", fill="y")

        table_label = ctk.CTkLabel(
            table_header_frame,
            text="Captured Packets",
            font=Style.get_font("heading"),
            text_color=Theme.TEXT_PRIMARY
        )
        table_label.pack(anchor="w")

        # Help text about binary payloads
        help_label = ctk.CTkLabel(
            table_header_frame,
            text="Encrypted or binary payloads display as [Binary Data]",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        help_label.pack(anchor="w")

        self.search_bar = SearchBar(
            search_frame,
            placeholder="Search by IP, port, protocol, or payload...",
            on_search=self._on_search,
            width=400
        )
        self.search_bar.pack(side="right")
        
        columns = ("timestamp", "protocol", "src", "dst", "length", "payload")
        
        tree_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background=Theme.BG_TERTIARY,
            foreground=Theme.TEXT_SECONDARY,
            fieldbackground=Theme.BG_TERTIARY,
            rowheight=28,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=Theme.BG_SECONDARY,
            foreground=Theme.TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", Theme.ACCENT_PRIMARY)],
            foreground=[("selected", Theme.BG_PRIMARY)]
        )
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )
        
        self.tree.heading("timestamp", text="Time")
        self.tree.heading("protocol", text="Protocol")
        self.tree.heading("src", text="Source")
        self.tree.heading("dst", text="Destination")
        self.tree.heading("length", text="Length")
        self.tree.heading("payload", text="Payload Preview")
        
        self.tree.column("timestamp", width=100, anchor="center")
        self.tree.column("protocol", width=80, anchor="center")
        self.tree.column("src", width=200, anchor="w")
        self.tree.column("dst", width=200, anchor="w")
        self.tree.column("length", width=80, anchor="center")
        self.tree.column("payload", width=300, anchor="w")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.tree.bind("<Double-1>", self._on_packet_select)
        self.tree.bind("<Return>", self._on_packet_select)
        
    def _build_bottom_bar(self, parent):
        """Build bottom info bar."""
        bottom_frame = ctk.CTkFrame(parent, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        self.packet_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Showing 0 packets",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.packet_count_label.pack(side="left")
        
        self.last_update_label = ctk.CTkLabel(
            bottom_frame,
            text="Last update: Never",
            font=Style.get_font("small"),
            text_color=Theme.TEXT_MUTED
        )
        self.last_update_label.pack(side="right")
        
    def _start_capture(self):
        """Start packet capture."""
        try:
            if self.sniffer.start(filter_protocol=self.filter_protocol):
                self.is_capturing = True
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                self.status_indicator.set_status("capturing", "Capturing...")
                self._clear_packets(silent=True)
        except Exception as e:
            ErrorDialog(self, "Capture Error", f"Failed to start capture:\n{str(e)}")
            
    def _stop_capture(self):
        """Stop packet capture."""
        self.sniffer.stop()
        self.is_capturing = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_indicator.set_status("idle", "Stopped")
        
    def _on_protocol_change(self, choice):
        """Handle protocol filter change."""
        self.filter_protocol = choice
        if self.is_capturing:
            self._stop_capture()
            self.after(300, self._start_capture)
            
    def _on_search(self, query: str):
        """Handle search query."""
        self.search_query = query.strip().lower()
        self._refresh_display()
        
    def _refresh_display(self):
        """Refresh table with filtered packets."""
        filtered = self.packet_store
        
        if self.filter_protocol != "ALL":
            filtered = PacketFilter.filter_by_protocol(filtered, self.filter_protocol)
            
        if self.search_query:
            filtered = PacketFilter.advanced_search(filtered, self.search_query)
            
        self.displayed_packets = filtered
        self._update_table()
        self._update_packet_count()
        
    def _update_table(self):
        """Update treeview with current packets."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for packet in self.displayed_packets[-500:]:
            values = PacketParser.format_packet_for_table(packet)
            self.tree.insert("", "end", values=values, tags=(packet.get("protocol", ""),))
            
        self._apply_protocol_tags()
        
    def _apply_protocol_tags(self):
        """Apply color tags to protocol column."""
        self.tree.tag_configure("TCP", foreground=Theme.TCP_COLOR)
        self.tree.tag_configure("UDP", foreground=Theme.UDP_COLOR)
        self.tree.tag_configure("ICMP", foreground=Theme.ICMP_COLOR)
        self.tree.tag_configure("HTTP", foreground=Theme.HTTP_COLOR)
        
    def _on_packet_select(self, event):
        """Handle packet selection."""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        idx = self.tree.index(item)
        
        if idx < len(self.displayed_packets):
            packet = self.displayed_packets[idx]
            details = PacketParser.get_detailed_info(packet)
            PacketDetailsDialog(self, details)
            
    def _show_export_dialog(self):
        """Export packets directly as JSON without dialogs."""
        if not self.packet_store:
            ErrorDialog(self, "No Data", "No packets to export.\nStart a capture first.")
            return

        # Direct export to logs folder
        filename = PacketExporter.generate_filename("json")
        filepath = PacketExporter.get_export_path(filename)

        try:
            success = PacketExporter.export_to_json(self.packet_store, filepath)
            if success:
                self.status_indicator.set_status("idle", f"Exported to {filename}")
            else:
                ErrorDialog(self, "Export Failed", "Could not export data to file.")
        except Exception as e:
            ErrorDialog(self, "Export Error", f"Export failed:\n{str(e)}")
            
    def _clear_packets(self, silent: bool = False):
        """Clear all captured packets."""
        self.packet_store.clear()
        self.displayed_packets.clear()
        self.sniffer.reset_stats()
        self._update_table()
        self._update_stats()
        self._update_packet_count()
        if not silent:
            self.status_indicator.set_status("idle", "Data cleared")
            
    def _update_stats(self):
        """Update statistics cards."""
        stats = self.sniffer.get_stats()
        
        self.total_card.set_value(stats["total_packets"])
        self.tcp_card.set_value(stats["tcp_count"])
        self.udp_card.set_value(stats["udp_count"])
        self.icmp_card.set_value(stats["icmp_count"])
        self.duration_card.set_value(int(stats["duration"]))
        
    def _update_packet_count(self):
        """Update packet count label."""
        total = len(self.packet_store)
        showing = len(self.displayed_packets)
        self.packet_count_label.configure(
            text=f"Showing {showing} of {total} packets"
        )
        
    def _start_update_loop(self):
        """Start the UI update loop."""
        self._update_ui()
        
    def _update_ui(self):
        """Main UI update loop - runs every 100ms."""
        while True:
            try:
                packet = self.packet_queue.get_nowait()
                if "error" in packet:
                    self._handle_error(packet["error"])
                else:
                    self.packet_store.append(packet)
                    if self._matches_filters(packet):
                        self.displayed_packets.append(packet)
                        values = PacketParser.format_packet_for_table(packet)
                        self.tree.insert("", "end", values=values, 
                                       tags=(packet.get("protocol", ""),))
                        if len(self.tree.get_children()) > 500:
                            self.tree.delete(self.tree.get_children()[0])
            except queue.Empty:
                break
                
        if self.is_capturing:
            self._update_stats()
            
        self.last_update_label.configure(
            text=f"Last update: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        self.after(100, self._update_ui)
        
    def _matches_filters(self, packet: Dict[str, Any]) -> bool:
        """Check if packet matches current filters."""
        if self.filter_protocol != "ALL":
            if packet.get("protocol", "").upper() != self.filter_protocol:
                return False
                
        if self.search_query:
            search_fields = [
                packet.get("src_ip", ""),
                packet.get("dst_ip", ""),
                packet.get("protocol", ""),
                str(packet.get("src_port", "")),
                str(packet.get("dst_port", "")),
                packet.get("payload", "")
            ]
            if not any(self.search_query in str(f).lower() for f in search_fields):
                return False
                
        return True
        
    def _handle_error(self, error_msg: str):
        """Handle capture errors."""
        self._stop_capture()
        ErrorDialog(self, "Capture Error", 
                   f"Packet capture failed:\n{error_msg}\n\n"
                   f"Note: You may need administrator privileges.")
        
    def _on_close(self):
        """Handle window close."""
        self.sniffer.stop()
        self.destroy()


# Keep reference for theme
Theme._lighten_color = staticmethod(Style._lighten_color)
