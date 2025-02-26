import utils.writeToFile
import json
import utils.findTrain
import utils.ptvApi
import discord
from discord.ext import commands
from discord import app_commands
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
import requests
import asyncio
from playsound import playsound
import traceback

from utils import getConfig


config = getConfig.Config()

search = app_commands.Group(name='search', description='Search')

@bot.event
async def on_ready():
    bot.tree.add_command(search)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    playsound('misc/sounds/startup.mp3')


@search.command(name='train', description='Search for a train carriage on the network.')
async def _search(interaction: discord.Interaction, *, input_string: str):
    try:
        await interaction.response.defer(thinking=True)
        o = utils.findTrain.Train(input_string)
        image = await o.main(interaction)
    except Exception as e:
        print(type(e).__name__)
        print(str(e))
        print(traceback.format_exc())
    
@bot.command()
async def ptvapi(ctx: commands.Context, *, input_string: str):
    data = utils.ptvApi.get(input_string)
    jsontext = json.dumps(data, indent=4, sort_keys=True)
    print(jsontext)
    # utils.writeToFile.write('a.json', jsontext)
    await ctx.send('done')

@bot.command('deps')
async def _searchdepartures(ctx: commands.Context, *, input_string: str):
    def f():
        routesData = utils.ptvApi.get('/v3/routes?route_types=0')
        routesData = routesData['routes']
        stationId = None
        for route in routesData:
            stops = utils.ptvApi.get(f'/v3/stops/route/{route['route_id']}/route_type/0')
            for stop in stops['stops']:
                print(stop['stop_name'])
                if stop['stop_name'].lower() == f'{input_string.lower()} station':
                    stationId = stop['stop_id']
                    break
            if stationId != None:
                break
        
        departures = utils.ptvApi.get(f'/v3/departures/route_type/0/stop/{stationId}?expand=All&max_results=1000')
        
        for departure in list(departures['runs'].keys()):
            if departures['runs'][departure]['vehicle_descriptor'] != None:
                
                for d in departures['departures']:
                    if d['run_ref'] == departure:
                        print(d["scheduled_departure_utc"], d['run_ref'])
            
        # utils.writeToFile.write('a.json', json.dumps(departures, indent=4, sort_keys=True))
        # ['runs']
        # realdeps = []
        # for departure in list(departures.keys()):
        #     if departures[departure]['vehicle_descriptor'] != None:
        #         realdeps.append(departures[departure])
            
        
        # utils.writeToFile.write('a.json', json.dumps(realdeps, indent=4, sort_keys=True))
        
    f()
    await ctx.send('done!')
    
    
    


# Sync command
@bot.command()
@commands.guild_only()
async def sync(ctx: commands.Context):
    if ctx.author.id in [707866373602148363,780303451980038165]:
        syncmsg = await ctx.send(f"Syncing commands...")
        synced = await ctx.bot.tree.sync()
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        await syncmsg.edit(content=f"Synced {len(synced)} command{'s' if len(synced) > 1 else ''}.")
        return
        
bot.run(config.bot.token)

