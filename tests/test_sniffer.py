"""
Unit tests for the network sniffer components.
"""

import unittest
import queue
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sniffer import PacketSniffer
from core.packet_parser import PacketParser
from core.filters import PacketFilter
from core.exporter import PacketExporter


def create_mock_packet(protocol="TCP", src_ip="192.168.1.1", dst_ip="192.168.1.2",
                      src_port=12345, dst_port=80, payload="test"):
    """Create a mock packet dictionary for testing."""
    return {
        "protocol": protocol,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "payload": payload,
        "length": 100,
        "timestamp": "12:00:00.000",
        "raw_packet": None
    }


class TestPacketFilter(unittest.TestCase):
    """Test packet filtering functionality."""
    
    def setUp(self):
        self.packets = [
            create_mock_packet("TCP", "192.168.1.1", "192.168.1.2", 12345, 80),
            create_mock_packet("UDP", "192.168.1.1", "192.168.1.3", 53, 53),
            create_mock_packet("ICMP", "192.168.1.1", "192.168.1.4"),
            create_mock_packet("TCP", "10.0.0.1", "192.168.1.2", 8080, 443),
        ]
        
    def test_filter_by_protocol(self):
        tcp_packets = PacketFilter.filter_by_protocol(self.packets, "TCP")
        self.assertEqual(len(tcp_packets), 2)
        
        udp_packets = PacketFilter.filter_by_protocol(self.packets, "UDP")
        self.assertEqual(len(udp_packets), 1)
        
        icmp_packets = PacketFilter.filter_by_protocol(self.packets, "ICMP")
        self.assertEqual(len(icmp_packets), 1)
        
    def test_filter_by_ip(self):
        packets = PacketFilter.filter_by_ip(self.packets, "192.168.1.2")
        self.assertEqual(len(packets), 2)
        
    def test_filter_by_port(self):
        packets = PacketFilter.filter_by_port(self.packets, 53)
        self.assertEqual(len(packets), 1)
        
    def test_advanced_search(self):
        results = PacketFilter.advanced_search(self.packets, "192.168")
        self.assertEqual(len(results), 4)


class TestPacketExporter(unittest.TestCase):
    """Test export functionality."""
    
    def setUp(self):
        self.packets = [
            create_mock_packet("TCP", "192.168.1.1", "192.168.1.2", 12345, 80, "GET / HTTP"),
            create_mock_packet("UDP", "192.168.1.1", "192.168.1.3", 53, 53, "DNS query"),
        ]
        self.test_dir = "logs"
        os.makedirs(self.test_dir, exist_ok=True)
        
    def test_generate_filename(self):
        filename = PacketExporter.generate_filename("json")
        self.assertTrue(filename.startswith("capture_"))
        self.assertTrue(filename.endswith(".json"))
        
    def test_export_to_json(self):
        test_file = os.path.join(self.test_dir, "test_export.json")
        result = PacketExporter.export_to_json(self.packets, test_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        if os.path.exists(test_file):
            os.remove(test_file)
            
    def test_export_to_txt(self):
        test_file = os.path.join(self.test_dir, "test_export.txt")
        result = PacketExporter.export_to_txt(self.packets, test_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        if os.path.exists(test_file):
            os.remove(test_file)
            
    def test_export_to_csv(self):
        test_file = os.path.join(self.test_dir, "test_export.csv")
        result = PacketExporter.export_to_csv(self.packets, test_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        if os.path.exists(test_file):
            os.remove(test_file)


class TestPacketParser(unittest.TestCase):
    """Test packet parser."""
    
    def test_format_packet_for_table(self):
        packet = create_mock_packet("TCP", "192.168.1.1", "192.168.1.2", 12345, 80, "test data")
        
        values = PacketParser.format_packet_for_table(packet)
        self.assertEqual(len(values), 6)
        self.assertEqual(values[1], "TCP")


class TestPacketSniffer(unittest.TestCase):
    """Test packet sniffer engine."""
    
    def setUp(self):
        self.packet_queue = queue.Queue()
        self.sniffer = PacketSniffer(self.packet_queue)
        
    def test_initial_state(self):
        self.assertFalse(self.sniffer.is_running)
        self.assertEqual(self.sniffer.packet_count, 0)
        
    def test_get_stats(self):
        stats = self.sniffer.get_stats()
        self.assertIn("total_packets", stats)
        self.assertIn("tcp_count", stats)
        self.assertIn("udp_count", stats)
        self.assertIn("icmp_count", stats)
        
    def test_reset_stats(self):
        self.sniffer.packet_count = 100
        self.sniffer.protocol_counts["TCP"] = 50
        self.sniffer.reset_stats()
        self.assertEqual(self.sniffer.packet_count, 0)
        self.assertEqual(self.sniffer.protocol_counts["TCP"], 0)


if __name__ == "__main__":
    unittest.main()
