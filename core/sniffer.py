"""
Network packet capture engine using scapy.
Handles live packet sniffing with threading for non-blocking operation.
"""

import threading
import queue
import time
from datetime import datetime
from typing import Callable, Optional, Dict, List, Any
from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw
from scapy.layers.http import HTTPRequest, HTTPResponse


class PacketSniffer:
    """Main packet sniffing engine with threading support."""
    
    def __init__(self, packet_queue: queue.Queue):
        self.packet_queue = packet_queue
        self.is_running = False
        self.sniffer_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.packet_count = 0
        self.start_time: Optional[float] = None
        self.protocol_counts = {"TCP": 0, "UDP": 0, "ICMP": 0, "OTHER": 0}
        self._lock = threading.Lock()
        
    def start(self, interface: Optional[str] = None, 
              filter_protocol: str = "ALL") -> bool:
        """Start packet capture in a background thread."""
        if self.is_running:
            return False
            
        self.is_running = True
        self.stop_event.clear()
        self.start_time = time.time()
        
        self.sniffer_thread = threading.Thread(
            target=self._sniff_packets,
            args=(interface, filter_protocol),
            daemon=True
        )
        self.sniffer_thread.start()
        return True
        
    def stop(self) -> bool:
        """Stop packet capture safely."""
        if not self.is_running:
            return False
            
        self.stop_event.set()
        self.is_running = False
        
        if self.sniffer_thread and self.sniffer_thread.is_alive():
            self.sniffer_thread.join(timeout=2.0)
            
        return True
        
    def _sniff_packets(self, interface: Optional[str], filter_protocol: str):
        """Internal sniffing loop running in separate thread."""
        bpf_filter = self._build_bpf_filter(filter_protocol)
        
        try:
            sniff(
                iface=interface,
                filter=bpf_filter if bpf_filter else None,
                prn=self._process_packet,
                stop_filter=lambda x: self.stop_event.is_set(),
                store=False
            )
        except Exception as e:
            self.packet_queue.put({"error": str(e)})
            
    def _build_bpf_filter(self, protocol: str) -> str:
        """Build Berkeley Packet Filter string based on protocol selection."""
        protocol = protocol.upper()
        if protocol == "TCP":
            return "tcp"
        elif protocol == "UDP":
            return "udp"
        elif protocol == "ICMP":
            return "icmp"
        return ""
        
    def _process_packet(self, packet):
        """Process and parse captured packet."""
        if self.stop_event.is_set():
            return
            
        packet_data = self._parse_packet(packet)
        if packet_data:
            with self._lock:
                self.packet_count += 1
                proto = packet_data.get("protocol", "OTHER")
                if proto in self.protocol_counts:
                    self.protocol_counts[proto] += 1
                else:
                    self.protocol_counts["OTHER"] += 1
                    
            self.packet_queue.put(packet_data)
            
    def _parse_packet(self, packet) -> Optional[Dict[str, Any]]:
        """Extract relevant information from a scapy packet."""
        if not packet.haslayer(IP):
            return None
            
        ip_layer = packet[IP]
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        packet_info = {
            "timestamp": timestamp,
            "src_ip": ip_layer.src,
            "dst_ip": ip_layer.dst,
            "protocol": "OTHER",
            "src_port": None,
            "dst_port": None,
            "length": len(packet),
            "payload": "",
            "raw_packet": packet
        }
        
        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            packet_info["protocol"] = "TCP"
            packet_info["src_port"] = tcp_layer.sport
            packet_info["dst_port"] = tcp_layer.dport
            packet_info["flags"] = self._parse_tcp_flags(tcp_layer.flags)
            
            if packet.haslayer(HTTPRequest):
                packet_info["protocol"] = "HTTP"
                http_layer = packet[HTTPRequest]
                packet_info["payload"] = f"{http_layer.Method.decode()} {http_layer.Path.decode()}"
            elif packet.haslayer(HTTPResponse):
                packet_info["protocol"] = "HTTP"
                packet_info["payload"] = "HTTP Response"
            elif packet.haslayer(Raw):
                raw_data = packet[Raw].load
                packet_info["payload"] = self._clean_payload(raw_data[:100])
                
        elif packet.haslayer(UDP):
            udp_layer = packet[UDP]
            packet_info["protocol"] = "UDP"
            packet_info["src_port"] = udp_layer.sport
            packet_info["dst_port"] = udp_layer.dport
            
            if packet.haslayer(Raw):
                raw_data = packet[Raw].load
                packet_info["payload"] = self._clean_payload(raw_data[:100])
                
        elif packet.haslayer(ICMP):
            packet_info["protocol"] = "ICMP"
            icmp_layer = packet[ICMP]
            packet_info["payload"] = f"Type: {icmp_layer.type}, Code: {icmp_layer.code}"
            
        return packet_info
        
    def _parse_tcp_flags(self, flags) -> str:
        """Convert TCP flags to readable string."""
        flag_str = str(flags)
        if not flag_str:
            return "NONE"
        return flag_str
        
    def _clean_payload(self, data: bytes) -> str:
        """Clean binary payload for display."""
        try:
            text = data.decode('utf-8', errors='replace')
            text = ''.join(char if char.isprintable() or char.isspace() else '.' 
                          for char in text)
            return text[:80] + "..." if len(text) > 80 else text
        except:
            return "[Binary Data]"
            
    def get_stats(self) -> Dict[str, Any]:
        """Return current capture statistics."""
        with self._lock:
            duration = time.time() - self.start_time if self.start_time else 0
            return {
                "total_packets": self.packet_count,
                "tcp_count": self.protocol_counts["TCP"],
                "udp_count": self.protocol_counts["UDP"],
                "icmp_count": self.protocol_counts["ICMP"],
                "other_count": self.protocol_counts["OTHER"],
                "duration": duration,
                "is_running": self.is_running
            }
            
    def reset_stats(self):
        """Reset all counters."""
        with self._lock:
            self.packet_count = 0
            self.protocol_counts = {"TCP": 0, "UDP": 0, "ICMP": 0, "OTHER": 0}
            self.start_time = time.time() if self.is_running else None
