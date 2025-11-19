#!/usr/bin/env python3
"""
Example usage of the custom proxy server
========================================

This script demonstrates various ways to use the custom proxy server
for different use cases and configurations.

Author: Custom IP Masks Project
Date: September 2025
"""

import json
import time
import requests
from proxy_server import ProxyServer
from config import ConfigManager, ProxyConfig

def example_basic_proxy():
    """
    Example 1: Basic proxy server with default configuration
    """
    print("=== Example 1: Basic Proxy Server ===")
    
    # Create proxy with default config
    proxy = ProxyServer()
    
    # Run proxy server (this will block, so run in separate terminal)
    print("Starting proxy server on 127.0.0.1:8888")
    print("Configure your browser to use this proxy and test with:")
    print("http://httpbin.org/ip")
    
    # proxy.run()  # Uncomment to run

def example_custom_config():
    """
    Example 2: Proxy server with custom configuration
    """
    print("\n=== Example 2: Custom Configuration ===")
    
    # Custom configuration
    config = {
        'host': '0.0.0.0',  # Listen on all interfaces
        'port': 9000,       # Custom port
        'debug': True,      # Enable debug mode
        'timeout': 60,      # Longer timeout
        'rate_limit': {
            'enabled': True,
            'requests_per_minute': 100
        },
        'add_headers': {
            'X-Custom-Proxy': 'MyProxy/1.0',
            'Accept-Language': 'en-US,en;q=0.9'
        },
        'blocked_domains': [
            'ads.example.com',
            'tracker.net'
        ]
    }
    
    proxy = ProxyServer(config)
    print(f"Custom proxy configured on {config['host']}:{config['port']}")
    
    # proxy.run()  # Uncomment to run

def example_proxy_chain():
    """
    Example 3: Using proxy chains for enhanced anonymity
    """
    print("\n=== Example 3: Proxy Chaining ===")
    
    config = {
        'host': '127.0.0.1',
        'port': 8888,
        'upstream_proxy': {
            'http': 'http://upstream-proxy:3128',
            'https': 'http://upstream-proxy:3128'
        },
        'auth': {
            'username': 'proxy_user',
            'password': 'proxy_pass'
        }
    }
    
    print("This configuration chains your requests through an upstream proxy")
    print("Traffic flow: Browser -> Custom Proxy -> Upstream Proxy -> Target")
    
    # proxy = ProxyServer(config)
    # proxy.run()  # Uncomment to run

def example_programmatic_usage():
    """
    Example 4: Using the proxy programmatically with requests
    """
    print("\n=== Example 4: Programmatic Usage ===")
    
    # First, you need to start the proxy server (in another terminal or thread)
    # python proxy_server.py
    
    # Configure requests to use the proxy
    proxies = {
        'http': 'http://127.0.0.1:8888',
        'https': 'http://127.0.0.1:8888'
    }
    
    try:
        # Test IP masking
        print("Testing IP masking...")
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        print(f"Masked IP: {response.json()}")
        
        # Test user agent
        print("\nTesting User-Agent rotation...")
        response = requests.get('http://httpbin.org/user-agent', proxies=proxies, timeout=10)
        print(f"User-Agent: {response.json()}")
        
        # Test headers
        print("\nTesting header manipulation...")
        response = requests.get('http://httpbin.org/headers', proxies=proxies, timeout=10)
        headers = response.json()['headers']
        print("Headers received by target server:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
    
    except requests.exceptions.ConnectionError:
        print("Error: Proxy server not running. Start it with: python proxy_server.py")
    except Exception as e:
        print(f"Error: {e}")

def example_configuration_file():
    """
    Example 5: Using configuration files
    """
    print("\n=== Example 5: Configuration File Usage ===")
    
    # Create sample configuration file
    sample_config = {
        "host": "0.0.0.0",
        "port": 8888,
        "debug": false,
        "timeout": 30,
        "log_level": "INFO",
        "log_file": "proxy.log",
        "rate_limit_enabled": true,
        "requests_per_minute": 120,
        "verify_ssl": false,
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
        "blocked_domains": [
            "ads.doubleclick.net",
            "googletagmanager.com"
        ]
    }
    
    # Save configuration to file
    with open('example_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration saved to 'example_config.json'")
    print("Use it with: python proxy_server.py --config example_config.json")
    
    # Load and use configuration
    config_manager = ConfigManager()
    try:
        config = config_manager.load_from_file('example_config.json')
        print("Configuration loaded successfully!")
        
        # Validate configuration
        errors = config_manager.validate_config()
        if errors:
            print("Configuration errors found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Configuration is valid!")
    
    except Exception as e:
        print(f"Error loading configuration: {e}")

def example_monitoring():
    """
    Example 6: Monitoring proxy server status
    """
    print("\n=== Example 6: Monitoring ===")
    
    try:
        # Check proxy status
        response = requests.get('http://127.0.0.1:8888/proxy/status', timeout=5)
        status = response.json()
        
        print("Proxy Server Status:")
        print(f"  Status: {status['status']}")
        print(f"  Uptime: {status['uptime_formatted']}")
        print(f"  Requests Processed: {status['requests_processed']}")
        print(f"  Configuration: {status['config']}")
        
        # Health check
        response = requests.get('http://127.0.0.1:8888/proxy/health', timeout=5)
        health = response.json()
        print(f"\nHealth Check: {health['status']} at {health['timestamp']}")
    
    except requests.exceptions.ConnectionError:
        print("Proxy server is not running")
    except Exception as e:
        print(f"Error checking status: {e}")

def main():
    """
    Run all examples (non-blocking ones)
    """
    print("Custom IP Masks - Proxy Server Examples")
    print("=" * 50)
    
    example_basic_proxy()
    example_custom_config()
    example_proxy_chain()
    example_configuration_file()
    
    print("\n" + "=" * 50)
    print("Testing examples (requires running proxy server):")
    print("1. Start proxy: python proxy_server.py")
    print("2. Run tests: python examples.py --test")
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        example_programmatic_usage()
        example_monitoring()

if __name__ == '__main__':
    main()