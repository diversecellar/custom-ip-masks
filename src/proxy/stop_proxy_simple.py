#!/usr/bin/env python3
"""
Simple Stop Script for Custom IP Masks Proxy Server
==================================================

A lightweight version that stops proxy servers without external dependencies.
Uses only built-in Python modules.

Usage:
    python stop_proxy_simple.py              # Stop default proxy on port 8888
    python stop_proxy_simple.py --port 9000  # Stop proxy on specific port
    python stop_proxy_simple.py --help       # Show help
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import platform
from typing import List, Optional

class SimpleProxyKiller:
    """
    Simple proxy killer using built-in tools
    """
    
    def __init__(self):
        self.is_windows = platform.system().lower() == 'windows'
    
    def check_port_in_use(self, port: int) -> bool:
        """
        Check if a port is in use using netstat
        
        Args:
            port (int): Port to check
            
        Returns:
            bool: True if port is in use
        """
        try:
            if self.is_windows:
                cmd = f'netstat -an | findstr ":{port}"'
            else:
                cmd = f'netstat -an | grep ":{port}"'
            
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            return result.returncode == 0 and str(port) in result.stdout
        
        except Exception:
            return False
    
    def find_process_by_port(self, port: int) -> Optional[str]:
        """
        Find process ID using a specific port
        
        Args:
            port (int): Port number
            
        Returns:
            Optional[str]: Process ID if found
        """
        try:
            if self.is_windows:
                # Use netstat to find process using port
                cmd = f'netstat -ano | findstr ":{port}"'
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                return parts[-1]  # PID is the last column
            else:
                # Use lsof on Unix-like systems
                cmd = f'lsof -ti:{port}'
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return result.stdout.strip()
        
        except Exception:
            pass
        
        return None
    
    def kill_process(self, pid: str, force: bool = False) -> bool:
        """
        Kill a process by PID
        
        Args:
            pid (str): Process ID
            force (bool): Force kill
            
        Returns:
            bool: True if successful
        """
        try:
            if self.is_windows:
                if force:
                    cmd = f'taskkill /F /PID {pid}'
                else:
                    cmd = f'taskkill /PID {pid}'
            else:
                if force:
                    cmd = f'kill -9 {pid}'
                else:
                    cmd = f'kill {pid}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return result.returncode == 0
        
        except Exception:
            return False
    
    def stop_proxy_by_port(self, port: int, force: bool = False) -> bool:
        """
        Stop proxy server on specific port
        
        Args:
            port (int): Port number
            force (bool): Force kill
            
        Returns:
            bool: True if stopped successfully
        """
        print(f"🔍 Checking for proxy server on port {port}...")
        
        if not self.check_port_in_use(port):
            print(f"  ℹ No process found using port {port}")
            return False
        
        print(f"  📡 Found process using port {port}")
        
        # Find the process ID
        pid = self.find_process_by_port(port)
        if not pid:
            print(f"  ❌ Could not find process ID for port {port}")
            return False
        
        print(f"  🎯 Found process ID: {pid}")
        
        # Try to kill the process
        if self.kill_process(pid, force):
            print(f"  ✓ Process {pid} {'force killed' if force else 'terminated'}")
            
            # Wait a moment and check if port is free
            time.sleep(2)
            if not self.check_port_in_use(port):
                print(f"  ✅ Port {port} is now free")
                return True
            else:
                print(f"  ⚠ Port {port} may still be in use")
                return False
        else:
            print(f"  ❌ Failed to stop process {pid}")
            return False
    
    def list_proxy_processes(self) -> None:
        """
        List processes that might be proxy servers
        """
        print("🔍 Looking for proxy-related processes...")
        
        try:
            if self.is_windows:
                cmd = 'tasklist | findstr python'
            else:
                cmd = 'ps aux | grep python'
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                print("Found Python processes:")
                print(result.stdout)
            else:
                print("No Python processes found")
        
        except Exception as e:
            print(f"Error listing processes: {e}")

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(
        description='Simple stop utility for Custom IP Masks Proxy Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stop_proxy_simple.py                # Stop proxy on port 8888
  python stop_proxy_simple.py --port 9000   # Stop proxy on port 9000
  python stop_proxy_simple.py --force       # Force kill process
  python stop_proxy_simple.py --list        # List Python processes
        """
    )
    
    parser.add_argument('--port', type=int, default=8888,
                       help='Port number of proxy to stop (default: 8888)')
    parser.add_argument('--force', action='store_true',
                       help='Force kill the process')
    parser.add_argument('--list', action='store_true',
                       help='List proxy-related processes')
    
    args = parser.parse_args()
    
    print("🛑 Custom IP Masks Proxy Server - Simple Stop Utility")
    print("=" * 55)
    
    killer = SimpleProxyKiller()
    
    try:
        if args.list:
            killer.list_proxy_processes()
            return
        
        if killer.stop_proxy_by_port(args.port, args.force):
            print(f"\n✅ Successfully stopped proxy on port {args.port}")
        else:
            print(f"\n❌ Failed to stop proxy on port {args.port}")
            print("Try using --force flag or check the process manually")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()