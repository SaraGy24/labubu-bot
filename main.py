import discord
from discord.ext import commands
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask
from threading import Thread
from datetime import datetime
import asyncio
import time
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1372233638355402856

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

products = [
    {"name": "Labubu Macaron", "url": "https://popmart.eu/products/the-monsters-exciting-macaron-vinyl-face-blind-box"},
    {"name": "Labubu Cola", "url": "https://popmart.eu/products/the-monsters-coca-cola-series-vinyl-face-blind-box"},
    {"name": "Labubu Bird", "url": "https://popmart.eu/products/the-monsters-birdy-vinyl-face-blind-box"},
    {"name": "Labubu Hunter", "url": "https://popmart.eu/products/the-monsters-hunter-vinyl-face-blind-box"},
]

product_status = {product["url"]: False for product in products}
last_check_time = None

def check_labubu_stock_selenium(driver, url):
    try:
        driver.get(url)
        # Várunk max 15 másodpercet, amíg megjelenik a gomb
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'index_btn__w5nKF')]"))
        )
        # Ellenőrizzük a gombokat
        buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'index_btn__w5nKF')]")
        for button in buttons:
            text = button.text.strip().lower()
            if "buy now" in text:
                print(f"{url} - KÉSZLETEN (gomb szöveg: '{text}').")
                return True
        print(f"{url} - NEM található BUY NOW gomb, vagy más szöveg van.")
        return False

    except Exception as e:
        print(f"Hiba a Selenium ellenőrzés során: {e}")
        return False

async def send_stock_message(product):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"🚨 **{product['name']} ELÉRHETŐ!** {product['url']}")

def labubu_checker_loop():
    global last_check_time
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    while True:
        last_check_time = datetime.now()
        print(f"[{last_check_time.strftime('%Y-%m-%d %H:%M:%S')}] ▶ Labubu stock ellenőrzés indul...")

        for product in products:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ➡ Ellenőrzés: {product['name']} - {product['url']}")
            try:
                result = check_labubu_stock_selenium(driver, product["url"])
                if result and not product_status[product["url"]]:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {product['name']} ELÉRHETŐ!")
                    asyncio.run_coroutine_threadsafe(send_stock_message(product), bot.loop)
                    product_status[product["url"]] = True
                elif not result and product_status[product["url"]]:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ {product['name']} kifogyott.")
                    product_status[product["url"]] = False
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ➡ {product['name']} változatlan.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠ Hiba a {product['name']} ellenőrzésekor: {e}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔁 Következő ellenőrzés 60 másodperc múlva...")
        time.sleep(60)

    driver.quit()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def status(ctx):
    status_message = f"🕒 Utolsó ellenőrzés: {last_check_time.strftime('%Y-%m-%d %H:%M:%S') if last_check_time else 'Még nem volt ellenőrzés'}\n\n"
    for product in products:
        status_message += f"**{product['name']}**: {'Elérhető ✅' if product_status[product['url']] else 'Nem elérhető ❌'}\n"
    await ctx.send(status_message)

@bot.command()
async def helpme(ctx):
    help_text = """
**Elérhető parancsok:**
`!ping` → Pong!
`!status` → Kiírja az összes figyelt termék státuszát.
`!helpme` → Ez a parancs.
"""
    await ctx.send(help_text)

app = Flask('')

@app.route('/')
def home():
    return "Bot él!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

@bot.event
async def on_ready():
    print(f"🤖 Bejelentkezve mint {bot.user}")
    Thread(target=labubu_checker_loop, daemon=True).start()

keep_alive()
bot.run(TOKEN)

