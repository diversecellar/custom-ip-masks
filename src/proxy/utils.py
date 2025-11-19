"""
Proxy Utilities and Helper Functions
===================================

This module provides utility functions for the custom proxy server including
header manipulation, IP masking, logging helpers, and security functions.

Author: Custom IP Masks Project
Date: September 2025
"""

import re
import time
import random
import hashlib
import ipaddress
from typing import Dict, List, Optional, Tuple, Any, Union
from urllib.parse import urlparse, parse_qs
from collections import defaultdict, deque
from datetime import datetime, timedelta

class HeaderUtils:
    """
    Utility class for HTTP header manipulation and anonymization
    """
    
    # Headers that commonly reveal proxy usage or client information
    PRIVACY_HEADERS = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Originating-IP',
        'CF-Connecting-IP',
        'X-Forwarded-Proto',
        'X-Forwarded-Host',
        'X-Forwarded-Port',
        'Via',
        'Forwarded',
        'X-Client-IP',
        'X-Cluster-Client-IP',
        'X-Remote-Addr',
        'X-Remote-IP'
    ]
    
    # Common browser User-Agent strings for rotation
    USER_AGENTS = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        # Firefox macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
        # Safari macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    ]
    
    @staticmethod
    def sanitize_headers(headers: Dict[str, str], remove_privacy: bool = True) -> Dict[str, str]:
        """
        Sanitize headers to remove privacy-revealing information
        
        Args:
            headers (Dict[str, str]): Original headers
            remove_privacy (bool): Whether to remove privacy headers
            
        Returns:
            Dict[str, str]: Sanitized headers
        """
        clean_headers = dict(headers)
        
        if remove_privacy:
            for header in HeaderUtils.PRIVACY_HEADERS:
                clean_headers.pop(header, None)
        
        # Remove Flask/Werkzeug specific headers
        werkzeug_headers = ['Host', 'Content-Length']
        for header in werkzeug_headers:
            clean_headers.pop(header, None)
        
        return clean_headers
    
    @staticmethod
    def add_anonymization_headers(headers: Dict[str, str]) -> Dict[str, str]:
        """
        Add headers to improve anonymization
        
        Args:
            headers (Dict[str, str]): Existing headers
            
        Returns:
            Dict[str, str]: Headers with anonymization additions
        """
        anon_headers = dict(headers)
        
        # Add common browser headers
        anon_headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        })
        
        return anon_headers
    
    @staticmethod
    def randomize_user_agent(headers: Dict[str, str]) -> Dict[str, str]:
        """
        Randomize User-Agent header
        
        Args:
            headers (Dict[str, str]): Existing headers
            
        Returns:
            Dict[str, str]: Headers with randomized User-Agent
        """
        new_headers = dict(headers)
        new_headers['User-Agent'] = random.choice(HeaderUtils.USER_AGENTS)
        return new_headers

class IPUtils:
    """
    Utility class for IP address manipulation and validation
    """
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """
        Check if an IP address is private
        
        Args:
            ip (str): IP address to check
            
        Returns:
            bool: True if IP is private
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        Validate IP address format
        
        Args:
            ip (str): IP address to validate
            
        Returns:
            bool: True if valid IP address
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def extract_ip_from_header(header_value: str) -> Optional[str]:
        """
        Extract the first valid IP from a header value
        
        Args:
            header_value (str): Header value that may contain IPs
            
        Returns:
            Optional[str]: First valid IP found or None
        """
        # Handle comma-separated IPs (common in X-Forwarded-For)
        ips = [ip.strip() for ip in header_value.split(',')]
        
        for ip in ips:
            if IPUtils.is_valid_ip(ip):
                return ip
        
        return None
    
    @staticmethod
    def mask_ip(ip: str, mask_level: int = 2) -> str:
        """
        Mask parts of an IP address for logging
        
        Args:
            ip (str): IP address to mask
            mask_level (int): Number of octets to mask (1-3)
            
        Returns:
            str: Masked IP address
        """
        if not IPUtils.is_valid_ip(ip):
            return "invalid.ip"
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            if ip_obj.version == 4:
                octets = str(ip_obj).split('.')
                for i in range(min(mask_level, 3)):
                    octets[-(i+1)] = 'xxx'
                return '.'.join(octets)
            else:
                # IPv6 masking
                parts = str(ip_obj).split(':')
                for i in range(min(mask_level * 2, len(parts) - 1)):
                    parts[-(i+1)] = 'xxxx'
                return ':'.join(parts)
        
        except Exception:
            return "masked.ip"

class RateLimiter:
    """
    Simple rate limiting utility using sliding window
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter
        
        Args:
            max_requests (int): Maximum requests allowed
            window_seconds (int): Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier
        
        Args:
            identifier (str): Unique identifier (e.g., IP address)
            
        Returns:
            bool: True if request is allowed
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests outside the window
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        
        return False
    
    def get_reset_time(self, identifier: str) -> float:
        """
        Get time until rate limit resets for identifier
        
        Args:
            identifier (str): Unique identifier
            
        Returns:
            float: Seconds until reset
        """
        if not self.requests[identifier]:
            return 0.0
        
        oldest_request = self.requests[identifier][0]
        reset_time = oldest_request + self.window_seconds
        return max(0.0, reset_time - time.time())

class URLUtils:
    """
    Utility class for URL manipulation and validation
    """
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid URL
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL for consistent processing
        
        Args:
            url (str): URL to normalize
            
        Returns:
            str: Normalized URL
        """
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Parse and rebuild URL to normalize
        parsed = urlparse(url)
        
        # Normalize domain to lowercase
        netloc = parsed.netloc.lower()
        
        # Remove default ports
        if netloc.endswith(':80') and parsed.scheme == 'http':
            netloc = netloc[:-3]
        elif netloc.endswith(':443') and parsed.scheme == 'https':
            netloc = netloc[:-4]
        
        # Rebuild URL
        return f"{parsed.scheme}://{netloc}{parsed.path or '/'}"
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """
        Extract domain from URL
        
        Args:
            url (str): URL to extract domain from
            
        Returns:
            Optional[str]: Domain name or None if invalid
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None
    
    @staticmethod
    def is_blocked_domain(url: str, blocked_domains: List[str]) -> bool:
        """
        Check if URL domain is in blocked list
        
        Args:
            url (str): URL to check
            blocked_domains (List[str]): List of blocked domains
            
        Returns:
            bool: True if domain is blocked
        """
        domain = URLUtils.extract_domain(url)
        if not domain:
            return False
        
        for blocked in blocked_domains:
            if domain == blocked or domain.endswith('.' + blocked):
                return True
        
        return False

class SecurityUtils:
    """
    Security utility functions for the proxy server
    """
    
    @staticmethod
    def generate_request_id() -> str:
        """
        Generate unique request ID for logging and tracking
        
        Returns:
            str: Unique request ID
        """
        timestamp = int(time.time() * 1000000)  # microseconds
        random_part = random.randint(1000, 9999)
        return f"{timestamp}-{random_part}"
    
    @staticmethod
    def hash_ip(ip: str, salt: str = "proxy_salt") -> str:
        """
        Hash IP address for privacy-preserving logging
        
        Args:
            ip (str): IP address to hash
            salt (str): Salt for hashing
            
        Returns:
            str: Hashed IP address
        """
        return hashlib.sha256((ip + salt).encode()).hexdigest()[:16]
    
    @staticmethod
    def validate_request_size(content_length: Optional[int], max_size: int) -> bool:
        """
        Validate request content length
        
        Args:
            content_length (Optional[int]): Content length from headers
            max_size (int): Maximum allowed size
            
        Returns:
            bool: True if size is acceptable
        """
        if content_length is None:
            return True  # No content-length header
        
        return content_length <= max_size
    
    @staticmethod
    def sanitize_log_data(data: str) -> str:
        """
        Sanitize data for safe logging (remove sensitive information)
        
        Args:
            data (str): Data to sanitize
            
        Returns:
            str: Sanitized data
        """
        # Remove potential passwords, tokens, etc.
        sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?[^"\'\s&]+',
            r'token["\']?\s*[:=]\s*["\']?[^"\'\s&]+',
            r'key["\']?\s*[:=]\s*["\']?[^"\'\s&]+',
            r'secret["\']?\s*[:=]\s*["\']?[^"\'\s&]+',
        ]
        
        sanitized = data
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, 'password=***REDACTED***', sanitized, flags=re.IGNORECASE)
        
        return sanitized

class ProxyChain:
    """
    Utility class for managing proxy chains and rotation
    """
    
    def __init__(self, proxies: List[Dict[str, str]]):
        """
        Initialize proxy chain
        
        Args:
            proxies (List[Dict]): List of proxy configurations
        """
        self.proxies = proxies
        self.current_index = 0
        self.failed_proxies = set()
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get next available proxy in rotation
        
        Returns:
            Optional[Dict]: Next proxy configuration or None
        """
        if not self.proxies:
            return None
        
        # Try to find a working proxy
        for _ in range(len(self.proxies)):
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            proxy_id = f"{proxy.get('http', '')}_{proxy.get('https', '')}"
            if proxy_id not in self.failed_proxies:
                return proxy
        
        # All proxies failed, reset failed list and try again
        self.failed_proxies.clear()
        return self.proxies[0] if self.proxies else None
    
    def mark_proxy_failed(self, proxy: Dict[str, str]) -> None:
        """
        Mark a proxy as failed
        
        Args:
            proxy (Dict): Proxy configuration that failed
        """
        proxy_id = f"{proxy.get('http', '')}_{proxy.get('https', '')}"
        self.failed_proxies.add(proxy_id)
    
    def get_proxy_count(self) -> int:
        """
        Get total number of proxies
        
        Returns:
            int: Number of proxies
        """
        return len(self.proxies)
    
    def get_failed_count(self) -> int:
        """
        Get number of failed proxies
        
        Returns:
            int: Number of failed proxies
        """
        return len(self.failed_proxies)