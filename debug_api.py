import requests
import json
import traceback

def test_api():
    url = "http://localhost:8000/task"
    payload = {
        "task": "Find the latest news about OpenAI"
    }
    
    print(f"🚀 Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        print("Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Is the server running? (uvicorn main:app --reload)")

if __name__ == "__main__":
    test_api()
