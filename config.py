"""
Proxy Configuration Management
=============================

This module provides configuration management for the custom proxy server,
including settings validation, environment variable loading, and security options.

Author: Custom IP Masks Project
Date: September 2025
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ProxyConfig:
    """
    Data class for proxy configuration with validation
    """
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8888
    debug: bool = False
    
    # Request settings
    timeout: int = 30
    max_content_length: int = 50 * 1024 * 1024  # 50MB
    max_redirects: int = 10
    
    # Security settings
    user_agents: List[str] = None
    remove_headers: List[str] = None
    add_headers: Dict[str, str] = None
    
    # Proxy chain settings
    upstream_proxy: Optional[Dict[str, str]] = None
    auth: Optional[Dict[str, str]] = None
    
    # Rate limiting
    rate_limit_enabled: bool = False
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "proxy.log"
    log_requests: bool = True
    log_responses: bool = False
    
    # SSL/TLS settings
    verify_ssl: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    
    # Filtering and blocking
    blocked_domains: List[str] = None
    allowed_domains: List[str] = None
    blocked_ips: List[str] = None
    
    def __post_init__(self):
        """Initialize default values for list/dict fields"""
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
            ]
        
        if self.remove_headers is None:
            self.remove_headers = [
                "X-Forwarded-For",
                "X-Real-IP", 
                "X-Originating-IP",
                "CF-Connecting-IP",
                "X-Forwarded-Proto",
                "X-Forwarded-Host",
                "Via",
                "Forwarded"
            ]
        
        if self.add_headers is None:
            self.add_headers = {
                "Accept-Encoding": "gzip, deflate",
                "Connection": "close",
                "Cache-Control": "no-cache"
            }
        
        if self.blocked_domains is None:
            self.blocked_domains = []
        
        if self.allowed_domains is None:
            self.allowed_domains = []
        
        if self.blocked_ips is None:
            self.blocked_ips = []

class ConfigManager:
    """
    Configuration manager for loading and validating proxy settings
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file (Optional[str]): Path to configuration file
        """
        self.config_file = config_file
        self.config = ProxyConfig()
    
    def load_from_file(self, file_path: str) -> ProxyConfig:
        """
        Load configuration from file (JSON or YAML)
        
        Args:
            file_path (str): Path to configuration file
            
        Returns:
            ProxyConfig: Loaded configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
            # Convert nested dictionaries to proper format
            if 'upstream_proxy' in data and data['upstream_proxy']:
                data['upstream_proxy'] = data['upstream_proxy']
            
            if 'auth' in data and data['auth']:
                data['auth'] = data['auth']
            
            # Create config object with validated data
            self.config = ProxyConfig(**data)
            return self.config
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {str(e)}")
        except TypeError as e:
            raise ValueError(f"Invalid configuration parameters: {str(e)}")
    
    def load_from_env(self) -> ProxyConfig:
        """
        Load configuration from environment variables
        
        Returns:
            ProxyConfig: Configuration loaded from environment
        """
        env_config = {}
        
        # Map environment variables to config fields
        env_mappings = {
            'PROXY_HOST': 'host',
            'PROXY_PORT': ('port', int),
            'PROXY_DEBUG': ('debug', lambda x: x.lower() in ['true', '1', 'yes']),
            'PROXY_TIMEOUT': ('timeout', int),
            'PROXY_MAX_CONTENT_LENGTH': ('max_content_length', int),
            'PROXY_LOG_LEVEL': 'log_level',
            'PROXY_LOG_FILE': 'log_file',
            'PROXY_VERIFY_SSL': ('verify_ssl', lambda x: x.lower() in ['true', '1', 'yes']),
            'PROXY_RATE_LIMIT_ENABLED': ('rate_limit_enabled', lambda x: x.lower() in ['true', '1', 'yes']),
            'PROXY_REQUESTS_PER_MINUTE': ('requests_per_minute', int),
            'PROXY_UPSTREAM_HTTP': 'upstream_http',
            'PROXY_UPSTREAM_HTTPS': 'upstream_https',
            'PROXY_AUTH_USERNAME': 'auth_username',
            'PROXY_AUTH_PASSWORD': 'auth_password'
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(config_key, tuple):
                    field_name, converter = config_key
                    try:
                        env_config[field_name] = converter(value)
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid value for {env_var}: {value}")
                else:
                    env_config[config_key] = value
        
        # Handle special cases for nested dictionaries
        if 'upstream_http' in env_config or 'upstream_https' in env_config:
            upstream_proxy = {}
            if 'upstream_http' in env_config:
                upstream_proxy['http'] = env_config.pop('upstream_http')
            if 'upstream_https' in env_config:
                upstream_proxy['https'] = env_config.pop('upstream_https')
            env_config['upstream_proxy'] = upstream_proxy
        
        if 'auth_username' in env_config and 'auth_password' in env_config:
            env_config['auth'] = {
                'username': env_config.pop('auth_username'),
                'password': env_config.pop('auth_password')
            }
        
        # Update default config with environment values
        config_dict = asdict(self.config)
        config_dict.update(env_config)
        
        self.config = ProxyConfig(**config_dict)
        return self.config
    
    def save_to_file(self, file_path: str, format: str = 'json') -> None:
        """
        Save current configuration to file
        
        Args:
            file_path (str): Path to save configuration
            format (str): File format ('json' or 'yaml')
        """
        config_dict = asdict(self.config)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def validate_config(self) -> List[str]:
        """
        Validate current configuration
        
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Port validation
        if not (1 <= self.config.port <= 65535):
            errors.append(f"Invalid port number: {self.config.port}")
        
        # Timeout validation
        if self.config.timeout <= 0:
            errors.append(f"Timeout must be positive: {self.config.timeout}")
        
        # Rate limit validation
        if self.config.rate_limit_enabled:
            if self.config.requests_per_minute <= 0:
                errors.append(f"Requests per minute must be positive: {self.config.requests_per_minute}")
            if self.config.requests_per_hour <= 0:
                errors.append(f"Requests per hour must be positive: {self.config.requests_per_hour}")
        
        # SSL file validation
        if self.config.ssl_cert_file and not os.path.exists(self.config.ssl_cert_file):
            errors.append(f"SSL certificate file not found: {self.config.ssl_cert_file}")
        
        if self.config.ssl_key_file and not os.path.exists(self.config.ssl_key_file):
            errors.append(f"SSL key file not found: {self.config.ssl_key_file}")
        
        # Log level validation
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.config.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {self.config.log_level}")
        
        return errors
    
    def get_config(self) -> ProxyConfig:
        """
        Get current configuration
        
        Returns:
            ProxyConfig: Current configuration
        """
        return self.config

def create_sample_config() -> str:
    """
    Create a sample configuration file
    
    Returns:
        str: Sample configuration as JSON string
    """
    sample_config = ProxyConfig(
        host="0.0.0.0",
        port=8888,
        debug=False,
        timeout=30,
        log_level="INFO",
        log_file="proxy.log",
        rate_limit_enabled=True,
        requests_per_minute=120,
        verify_ssl=False
    )
    
    return json.dumps(asdict(sample_config), indent=2)

if __name__ == "__main__":
    # Example usage
    print("Sample configuration:")
    print(create_sample_config())