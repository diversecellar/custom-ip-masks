#!/usr/bin/env python3
"""
Simple launcher script for the custom proxy server
==================================================

This script provides an easy way to start the proxy server with
different configurations and command-line options.

Author: Custom IP Masks Project
Date: September 2025
"""

import os
import sys
import json
import argparse
from pathlib import Path

def main():
    """
    Main launcher function with command-line argument parsing
    """
    parser = argparse.ArgumentParser(
        description='Custom IP Masks - Proxy Server Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                          # Start with default settings
  python launcher.py --port 9000             # Start on port 9000
  python launcher.py --config config.json    # Use configuration file
  python launcher.py --host 0.0.0.0 --debug # Debug mode, listen on all interfaces
        """
    )
    
    # Server configuration options
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host to bind the proxy server (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888,
                       help='Port to bind the proxy server (default: 8888)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file (JSON or YAML)')
    
    # Proxy options
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str, default='proxy.log',
                       help='Log file path (default: proxy.log)')
    
    # Rate limiting
    parser.add_argument('--rate-limit', action='store_true',
                       help='Enable rate limiting')
    parser.add_argument('--max-requests', type=int, default=60,
                       help='Maximum requests per minute (default: 60)')
    
    # Security options
    parser.add_argument('--no-ssl-verify', action='store_true',
                       help='Disable SSL certificate verification')
    parser.add_argument('--block-domains', nargs='+',
                       help='List of domains to block')
    
    # Upstream proxy
    parser.add_argument('--upstream-proxy', type=str,
                       help='Upstream proxy URL (e.g., http://proxy:3128)')
    parser.add_argument('--proxy-auth', type=str,
                       help='Proxy authentication in format username:password')
    
    # Utility options
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if all dependencies are installed')
    parser.add_argument('--generate-config', type=str,
                       help='Generate sample configuration file')
    parser.add_argument('--validate-config', type=str,
                       help='Validate configuration file')
    
    args = parser.parse_args()
    
    # Handle utility commands first
    if args.check_deps:
        check_dependencies()
        return
    
    if args.generate_config:
        generate_config_file(args.generate_config)
        return
    
    if args.validate_config:
        validate_config_file(args.validate_config)
        return
    
    # Build configuration
    config = build_config(args)
    
    # Start the proxy server
    start_proxy_server(config)

def check_dependencies():
    """
    Check if all required dependencies are installed
    """
    print("Checking dependencies...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('requests', 'requests'),
        ('urllib3', 'urllib3'),
        ('yaml', 'PyYAML')
    ]
    
    missing_packages = []
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✓ {pip_name}")
        except ImportError:
            print(f"✗ {pip_name} (missing)")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        sys.exit(1)
    else:
        print("\nAll dependencies are installed!")

def generate_config_file(filename):
    """
    Generate a sample configuration file
    """
    sample_config = {
        "host": "127.0.0.1",
        "port": 8888,
        "debug": False,
        "timeout": 30,
        "log_level": "INFO",
        "log_file": "proxy.log",
        "rate_limit_enabled": True,
        "requests_per_minute": 60,
        "verify_ssl": False,
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        ],
        "remove_headers": [
            "X-Forwarded-For",
            "X-Real-IP",
            "Via"
        ],
        "add_headers": {
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close"
        },
        "blocked_domains": [],
        "upstream_proxy": None,
        "auth": None
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"Sample configuration generated: {filename}")
        print(f"Edit the file and use with: python launcher.py --config {filename}")
    except Exception as e:
        print(f"Error generating config file: {e}")
        sys.exit(1)

def validate_config_file(filename):
    """
    Validate a configuration file
    """
    if not os.path.exists(filename):
        print(f"Configuration file not found: {filename}")
        sys.exit(1)
    
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        
        # Basic validation
        required_fields = ['host', 'port']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            print(f"Missing required fields: {', '.join(missing_fields)}")
            sys.exit(1)
        
        # Port validation
        if not (1 <= config['port'] <= 65535):
            print(f"Invalid port number: {config['port']}")
            sys.exit(1)
        
        print(f"Configuration file '{filename}' is valid!")
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error validating configuration: {e}")
        sys.exit(1)

def build_config(args):
    """
    Build configuration from command-line arguments
    """
    config = {}
    
    # Load from config file if specified
    if args.config:
        if not os.path.exists(args.config):
            print(f"Configuration file not found: {args.config}")
            sys.exit(1)
        
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            sys.exit(1)
    
    # Override with command-line arguments
    config.update({
        'host': args.host,
        'port': args.port,
        'debug': args.debug,
        'timeout': args.timeout,
        'logging': {
            'level': args.log_level,
            'file': args.log_file
        }
    })
    
    # Rate limiting
    if args.rate_limit:
        config['rate_limit'] = {
            'enabled': True,
            'requests_per_minute': args.max_requests
        }
    
    # SSL verification
    if args.no_ssl_verify:
        config['verify_ssl'] = False
    
    # Blocked domains
    if args.block_domains:
        config['blocked_domains'] = args.block_domains
    
    # Upstream proxy
    if args.upstream_proxy:
        config['upstream_proxy'] = {
            'http': args.upstream_proxy,
            'https': args.upstream_proxy
        }
    
    # Proxy authentication
    if args.proxy_auth:
        try:
            username, password = args.proxy_auth.split(':', 1)
            config['auth'] = {
                'username': username,
                'password': password
            }
        except ValueError:
            print("Invalid proxy auth format. Use: username:password")
            sys.exit(1)
    
    return config

def start_proxy_server(config):
    """
    Start the proxy server with the given configuration
    """
    print("Starting Custom IP Masks Proxy Server...")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"Debug: {config.get('debug', False)}")
    print(f"Log Level: {config.get('logging', {}).get('level', 'INFO')}")
    
    if config.get('upstream_proxy'):
        print(f"Upstream Proxy: {config['upstream_proxy']}")
    
    if config.get('rate_limit', {}).get('enabled'):
        rpm = config['rate_limit'].get('requests_per_minute', 60)
        print(f"Rate Limiting: {rpm} requests/minute")
    
    print("-" * 50)
    print("Configure your browser to use this proxy:")
    print(f"  HTTP Proxy: {config['host']}:{config['port']}")
    print(f"  HTTPS Proxy: {config['host']}:{config['port']}")
    print("-" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Import and start the proxy server
        from proxy_server import ProxyServer
        proxy = ProxyServer(config)
        proxy.run()
    
    except ImportError as e:
        print(f"Error importing proxy server: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nProxy server stopped by user")
    
    except Exception as e:
        print(f"Error starting proxy server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()