# 🎭 Custom IP Masks

A powerful, flexible HTTP/HTTPS proxy server built with Flask that allows you to mask your IP address and browse the web anonymously.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ⚠️ Disclaimer

**This tool is for educational and legitimate privacy purposes only.** Users are responsible for complying with all applicable laws and regulations. The authors are not responsible for any misuse of this software.

## ✨ Features

### 🔒 Privacy & Security
- **IP Masking**: Hide your real IP address from target servers
- **Header Sanitization**: Remove privacy-revealing headers automatically
- **User-Agent Rotation**: Randomly rotate browser signatures to avoid detection
- **SSL/TLS Support**: Handle encrypted connections securely

### ⚡ Advanced Functionality
- **Proxy Chaining**: Route traffic through multiple proxy servers
- **Domain Filtering**: Block or allow specific domains
- **Rate Limiting**: Prevent abuse and maintain server stability
- **Authentication Support**: Secure access with username/password

### 🛠️ Easy to Use
- **Simple Setup**: Quick installation with minimal dependencies
- **Configuration Management**: Flexible setup via files or environment variables
- **Health Monitoring**: Built-in status and health check endpoints
- **Comprehensive Logging**: Monitor activity while protecting privacy

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/diversecellar/custom-ip-masks.git
cd custom-ip-masks

# Install dependencies
pip install -r requirements-minimal.txt
```

### 2. Start the Proxy

```bash
python start_proxy.py
```

### 3. Configure Your Browser

Set your browser proxy settings to:
- **HTTP Proxy**: `127.0.0.1:8888`
- **HTTPS Proxy**: `127.0.0.1:8888`

### 4. Test Your Setup

Visit [httpbin.org/ip](http://httpbin.org/ip) - your displayed IP should be different from your real IP.

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 3 steps
- **[Full Documentation](README.md)** - Comprehensive setup and configuration
- **[Examples](examples.py)** - Usage examples and demonstrations

## 🔧 Usage Examples

### Basic Usage
```bash
# Start with default settings
python start_proxy.py

# Custom port
python start_proxy.py --port 9000

# Allow external connections
python start_proxy.py --open-access

# Debug mode
python start_proxy.py --debug
```

### Programmatic Usage
```python
import requests

proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}

response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())
```

### Stop the Proxy
```bash
# Simple stop
python stop_proxy_simple.py

# Advanced stop with process management
python stop_proxy.py

# Windows batch file
stop_proxy.bat
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Quick test
python test_proxy.py --quick

# Full test suite
python test_proxy.py
```

## ⚙️ Configuration

### Command Line Options
```bash
python start_proxy.py --help
```

### Configuration File
Create a `config.json` file:
```json
{
  "host": "0.0.0.0",
  "port": 8888,
  "rate_limit_enabled": true,
  "requests_per_minute": 120,
  "blocked_domains": ["ads.example.com", "tracker.net"]
}
```

### Environment Variables
```bash
export PROXY_HOST=0.0.0.0
export PROXY_PORT=8888
export PROXY_RATE_LIMIT_ENABLED=true
```

## 📁 Project Structure

```
custom-ip-masks/
├── proxy_server.py          # Main proxy server
├── start_proxy.py           # Easy startup script
├── stop_proxy.py            # Advanced stop utility
├── stop_proxy_simple.py     # Simple stop utility
├── config.py                # Configuration management
├── utils.py                 # Utility functions
├── test_proxy.py            # Test suite
├── examples.py              # Usage examples
├── requirements.txt         # Full dependencies
├── requirements-minimal.txt # Essential dependencies only
├── README.md               # Full documentation
├── QUICKSTART.md           # Quick start guide
└── stop_proxy.bat          # Windows stop script
```

## 🛡️ Security Features

- **Header Sanitization**: Removes `X-Forwarded-For`, `X-Real-IP`, `Via`, etc.
- **User-Agent Randomization**: Rotates between realistic browser signatures
- **SSL Handling**: Properly manages HTTPS connections
- **Rate Limiting**: Prevents abuse and detection
- **Domain Blocking**: Filter malicious or unwanted sites

## 💻 Platform Support

- ✅ **Windows** (Tested on Windows 10/11)
- ✅ **macOS** (Compatible)
- ✅ **Linux** (Compatible)

## 📋 Requirements

- Python 3.7 or higher
- Flask 3.0+
- requests 2.31+
- urllib3 2.0+
- PyYAML 6.0+ (optional)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Powered by [requests](https://requests.readthedocs.io/)
- Inspired by privacy and security research

## ⚡ Performance

- Handles 100+ concurrent connections
- Sub-second response times
- Minimal memory footprint
- Efficient request forwarding

## 🔗 Related Projects

- [Tor](https://www.torproject.org/) - The Onion Router
- [Privoxy](https://www.privoxy.org/) - Privacy enhancing proxy
- [mitmproxy](https://mitmproxy.org/) - Interactive TLS-capable intercepting proxy

---

**⭐ Star this repo if you find it useful!**

**🛡️ Use responsibly and in compliance with all applicable laws.**