import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import time
from datetime import datetime


TOKEN = os.getenv("DISCORD_TOKEN")
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

def check_labubu_stock_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        if driver.find_elements(By.XPATH, "//div[contains(text(), 'ADD TO CART')]") or driver.find_elements(By.XPATH, "//div[contains(text(), 'BUY NOW')]"):
            print(f"{url} - KÉSZLETEN (Selenium észlelte a gombot)")
            driver.quit()
            return True
        else:
            print(f"{url} - NEM elérhető (Selenium szerint nincs gomb)")
            driver.quit()
            return False
    except Exception as e:
        print(f"Hiba a Selenium ellenőrzés során: {e}")
        return False
         
# (a meglévő kódodban legyen globálisan ez:)
last_check_time = None  # utolsó ellenőrzés ideje globálisan

def labubu_checker_loop():
    global last_check_time
    while True:
        last_check_time = datetime.now()
        print(f"[{last_check_time.strftime('%Y-%m-%d %H:%M:%S')}] ▶ Labubu stock ellenőrzés indul...")

        for product in products:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ➡ Ellenőrzés: {product['name']} - {product['url']}")
            try:
                result = check_labubu_stock_selenium(product["url"])
                if result and not product_status[product["url"]]:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ {product['name']} ELÉRHETŐ! Üzenet elküldve.")
                    product_status[product["url"]] = True
                elif not result and product_status[product["url"]]:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ {product['name']} kifogyott.")
                    product_status[product["url"]] = False
                else:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ➡ {product['name']} állapota nem változott.")
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠ Hiba a {product['name']} ellenőrzésekor: {e}")

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔁 Következő ellenőrzés 60 másodperc múlva...")
        time.sleep(60)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def status(ctx):
    status_message = ""
    for product in products:
        status_message += f"**{product['name']}**: {'Elérhető ✅' if product_status[product['url']] else 'Nem elérhető ❌'}\n"
    await ctx.send(status_message)

@bot.command()
async def helpme(ctx):
    help_text = """
**Elérhető parancsok:**
`!ping` → Válasz: Pong!
`!status` → Kiírja az összes figyelt Labubu státuszát.
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
    t = Thread(target=run_flask)
    t.start()

keep_alive()
stock_thread = Thread(target=labubu_checker_loop)
stock_thread.start()

bot.run(TOKEN)


