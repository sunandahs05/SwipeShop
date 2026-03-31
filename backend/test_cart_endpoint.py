import requests
import json

# Test the /api/cart endpoint
print("Testing /api/cart endpoint...\n")

# First, get a session cookie by logging in
session = requests.Session()

# Login
login_data = {
    'email': 'test@gmail.com',
    'password': 'test123'
}

print("1️⃣  Logging in as test@gmail.com...")
response = session.post('http://localhost:5000/login', data=login_data)
print(f"   Status: {response.status_code}")

# Test /api/cart
print("\n2️⃣  Calling /api/cart endpoint...")
response = session.get('http://localhost:5000/api/cart')
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text[:200]}")

if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Success! Cart has {len(data)} items")
    if data:
        print("\n   Cart Items:")
        for item in data:
            print(f"   - {item}")
else:
    print(f"   ❌ Error: {response.text}")
