import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        # Using OpenWeatherMap API (free tier)
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', 'demo_key')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geo_url = "http://api.openweathermap.org/geo/1.0"
        
    def get_coordinates(self, location):
        """Get latitude and longitude for a location"""
        try:
            cache_key = f"coords_{location.replace(' ', '_').lower()}"
            coords = cache.get(cache_key)
            
            if coords:
                return coords
                
            url = f"{self.geo_url}/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                coords = {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon'],
                    'name': data[0]['name'],
                    'country': data[0]['country']
                }
                # Cache for 24 hours
                cache.set(cache_key, coords, 86400)
                return coords
            return None
            
        except Exception as e:
            logger.error(f"Error getting coordinates for {location}: {str(e)}")
            return None
    
    def get_current_weather(self, location):
        """Get current weather for a location"""
        try:
            cache_key = f"current_weather_{location.replace(' ', '_').lower()}"
            weather_data = cache.get(cache_key)
            
            if weather_data:
                return weather_data
            
            coords = self.get_coordinates(location)
            if not coords:
                return None
                
            url = f"{self.base_url}/weather"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_data = {
                'location': f"{coords['name']}, {coords['country']}",
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'uv_index': None,  # Would need separate API call
                'timestamp': datetime.now(),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset'])
            }
            
            # Cache for 10 minutes
            cache.set(cache_key, weather_data, 600)
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting current weather for {location}: {str(e)}")
            return None
    
    def get_weather_forecast(self, location, days=5):
        """Get weather forecast for a location"""
        try:
            cache_key = f"forecast_{location.replace(' ', '_').lower()}_{days}"
            forecast_data = cache.get(cache_key)
            
            if forecast_data:
                return forecast_data
            
            coords = self.get_coordinates(location)
            if not coords:
                return None
                
            url = f"{self.base_url}/forecast"
            params = {
                'lat': coords['lat'],
                'lon': coords['lon'],
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process forecast data (5-day forecast with 3-hour intervals)
            daily_forecasts = {}
            
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'date': date,
                        'temps': [],
                        'humidity': [],
                        'descriptions': [],
                        'icons': [],
                        'wind_speeds': [],
                        'precipitation': 0
                    }
                
                daily_forecasts[date]['temps'].append(item['main']['temp'])
                daily_forecasts[date]['humidity'].append(item['main']['humidity'])
                daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
                daily_forecasts[date]['icons'].append(item['weather'][0]['icon'])
                daily_forecasts[date]['wind_speeds'].append(item['wind']['speed'])
                
                # Add precipitation if available
                if 'rain' in item:
                    daily_forecasts[date]['precipitation'] += item['rain'].get('3h', 0)
                if 'snow' in item:
                    daily_forecasts[date]['precipitation'] += item['snow'].get('3h', 0)
            
            # Process daily summaries
            forecast_list = []
            for date, day_data in list(daily_forecasts.items())[:days]:
                forecast_list.append({
                    'date': date,
                    'temp_max': round(max(day_data['temps'])),
                    'temp_min': round(min(day_data['temps'])),
                    'humidity': round(sum(day_data['humidity']) / len(day_data['humidity'])),
                    'description': max(set(day_data['descriptions']), key=day_data['descriptions'].count),
                    'icon': max(set(day_data['icons']), key=day_data['icons'].count),
                    'wind_speed': round(sum(day_data['wind_speeds']) / len(day_data['wind_speeds']), 1),
                    'precipitation': round(day_data['precipitation'], 1)
                })
            
            # Cache for 1 hour
            cache.set(cache_key, forecast_list, 3600)
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error getting forecast for {location}: {str(e)}")
            return None
    
    def get_weather_alerts(self, location):
        """Get weather alerts for a location"""
        try:
            coords = self.get_coordinates(location)
            if not coords:
                return []
                
            # This would require One Call API (paid) for alerts
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting weather alerts for {location}: {str(e)}")
            return []
    
    def get_agricultural_advice(self, weather_data, forecast_data):
        """Generate agricultural advice based on weather data"""
        if not weather_data or not forecast_data:
            return []
        
        advice = []
        current_temp = weather_data['temperature']
        current_humidity = weather_data['humidity']
        
        # Temperature-based advice
        if current_temp > 35:
            advice.append({
                'type': 'warning',
                'title': 'High Temperature Alert',
                'message': 'Extreme heat detected. Ensure adequate irrigation and consider shade protection for sensitive crops.',
                'icon': 'fas fa-thermometer-full'
            })
        elif current_temp < 5:
            advice.append({
                'type': 'danger',
                'title': 'Frost Warning',
                'message': 'Low temperatures may cause frost damage. Protect sensitive plants and consider covering crops.',
                'icon': 'fas fa-snowflake'
            })
        
        # Humidity-based advice
        if current_humidity > 80:
            advice.append({
                'type': 'warning',
                'title': 'High Humidity',
                'message': 'High humidity increases disease risk. Monitor crops for fungal infections and ensure good ventilation.',
                'icon': 'fas fa-tint'
            })
        elif current_humidity < 30:
            advice.append({
                'type': 'info',
                'title': 'Low Humidity',
                'message': 'Low humidity detected. Increase irrigation frequency and consider mulching to retain soil moisture.',
                'icon': 'fas fa-sun'
            })
        
        # Precipitation forecast advice
        total_precipitation = sum(day['precipitation'] for day in forecast_data)
        if total_precipitation > 50:
            advice.append({
                'type': 'info',
                'title': 'Heavy Rain Expected',
                'message': f'Significant rainfall ({total_precipitation}mm) expected in the next 5 days. Ensure proper drainage and delay fertilizer application.',
                'icon': 'fas fa-cloud-rain'
            })
        elif total_precipitation < 5:
            advice.append({
                'type': 'warning',
                'title': 'Dry Period Ahead',
                'message': 'Little rainfall expected. Plan irrigation schedule and consider drought-resistant practices.',
                'icon': 'fas fa-sun'
            })
        
        # Seasonal advice
        current_month = datetime.now().month
        if current_month in [3, 4, 5]:  # Spring
            advice.append({
                'type': 'success',
                'title': 'Spring Planting Season',
                'message': 'Optimal time for planting most crops. Prepare soil and plan your planting schedule.',
                'icon': 'fas fa-seedling'
            })
        elif current_month in [6, 7, 8]:  # Summer
            advice.append({
                'type': 'info',
                'title': 'Summer Growing Season',
                'message': 'Monitor crops closely for pests and diseases. Maintain consistent irrigation.',
                'icon': 'fas fa-leaf'
            })
        elif current_month in [9, 10, 11]:  # Fall
            advice.append({
                'type': 'success',
                'title': 'Harvest Season',
                'message': 'Time to harvest mature crops and prepare for winter storage.',
                'icon': 'fas fa-warehouse'
            })
        else:  # Winter
            advice.append({
                'type': 'info',
                'title': 'Winter Preparation',
                'message': 'Protect crops from cold weather and plan for next growing season.',
                'icon': 'fas fa-snowflake'
            })
        
        return advice

# Global weather service instance
weather_service = WeatherService()

def get_weather_service():
    """Get the weather service instance"""
    return weather_service