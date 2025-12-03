# IP Masquerade - Flexible Proxy Server for Equitable Internet Access

**Last updated**: December 04, 2025<br>
**Author**: [Paul Namalomba](https://github.com/paulnamalomba)<br>
  - SESKA Computational Engineer<br>
  - Software Developer<br>
  - PhD Candidate (Civil Engineering Spec. Computational and Applied Mechanics)<br>
**Version**: v0.1.5 (Dec 2025)<br>
**Contact**: [kabwenzenamalomba@gmail.com](kabwenzenamalomba@gmail.com)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Redis](https://img.shields.io/badge/Redis-6.0%2B-orange.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, flexible, customised HTTP/HTTPS proxy server built with **Python** and **Flask** that allows you to mask your IP address and browse the web anonymously. This proxy server provides advanced features for privacy, security, and traffic management. 

The app can only be ran in the terminal, and all installation, configuration and usage information is shown as per below.

The app is coded with the philosophy of "spacing, readability and independence" over "compactness and minimilisation".

## Important Disclaimer

**This tool is for educational and legitimate privacy purposes only.** Users are responsible for complying with all applicable local internet, data security and governance laws and regulations. The authors are not responsible for any misuse of this software and will not be accessible for anything other than bug-fixing and management.

## Features

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

## Requirements

- Python 3.9 or higher
- Flask web framework
- Additional dependencies (see `requirements.txt`) - VERY IMPORTANT

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd custom-ip-masks

# Create and activate a virtual environment with your prefered name: <venv_name> (Highly recommended)
python -m venv <venv_name>
source <venv_name>/bin/activate  # On Windows, use `<venv_name>\Scripts\activate`

# Upgrade global pip (Optional)
python -m pip install --upgrade pip

# Upgrade setuptools and wheel (Optional)
pip install --upgrade setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Proxy

```bash
# Easy startup with helpful output
python src/start_proxy.py

# Or start the main server directly
python src/proxy_server.py
```

The proxy server will start on `http://127.0.0.1:8888` by default.

### 3. Stop the Proxy

When you're done using the proxy, you can stop it using several methods:

```bash
# Method 1: Keyboard shortcut (easiest)
# Press Ctrl+C in the terminal where the proxy is running

# Method 2: Simple stop script (no extra dependencies)
python src/stop_proxy_simple.py

# Method 3: Advanced stop script (requires psutil)
python src/stop_proxy.py

# Method 4: Windows batch file
stop_proxy.bat

# Method 5: Stop specific port
python src/stop_proxy_simple.py --port 8888

# Method 6: Force stop
python src/stop_proxy_simple.py --force

# Method 7: Check if proxy is running
python src/stop_proxy.py --status
```

### 4. Configure Your Browser

Configure your browser to use the proxy server:

- **HTTP Proxy**: `127.0.0.1:8888`
- **HTTPS Proxy**: `127.0.0.1:8888`
- **SOCKS Proxy**: Not supported (HTTP/HTTPS only)

### 5. Test the Proxy

#### How to verify your IP is masked

- Step 1: Check your direct public IP (no proxy)
  - macOS/Linux:
    ```bash
    curl -s https://api.ipify.org?format=json
    ```
  - Windows PowerShell:
    ```powershell
    curl https://api.ipify.org?format=json
    ```

- Step 2: Check via this proxy
  - Any OS:
    ```bash
    curl -s --proxy http://127.0.0.1:8888 https://api.ipify.org?format=json
    ```
  - Or set environment variables, then run your command:
    - PowerShell:
      ```powershell
      $env:HTTP_PROXY="http://127.0.0.1:8888"
      $env:HTTPS_PROXY="http://127.0.0.1:8888"
      curl https://api.ipify.org?format=json
      ```
    - CMD:
      ```cmd
      set HTTP_PROXY=http://127.0.0.1:8888
      set HTTPS_PROXY=http://127.0.0.1:8888
      curl https://api.ipify.org?format=json
      ```
    - macOS/Linux:
      ```bash
      HTTP_PROXY=http://127.0.0.1:8888 HTTPS_PROXY=http://127.0.0.1:8888 curl -s https://api.ipify.org?format=json
      ```

- Step 3: Compare results
  - If the IPs differ, your traffic is masked by the proxy.
  - If they are the same, your proxy is exiting with the same public IP as your machine. To change the egress IP, either:
    - Configure an upstream proxy/VPN in config.json (upstream_proxy), or
    - Run this proxy on a host/network with a different public IP.

- Optional: Verify header sanitization
  - Expect no X-Forwarded-For or X-Real-IP in proxied requests:
    ```bash
    curl -s --proxy http://127.0.0.1:8888 https://httpbin.org/headers
    ```
    Check that headers like X-Forwarded-For, X-Real-IP, Via, Forwarded are absent.

- Programmatic check (Python):
  ```python
  import requests
  proxies = {'http': 'http://127.0.0.1:8888','https': 'http://127.0.0.1:8888'}
  print("Direct:", requests.get('https://api.ipify.org?format=json').json())
  print("Proxy :", requests.get('https://api.ipify.org?format=json', proxies=proxies).json())
  ```

## Configuration

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
python src/proxy_server.py --config config.json

# Start with environment variables
PROXY_PORT=9000 python src/proxy_server.py
```

## Usage Examples

### Complete Workflow

```bash
# 1. Start the proxy server
python src/start_proxy.py

# 2. (Configure your browser to use 127.0.0.1:8888)

# 3. Test the proxy
python src/test_proxy.py --quick

# 4. When finished, stop the proxy
python src/stop_proxy_simple.py
```

### Basic Web Browsing

1. Start the proxy server: `python src/start_proxy.py`
2. Configure your browser to use `127.0.0.1:8888` as HTTP/HTTPS proxy
3. Browse normally - your IP will be masked
4. Stop when done: `python src/stop_proxy_simple.py`

### Advanced Start/Stop Options

```bash
# Start with custom options
python src/start_proxy.py --port 9000 --debug --open-access

# Stop specific port
python src/stop_proxy_simple.py --port 9000

# Force stop if needed
python src/stop_proxy_simple.py --force

# Check proxy status
python src/stop_proxy.py --status

# List all proxy processes
python src/stop_proxy.py --list
```

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

## Security Features

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
  "blocked_domains": [],
  "allowed_domains": []
}
```

## Monitoring

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
    "auth_enabled": false,
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

## Proxy Chaining

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

## Advanced Configuration

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

## Troubleshooting

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
python src/proxy_server.py --debug
```

Or in configuration:
```json
{
  "debug": true,
  "log_level": "DEBUG"
}
```

## Security Considerations

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

## License

This project is provided for educational purposes. Users are responsible for compliance with all applicable laws and regulations.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration examples
3. Check log files for error details
4. Create an issue with detailed information

## Updates

Keep your proxy server updated:

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for security updates regularly
```

---

**Remember**: Use this tool responsibly and in compliance with all applicable laws and terms of service.

---

## Version History

- Check `CHANGELOG.md` for detailed version history and updates.

---

**Author**: Paul Namalomba<br>
**Created**: September, 2025<br>
**Version**: Rolling (v0.1.4 as of Nov 2025)