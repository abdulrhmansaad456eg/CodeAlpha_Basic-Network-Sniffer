"""
Advanced packet parsing utilities for detailed packet inspection.
"""

from typing import Dict, Any, List, Optional
from scapy.all import IP, TCP, UDP, ICMP, Raw, ARP, DNS, DNSQR
from scapy.layers.http import HTTPRequest, HTTPResponse


class PacketParser:
    """Parse packets for detailed analysis and display."""
    
    @staticmethod
    def get_detailed_info(packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed packet information for the details view."""
        raw_packet = packet_data.get("raw_packet")
        if not raw_packet:
            return {}
            
        details = {
            "general": {
                "Timestamp": packet_data.get("timestamp", "N/A"),
                "Protocol": packet_data.get("protocol", "N/A"),
                "Packet Length": f"{packet_data.get('length', 0)} bytes",
                "Source IP": packet_data.get("src_ip", "N/A"),
                "Destination IP": packet_data.get("dst_ip", "N/A"),
            },
            "ip_layer": {},
            "transport_layer": {},
            "payload": {}
        }
        
        if raw_packet.haslayer(IP):
            ip = raw_packet[IP]
            details["ip_layer"] = {
                "Version": ip.version,
                "Header Length": f"{ip.ihl * 4} bytes",
                "Total Length": f"{ip.len} bytes",
                "Identification": ip.id,
                "TTL": ip.ttl,
                "Checksum": hex(ip.chksum) if ip.chksum else "0x0000",
                "Source": ip.src,
                "Destination": ip.dst,
            }
            
        protocol = packet_data.get("protocol", "")
        
        if protocol == "TCP" and raw_packet.haslayer(TCP):
            tcp = raw_packet[TCP]
            details["transport_layer"] = {
                "Source Port": tcp.sport,
                "Destination Port": tcp.dport,
                "Sequence Number": tcp.seq,
                "Acknowledgment": tcp.ack,
                "Data Offset": f"{tcp.dataofs * 4} bytes",
                "Flags": str(tcp.flags),
                "Window Size": tcp.window,
                "Checksum": hex(tcp.chksum) if tcp.chksum else "0x0000",
            }
            
        elif protocol == "UDP" and raw_packet.haslayer(UDP):
            udp = raw_packet[UDP]
            details["transport_layer"] = {
                "Source Port": udp.sport,
                "Destination Port": udp.dport,
                "Length": f"{udp.len} bytes",
                "Checksum": hex(udp.chksum) if udp.chksum else "0x0000",
            }
            
        elif protocol == "ICMP" and raw_packet.haslayer(ICMP):
            icmp = raw_packet[ICMP]
            details["transport_layer"] = {
                "Type": icmp.type,
                "Code": icmp.code,
                "Checksum": hex(icmp.chksum) if icmp.chksum else "0x0000",
                "ID": getattr(icmp, 'id', 'N/A'),
                "Sequence": getattr(icmp, 'seq', 'N/A'),
            }
            
        payload_text = packet_data.get("payload", "")
        if payload_text:
            details["payload"] = {
                "Preview": payload_text[:500],
                "Size": f"{len(payload_text)} characters"
            }
        else:
            details["payload"] = {"Preview": "[No payload data]", "Size": "0 bytes"}
            
        return details
        
    @staticmethod
    def format_packet_for_table(packet_data: Dict[str, Any]) -> List[str]:
        """Format packet data for table display."""
        src_port = packet_data.get("src_port")
        dst_port = packet_data.get("dst_port")
        
        src_display = packet_data.get("src_ip", "N/A")
        dst_display = packet_data.get("dst_ip", "N/A")
        
        if src_port:
            src_display += f":{src_port}"
        if dst_port:
            dst_display += f":{dst_port}"
            
        payload = packet_data.get("payload", "")
        if len(payload) > 40:
            payload = payload[:37] + "..."
            
        return [
            str(packet_data.get("timestamp", "")),
            packet_data.get("protocol", ""),
            src_display,
            dst_display,
            str(packet_data.get("length", 0)),
            payload
        ]
