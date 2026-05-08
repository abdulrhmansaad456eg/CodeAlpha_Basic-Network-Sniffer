"""
Packet filtering and search utilities.
"""

import re
from typing import List, Dict, Any, Callable


class PacketFilter:
    """Filter and search through captured packets."""
    
    @staticmethod
    def filter_by_protocol(packets: List[Dict[str, Any]], 
                          protocol: str) -> List[Dict[str, Any]]:
        """Filter packets by protocol type."""
        if protocol.upper() == "ALL":
            return packets
        return [p for p in packets if p.get("protocol", "").upper() == protocol.upper()]
        
    @staticmethod
    def filter_by_ip(packets: List[Dict[str, Any]], 
                     ip_address: str) -> List[Dict[str, Any]]:
        """Filter packets by source or destination IP."""
        ip_address = ip_address.strip()
        return [
            p for p in packets 
            if ip_address in p.get("src_ip", "") or ip_address in p.get("dst_ip", "")
        ]
        
    @staticmethod
    def filter_by_port(packets: List[Dict[str, Any]], 
                       port: int) -> List[Dict[str, Any]]:
        """Filter packets by source or destination port."""
        return [
            p for p in packets 
            if p.get("src_port") == port or p.get("dst_port") == port
        ]
        
    @staticmethod
    def search_payload(packets: List[Dict[str, Any]], 
                       search_term: str,
                       case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search packets by payload content."""
        if not case_sensitive:
            search_term = search_term.lower()
            
        results = []
        for packet in packets:
            payload = packet.get("payload", "")
            if not case_sensitive:
                payload = payload.lower()
            if search_term in payload:
                results.append(packet)
        return results
        
    @staticmethod
    def advanced_search(packets: List[Dict[str, Any]],
                       query: str,
                       search_in: List[str] = None) -> List[Dict[str, Any]]:
        """
        Advanced search across multiple packet fields.
        
        Args:
            packets: List of packet dictionaries
            query: Search string
            search_in: List of fields to search (ip, port, protocol, payload)
        """
        if search_in is None:
            search_in = ["ip", "port", "protocol", "payload"]
            
        query = query.lower().strip()
        results = []
        
        for packet in packets:
            match_found = False
            
            if "ip" in search_in:
                if (query in packet.get("src_ip", "").lower() or 
                    query in packet.get("dst_ip", "").lower()):
                    match_found = True
                    
            if "port" in search_in and not match_found:
                src_port = str(packet.get("src_port", ""))
                dst_port = str(packet.get("dst_port", ""))
                if query in src_port or query in dst_port:
                    match_found = True
                    
            if "protocol" in search_in and not match_found:
                if query in packet.get("protocol", "").lower():
                    match_found = True
                    
            if "payload" in search_in and not match_found:
                if query in packet.get("payload", "").lower():
                    match_found = True
                    
            if match_found:
                results.append(packet)
                
        return results
