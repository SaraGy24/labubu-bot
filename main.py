from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

chrome_options.binary_location = "/usr/bin/chromium-browser"

# ÚJ: Service objektum létrehozása és átadása helyesen
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

import os
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = 123456789012345678  # Cseréld ki a saját csatorna ID-re

PRODUCTS = [
    {"name": "Labubu Macaron", "url": "https://popmart.eu/products/the-monsters-exciting-macaron-vinyl-face-blind-box"},
    {"name": "Labubu Cola", "url": "https://popmart.eu/products/the-monsters-coca-cola-series-vinyl-face-blind-box"},
    {"name": "Labubu BIE", "url": "https://www.popmart.com/hu/products/1991"},
    {"name": "Labubu Hunter", "url": "https://popmart.eu/products/the-monsters-hunter-vinyl-face-blind-box"},
]

GOMB_CSS = ".index_btn__w5nKF"
FRISSÍTÉS_IDŐ = 20

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

statuszok = {product['url']: False for product in PRODUCTS}

@bot.event
async def on_ready():
    print(f"✅ Bejelentkezve mint {bot.user}")
    popmart_figyelo.start()

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def helpme(ctx):
    helpme_text = (
        "**Elérhető parancsok:**\n"
        "`!ping` → Válaszol Pong!\n"
        "`!stock` → Összes termék aktuális állapota időbélyeggel.\n"
    )
    await ctx.send(helpme_text)

@bot.command()
async def stock(ctx):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stock_list = f"📊 **Termék státuszok ({now}):**\n\n"
    for product in PRODUCTS:
        state = "✅ Raktáron" if statuszok[product['url']] else "❌ Nincs készleten"
        stock_list += f"**{product['name']}** → {state}\n{product['url']}\n\n"
    await ctx.send(stock_list)

@tasks.loop(seconds=FRISSÍTÉS_IDŐ)
async def popmart_figyelo():
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    for product in PRODUCTS:
        url = product['url']
        name = product['name']
        try:
            driver.get(url)
            await asyncio.sleep(2)

            gomb = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, GOMB_CSS))
            )

            if not statuszok[url]:
                try:
                    kep_elem = driver.find_element(By.CSS_SELECTOR, ".swiper-slide-active img")
                    kep_url = kep_elem.get_attribute("src")
                except:
                    kep_url = None

                embed = discord.Embed(title=f"🎯 RAKTÁRON: {name}", url=url, description="Elérhető a Pop Mart webshopban!", color=discord.Color.green())
                if kep_url:
                    embed.set_image(url=kep_url)
                embed.set_footer(text="Pop Mart figyelő bot")

                await channel.send("@everyone", embed=embed)
                print(f"✅ Elérhető lett és pingelve: {name}")
                
                statuszok[url] = True

        except:
            if statuszok[url]:
                print(f"❌ Már nem elérhető: {name}")
            statuszok[url] = False

    driver.quit()

bot.run(TOKEN)
