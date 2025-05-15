import discord
from discord.ext import commands, tasks
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from flask import Flask
from threading import Thread
import os
import asyncio

# Discord token beolvasása környezeti változóból
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents konfigurálása
intents = discord.Intents.default()
intents.message_content = True

# Discord bot inicializálása
bot = commands.Bot(command_prefix="!", intents=intents)

# Terméklista
products = [
     {"name": "Labubu Macaron", "url": "https://popmart.eu/products/the-monsters-exciting-macaron-vinyl-face-blind-box"},
    {"name": "Labubu Cola", "url": "https://popmart.eu/products/the-monsters-coca-cola-series-vinyl-face-blind-box"},
    {"name": "Labubu Bird", "url": "https://popmart.eu/products/the-monsters-birdy-vinyl-face-blind-box"},
    {"name": "Labubu Hunter", "url": "https://popmart.eu/products/the-monsters-hunter-vinyl-face-blind-box"},
]

# Státusz tároló
product_status = {product["url"]: False for product in products}


# Selenium stock checker (blokkoló, de safe módon hívjuk majd executorban)
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
        print(f"HIBA a Selenium lekérdezésnél: {e}")
        return False


# Aszinkron háttér task Selenium futtatással executorban
@tasks.loop(seconds=120)
async def labubu_checker():
    loop = asyncio.get_running_loop()
    for product in products:
        is_available = await loop.run_in_executor(None, check_labubu_stock_selenium, product['url'])
        if is_available and not product_status[product['url']]:
            print(f"{product['name']} ELÉRHETŐ! Üzenet elküldve.")
            product_status[product['url']] = True
        elif not is_available and product_status[product['url']]:
            print(f"{product['name']} kifogyott.")
            product_status[product['url']] = False
        else:
            print(f"{product['name']} változatlan ({'elérhető' if product_status[product['url']] else 'nem elérhető'}).")


# Discord parancsok
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


# Webserver, hogy Render életben tartsa a botot
app = Flask('')

@app.route('/')
def home():
    return "Labubu bot él!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# Indítás
keep_alive()
labubu_checker.start()
bot.run(TOKEN)

