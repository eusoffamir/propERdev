#!/usr/bin/env python3
"""
Test script to verify admin access to database viewer
"""

import requests
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_admin_access():
    """Test admin access to database viewer"""
    base_url = "http://127.0.0.1:5000"
    
    # Test 1: Try to access admin route without login (should redirect to login)
    print("Testing admin access without login...")
    try:
        response = requests.get(f"{base_url}/admin/", allow_redirects=False)
        if response.status_code == 302:  # Redirect to login
            print("✅ Correctly redirected to login when not authenticated")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the app is running.")
        return
    
    # Test 2: Try to access admin route with login (you'll need to manually test this)
    print("\nTo test admin access with login:")
    print("1. Start the application: python run.py")
    print("2. Go to http://127.0.0.1:5000")
    print("3. Login with admin credentials (e.g., eusoff@proper.com / eusoff123)")
    print("4. Click on 'Database Viewer' in the admin dashboard")
    print("5. You should now be able to see all database tables")

if __name__ == "__main__":
    test_admin_access() 