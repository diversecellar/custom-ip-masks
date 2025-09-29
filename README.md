# Custom IP Masks - Proxy Server

A powerful, flexible HTTP/HTTPS proxy server built with Flask that allows you to mask your IP address and browse the web anonymously. This proxy server provides advanced features for privacy, security, and traffic management.

## ⚠️ Important Disclaimer

**This tool is for educational and legitimate privacy purposes only.** Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse of this software.

## 🌟 Features

### Core Functionality
- **HTTP/HTTPS Proxy**: Forward requests while masking your real IP address
- **Header Manipulation**: Remove tracking headers and add anonymization headers
- **User-Agent Rotation**: Automatically rotate User-Agent strings to avoid detection
- **SSL/TLS Support**: Handle encrypted connections securely

### Privacy & Security
- **IP Masking**: Hide your real IP address from target servers
- **Header Sanitization**: Remove privacy-revealing headers automatically
- **Request Logging**: Comprehensive logging with privacy protection
- **Rate Limiting**: Prevent abuse and maintain server stability

### Advanced Features
- **Proxy Chaining**: Route traffic through multiple proxy servers
- **Domain Filtering**: Block or allow specific domains
- **Configuration Management**: Flexible configuration via files or environment variables
- **Health Monitoring**: Built-in status and health check endpoints

## 📋 Requirements

- Python 3.7 or higher
- Flask web framework
- Additional dependencies (see `requirements.txt`)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd custom-ip-masks

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Start the proxy server with default settings
python proxy_server.py
```

The proxy server will start on `http://127.0.0.1:8888` by default.

### 3. Configure Your Browser

Configure your browser to use the proxy server:

- **HTTP Proxy**: `127.0.0.1:8888`
- **HTTPS Proxy**: `127.0.0.1:8888`
- **SOCKS Proxy**: Not supported (HTTP/HTTPS only)

### 4. Test the Proxy

Visit `http://httpbin.org/ip` in your browser to see if your IP is being masked.

## 🔧 Configuration

### Configuration File

Create a `config.json` file for custom settings:

```json
{
  "host": "0.0.0.0",
  "port": 8888,
  "debug": false,
  "timeout": 30,
  "log_level": "INFO",
  "log_file": "proxy.log",
  "rate_limit_enabled": true,
  "requests_per_minute": 120,
  "verify_ssl": false,
  "upstream_proxy": {
    "http": "http://upstream-proxy:3128",
    "https": "http://upstream-proxy:3128"
  },
  "auth": {
    "username": "your_username",
    "password": "your_password"
  },
  "blocked_domains": [
    "malicious-site.com",
    "tracking-domain.com"
  ]
}
```

### Environment Variables

Configure using environment variables:

```bash
export PROXY_HOST=0.0.0.0
export PROXY_PORT=8888
export PROXY_LOG_LEVEL=INFO
export PROXY_RATE_LIMIT_ENABLED=true
export PROXY_UPSTREAM_HTTP=http://upstream-proxy:3128
```

### Command Line Usage

```bash
# Start with custom configuration
python proxy_server.py --config config.json

# Start with environment variables
PROXY_PORT=9000 python proxy_server.py
```

## 📖 Usage Examples

### Basic Web Browsing

1. Start the proxy server
2. Configure your browser to use `127.0.0.1:8888` as HTTP/HTTPS proxy
3. Browse normally - your IP will be masked

### Programmatic Usage

```python
import requests

# Configure requests to use the proxy
proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}

# Make requests through the proxy
response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())
```

### Direct URL Forwarding

```bash
# Forward specific URL
curl "http://127.0.0.1:8888?url=http://example.com"

# Using custom header
curl -H "X-Target-URL: http://example.com" http://127.0.0.1:8888
```

## 🛡️ Security Features

### Header Sanitization

The proxy automatically removes headers that could reveal your identity:

- `X-Forwarded-For`
- `X-Real-IP`
- `X-Originating-IP`
- `CF-Connecting-IP`
- `Via`
- `Forwarded`

### User-Agent Rotation

Automatically rotates between common browser User-Agent strings to avoid fingerprinting.

### Rate Limiting

Built-in rate limiting prevents abuse:

- Requests per minute: Configurable (default: 60)
- Requests per hour: Configurable (default: 1000)
- Per-IP tracking for fair usage

### Domain Filtering

Configure allowed/blocked domains:

```json
{
  "blocked_domains": ["malicious.com", "tracker.net"],
  "allowed_domains": ["safe-site.com", "trusted.org"]
}
```

## 📊 Monitoring

### Status Endpoint

Check proxy status:

```bash
curl http://127.0.0.1:8888/proxy/status
```

Response:
```json
{
  "status": "running",
  "uptime_seconds": 3600,
  "requests_processed": 150,
  "config": {
    "host": "127.0.0.1",
    "port": 8888,
    "upstream_proxy": false
  }
}
```

### Health Check

```bash
curl http://127.0.0.1:8888/proxy/health
```

### Logs

Monitor the log file for detailed request information:

```bash
tail -f proxy.log
```

## 🔗 Proxy Chaining

Chain multiple proxies for enhanced anonymity:

```json
{
  "upstream_proxy": {
    "http": "http://proxy1:3128",
    "https": "http://proxy1:3128"
  }
}
```

Your traffic flow: `Your Browser → Custom Proxy → Upstream Proxy → Target Server`

## ⚙️ Advanced Configuration

### SSL/TLS Configuration

For HTTPS support with custom certificates:

```json
{
  "ssl_cert_file": "/path/to/cert.pem",
  "ssl_key_file": "/path/to/key.pem",
  "verify_ssl": true
}
```

### Custom Headers

Add custom headers to all requests:

```json
{
  "add_headers": {
    "X-Custom-Header": "CustomValue",
    "Accept-Language": "en-US,en;q=0.9"
  }
}
```

### Logging Configuration

Detailed logging setup:

```json
{
  "logging": {
    "level": "DEBUG",
    "file": "proxy.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_requests": true,
    "log_responses": false
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if the proxy server is running
   - Verify the host and port configuration
   - Check firewall settings

2. **SSL Certificate Errors**
   - Set `verify_ssl: false` in configuration for testing
   - Ensure proper SSL certificates for production

3. **Rate Limiting**
   - Increase rate limits in configuration
   - Check logs for rate limit violations

4. **Performance Issues**
   - Adjust timeout values
   - Consider using upstream proxies
   - Monitor system resources

### Debug Mode

Enable debug mode for detailed error information:

```bash
python proxy_server.py --debug
```

Or in configuration:
```json
{
  "debug": true,
  "log_level": "DEBUG"
}
```

## 🔒 Security Considerations

### Important Security Notes

1. **HTTPS Interception**: This proxy can intercept HTTPS traffic. Only use with sites you trust or for testing.

2. **Logging**: Request details are logged. Ensure log files are properly secured.

3. **Network Security**: Run on trusted networks only. Consider firewall rules.

4. **Authentication**: Implement authentication for production use.

5. **Rate Limiting**: Always enable rate limiting to prevent abuse.

### Production Deployment

For production use:

1. Use HTTPS with proper certificates
2. Implement authentication
3. Set up proper firewall rules
4. Monitor logs regularly
5. Use a reverse proxy (nginx/Apache)
6. Enable rate limiting
7. Regular security updates

## 📝 License

This project is provided for educational purposes. Users are responsible for compliance with all applicable laws and regulations.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration examples
3. Check log files for error details
4. Create an issue with detailed information

## 🔄 Updates

Keep your proxy server updated:

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for security updates regularly
```

---

**Remember**: Use this tool responsibly and in compliance with all applicable laws and terms of service.