import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread
from selenium import webdriver

import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

products = [
    {
        "name": "Big Into Energy Labubu",
        "image": "https://prod-eurasian-res.popmart.com/default/20250422_091913_954253____1_____1200x1200.jpg",
        "url": "https://www.popmart.com/hu/products/1991"
    },
    {
        "name": "Exciting Macaron",
        "image": "https://prod-eurasian-res.popmart.com/default/20231026_101051_200156__1200x1200.jpg",
        "url": "https://www.popmart.com/hu/products/527/THE-MONSTERS---Exciting-Macaron-Vinyl-Face-Blind-Box"
    },
    {
        "name": "Have a Seat",
        "image": "https://prod-eurasian-res.popmart.com/default/20240710_104422_660558____1_____1200x1200.jpg",
        "url": "https://www.popmart.com/hu/products/1194/THE-MONSTERS---Have-a-Seat-Vinyl-Plush-Blind-Box"
    },
    {
        "name": "Coca-Cola Labubu",
        "image": "https://prod-eurasian-res.popmart.com/default/20241217_163807_637795____1_____1200x1200.jpg",
        "url": "https://www.popmart.com/hu/products/1625/THE-MONSTERS-COCA-COLA-SERIES-Vinyl-Face-Blind-Box"
    }
]

# Emlékeztető a termék állapotához
product_status = {product['url']: False for product in products}

@bot.event
async def on_ready():
    print(f'Bejelentkezve mint: {bot.user.name}')
    labubu_checker.start()

@tasks.loop(seconds=60)
async def labubu_checker():
    channel = bot.get_channel(1372233638355402856)  # IDE a saját csatorna ID-d!
    for product in products:
        available = check_labubu_stock(product["url"])
        if available and not product_status[product['url']]:
            embed = discord.Embed(
                title=f"{product['name']} elérhető!",
                description=f"[Nézd meg itt]({product['url']})",
                color=0xffcc00
            )
            embed.set_image(url=product['image'])
            await channel.send("@everyone", embed=embed)
            print(f"{product['name']} ELÉRHETŐ! Üzenet elküldve.")
            product_status[product['url']] = True
        elif not available and product_status[product['url']]:
            print(f"{product['name']} kifogyott.")
            product_status[product['url']] = False
        else:
            print(f"{product['name']} változatlan ({'elérhető' if product_status[product['url']] else 'nem elérhető'}).")

def check_labubu_stock_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)

        driver.get(url)

        # Próbálja megkeresni az "ADD TO CART" vagy "BUY NOW" gombot
        if driver.find_elements(By.XPATH, "//div[contains(text(), 'ADD TO CART')]") or driver.find_elements(By.XPATH, "//div[contains(text(), 'BUY NOW')]"):
            print(f"{url} - KÉSZLETEN (Selenium észlelte a gombot)")
            driver.quit()
            return True
        else:
            print(f"{url} - NEM elérhető (Selenium szerint nincs gomb)")
            driver.quit()
            return False
# Parancs: !ping -> Pong!
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Parancs: !status -> Összegzi az elérhetőségeket
@bot.command()
async def status(ctx):
    status_message = ""
    for product in products:
        status_message += f"**{product['name']}**: {'Elérhető ✅' if product_status[product['url']] else 'Nem elérhető ❌'}\n"
    await ctx.send(status_message)

# Parancs: !help -> Lista a parancsokról
@bot.command()
async def helpme(ctx):
    help_text = """
    **Elérhető parancsok:**
    `!ping` → Válasz: Pong!
    `!status` → Kiírja az összes figyelt Labubu státuszát.
    `!helpme` → Ez a parancs.
    """
    await ctx.send(help_text)
# Keep-alive trükk
app = Flask('')

@app.route('/')
def home():
    return "Bot él!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
keep_alive()
bot.run(TOKEN)

