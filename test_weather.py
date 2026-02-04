"""Quick test script to verify the WeatherAPI.com integration."""

import asyncio
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from tools.weather_tool import WeatherTool


async def test_weather():
    """Test weather fetching for Kanpur Nagar."""
    print("🧪 Testing WeatherAPI.com Weather Integration...")
    print("=" * 50)
    
    weather_tool = WeatherTool()
    
    # Check if API key is set
    if not weather_tool.api_key or weather_tool.api_key == "your_weatherapi_key_here":
        print("❌ API Key not set!")
        print("\nPlease:")
        print("1. Sign up for free at: https://www.weatherapi.com/signup.aspx")
        print("2. Get your API key from: https://www.weatherapi.com/my/")
        print("3. Add it to .env file as: WEATHER_API_KEY=your_actual_key")
        return
    
    # Test cities
    test_cities = ["Kanpur Nagar", "Delhi", "Mumbai", "New York"]
    
    for city in test_cities:
        print(f"\n📍 Fetching weather for: {city}")
        result = await weather_tool.execute(city=city, units="metric")
        
        if result.success:
            print("✅ Success!")
            for key, value in result.data.items():
                print(f"   {key.capitalize()}: {value}")
        else:
            print(f"❌ Error: {result.error}")
        
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(test_weather())
