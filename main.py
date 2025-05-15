import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from flask import Flask
from threading import Thread

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

def check_labubu_stock(url):
    try:
        response = requests.get(url)
        print(f"HTTP státusz: {response.status_code} - {url}")
        if response.status_code != 200:
            return False
       if "ADD TO CART" in response.text.upper() or "BUY NOW" in response.text.upper():
            print(f"{url} - KÉSZLETEN (Add to Cart gomb megtalálva).")
            return True
        else:
            print(f"{url} - NEM elérhető (nincs Add to Cart).")
            return False
    except Exception as e:
        print(f"HIBA a lekérdezésnél: {e}")
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

