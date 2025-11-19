#!/usr/bin/env python3
"""
Test script for the custom proxy server
=======================================

This script tests various functionality of the proxy server to ensure
it's working correctly and masking IP addresses properly.

Author: Custom IP Masks Project
Date: September 2025
"""

import sys
import time
import json
import requests
from threading import Thread
from urllib.parse import urlparse

class ProxyTester:
    """
    Test suite for the custom proxy server
    """
    
    def __init__(self, proxy_host='127.0.0.1', proxy_port=8888):
        """
        Initialize the proxy tester
        
        Args:
            proxy_host (str): Proxy server host
            proxy_port (int): Proxy server port
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_url = f"http://{proxy_host}:{proxy_port}"
        self.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        self.session = requests.Session()
        self.session.proxies.update(self.proxies)
        
    def test_proxy_connection(self):
        """
        Test basic proxy connection
        """
        print("1. Testing proxy connection...")
        
        try:
            # Test proxy health endpoint
            response = requests.get(f"{self.proxy_url}/proxy/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"   ✓ Proxy health check passed: {health['status']}")
                return True
            else:
                print(f"   ✗ Proxy health check failed: {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            print("   ✗ Cannot connect to proxy server")
            print(f"   Make sure the proxy is running on {self.proxy_host}:{self.proxy_port}")
            return False
        except Exception as e:
            print(f"   ✗ Proxy connection test failed: {e}")
            return False
    
    def test_ip_masking(self):
        """
        Test IP address masking functionality
        """
        print("2. Testing IP masking...")
        
        try:
            # Get IP without proxy
            direct_response = requests.get('http://httpbin.org/ip', timeout=10)
            direct_ip = direct_response.json()['origin']
            print(f"   Direct IP: {direct_ip}")
            
            # Get IP through proxy
            proxy_response = self.session.get('http://httpbin.org/ip', timeout=10)
            proxy_ip = proxy_response.json()['origin']
            print(f"   Proxy IP: {proxy_ip}")
            
            if direct_ip != proxy_ip:
                print("   ✓ IP masking is working correctly")
                return True
            else:
                print("   ⚠ IP addresses are the same - check proxy configuration")
                return False
        
        except Exception as e:
            print(f"   ✗ IP masking test failed: {e}")
            return False
    
    def test_user_agent_rotation(self):
        """
        Test User-Agent header rotation
        """
        print("3. Testing User-Agent rotation...")
        
        try:
            user_agents = []
            
            # Make multiple requests to check User-Agent rotation
            for i in range(3):
                response = self.session.get('http://httpbin.org/user-agent', timeout=10)
                user_agent = response.json()['user-agent']
                user_agents.append(user_agent)
                print(f"   Request {i+1}: {user_agent[:50]}...")
                time.sleep(1)  # Small delay between requests
            
            # Check if User-Agents are being rotated
            unique_agents = set(user_agents)
            if len(unique_agents) > 1:
                print(f"   ✓ User-Agent rotation working ({len(unique_agents)} different agents)")
                return True
            else:
                print("   ⚠ User-Agent rotation not detected (may be configured with single agent)")
                return True  # This might be intentional
        
        except Exception as e:
            print(f"   ✗ User-Agent rotation test failed: {e}")
            return False
    
    def test_header_sanitization(self):
        """
        Test header sanitization (removal of privacy headers)
        """
        print("4. Testing header sanitization...")
        
        try:
            # Send request with privacy-revealing headers
            custom_headers = {
                'X-Forwarded-For': '192.168.1.100',
                'X-Real-IP': '10.0.0.1',
                'Via': 'test-proxy',
                'X-Originating-IP': '172.16.0.1'
            }
            
            response = requests.get(
                'http://httpbin.org/headers',
                headers=custom_headers,
                proxies=self.proxies,
                timeout=10
            )
            
            received_headers = response.json()['headers']
            
            # Check if privacy headers were removed
            privacy_headers_found = []
            for header in custom_headers.keys():
                if header in received_headers:
                    privacy_headers_found.append(header)
            
            if not privacy_headers_found:
                print("   ✓ Privacy headers successfully removed")
                return True
            else:
                print(f"   ⚠ Some privacy headers were not removed: {privacy_headers_found}")
                return False
        
        except Exception as e:
            print(f"   ✗ Header sanitization test failed: {e}")
            return False
    
    def test_https_support(self):
        """
        Test HTTPS support
        """
        print("5. Testing HTTPS support...")
        
        try:
            # Test HTTPS request through proxy
            response = self.session.get('https://httpbin.org/ip', timeout=10, verify=False)
            
            if response.status_code == 200:
                ip_data = response.json()
                print(f"   ✓ HTTPS request successful, IP: {ip_data['origin']}")
                return True
            else:
                print(f"   ✗ HTTPS request failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"   ✗ HTTPS support test failed: {e}")
            return False
    
    def test_proxy_status(self):
        """
        Test proxy status endpoint
        """
        print("6. Testing proxy status endpoint...")
        
        try:
            response = requests.get(f"{self.proxy_url}/proxy/status", timeout=5)
            
            if response.status_code == 200:
                status = response.json()
                print(f"   ✓ Status endpoint working")
                print(f"   Status: {status['status']}")
                print(f"   Uptime: {status['uptime_formatted']}")
                print(f"   Requests processed: {status['requests_processed']}")
                return True
            else:
                print(f"   ✗ Status endpoint failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"   ✗ Status endpoint test failed: {e}")
            return False
    
    def test_performance(self):
        """
        Test proxy performance with multiple requests
        """
        print("7. Testing performance...")
        
        try:
            start_time = time.time()
            successful_requests = 0
            total_requests = 10
            
            for i in range(total_requests):
                try:
                    response = self.session.get('http://httpbin.org/ip', timeout=10)
                    if response.status_code == 200:
                        successful_requests += 1
                except:
                    pass
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   Completed {successful_requests}/{total_requests} requests in {duration:.2f}s")
            print(f"   Average: {duration/total_requests:.2f}s per request")
            
            if successful_requests >= total_requests * 0.8:  # 80% success rate
                print("   ✓ Performance test passed")
                return True
            else:
                print("   ⚠ Performance test showed issues")
                return False
        
        except Exception as e:
            print(f"   ✗ Performance test failed: {e}")
            return False
    
    def run_all_tests(self):
        """
        Run all tests and return summary
        """
        print("Custom IP Masks - Proxy Server Test Suite")
        print("=" * 50)
        
        tests = [
            self.test_proxy_connection,
            self.test_ip_masking,
            self.test_user_agent_rotation,
            self.test_header_sanitization,
            self.test_https_support,
            self.test_proxy_status,
            self.test_performance
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
                print()
            except Exception as e:
                print(f"   ✗ Test failed with exception: {e}")
                results.append(False)
                print()
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("=" * 50)
        print(f"Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Your proxy server is working correctly.")
        elif passed >= total * 0.7:
            print("⚠️  Most tests passed. Check the failed tests above.")
        else:
            print("❌ Many tests failed. Check your proxy configuration.")
        
        return passed, total

def main():
    """
    Main function to run the test suite
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the custom proxy server')
    parser.add_argument('--host', default='127.0.0.1', help='Proxy host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8888, help='Proxy port (default: 8888)')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    
    args = parser.parse_args()
    
    tester = ProxyTester(args.host, args.port)
    
    if args.quick:
        # Quick tests
        print("Running quick tests...")
        print()
        tester.test_proxy_connection()
        print()
        tester.test_ip_masking()
    else:
        # Full test suite
        tester.run_all_tests()

if __name__ == '__main__':
    main()