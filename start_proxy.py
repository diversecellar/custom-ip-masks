#!/usr/bin/env python3
"""
Quick Start Script for Custom IP Masks Proxy Server
==================================================

This script provides a simple way to start the proxy server quickly
with sensible defaults.

Usage:
    python start_proxy.py              # Start with defaults
    python start_proxy.py --port 9000  # Start on port 9000
    python start_proxy.py --help       # Show all options
"""

import sys
import argparse
from proxy_server import ProxyServer

def main():
    parser = argparse.ArgumentParser(
        description='Quick start for Custom IP Masks Proxy Server',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host to bind (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888,
                       help='Port to bind (default: 8888)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--open-access', action='store_true',
                       help='Allow access from all IPs (sets host to 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Configuration
    config = {
        'host': '0.0.0.0' if args.open_access else args.host,
        'port': args.port,
        'debug': args.debug,
        'timeout': 30,
        'logging': {
            'level': 'DEBUG' if args.debug else 'INFO',
            'file': 'proxy.log',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'rate_limit': {
            'enabled': True,
            'requests_per_minute': 120
        }
    }
    
    print("🚀 Starting Custom IP Masks Proxy Server...")
    print(f"📍 Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"🐛 Debug: {config['debug']}")
    print()
    print("📋 Configuration Instructions:")
    print("   Configure your browser proxy settings:")
    print(f"   • HTTP Proxy:  {config['host']}:{config['port']}")
    print(f"   • HTTPS Proxy: {config['host']}:{config['port']}")
    print()
    print("🧪 Test your setup:")
    print("   Visit: http://httpbin.org/ip")
    print("   Your IP should be different when using the proxy")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        proxy = ProxyServer(config)
        proxy.run()
    except KeyboardInterrupt:
        print("\n👋 Proxy server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()