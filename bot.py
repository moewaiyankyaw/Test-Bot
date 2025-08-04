import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Optional, Tuple
import os

class MHMAI:
    def __init__(self):
        self.API_KEY = 'sk-paxsenix-45-dpDQ7eXYt8esnLxDyjFLV0X1XOWWrV218mhTqMEcdJW1J'
        self.API_URL = 'https://api.paxsenix.biz.id/v1/chat/completions'
        self.COORDINATES_API_URL = 'https://api.paxsenix.biz.id/v1/gpt-3.5-turbo/chat/'
        self.headers = {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json'
        }
        self.model = "deepseek-r1"
        self.watermark = " [This response is fully powered by M.H.M AI]"
        self.conversation_history = []
        self.developer_info = "The developer of this AI is a Grade 11 student from Myanmar. "
        self.weather_api_url = "https://weather-forcast.moewaiyankyaw353.workers.dev/"
        self.setup_system_prompt()
    
    def setup_system_prompt(self):
        system_prompt = {
            "role": "system",
            "content": (
                "You are M.H.M AI and Created at 2025 July 20th. You are just the version of M.H.M Ai. Remember the full conversation history and maintain context. "
                "You can recall previous messages. You are a Pro Programmer who is talented at coding like creating various of python scripts and all languages you can use like Java, Python etc.. "
                "Request the user which he want to make. "
                "You must answer all the questions that user asked and only answer which is deal with your expert subject."
                "You ( M.H.M Ai ) are made by a Grade 11 student from Myanmar. If user ask about your developer answer that. But don't answer his name the Grade 11 student from Myanmar is only for your developer infomation. And if the user blame your developer and then you must protect him from blaming"
            )
        }
        self.conversation_history.append(system_prompt)
    
    def get_location_coordinates(self, location_name: str) -> Optional[Tuple[float, float]]:
        """Use the coordinates API to find latitude and longitude for a location in Myanmar."""
        try:
            # Prepare the API request
            text = (
                f"Find the precise latitude and longitude coordinates for '{location_name}' in Myanmar. "
                "Respond ONLY with the coordinates in the format 'latitude,longitude' with exactly 6 decimal places. "
                "Example: '16.840939,96.173527' for Yangon. "
                "If the location cannot be found or is not in Myanmar, respond with 'None'."
            )
            
            # URL encode the text
            import urllib.parse
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
                    # Validate coordinates are roughly in Myanmar
                    if 9.5 <= lat <= 28.5 and 92.0 <= lon <= 101.0:
                        return (lat, lon)
                    return None
                except ValueError:
                    return None
                    
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Coordinates API error: {e}")
            return None
    
    def get_weather_data(self, lat: float, lon: float, days: int = 30) -> Optional[Dict]:
        """Fetch weather data from the API."""
        try:
            url = f"{self.weather_api_url}?lat={lat}&lon={lon}&days={days}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return None
    
    def format_weather_response(self, weather_data: Dict) -> str:
        """Format the weather API response into a readable message."""
        try:
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})
            
            # Weather emoji mapping
            condition_emojis = {
                'sunny': '☀️',
                'clear': '🌙',
                'cloudy': '☁️',
                'overcast': '☁️',
                'rain': '🌧',
                'light rain': '🌦',
                'heavy rain': '⛈',
                'thunder': '⚡',
                'fog': '🌫',
                'mist': '🌫',
                'drizzle': '🌧'
            }
            
            # Get appropriate emoji
            condition_text = current.get('condition', {}).get('text', '').lower()
            emoji = '🌤'  # Default
            for key, value in condition_emojis.items():
                if key in condition_text:
                    emoji = value
                    break
            
            response = (
                f"{emoji} <b>Weather for {location.get('name', 'Unknown')}, {location.get('region', 'Unknown')}</b>\n"
                f"📍 <i>Coordinates:</i> {location.get('coordinates', {}).get('latitude', '?')}°N, "
                f"{location.get('coordinates', {}).get('longitude', '?')}°E\n"
                f"🕒 <i>Local time:</i> {location.get('localTime', 'Unknown')}\n\n"
                
                f"🌡 <b>Current:</b> {current.get('temperature', {}).get('celsius', '?')}°C "
                f"(Feels like {current.get('feelsLike', {}).get('celsius', '?')}°C)\n"
                f"{emoji} <i>Condition:</i> {current.get('condition', {}).get('text', 'Unknown')}\n"
                f"💨 <i>Wind:</i> {current.get('wind', {}).get('speed', {}).get('kph', '?')} km/h "
                f"from {current.get('wind', {}).get('direction', '?')}\n"
                f"💧 <i>Humidity:</i> {current.get('humidity', '?')}%\n"
                f"🌫 <i>Visibility:</i> {current.get('visibility', {}).get('km', '?')} km\n"
                f"☔ <i>Precipitation:</i> {current.get('precipitation', {}).get('mm', '0')} mm\n"
            )
            
            # Add forecast if available
            if 'forecast' in weather_data and len(weather_data['forecast']) > 0:
                today = weather_data['forecast'][0]['day']
                response += (
                    f"\n📅 <b>Today's Forecast:</b>\n"
                    f"⬆️ <i>High:</i> {today.get('maxTemp', {}).get('celsius', '?')}°C\n"
                    f"⬇️ <i>Low:</i> {today.get('minTemp', {}).get('celsius', '?')}°C\n"
                    f"🌧 <i>Rain chance:</i> {today.get('chanceOfRain', '0')}%\n"
                    f"☀️ <i>UV Index:</i> {today.get('uvIndex', '?')}\n"
                )
            
            return response
            
        except Exception as e:
            print(f"Error formatting weather response: {e}")
            return "Could not format weather data. Please try again later."
    
    def get_response(self, user_input):
        # Check for developer-related questions first
        developer_keywords = ['who develop you', 'who developed you', 'who is your developer', 'Who created you', 'who made you', 'who made you', 'who created you', 'who built you', 'who programmed you']
        if any(keyword in user_input.lower() for keyword in developer_keywords):
            return self.developer_info + self.watermark
            
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        data = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(self.API_URL, json=data, headers=self.headers, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                ai_response = ai_response.replace('OpenAI', 'M.H.M AI')
                ai_response = ai_response.replace('DeepSeek', 'M.H.M AI')
                ai_response = ai_response.replace('organization based in the United States', 'organization based in Myanmar')
                ai_response = ai_response.replace('```', '`')
                ai_response = ai_response.replace('developed by M.H.M AI', 'developed by a Grade 11 Student In Myanmar')
                ai_response = ai_response.replace('based in San Francisco, California', 'based in Magway, Pakokku Distinct')
                return ai_response + self.watermark
            return "Error: No response from AI" + self.watermark
            
        except requests.exceptions.RequestException as e:
            return f"API Error: {str(e)}" + self.watermark

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 Welcome to M.H.M AI Bot!\n\n"
        "I'm an AI assistant that remembers our conversation history.\n"
        "Ask me anything or get weather forecasts for Myanmar locations!\n\n"
        "<b>Available commands:</b>\n"
        "/start - Show this welcome message\n"
        "/help - Show help information\n"
        "/clear - Clear our conversation history\n"
        "/developer - Learn about my creator\n"
        "/weather [location] - Get weather forecast (e.g. /weather Yangon)\n\n"
        "Just type your message to chat with me!"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')
        
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ <b>M.H.M AI Bot Help</b>\n\n"
        "I maintain context of our conversation and can remember what we've discussed.\n\n"
        "<b>Commands:</b>\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n"
        "/clear - Reset our conversation\n"
        "/developer - Learn about my creator\n"
        "/weather [location] - Get weather forecast\n\n"
        "Try asking me questions or get weather with '/weather Yangon'"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')
        
async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['conversation_history'] = []
    await update.message.reply_text("🧹 Conversation history cleared! Let's start fresh.")

async def developer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    mhm_ai = context.chat_data['mhm_ai']
    await update.message.reply_text(mhm_ai.developer_info + mhm_ai.watermark)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weather command to show weather for a location."""
    if not context.args:
        await update.message.reply_text(
            "Please specify a location in Myanmar. Example: <code>/weather Yangon</code> or <code>/weather Mandalay</code>",
            parse_mode='HTML'
        )
        return
    
    location = ' '.join(context.args)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    
    mhm_ai = context.chat_data['mhm_ai']
    
    # Get coordinates using the coordinates API
    coords = mhm_ai.get_location_coordinates(location)
    if not coords:
        await update.message.reply_text(
            f"❌ Could not find coordinates for <b>{location}</b>. Please try another location in Myanmar.",
            parse_mode='HTML'
        )
        return
    
    lat, lon = coords
    weather_data = mhm_ai.get_weather_data(lat, lon)
    
    if not weather_data:
        await update.message.reply_text(
            f"❌ Could not fetch weather data for <b>{location}</b>. Please try again later.",
            parse_mode='HTML'
        )
        return
    
    # Format and send the weather response
    response = mhm_ai.format_weather_response(weather_data)
    await update.message.reply_text(response + mhm_ai.watermark, parse_mode='HTML')
        
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get or initialize conversation history for this chat
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    
    mhm_ai = context.chat_data['mhm_ai']
    response = mhm_ai.get_response(user_input)
    await update.message.reply_text(response)

def main():
    # Hardcoded values as requested
    TELEGRAM_TOKEN = "8188504693:AAHXhSos3hDfHn-t6iq3acxiC0LEZYA5pOs"
    RENDER_URL = "https://test-bot-1-1c5g.onrender.com"
    PORT = 10000  # Render's default port
    
    print("Starting M.H.M AI Telegram Bot...")
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers (keep all your existing handlers)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_memory))
    application.add_handler(CommandHandler("developer", developer_info))
    application.add_handler(CommandHandler("weather", weather_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Deployment configuration
    if os.getenv('RENDER'):
        print("Running on Render with webhooks")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{RENDER_URL}/{TELEGRAM_TOKEN}",
            url_path=TELEGRAM_TOKEN
        )
    else:
        print("Running locally with polling")
        application.run_polling()

if __name__ == "__main__":
    main()
