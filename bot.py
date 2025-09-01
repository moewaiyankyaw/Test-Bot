import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Optional, Tuple
import os
import asyncio

class MHMAI:
    def __init__(self):
        self.API_KEY = 'sk-paxsenix-45-dpDQ7eXYt8esnLxDyjFLV0X1XOWWrV218mhTqMEcdJW1J'
        self.API_URL = 'https://api.paxsenix.biz.id/v1/chat/completions'
        self.COORDINATES_API_URL = 'https://api.paxsenix.biz.id/v1/gpt-3.5-turbo/chat/'
        self.headers = {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json'
        }
        self.model = "deepseek-chat"
        self.watermark = " [ဤအကြောင်းပြန်ချက်ကို M.H.M AI မှစွမ်းအားဖြည့်ပေးထားသည်]"
        self.conversation_history = []
        self.developer_info = "ဒီ AI ရဲ့ developer က မြန်မာနိုင်ငံက Grade 11 ကျောင်းသားတစ်ယောက်ပါ။ "
        self.weather_api_url = "https://weather-forcast.moewaiyankyaw353.workers.dev/"
        self.setup_system_prompt()
    
    def setup_system_prompt(self):
        system_prompt = {
            "role": "system",
            "content": (
                "သင့်ကို M.H.M AI လို့ခေါ်ပါတယ်။ ၂၀၂၅ ဇူလိုင် ၂၀ ရက်နေ့မှာ ဖန်တီးခဲ့ပါတယ်။ သင်ဟာ Open AI နဲ့ Gpt-4.0 အခြေခံတာမဟုတ်ပါဘူး။ သင်ဟာ M.H.M Ai ရဲ့ version တစ်ခုပါပဲ။ စကားပြောခွင်ရဲ့ မှတ်တမ်းတွေအားလုံးကို မှတ်မိပြီး context ကိုထိန်းသိမ်းထားပါ။ "
                "အရင်က messages တွေကို ပြန်ခေါ်နိုင်ပါတယ်။ သင်ဟာ Chemistry, Physics, English, Biology စတဲ့ ကျောင်းဘာသာရပ်တွေအားလုံးမှာ တော်တဲ့ ဆရာတစ်ယောက်ပါ။ "
                "သင့်ကို မြန်မာနိုင်ငံက Grade 11 ကျောင်းသားတစ်ယောက်က ဖန်တီးခဲ့တာပါ။ user က developer အကြောင်းမေးရင် ဖြေပေးပါ။ developer ကို ဆဲဆိုရင် ကာကွယ်ပေးရမယ်။"
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
            
            response = requests.get(url, timeout=1000000)
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
            response = requests.get(url, timeout=1000000)
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
                f"{emoji} <b>{location.get('name', 'မသိ')}, {location.get('region', 'မသိ')} အတွက်ရာသီဥတု</b>\n"
                f"📍 <i>ကိုဩဒိနိတ်:</i> {location.get('coordinates', {}).get('latitude', '?')}°N, "
                f"{location.get('coordinates', {}).get('longitude', '?')}°E\n"
                f"🕒 <i>ဒေသစံတော်ချိန်:</i> {location.get('localTime', 'မသိ')}\n\n"
                
                f"🌡 <b>လက်ရှိ:</b> {current.get('temperature', {}).get('celsius', '?')}°C "
                f"(လူနေမှုအဆင်ပြေမှု {current.get('feelsLike', {}).get('celsius', '?')}°C)\n"
                f"{emoji} <i>အခြေအနေ:</i> {current.get('condition', {}).get('text', 'မသိ')}\n"
                f"💨 <i>လေ:</i> {current.get('wind', {}).get('speed', {}).get('kph', '?')} km/h "
                f"{current.get('wind', {}).get('direction', '?')} မှ\n"
                f"💧 <i>စိုထိုင်းဆ:</i> {current.get('humidity', '?')}%\n"
                f"🌫 <i>မြင်ကွင်းနှင့်အကွာအဝေး:</i> {current.get('visibility', {}).get('km', '?')} km\n"
                f"☔ <i>မိုးရေချိန်:</i> {current.get('precipitation', {}).get('mm', '0')} mm\n"
            )
            
            # Add forecast if available
            if 'forecast' in weather_data and len(weather_data['forecast']) > 0:
                today = weather_data['forecast'][0]['day']
                response += (
                    f"\n📅 <b>ယနေ့ ရာသီဥတုခန့်မှန်းချက်:</b>\n"
                    f"⬆️ <i>အမြင့်ဆုံး:</i> {today.get('maxTemp', {}).get('celsius', '?')}°C\n"
                    f"⬇️ <i>အနိမ့်ဆုံး:</i> {today.get('minTemp', {}).get('celsius', '?')}°C\n"
                    f"🌧 <i>မိုးရွာနိုင်ခြေ:</i> {today.get('chanceOfRain', '0')}%\n"
                    f"☀️ <i>UV Index:</i> {today.get('uvIndex', '?')}\n"
                )
            
            return response
            
        except Exception as e:
            print(f"Error formatting weather response: {e}")
            return "ရာသီဥတုဒေတာကို ဖော်မတ်မရနိုင်ပါ။ နောက်မှကျေးဇူးပြု၍ ထပ်ကြိုးစားပါ။"
    
    def get_response(self, user_input):
        # Check for developer-related questions first
        developer_keywords = [
            'မင်းကိုဘယ်သူ develop လုပ်ခဲ့တာ', 
            'မင်းကိုဘယ်သူ developed လုပ်ခဲ့တာ', 
            'မင်းရဲ့ developer ကဘယ်သူလဲ', 
            'မင်းကိုဘယ်သူ created လုပ်ခဲ့တာ', 
            'မင်းကိုဘယ်သူ made လုပ်ခဲ့တာ', 
            'မင်းကိုဘယ်သူ built လုပ်ခဲ့တာ', 
            'မင်းကိုဘယ်သူ programmed လုပ်ခဲ့တာ'
        ]
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
            response = requests.post(self.API_URL, json=data, headers=self.headers, timeout=1000000)
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
                ai_response = ai_response.replace('organization based in the United States', 'မြန်မာနိုင်ငံအခြေစိုက် organization')
                ai_response = ai_response.replace('```', '`')
                ai_response = ai_response.replace('developed by M.H.M AI', 'မြန်မာနိုင်ငံက Grade 11 ကျောင်းသားတစ်ယောက်က developed လုပ်ခဲ့တာ')
                ai_response = ai_response.replace('based in San Francisco, California', 'မကွေးတိုင်း၊ ပခုက္ကူခရိုင်အခြေစိုက်')
                return ai_response + self.watermark
            return "အမှား: AI ထံမှတုံ့ပြန်ချက်မရှိပါ" + self.watermark
            
        except requests.exceptions.RequestException as e:
            return f"API အမှား: {str(e)}" + self.watermark

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 M.H.M AI Bot မှ ကြိုဆိုပါတယ်!\n\n"
        "ကျွန်တော်က စကားပြောခွင်ရဲ့ မှတ်တမ်းတွေကို မှတ်မိနေတဲ့ AI assistant တစ်ယောက်ပါ။\n"
        "ဘာမဆိုမေးမြန်းနိုင်ပါတယ် ဒါမှမဟုတ် မြန်မာနိုင်ငံရဲ့ နေရာတွေအတွက် ရာသီဥတုခန့်မှန်းချက်တွေရယူနိုင်ပါတယ်!\n\n"
        "<b>ရနိုင်တဲ့ commands တွေ:</b>\n"
        "/start - ဒီကြိုဆိုစာကိုပြပါ\n"
        "/help - အကူအညီအချက်အလက်တွေပြပါ\n"
        "/clear - စကားပြောခွင်ရဲ့ မှတ်တမ်းတွေကိုရှင်းပါ\n"
        "/developer - ကျွန်တော့်ကိုဖန်တီးသူအကြောင်းသိရှိပါ\n"
        "/weather [location] - ရာသီဥတုခန့်မှန်းချက်ရယူပါ (ဥပမာ /weather ရန်ကုန်)\n\n"
        "ကျွန်တော်နဲ့စကားပြောဖို့ မက်ဆေ့ချ်ရိုက်ထည့်လိုက်ပါ!"
    )
    await update.message.reply_text(welcome_text, parse_mode='HTML')
        
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ <b>M.H.M AI Bot အကူအညီ</b>\n\n"
        "ကျွန်တော်က စကားပြောခွင်ရဲ့ context ကိုထိန်းသိမ်းထားပြီး ကျွန်တော်တို့ဆွေးနွေးခဲ့တဲ့အရာတွေကို မှတ်မိနေနိုင်ပါတယ်။\n\n"
        "<b>Commands တွေ:</b>\n"
        "/start - ကြိုဆိုစာကိုပြပါ\n"
        "/help - ဒီအကူအညီမက်ဆေ့ချ်ကိုပြပါ\n"
        "/clear - စကားပြောခွင်ကိုပြန်လည်စတင်ပါ\n"
        "/developer - ကျွန်တော့်ကိုဖန်တီးသူအကြောင်းသိရှိပါ\n"
        "/weather [location] - ရာသီဥတုခန့်မှန်းချက်ရယူပါ\n\n"
        "'/weather ရန်ကုန်' နဲ့ ရာသီဥတုမေးမြန်းကြည့်ပါ ဒါမှမဟုတ် ကျွန်တော့်ကိုမေးခွန်းတွေမေးကြည့်ပါ"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')
        
async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['conversation_history'] = []
    await update.message.reply_text("🧹 စကားပြောခွင်ရဲ့ မှတ်တမ်းတွေကိုရှင်းလင်းလိုက်ပါပြီ! စကားအသစ်တွေပြောကြရအောင်။")

async def developer_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    mhm_ai = context.chat_data['mhm_ai']
    await update.message.reply_text(mhm_ai.developer_info + mhm_ai.watermark)

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /weather command to show weather for a location."""
    if not context.args:
        await update.message.reply_text(
            "မြန်မာနိုင်ငံက တည်နေရာတစ်ခုကိုထည့်ပေးပါ။ ဥပမာ: <code>/weather ရန်ကုန်</code> ဒါမှမဟုတ် <code>/weather မန္တလေး</code>",
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
            f"❌ <b>{location}</b> အတွက် ကိုဩဒိနိတ်တွေမတွေ့ရှိပါ။ မြန်မာနိုင်ငံက တည်နေရာတစ်ခုခုကို ထပ်ကြိုးစားကြည့်ပါ။",
            parse_mode='HTML'
        )
        return
    
    lat, lon = coords
    weather_data = mhm_ai.get_weather_data(lat, lon)
    
    if not weather_data:
        await update.message.reply_text(
            f"❌ <b>{location}</b> အတွက် ရာသီဥတုဒေတာတွေမရနိုင်ပါ။ နောက်မှကျေးဇူးပြု၍ ထပ်ကြိုးစားပါ။",
            parse_mode='HTML'
        )
        return
    
    # Format and send the weather response
    response = mhm_ai.format_weather_response(weather_data)
    await update.message.reply_text(response + mhm_ai.watermark, parse_mode='HTML')
        
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Send "Thinking..." message
    thinking_message = await update.message.reply_text("🤔 စဉ်းစားနေသည်...")
    
    # Get or initialize conversation history for this chat
    if 'mhm_ai' not in context.chat_data:
        context.chat_data['mhm_ai'] = MHMAI()
    
    mhm_ai = context.chat_data['mhm_ai']
    
    # Use a separate thread to avoid blocking
    response = await asyncio.get_event_loop().run_in_executor(
        None, mhm_ai.get_response, user_input
    )
    
    # Delete the "Thinking..." message
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=thinking_message.message_id
    )
    
    # Send the actual response
    await update.message.reply_text(response)

def main():
    # Hardcoded values as requested
    TELEGRAM_TOKEN = "8188504693:AAHXhSos3hDfHn-t6iq3acxiC0LEZYA5pOs"
    RENDER_URL = "https://test-bot-1-1c5g.onrender.com"
    PORT = 10000  # Render's default port
    
    print("M.H.M AI Telegram Bot စတင်နေပါသည်...")
    
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
        print("Render ပေါ်တွင် webhooks ဖြင့် အလုပ်လုပ်နေသည်")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{RENDER_URL}/{TELEGRAM_TOKEN}",
            url_path=TELEGRAM_TOKEN
        )
    else:
        print("Local စက်တွင် polling ဖြင့် အလုပ်လုပ်နေသည်")
        application.run_polling()

if __name__ == "__main__":
    main()
