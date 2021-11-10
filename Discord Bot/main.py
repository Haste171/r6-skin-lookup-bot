import discord, requests, json, os, time, base64, time
from discord.ext import commands
import numpy as np
from colorama import Fore, Style, init

init(convert=True)

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
client = commands.Bot(command_prefix='$', intents=intents)

print(f'''{Fore.BLUE}{Style.DIM}
Skin Checker                             
    ''')
time.sleep(2)

@client.event
async def on_ready():
    print(f'Launched: {client.user.name} // {client.user.id}\n')


def __init__(self, client):
    self.client = client
    self.headers = {
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'Ubi-AppId': '314d4fef-e568-454a-ae06-43e3bece12a6',
        'Ubi-SessionId': '7710bcb4-b22e-49d2-8d20-402fc457f117',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Ubi-RequestedPlatformType': 'uplay',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'GenomeId': '85c31714-0941-4876-a18d-2c7e9dce8d40',
        'Ubi-LocaleCode': "en-US"
    }
    self.token = self.login()
    self.space_id = "5172a557-50b5-4665-b7db-e3f2e8c5041d"
    self.session = requests.Session()


# EXTRACTING ITEM NAMES 
# ////////////////////////////////
def extract_item_names(self, item_names):
    items = {}
    for item_name in item_names:
        if item_name['type'] not in items:
            items[item_name['type']] = {}

        if item_name['itemId'] not in items[item_name['type']]:
            items[item_name['type']][item_name['itemId']] = item_name['nameId']
    return items


# GETTING THE USERS INVENTORY
# ////////////////////////////////////
def get_inventory(self, profile_id, load):
    final_ids = []; temp_list=[]
    r=self.session.get(f'https://public-ubiservices.ubi.com/v1/profiles/{profile_id}/inventory?spaceId={self.space_id}', headers=self.headers)

    for item in r.json()['items']:
        for num in range(len(load["items"])):
            if item['itemId'] in load["items"][num].values():
                final_ids.append(item['itemId'])

    splits = np.array_split(final_ids, round((len(final_ids)/50) + 1))
    for array in splits:
        r = self.session.get(f'https://public-ubiservices.ubi.com/v1/spaces/items?spaceId={self.space_id}&itemIds={",".join(str(i) for i in list(array))}', headers=self.headers)
        for x in r.json()['items']:
            temp_list.append(x)

    return self.extract_item_names(temp_list)


# REFORMATTING THE SKINS
# ////////////////////////////////
def reformat_skins(self, skins, format_list):
    formatted = {}
    for skin_type in skins:
        for skin_id in skins[skin_type]:
            for format_items in format_list["items"]:
                if skin_id == format_items["id"]:
                    if format_items["category"] not in formatted:
                        formatted.update({format_items["category"]: []})
                    formatted[format_items["category"]].append(format_items["name"])
    return formatted


# GRABBING AUTH KEY FROM LOGIN.TXT
# //////////////////////////////////
def login(self):
    self.headers["Authorization"] = "Basic " + base64.b64encode(bytes(open("data/login.txt", "r").readline(), "utf-8")).decode("utf-8")
    with requests.Session() as session:
        r = session.post("https://public-ubiservices.ubi.com/v3/profiles/sessions", json={"Content-Type":"application/json"}, headers=self.headers)
        if r.status_code == 200:
            if r.json()["ticket"]:
                token = "Ubi_v1 t=" + r.json()["ticket"]
                self.headers['Authorization'] = token
                return True
        return False


# MAIN FUNCTION
# //////////////////
def get_skins(self, username):
    r = self.session.get(f'https://public-ubiservices.ubi.com/v2/profiles?nameOnPlatform={username}&platformType=uplay', headers=self.headers)
    if "message" in r.json() and "Ticket is expired" in r.json()["message"]:
        self.login()

    profile = r.json()['profiles'][0]
    profile_name = profile['nameOnPlatform']
    profile_id = profile['profileId']

    format = json.load(open(os.path.dirname(__file__) + '\\..\\data\\format.json', 'r'))
    result = {"name": profile_name,"skins": None}

    skins = self.get_inventory(profile_id, format)
    result['skins'] = self.reformat_skins(skins, format)

    return result

@commands.command(aliases=['s'])
async def skins(self, ctx, name:str):
    print(f"{ctx.author} used the 'skins' command. Guild: {ctx.guild.id}")
    try:  
        embed=discord.Embed(color=0x000000)
        embed.set_author(name=name, url=f"https://r6.tracker.network/profile/pc/{name}")
        load = self.get_skins(name)

        for type in load["skins"]:
            embed.add_field(name=type, value='\n'.join(str(e) for e in load["skins"][type]))
        await ctx.send(embed=embed)
    except:
        embed3=discord.Embed(title='Error',color=0x000000, description='User doesn\'t exist or doesn\'t have R6')
        await ctx.send(embed=embed3)

client.run('ODk3ODk0NjAyMTg5NzI5Nzky.YWcTgw.zUWyUkOI-4ahfcURK100dDL1Q-M')
