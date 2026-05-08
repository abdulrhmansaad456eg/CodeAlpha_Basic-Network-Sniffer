"""
Network Sniffer
A modern packet capture tool for cybersecurity education.

Entry point for the application.
"""

import sys
import os
import platform
import subprocess


def check_windows_environment():
    """Check if running on Windows and configure scapy."""
    if platform.system() != "Windows":
        print("Warning: This application is optimized for Windows 11.")
        return True
        
    try:
        from scapy.arch.windows import get_windows_if_list
        return True
    except ImportError:
        pass
        
    return True


def check_admin_privileges():
    """Check if running with administrator privileges."""
    if platform.system() == "Windows":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    return True


def main():
    """Main entry point."""
    print("=" * 60)
    print("Network Sniffer")
    print("Packet Capture & Analysis Tool")
    print("=" * 60)
    
    check_windows_environment()
    
    is_admin = check_admin_privileges()
    if not is_admin:
        print("\n[WARNING] Not running as administrator.")
        print("Packet capture may fail without elevated privileges.")
        print("Please run this application as administrator for full functionality.\n")
    
    try:
        from ui.main_window import MainWindow
        
        app = MainWindow()
        app.mainloop()
        
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()
