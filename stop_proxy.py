#!/usr/bin/env python3
"""
Stop Script for Custom IP Masks Proxy Server
============================================

This script helps you stop running proxy server instances gracefully.
It can find and terminate proxy servers by port, process name, or PID.

Usage:
    python stop_proxy.py              # Stop default proxy on port 8888
    python stop_proxy.py --port 9000  # Stop proxy on specific port
    python stop_proxy.py --all        # Stop all proxy instances
    python stop_proxy.py --force      # Force kill proxy processes
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import psutil
import requests
from typing import List, Optional

class ProxyKiller:
    """
    Utility class to find and stop proxy server processes
    """
    
    def __init__(self):
        self.default_port = 8888
        self.proxy_process_names = [
            'python',
            'start_proxy.py',
            'proxy_server.py',
            'launcher.py'
        ]
    
    def find_proxy_processes(self, port: Optional[int] = None) -> List[psutil.Process]:
        """
        Find running proxy server processes
        
        Args:
            port (Optional[int]): Specific port to check
            
        Returns:
            List[psutil.Process]: List of proxy processes found
        """
        processes = []
        target_port = port or self.default_port
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
                try:
                    # Check by command line arguments
                    cmdline = proc.info['cmdline']
                    if cmdline and any('proxy' in str(arg).lower() for arg in cmdline):
                        # Check if it's using the target port
                        if self._process_uses_port(proc, target_port):
                            processes.append(proc)
                        # Also include if command line mentions the port
                        elif any(str(target_port) in str(arg) for arg in cmdline):
                            processes.append(proc)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        
        except Exception as e:
            print(f"Warning: Error scanning processes: {e}")
        
        return processes
    
    def _process_uses_port(self, process: psutil.Process, port: int) -> bool:
        """
        Check if a process is using a specific port
        
        Args:
            process (psutil.Process): Process to check
            port (int): Port number to check
            
        Returns:
            bool: True if process is using the port
        """
        try:
            connections = process.connections(kind='inet')
            for conn in connections:
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return False
    
    def find_processes_by_port(self, port: int) -> List[psutil.Process]:
        """
        Find processes listening on a specific port
        
        Args:
            port (int): Port number to check
            
        Returns:
            List[psutil.Process]: Processes using the port
        """
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if self._process_uses_port(proc, port):
                        processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            print(f"Warning: Error finding processes by port: {e}")
        
        return processes
    
    def check_proxy_status(self, port: int) -> bool:
        """
        Check if proxy server is responding on the given port
        
        Args:
            port (int): Port to check
            
        Returns:
            bool: True if proxy is responding
        """
        try:
            response = requests.get(
                f"http://127.0.0.1:{port}/proxy/health",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
    
    def stop_proxy_gracefully(self, port: int) -> bool:
        """
        Try to stop proxy gracefully by sending a shutdown request
        
        Args:
            port (int): Port of the proxy to stop
            
        Returns:
            bool: True if successfully stopped
        """
        try:
            # Try to send a graceful shutdown signal (if implemented)
            response = requests.post(
                f"http://127.0.0.1:{port}/proxy/shutdown",
                timeout=5
            )
            if response.status_code == 200:
                time.sleep(1)
                return not self.check_proxy_status(port)
        except:
            pass
        
        return False
    
    def stop_processes(self, processes: List[psutil.Process], force: bool = False) -> int:
        """
        Stop a list of processes
        
        Args:
            processes (List[psutil.Process]): Processes to stop
            force (bool): Whether to force kill
            
        Returns:
            int: Number of processes stopped
        """
        stopped_count = 0
        
        for proc in processes:
            try:
                print(f"Stopping process {proc.pid} ({proc.name()})...")
                
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                
                # Wait for process to terminate
                try:
                    proc.wait(timeout=5)
                    stopped_count += 1
                    print(f"  ✓ Process {proc.pid} stopped")
                except psutil.TimeoutExpired:
                    if not force:
                        print(f"  Process {proc.pid} didn't terminate, force killing...")
                        proc.kill()
                        stopped_count += 1
                        print(f"  ✓ Process {proc.pid} force killed")
            
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"  ⚠ Could not stop process {proc.pid}: {e}")
            except Exception as e:
                print(f"  ✗ Error stopping process {proc.pid}: {e}")
        
        return stopped_count
    
    def stop_by_port(self, port: int, force: bool = False) -> bool:
        """
        Stop proxy server running on specific port
        
        Args:
            port (int): Port number
            force (bool): Whether to force kill
            
        Returns:
            bool: True if stopped successfully
        """
        print(f"🔍 Looking for proxy server on port {port}...")
        
        # First check if proxy is responding
        if self.check_proxy_status(port):
            print("  📡 Proxy server is responding")
            
            # Try graceful shutdown first
            if not force and self.stop_proxy_gracefully(port):
                print("  ✓ Proxy stopped gracefully")
                return True
        
        # Find processes using the port
        processes = self.find_processes_by_port(port)
        
        if not processes:
            print(f"  ℹ No processes found listening on port {port}")
            return False
        
        print(f"  🎯 Found {len(processes)} process(es) using port {port}")
        stopped = self.stop_processes(processes, force)
        
        # Verify the port is free
        time.sleep(1)
        if not self.check_proxy_status(port):
            print(f"  ✅ Port {port} is now free")
            return True
        else:
            print(f"  ⚠ Port {port} may still be in use")
            return False
    
    def stop_all_proxies(self, force: bool = False) -> int:
        """
        Stop all proxy server instances
        
        Args:
            force (bool): Whether to force kill
            
        Returns:
            int: Number of processes stopped
        """
        print("🔍 Looking for all proxy server processes...")
        
        processes = self.find_proxy_processes()
        
        if not processes:
            print("  ℹ No proxy processes found")
            return 0
        
        print(f"  🎯 Found {len(processes)} proxy process(es)")
        stopped = self.stop_processes(processes, force)
        
        return stopped

def main():
    """
    Main function with command-line argument parsing
    """
    parser = argparse.ArgumentParser(
        description='Stop Custom IP Masks Proxy Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stop_proxy.py                # Stop default proxy (port 8888)
  python stop_proxy.py --port 9000   # Stop proxy on port 9000
  python stop_proxy.py --all         # Stop all proxy instances
  python stop_proxy.py --force       # Force kill proxy processes
  python stop_proxy.py --status      # Check proxy status only
        """
    )
    
    parser.add_argument('--port', type=int, default=8888,
                       help='Port number of proxy to stop (default: 8888)')
    parser.add_argument('--all', action='store_true',
                       help='Stop all proxy server instances')
    parser.add_argument('--force', action='store_true',
                       help='Force kill processes (use if graceful stop fails)')
    parser.add_argument('--status', action='store_true',
                       help='Check proxy status without stopping')
    parser.add_argument('--list', action='store_true',
                       help='List all proxy processes without stopping')
    
    args = parser.parse_args()
    
    print("🛑 Custom IP Masks Proxy Server - Stop Utility")
    print("=" * 50)
    
    killer = ProxyKiller()
    
    try:
        if args.status:
            # Just check status
            if killer.check_proxy_status(args.port):
                print(f"✅ Proxy server is running on port {args.port}")
                sys.exit(0)
            else:
                print(f"❌ No proxy server responding on port {args.port}")
                sys.exit(1)
        
        elif args.list:
            # List proxy processes
            processes = killer.find_proxy_processes()
            if processes:
                print(f"Found {len(processes)} proxy process(es):")
                for proc in processes:
                    try:
                        print(f"  PID {proc.pid}: {proc.name()} - {' '.join(proc.cmdline())}")
                    except:
                        print(f"  PID {proc.pid}: {proc.name()}")
            else:
                print("No proxy processes found")
            sys.exit(0)
        
        elif args.all:
            # Stop all proxies
            stopped = killer.stop_all_proxies(args.force)
            if stopped > 0:
                print(f"\n✅ Stopped {stopped} proxy process(es)")
            else:
                print("\n❌ No proxy processes were stopped")
        
        else:
            # Stop specific port
            if killer.stop_by_port(args.port, args.force):
                print(f"\n✅ Proxy server on port {args.port} stopped successfully")
            else:
                print(f"\n❌ Failed to stop proxy server on port {args.port}")
                print("Try using --force flag or check if the process is running")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()