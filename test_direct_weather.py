"""Direct test for WeatherAPI.com - bypasses .env caching issues."""
import asyncio
import httpx


async def test_direct():
    """Test WeatherAPI.com directly."""
    # Read API key from .env file
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('WEATHER_API_KEY='):
                api_key = line.split('=')[1].split('#')[0].strip()
                break
    
    print(f"🔑 API Key found: {api_key[:10]}..." if api_key else "❌ No API key found")
    print("\n🧪 Testing WeatherAPI.com for Kanpur Nagar...")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": api_key,
            "q": "Kanpur",
            "aqi": "no"
        }
        
        try:
            response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                location = data["location"]
                current = data["current"]
                
                print("✅ SUCCESS! Weather data retrieved:")
                print(f"   📍 City: {location['name']}, {location['country']}")
                print(f"   🌡️  Temperature: {current['temp_c']}°C (Feels like: {current['feelslike_c']}°C)")
                print(f"   💧 Humidity: {current['humidity']}%")
                print(f"   ☁️  Conditions: {current['condition']['text']}")
                print(f"   💨 Wind Speed: {current['wind_kph']} km/h")
                print(f"   👁️  Visibility: {current['vis_km']} km")
            elif response.status_code == 401:
                print("❌ ERROR: Invalid API key")
                print("   Please check your API key at: https://www.weatherapi.com/my/")
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ ERROR: {error_data.get('error', {}).get('message', 'Bad Request')}")
            else:
                print(f"❌ ERROR: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_direct())
