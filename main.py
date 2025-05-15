import os
import discord
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

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
product_status = {product["url"]: False for product in products}

def check_labubu_stock_selenium(url):
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        if driver.find_elements(By.XPATH, "//div[contains(text(), 'ADD TO CART')]") or \
           driver.find_elements(By.XPATH, "//div[contains(text(), 'BUY NOW')]"):
            print(f"[INFO] {url} - KÉSZLETEN (Selenium észlelte a gombot)")
            driver.quit()
            return True
        else:
            print(f"[INFO] {url} - NEM elérhető (Selenium szerint nincs gomb)")
            driver.quit()
            return False
    except Exception as e:
        print(f"[HIBA] Selenium hiba: {e}")
        return False

@tasks.loop(minutes=1)
async def labubu_checker():
    try:
        print("[INFO] Labubu stock check indul...")

        for product in products:
            available = check_labubu_stock_selenium(product['url'])

            if available and not product_status[product['url']]:
                print(f"[INFO] {product['name']} ELÉRHETŐ! Üzenet elküldve.")
                channel = bot.get_channel(YOUR_CHANNEL_ID)  # ← CSATORNA ID IDE
                if channel:
                    await channel.send(f"🚨 **{product['name']} ELÉRHETŐ!** {product['url']}")
                product_status[product['url']] = True

            elif not available and product_status[product['url']]:
                print(f"[INFO] {product['name']} kifogyott.")
                product_status[product['url']] = False

            else:
                print(f"[INFO] {product['name']} állapot változatlan.")

    except Exception as e:
        print(f"[HIBA] labubu_checker loop hibája: {e}")

@bot.event
async def on_ready():
    print(f"[INFO] Bejelentkezve: {bot.user}")
    if not labubu_checker.is_running():
        labubu_checker.start()

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
    
@bot.command()
async def status(ctx):
    status_message = ""
    for product in products:
        status_emoji = "✅ ELÉRHETŐ" if product_status[product['url']] else "❌ NEM elérhető"
        status_message += f"**{product['name']}** → {status_emoji}\n"
    await ctx.send(status_message)

@bot.command()
async def helpme(ctx):
    help_text = """
    **Elérhető parancsok:**
    `!ping` → Ellenőrzi, hogy a bot él-e.
    `!status` → Kiírja az összes figyelt termék aktuális státuszát.
    `!helpme` → Ez a parancs (parancslista).
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
