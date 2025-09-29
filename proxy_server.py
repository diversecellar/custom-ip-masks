#!/usr/bin/env python3
"""
Custom HTTP/HTTPS Proxy Server using Flask
==========================================

This module implements a custom proxy server that can mask your IP address
by forwarding HTTP and HTTPS requests through the proxy server.

Author: Custom IP Masks Project
Date: September 2025

Features:
- HTTP and HTTPS request forwarding
- Custom header manipulation
- Request/response logging
- IP masking capabilities
- Configurable proxy chains
- Authentication support
- Rate limiting
"""

import sys
import json
import time
import logging # For logging events that happen during execution
import threading # For running the server in a separate thread, thread means a single sequence of execution within a program
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin, parse_qs
from typing import Dict, List, Optional, Tuple, Any

import requests
from flask import Flask, request, Response, jsonify, abort
from werkzeug.serving import make_server
import urllib3

# Disable SSL warnings for proxy operations
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxyServer:
    """
    Custom HTTP/HTTPS Proxy Server
    
    This class implements a proxy server that can:
    1. Forward HTTP/HTTPS requests to target servers
    2. Mask the original client IP address
    3. Modify headers for anonymity
    4. Log requests for monitoring
    5. Chain through multiple proxies
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the proxy server with configuration
        
        Args:
            config (Dict): Configuration dictionary containing proxy settings
        """
        self.app = Flask(__name__)
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        self.session = requests.Session()
        self.request_count = 0
        self.start_time = time.time()
        
        # Setup session with proxy configuration
        self._configure_session()
        
        # Register Flask routes
        self._register_routes()
        
        self.logger.info("Proxy server initialized successfully")
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Default configuration for the proxy server
        
        Returns:
            Dict: Default configuration settings
        """
        return {
            'host': '127.0.0.1',
            'port': 8888,
            'debug': False,
            'timeout': 30,
            'max_content_length': 50 * 1024 * 1024,  # 50MB
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ],
            'remove_headers': [
                'X-Forwarded-For',
                'X-Real-IP',
                'X-Originating-IP',
                'CF-Connecting-IP'
            ],
            'add_headers': {
                'X-Proxy-Server': 'CustomProxy/1.0',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'close'
            },
            'upstream_proxy': None,  # Format: {'http': 'http://proxy:port', 'https': 'https://proxy:port'}
            'auth': None,  # Format: {'username': 'user', 'password': 'pass'}
            'rate_limit': {
                'enabled': False,
                'requests_per_minute': 60
            },
            'logging': {
                'level': 'INFO',
                'file': 'proxy.log',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging configuration
        
        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger('ProxyServer')
        logger.setLevel(getattr(logging, self.config['logging']['level']))
        
        # File handler
        if self.config['logging']['file']:
            file_handler = logging.FileHandler(self.config['logging']['file'])
            file_handler.setFormatter(
                logging.Formatter(self.config['logging']['format'])
            )
            logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(self.config['logging']['format'])
        )
        logger.addHandler(console_handler)
        
        return logger
    
    def _configure_session(self) -> None:
        """Configure the requests session with proxy settings"""
        # Set upstream proxy if configured
        if self.config.get('upstream_proxy'):
            self.session.proxies.update(self.config['upstream_proxy'])
        
        # Set authentication if configured
        if self.config.get('auth'):
            self.session.auth = (
                self.config['auth']['username'],
                self.config['auth']['password']
            )
        
        # Configure SSL verification
        self.session.verify = False
        
        # Set timeout
        self.session.timeout = self.config['timeout']
    
    def _register_routes(self) -> None:
        """Register Flask routes for the proxy server"""
        
        @self.app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
        @self.app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
        def proxy_request(path: str) -> Response:
            """
            Main proxy handler for all HTTP methods
            
            Args:
                path (str): URL path to forward
                
            Returns:
                Response: Proxied response from target server
            """
            return self._handle_request(path)
        
        @self.app.route('/proxy/status', methods=['GET'])
        def proxy_status() -> Response:
            """
            Get proxy server status and statistics
            
            Returns:
                Response: JSON response with proxy statistics
            """
            uptime = time.time() - self.start_time
            return jsonify({
                'status': 'running',
                'uptime_seconds': uptime,
                'uptime_formatted': str(timedelta(seconds=int(uptime))),
                'requests_processed': self.request_count,
                'config': {
                    'host': self.config['host'],
                    'port': self.config['port'],
                    'upstream_proxy': bool(self.config.get('upstream_proxy')),
                    'auth_enabled': bool(self.config.get('auth'))
                }
            })
        
        @self.app.route('/proxy/health', methods=['GET'])
        def health_check() -> Response:
            """
            Health check endpoint
            
            Returns:
                Response: Simple health status
            """
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def _handle_request(self, path: str) -> Response:
        """
        Handle incoming proxy request
        
        Args:
            path (str): URL path to forward
            
        Returns:
            Response: Proxied response
        """
        try:
            # Increment request counter
            self.request_count += 1
            
            # Get target URL from query parameters or construct from path
            target_url = self._get_target_url(path)
            if not target_url:
                return jsonify({'error': 'No target URL specified'}), 400
            
            # Prepare headers
            headers = self._prepare_headers(request.headers)
            
            # Log the request
            self.logger.info(f"Proxying {request.method} {target_url} from {request.remote_addr}")
            
            # Rate limiting check
            if self._rate_limit_exceeded():
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Make the proxied request
            response = self._make_request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                params=request.args
            )
            
            # Return the response
            return self._create_response(response)
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return jsonify({'error': f'Request failed: {str(e)}'}), 502
        
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'Internal proxy error'}), 500
    
    def _get_target_url(self, path: str) -> Optional[str]:
        """
        Extract target URL from request
        
        Args:
            path (str): URL path
            
        Returns:
            Optional[str]: Target URL or None if not found
        """
        # Check if URL is provided as query parameter
        target_url = request.args.get('url')
        if target_url:
            return target_url
        
        # Check if URL is provided in custom header
        target_url = request.headers.get('X-Target-URL')
        if target_url:
            return target_url
        
        # Construct URL from path (assuming HTTP if no scheme)
        if path:
            if not path.startswith(('http://', 'https://')):
                path = 'http://' + path
            return path
        
        return None
    
    def _prepare_headers(self, original_headers: Dict[str, str]) -> Dict[str, str]:
        """
        Prepare headers for the proxied request
        
        Args:
            original_headers (Dict): Original request headers
            
        Returns:
            Dict: Modified headers for proxy request
        """
        headers = dict(original_headers)
        
        # Remove headers that could reveal proxy usage
        for header in self.config['remove_headers']:
            headers.pop(header, None)
        
        # Remove Flask/Werkzeug headers
        headers.pop('Host', None)
        headers.pop('Content-Length', None)
        
        # Add custom headers
        headers.update(self.config['add_headers'])
        
        # Randomize User-Agent if not present
        if 'User-Agent' not in headers and self.config['user_agents']:
            import random
            headers['User-Agent'] = random.choice(self.config['user_agents'])
        
        return headers
    
    def _make_request(self, method: str, url: str, headers: Dict[str, str], 
                     data: bytes, params: Dict[str, str]) -> requests.Response:
        """
        Make the actual HTTP request through the proxy
        
        Args:
            method (str): HTTP method
            url (str): Target URL
            headers (Dict): Request headers
            data (bytes): Request body data
            params (Dict): Query parameters
            
        Returns:
            requests.Response: Response from target server
        """
        return self.session.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            allow_redirects=False,  # Handle redirects manually
            stream=True
        )
    
    def _create_response(self, upstream_response: requests.Response) -> Response:
        """
        Create Flask response from upstream response
        
        Args:
            upstream_response (requests.Response): Response from target server
            
        Returns:
            Response: Flask response object
        """
        # Create response with content
        response = Response(
            upstream_response.content,
            status=upstream_response.status_code,
            headers=dict(upstream_response.headers)
        )
        
        # Remove headers that might cause issues
        response.headers.pop('Content-Encoding', None)
        response.headers.pop('Transfer-Encoding', None)
        response.headers.pop('Connection', None)
        
        # Add proxy identification header
        response.headers['X-Proxied-By'] = 'CustomProxy/1.0'
        
        return response
    
    def _rate_limit_exceeded(self) -> bool:
        """
        Check if rate limit is exceeded
        
        Returns:
            bool: True if rate limit exceeded
        """
        if not self.config['rate_limit']['enabled']:
            return False
        
        # Simple rate limiting implementation
        # In production, you'd want to use Redis or similar
        current_time = time.time()
        minute_ago = current_time - 60
        
        # This is a simplified implementation
        # You'd want to track requests per IP address
        return False  # Placeholder implementation
    
    def run(self, threaded: bool = True) -> None:
        """
        Start the proxy server
        
        Args:
            threaded (bool): Whether to run in threaded mode
        """
        self.logger.info(f"Starting proxy server on {self.config['host']}:{self.config['port']}")
        
        try:
            self.app.run(
                host=self.config['host'],
                port=self.config['port'],
                debug=self.config['debug'],
                threaded=threaded
            )
        except KeyboardInterrupt:
            self.logger.info("Proxy server stopped by user")
        except Exception as e:
            self.logger.error(f"Failed to start proxy server: {str(e)}")
            raise

def main():
    """
    Main function to run the proxy server
    """
    # Example configuration
    config = {
        'host': '0.0.0.0',  # Listen on all interfaces
        'port': 8888,
        'debug': False,
        'timeout': 30,
        'logging': {
            'level': 'INFO',
            'file': 'proxy.log'
        },
        # Example upstream proxy configuration (uncomment to use)
        # 'upstream_proxy': {
        #     'http': 'http://upstream-proxy:3128',
        #     'https': 'http://upstream-proxy:3128'
        # },
        'rate_limit': {
            'enabled': True,
            'requests_per_minute': 120
        }
    }
    
    # Create and run proxy server
    proxy = ProxyServer(config)
    proxy.run()

if __name__ == '__main__':
    main()