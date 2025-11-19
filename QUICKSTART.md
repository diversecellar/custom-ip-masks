# Quick Installation & Setup Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd custom-ip-masks
pip install -r requirements-minimal.txt
```

### Step 2: Start the Proxy
```bash
python src/start_proxy.py
```

### Step 3: Stop the Proxy (When Done)
```bash
# Option 1: Simple stop (no extra dependencies)
python src/stop_proxy_simple.py

# Option 2: Advanced stop (requires psutil)
python src/stop_proxy.py

# Option 3: Windows batch file
stop_proxy.bat

# Option 4: Manual stop
# Press Ctrl+C in the proxy terminal
```

### Step 4: Configure Your Browser
Set your browser proxy settings to:
- **HTTP Proxy**: `127.0.0.1:8888`
- **HTTPS Proxy**: `127.0.0.1:8888`

## 🧪 Test Your Setup

1. **Start the proxy server** (if not already running):
   ```bash
   python start_proxy.py
   ```

2. **Test IP masking** by visiting: http://httpbin.org/ip
   - Your displayed IP should be different from your real IP

3. **Run the test suite**:
   ```bash
   python test_proxy.py --quick
   ```

## 🔧 Command Line Options

```bash
# Basic usage
python src/start_proxy.py

# Custom port
python src/start_proxy.py --port 9000

# Allow external connections
python src/start_proxy.py --open-access

# Debug mode
python src/start_proxy.py --debug

# Show help
python src/start_proxy.py --help
```

## 📋 Browser Configuration

### Chrome/Edge
1. Settings → Advanced → System → Open proxy settings
2. Set HTTP and HTTPS proxy to: `127.0.0.1:8888`

### Firefox
1. Settings → Network Settings → Settings button
2. Manual proxy configuration
3. HTTP Proxy: `127.0.0.1` Port: `8888`
4. Check "Use this proxy server for all protocols"

### Programmatic Usage (Python)
```python
import requests

proxies = {
    'http': 'http://127.0.0.1:8888',
    'https': 'http://127.0.0.1:8888'
}

response = requests.get('http://httpbin.org/ip', proxies=proxies)
print(response.json())
```

## 🛟 Troubleshooting

### Connection Issues
- Make sure the proxy server is running
- Check if port 8888 is available
- Try a different port: `python src/start_proxy.py --port 9000`

### Permission Issues
- On Windows: Run terminal as Administrator
- On Mac/Linux: Use `sudo` if needed for ports < 1024

### Installation Issues
- Use minimal requirements: `pip install -r requirements-minimal.txt`
- Update pip: `pip install --upgrade pip`
- Use virtual environment if needed

## ⚡ Next Steps

1. **Advanced Configuration**: See `README.md` for full configuration options
2. **Security**: Enable authentication for production use
3. **Performance**: Configure upstream proxies for better speed
4. **Monitoring**: Check logs in `proxy.log`

## 🔒 Important Security Notes

- This tool is for educational and legitimate privacy purposes only
- Always comply with applicable laws and terms of service
- The proxy can see all your traffic - use responsibly
- Consider using HTTPS websites for additional security

---

**Need help?** Check the full documentation in `README.md` or run the test suite with `python src/test_proxy.py`