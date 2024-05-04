import aiohttp, asyncio
from bs4 import BeautifulSoup as htmlparser
from utils.log import Logger
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

cookie_file = 'cookie.txt'

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=',', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

class RobloxAPI:
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file

    async def get_user_experiences(self, uid: int):
        """
        Get an user exeprinces.
        """
        url = f'https://games.roblox.com/v2/users/{uid}/games?accessFilter=2&limit=10&sortOrder=Asc'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                games = data['data']
                filtered_games = [game for game in games if game['creator']['id'] == uid]
                return filtered_games[0] if filtered_games else None

    async def get_csrf_token(self):
        """
        Get the CSRF token from the Roblox website.
        """
        url = "https://www.roblox.com/home"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            "Cookie": f".ROBLOSECURITY={self.get_cookie()}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                html = await response.text()
                soup = htmlparser(html, "html.parser")
                csrf_tag = soup.find("meta", {"name": "csrf-token"})
                csrf_token = csrf_tag["data-token"]
                if csrf_token:
                    return csrf_token
                else:
                    return False

    async def CreateGamepass(self, game_id: int, name: str, description: str):
        url = "https://apis.roblox.com/game-passes/v1/game-passes"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.get_cookie()}",
            "x-csrf-token": await self.get_csrf_token() 
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=aiohttp.FormData({"Name": name, "Description": description, "UniverseId": str(game_id)})) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    Logger.log(f"{response.status} {await response.json*()}", "ERROR")
                    return False

    async def SetGamepassPrice(self, gamepass_id: int, price: int):
        url = f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass_id}/details"
        headers = {
            "Cookie": f".ROBLOSECURITY={self.get_cookie()}",
            "x-csrf-token": await self.get_csrf_token() 
        }
        data = {
            "IsForSale": "true",
            "Price": str(price)
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=aiohttp.FormData(data)) as response:
                if response.status == 200:
                    return True
                else:
                    return False

    async def user_auth(self):
        url = 'https://users.roblox.com/v1/users/authenticated'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/jxl,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://devforum.roblox.com/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Connection': 'keep-alive',
            'Cookie': f'.ROBLOSECURITY={self.get_cookie()}',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'TE': 'trailers'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    data = await response.json()
                    cookie = self.get_cookie()
                    Logger.log(f"{response.status} {data} | invalid with cookie: {cookie}", "ERROR")
                data = await response.json()
                return data

    def get_cookie(self):
        with open(self.cookie_file, 'r') as file:
            cookie = file.readline().strip()
        return cookie

    async def main(self):
        auth = await self.user_auth()
        uid = auth['id']
        if uid:
            data = await self.get_user_experiences(uid)
            # Logger.log(data, 'INFO')
            if data:
                game_id = data['id']
                gamepass = await RobloxAPI.CreateGamepass(game_id=game_id, name="ooftest", description="Gyat")
                if gamepass:
                    gamepass_id = gamepass['gamePassId']
                    Logger.log(f"Created gamepass with id {gamepass_id}", 'INFO')
                    setPrice = await RobloxAPI.SetGamepassPrice(gamepass_id=gamepass_id, price=100)
                    if setPrice:
                        Logger.log(f"Set price for gamepass {gamepass_id} to 100", 'INFO')
            else:
                Logger.log('No experiences found.', 'ERROR')
        else:
            Logger.log('Improper token passed.', 'ERROR')


# if __name__ == '__main__':
#     api = RobloxAPI('cookie.txt')
#     asyncio.run(api.main())

@bot.command()
async def setcookie(ctx, cookie: str):
    """
    Sets the cookie for the bot to use.
    """
    try:
        cookie_file = 'cookie.txt'
        with open(cookie_file, 'w') as file:
            file.write(cookie)
        await ctx.send('Cookie set successfully.')
    except Exception as e:
        await ctx.send(f'Error setting cookie: {str(e)}')

@bot.command()
async def create(ctx, price: int, name: str):
    """
    Create a gamepass with the given price and name.
    """
    message = await ctx.reply('> Initializing...')
    auth = await RobloxAPI('cookie.txt').user_auth()
    uid = auth['id']
    if uid:
        data = await RobloxAPI('cookie.txt').get_user_experiences(uid)
        # Logger.log(data, 'INFO')
        if data:
            game_id = data['id']
            gamepass = await RobloxAPI('cookie.txt').CreateGamepass(game_id=game_id, name=name, description="heh...")
            if gamepass:
                gamepass_id = gamepass['gamePassId']
                await message.edit(content=f'> Created gamepass with name {name} and id {gamepass_id}')
                setPrice = await RobloxAPI('cookie.txt').SetGamepassPrice(gamepass_id=gamepass_id, price=price)
                if setPrice:
                    await message.edit(content=f'> Set price for gamepass to {price}')
                    await message.edit(content=f'> https://www.roblox.com/game-pass/{gamepass_id}')
        else:
            await message.edit(content='> No experiences found for user.')
    else:
        await message.edit(content='> Improper cookie passed')


load_dotenv()

bot.run(os.getenv('TOKEN'))
