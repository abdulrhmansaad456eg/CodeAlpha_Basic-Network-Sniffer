"""
Export captured packets to various file formats.
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any


class PacketExporter:
    """Export packet data to different formats."""
    
    @staticmethod
    def export_to_json(packets: List[Dict[str, Any]], 
                       filepath: str) -> bool:
        """Export packets to JSON format."""
        try:
            export_data = []
            for packet in packets:
                packet_copy = packet.copy()
                packet_copy.pop("raw_packet", None)
                export_data.append(packet_copy)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JSON export error: {e}")
            return False
            
    @staticmethod
    def export_to_txt(packets: List[Dict[str, Any]], 
                      filepath: str) -> bool:
        """Export packets to human-readable text format."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("NETWORK PACKET CAPTURE LOG\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Packets: {len(packets)}\n")
                f.write("=" * 80 + "\n\n")
                
                for i, packet in enumerate(packets, 1):
                    f.write(f"Packet #{i}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"Timestamp: {packet.get('timestamp', 'N/A')}\n")
                    f.write(f"Protocol: {packet.get('protocol', 'N/A')}\n")
                    f.write(f"Source: {packet.get('src_ip', 'N/A')}")
                    if packet.get('src_port'):
                        f.write(f":{packet['src_port']}")
                    f.write("\n")
                    f.write(f"Destination: {packet.get('dst_ip', 'N/A')}")
                    if packet.get('dst_port'):
                        f.write(f":{packet['dst_port']}")
                    f.write("\n")
                    f.write(f"Length: {packet.get('length', 0)} bytes\n")
                    
                    payload = packet.get('payload', '')
                    if payload:
                        f.write(f"Payload: {payload}\n")
                    f.write("\n")
                    
            return True
        except Exception as e:
            print(f"TXT export error: {e}")
            return False
            
    @staticmethod
    def export_to_csv(packets: List[Dict[str, Any]], 
                      filepath: str) -> bool:
        """Export packets to CSV format."""
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'Protocol', 'Source IP', 'Source Port',
                    'Destination IP', 'Destination Port', 'Length', 'Payload'
                ])
                
                for packet in packets:
                    writer.writerow([
                        packet.get('timestamp', ''),
                        packet.get('protocol', ''),
                        packet.get('src_ip', ''),
                        packet.get('src_port', ''),
                        packet.get('dst_ip', ''),
                        packet.get('dst_port', ''),
                        packet.get('length', 0),
                        packet.get('payload', '')
                    ])
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
            
    @staticmethod
    def generate_filename(extension: str) -> str:
        """Generate a timestamped filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"capture_{timestamp}.{extension}"
        
    @staticmethod
    def get_export_path(filename: str, logs_dir: str = "logs") -> str:
        """Get full path for export file."""
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        return os.path.join(logs_dir, filename)
