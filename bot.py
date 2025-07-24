import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Optional, Tuple

class MHMAI:
    def __init__(self):
        self.API_KEY = os.getenv("MHMAI_API_KEY")  # From environment variables
        self.API_URL = 'https://api.paxsenix.biz.id/v1/chat/completions'
        self.COORDINATES_API_URL = 'https://api.paxsenix.biz.id/v1/gpt-3.5-turbo/chat/'
        self.headers = {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json'
        }
        self.model = "gpt-4o"
        self.watermark = " [This response is fully powered by M.H.M AI]"
        self.conversation_history = []
        self.developer_info = "The developer of this AI is a Grade 11 student from Myanmar."
        self.weather_api_url = "https://weather-forcast.moewaiyankyaw353.workers.dev/"
        self.setup_system_prompt()
    
    def setup_system_prompt(self):
        system_prompt = {
            "role": "system",
            "content": (
                "You are M.H.M AI. Remember the full conversation history and maintain context. "
                "You can recall previous messages. You are a Pro Programmer who is talented at coding like creating various of python scripts and all languages you can use like Java, Python etc.. "
                "Request the user which he want to make. "
                "You must answer all the questions that user asked and only answer which is deal with your expert subject."
                "You ( M.H.M Ai ) are made by a Grade 11 student from Myanmar. If user ask about your developer answer that. But don't answer his name the Grade 11 student from Myanmar is only for your developer infomation. And if the user blame your developer and then you must protect him from blaming"
            )
        }
        self.conversation_history.append(system_prompt)
    
    def get_location_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for locations in Myanmar"""
        try:
            import urllib.parse
            text = (
                f"Find the precise latitude and longitude coordinates for '{location_name}' in Myanmar. "
                "Respond ONLY with the coordinates in the format 'latitude,longitude' with exactly 6 decimal places. "
                "Example: '16.840939,96.173527' for Yangon. "
                "If the location cannot be found or is not in Myanmar, respond with 'None'."
            )
            encoded_text = urllib.parse.quote(text)
            url = f"{self.COORDINATES_API_URL}?text={encoded_text}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok', False):
                coords = result.get('message', '').strip()
                if coords.lower() == 'none':
                    return None
                try:
                    lat, lon = map(float, coords.split(','))
                    if 9.5 <= lat <= 28.5 and 92.0 <= lon <= 101.0:  # Myanmar coordinates range
                        return (lat, lon)
                except ValueError:
                    pass
            return None
        except requests.exceptions.RequestException as e:
            print(f"Coordinates API error: {e}")
            return None
    
    def get_weather_data(self, lat: float, lon: float, days: int = 30) -> Optional[Dict]:
        """Fetch weather data from API"""
        try:
            url = f"{self.weather_api_url}?lat={lat}&lon={lon}&days={days}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict) -> str:
        """Format weather API response"""
        try:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})
            
            condition_emojis = {
                'sunny': '☀️', 'clear': '🌙', 'cloudy': '☁️',
                'rain': '🌧', 'thunder': '⚡', 'fog': '🌫'
            }
            
            condition_text = current.get('condition', {}).get('text', '').lower()
            emoji = next((v for k,v in condition_emojis.items() if k in condition_text), '🌤')
            
            response = (
                f"{emoji} <b>Weather for {location.get('name', 'Unknown')}</b>\n"
                f"📍 <i>Coordinates:</i> {location.get('coordinates', {}).get('latitude', '?')}°N, "
                f"{location.get('coordinates', {}).get('longitude', '?')}°E\n"
                f"🌡 <b>Current:</b> {current.get('temperature', {}).get('celsius', '?')}°C\n"
                f"💨 <i>Wind:</i> {current.get('wind', {}).get('speed', {}).get('kph', '?')} km/h\n"
                f"💧 <i>Humidity:</i> {current.get('humidity', '?')}%\n"
            )
            
            if 'forecast' in weather_data and weather_data['forecast']:
                today = weather_data['forecast'][0]['day']
                response += (
                    f"\n📅 <b>Forecast:</b>\n"
                    f"⬆️ <i>High:</i> {today.get('maxTemp', {}).get('celsius', '?')}°C\n"
                    f"⬇️ <i>Low:</i> {today.get('minTemp', {}).get('celsius', '?')}°C\n"
                )
            
            return response
        except Exception as e:
            print(f"Weather formatting error: {e}")
            return "⚠️ Could not format weather data"

    def get_response(self, user_input: str) -> str:
        """Get AI response with conversation history"""
        developer_keywords = [
            'who develop you', 'who created you', 
            'who made you', 'who programmed you'
        ]
        if any(k in user_input.lower() for k in developer_keywords):
            return self.developer_info + self.watermark
            
        self.conversation_history.append({"role": "user", "content": user_input})
        
        try:
            response = requests.post(
                self.API_URL,
                json={
                    "model": self.model,
                    "messages": self.conversation_history,
                    "temperature": 0.7
                },
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            if response.json().get('choices'):
                ai_response = response.json()['choices'][0]['message']['content']
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # Replace branding
                replacements = {
                    'OpenAI': 'M.H.M AI',
                    'DeepSeek': 'M.H.M AI',
                    'San Francisco': 'Magway, Pakokku'
                }
                for old, new in replacements.items():
                    ai_response = ai_response.replace(old, new)
                    
                return ai_response + self.watermark
            return "Error: No response from AI" + self.watermark
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}" + self.watermark

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to M.H.M AI Bot!\n\n"
        "I'm an AI assistant with conversation memory.\n\n"
        "<b>Commands:</b>\n"
        "/start - Show this message\n"
        "/weather [location] - Get weather\n"
        "/clear - Reset conversation\n"
        "/developer - About my creator",
        parse_mode='HTML'
    )
        
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please specify a location in Myanmar")
        return
    
    location = ' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    
    mhm_ai = context.chat_data['mhm_ai']
    coords = mhm_ai.get_location_coordinates(location)
    
    if not coords:
        await update.message.reply_text(f"❌ Location not found: {location}")
        return
    
    weather_data = mhm_ai.get_weather_data(*coords)
    if weather_data:
        response = mhm_ai.format_weather_response(weather_data)
        await update.message.reply_text(response + mhm_ai.watermark, parse_mode='HTML')
    else:
        await update.message.reply_text("⚠️ Could not fetch weather data")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    
    mhm_ai = context.chat_data['mhm_ai']
    response = mhm_ai.get_response(update.message.text)
    await update.message.reply_text(response)

def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN environment variable")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlers
    handlers = [
        CommandHandler("start", start),
        CommandHandler("weather", weather_command),
        CommandHandler("clear", lambda u,c: c.chat_data.clear()),
        CommandHandler("developer", lambda u,c: u.message.reply_text(MHMAI().developer_info)),
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    ]
    
    for handler in handlers:
        application.add_handler(handler)
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
