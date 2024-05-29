from discord.ext import commands, tasks
from discord import app_commands
import discord
import json
import requests
import re
import asyncio
import threading
import queue
import datetime
import time
import csv
import random
import pandas as pd
from typing import Literal, Optional
import typing
import enum
from re import A

from utils.search import *
from utils.colors import *
from utils.stats import *
from utils.pageScraper import *
from utils.trainImage import *
from utils.checktype import *
from utils.montagueAPI import *
from utils.map.map import *
from utils.game.lb import *
from utils.trainlogger.main import *
from utils.trainset import *
from utils.trainlogger.stats import *
from utils.trainlogger.ids import *


file = open('utils/stations.txt','r')
all_stations_list = []
metro_stations_list = []
for line in file:
    line = line.strip()
    all_stations_list.append(line)
    if len(metro_stations_list) != 221:
        metro_stations_list.append(line)
file.close()

# reading config file

config = dotenv_values(".env")

BOT_TOKEN = config['BOT_TOKEN']
STARTUP_CHANNEL_ID = int(config['STARTUP_CHANNEL_ID']) # channel id to send the startup message
RARE_SERVICE_CHANNEL_ID = int(config['RARE_SERVICE_CHANNEL_ID'])
COMMAND_PREFIX = config['COMMAND_PREFIX']
USER_ID = config['USER_ID']
RARE_SERVICE_SEARCHER = config['RARE_SERVICE_SEARCHER']

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())
log_channel = bot.get_channel(STARTUP_CHANNEL_ID)

channel_game_status = {} #thing to store what channels are running the guessing game

try:    
    os.mkdir('utils/game/scores')
except FileExistsError:
    pass    

def convert_to_unix_time(date: datetime.datetime) -> str:
    # Get the end date
    end_date = date

    # Get a tuple of the date attributes
    date_tuple = (end_date.year, end_date.month, end_date.day, end_date.hour, end_date.minute, end_date.second)

    # Convert to unix time
    return f'<t:{int(time.mktime(datetime.datetime(*date_tuple).timetuple()))}:R>'

async def all_station_autocompletion(
    interaction: discord.Interaction,
    current: str
) -> typing.List[app_commands.Choice[str]]:
    stations = all_stations_list.copy()
    return [
        app_commands.Choice(name=station, value=station)
        for station in stations if current.lower() in station.lower()
    ]
async def metro_station_autocompletion(
    interaction: discord.Interaction,
    current: str
) -> typing.List[app_commands.Choice[str]]:
    stations = metro_stations_list.copy()
    return [
        app_commands.Choice(name=station, value=station)
        for station in stations if current.lower() in station.lower()
    ]

lines_dictionary = {
    'Alamein': [['Richmond', 'East Richmond', 'Burnley', 'Hawthorn', 'Glenferrie', 'Auburn', 'Camberwell', 'Riversdale', 'Willison', 'Hartwell', 'Burwood', 'Ashburton', 'Alamein'],0x01518a],
    'Belgrave': [['Richmond', 'East Richmond', 'Burnley', 'Hawthorn', 'Glenferrie', 'Auburn', 'Camberwell', 'East Camberwell', 'Canterbury', 'Chatham', 'Union', 'Box Hill', 'Laburnum', 'Blackburn', 'Nunawading', 'Mitcham', 'Heatherdale', 'Ringwood', 'Heathmont', 'Bayswater', 'Boronia', 'Ferntree Gully', 'Upper Ferntree Gully', 'Upwey', 'Tecoma', 'Belgrave'],0x01518a],
    'Craigieburn': [['North Melbourne', 'Kensington', 'Newmarket', 'Ascot Vale', 'Moonee Ponds', 'Essendon', 'Glenbervie', 'Strathmore', 'Pascoe Vale', 'Oak Park', 'Glenroy', 'Jacana', 'Broadmeadows', 'Coolaroo', 'Roxburgh Park', 'Craigieburn'],0xfcb818],
    'Cranbourne': [['Richmond', 'South Yarra', 'Malvern', 'Caulfield', 'Carnegie', 'Murrumbeena', 'Hughesdale', 'Oakleigh', 'Huntingdale', 'Clayton', 'Westall', 'Springvale', 'Sandown Park', 'Noble Park', 'Yarraman', 'Dandenong', 'Lynbrook', 'Merinda Park', 'Cranbourne'],0x00a8e4],
    'Flemington Racecourse': [['Flemington Racecourse', 'Showgrounds', 'North Melbourne', 'Southern Cross', 'Flinders Street'],0x8a8c8f],
    'Frankston': [['Flinders Street', 'Richmond', 'South Yarra', 'Hawksburn', 'Toorak', 'Armadale', 'Malvern', 'Caulfield', 'Glen Huntly', 'Ormond', 'McKinnon', 'Bentleigh', 'Patterson', 'Moorabbin', 'Highett', 'Southland', 'Cheltenham', 'Mentone', 'Parkdale', 'Mordialloc', 'Aspendale', 'Edithvale', 'Chelsea', 'Bonbeach', 'Carrum', 'Seaford', 'Kananook', 'Frankston'],0x009645],
    'Glen Waverley': [['Richmond', 'East Richmond', 'Burnley', 'Heyington', 'Kooyong', 'Tooronga', 'Gardiner', 'Glen Iris', 'Darling', 'East Malvern', 'Holmesglen', 'Jordanville', 'Mount Waverley', 'Syndal', 'Glen Waverley'],0x01518a],
    'Hurstbridge': [['Jolimont', 'West Richmond', 'North Richmond', 'Collingwood', 'Victoria Park', 'Clifton Hill', 'Westgarth', 'Dennis', 'Fairfield', 'Alphington', 'Darebin', 'Ivanhoe', 'Eaglemont', 'Heidelberg', 'Rosanna', 'Macleod', 'Watsonia', 'Greensborough', 'Montmorency', 'Eltham', 'Diamond Creek', 'Wattle Glen', 'Hurstbridge'],0xd0202e],
    'Lilydale': [['Richmond', 'East Richmond', 'Burnley', 'Hawthorn', 'Glenferrie', 'Auburn', 'Camberwell', 'East Camberwell', 'Canterbury', 'Chatham', 'Union', 'Box Hill', 'Laburnum', 'Blackburn', 'Nunawading', 'Mitcham', 'Heatherdale', 'Ringwood', 'Ringwood East', 'Croydon', 'Mooroolbark', 'Lilydale'],0x01518a],
    'Mernda': [['Jolimont', 'West Richmond', 'North Richmond', 'Collingwood', 'Victoria Park', 'Clifton Hill', 'Rushall', 'Merri', 'Northcote', 'Croxton', 'Thornbury', 'Bell', 'Preston', 'Regent', 'Reservoir', 'Ruthven', 'Keon Park', 'Thomastown', 'Lalor', 'Epping', 'South Morang', 'Middle Gorge', 'Hawkstowe', 'Mernda'],0xd0202e],
    'Pakenham': [['Richmond', 'South Yarra', 'Malvern', 'Caulfield', 'Carnegie', 'Murrumbeena', 'Hughesdale', 'Oakleigh', 'Huntingdale', 'Clayton', 'Westall', 'Springvale', 'Sandown Park', 'Noble Park', 'Yarraman', 'Dandenong', 'Hallam', 'Narre Warren', 'Berwick', 'Beaconsfield', 'Officer', 'Cardinia Road', 'Pakenham'],0x00a8e4],
    'Sandringham': [['Flinders Street', 'Richmond', 'South Yarra', 'Prahran', 'Windsor', 'Balaclava', 'Ripponlea', 'Elsternwick', 'Gardenvale', 'North Brighton', 'Middle Brighton', 'Brighton Beach', 'Hampton', 'Sandringham'],0xf17fb1],
    'Stony Point': [['Stony Point', 'Crib Point', 'Morradoo', 'Bittern', 'Hastings', 'Tyabb', 'Somerville', 'Baxter', 'Leawarra', 'Frankston'],0x009645],
    'Sunbury': [['North Melbourne', 'Footscray', 'Middle Footscray', 'West Footscray', 'Tottenham', 'Sunshine', 'Albion', 'Ginifer', 'St Albans', 'Keilor Plains', 'Watergardens', 'Diggers Rest', 'Sunbury'],0xfcb818],
    'Upfield': [['North Melbourne', 'Macaulay', 'Flemington Bridge', 'Royal Park', 'Jewell', 'Brunswick', 'Anstey', 'Moreland', 'Coburg', 'Batman', 'Merlynston', 'Fawkner', 'Gowrie', 'Upfield'],0xfcb818],
    'Werribee': [['Flinders Street', 'Southern Cross', 'North Melbourne', 'South Kensington', 'Footscray', 'Seddon', 'Yarraville', 'Spotswood', 'Newport', 'Seaholme', 'Altona', 'Westona', 'Laverton', 'Aircraft', 'Williams Landing', 'Hoppers Crossing', 'Werribee'],0x009645],
    'Williamstown': [['Flinders Street', 'Southern Cross', 'North Melbourne', 'South Kensington', 'Footscray', 'Seddon', 'Yarraville', 'Spotswood', 'Newport', 'North Williamstown', 'Williamstown Beach', 'Williamstown'],0x009645],
    'Unknown/Other':[[None], 0x000000],
}
linelist = [
    None,
    'Alamein', #1
    'Belgrave', #2
    'Craigieburn', #3
    'Cranbourne', #4
    'Mernda', #5
    'Frankston', #6
    'Glen Waverley', #7
    'Hurstbridge', #8
    'Lilydale', #9
    None,
    'Pakenham', #11
    'Sandringham', #12
    None,
    'Sunbury', #14
    'Upfield', #15
    'Werribee', #16
    'Williamstown' #17
]


# grouping commands

class CommandGroups(app_commands.Group):
    ...
trainlogs = CommandGroups(name='train-logs')
games = CommandGroups(name='games')
search = CommandGroups(name='search')
stats = CommandGroups(name='stats')


# startup

@bot.event
async def on_ready():
    print("Bot started")
    channel = bot.get_channel(STARTUP_CHANNEL_ID)

    bot.tree.add_command(trainlogs)
    bot.tree.add_command(games)
    bot.tree.add_command(search)
    bot.tree.add_command(stats)

    with open('logs.txt', 'a') as file:
        file.write(f"\n{datetime.datetime.now()} - Bot started")
    await channel.send(f"<@{USER_ID}> Bot is online! {convert_to_unix_time(datetime.datetime.now())}")
    if RARE_SERVICE_SEARCHER == 'on':
        task_loop.start()
        print('Rare service searcher is enabled!')


# rare service finder

@tasks.loop(minutes=10)
async def task_loop():
    print('its on')
    log_channel = bot.get_channel(RARE_SERVICE_CHANNEL_ID)
    await log_channel.send(f'Searching for rare services...')

    # Create a new thread to run checkRareTrainsOnRoute
    thread = threading.Thread(target=search_rare_services_in_thread)
    thread.start()

def search_rare_services_in_thread():
    rareservices = findRareServices('all')
    asyncio.run_coroutine_threadsafe(log_rare_services(rareservices), bot.loop)

async def log_rare_services(result):
    channel = bot.get_channel(RARE_SERVICE_CHANNEL_ID)

    if result in ['none' or None]:
        embed = discord.Embed(title=f'There was an error getting rare services')
        await channel.send(embed=embed)
        return
        
    if len(result) == 0:
        embed = discord.Embed(title=f'No rare services found')
        await channel.send(embed=embed)
        return
    
    await channel.send('<@&1227743193538498622>')
    embed = discord.Embed(title=f'{len(result)} Rare Service{"" if len(result) == 1 else "s"} found!')
    await channel.send(embed=embed)

    i = 0
    for trip in result:
        i += 1
        time = trip[0]
        desto = trip[1]
        set = trip[2]
        type = trip[3]
        line = trip[4]
        embed = discord.Embed(title=f'{i}. {desto} ({time})', color=lines_dictionary[line][1])
        embed.add_field(name='Line:',value=line)
        embed.add_field(name='Type:',value=type)
        embed.add_field(name='Set:',value=set,inline=False)
        embed.set_thumbnail(url=getIcon(type))
        await channel.send(embed=embed)

    
# /search metro-line BROKEN
    
@search.command(name="metro-line", description="Show info about a Metro line")
@app_commands.describe(line = "What Metro line to show info about?")
@app_commands.choices(line=[
        app_commands.Choice(name="Alamein", value="Alamein"),
        app_commands.Choice(name="Belgrave", value="Belgrave"),
        app_commands.Choice(name="Craigieburn", value="Craigieburn"),
        app_commands.Choice(name="Cranbourne", value="Cranbourne"),
        app_commands.Choice(name="Frankston", value="Frankston"),
        app_commands.Choice(name="Glen Waverley", value="Glen%20Waverley"),
        app_commands.Choice(name="Hurstbridge", value="Hurstbridge"),
        app_commands.Choice(name="Lilydale", value="Lilydale"),
        app_commands.Choice(name="Mernda", value="Mernda"),
        app_commands.Choice(name="Pakenham", value="Pakenham"),
        app_commands.Choice(name="Sandringham", value="Sandringham"),
        app_commands.Choice(name="Stony Point", value="Stony%20Point"),
        app_commands.Choice(name="Sunbury", value="Sunbury"),
        app_commands.Choice(name="Upfield", value="Upfield"),
        app_commands.Choice(name="Werribee", value="Werribee"),
])

async def line_info(ctx, line: str):
    embed = discord.Embed(title='This command isn\'t working right now!', description='domino6658 is working on fixing it')
    await ctx.response.send_message(embed=embed,ephemeral=True)
    return

    json_info_str = route_api_request(line, "0")
    json_info_str = json_info_str.replace("'", "\"")  # Replace single quotes with double quotes
    json_info = json.loads(json_info_str)
    
    routes = json_info['routes']
    status = json_info['status']
    version = status['version']
    health = status['health']
    
    route = routes[0]
    route_service_status = route['route_service_status']
    description = route_service_status['description']
    timestamp = route_service_status['timestamp']
    route_type = route['route_type']
    route_id = route['route_id']
    route_name = route['route_name']
    route_number = route['route_number']
    route_gtfs_id = route['route_gtfs_id']
    geopath = route['geopath']
    
    print(f"route id: {route_id}")
    
    
    # disruption info
    disruptionDescription = ""
    try:
        # print(disruption_api_request(route_id))
        disruptions = disruption_api_request(route_id)
        print(disruptions)
        
        # Extracting title and description
        general_disruption = disruptions["disruptions"]["metro_train"][0]
        disruptionTitle = general_disruption["title"]
        disruptionDescription = general_disruption["description"]

        # print("Title:", title)
        # print("Description:", description)
        
    except Exception as e:
        # await ctx.response.send_message(f"error:\n`{e}`")
        print(e)

    color = genColor(description)
    print(f"Status color: {color}")
    
    embed = discord.Embed(title=f'**__{description}__**', color=color)
    embed.set_author(name=f"{route_name} Line")
    # embed.add_field(name=description, value='', inline=False)
    if disruptionDescription:
        embed.add_field(name='Distruption Info',value=disruptionDescription, inline=False)
        

    
    await ctx.response.send_message(embed=embed)
    with open('logs.txt', 'a') as file:
                file.write(f"\n{datetime.datetime.now()} - user sent line info command with input {line}")


# / search run BROKEN

@search.command(name="run", description="Show runs for a route")
@app_commands.describe(runid = "route id")
async def runs(ctx, runid: str):
    embed = discord.Embed(title='This command isn\'t working right now!', description='domino6658 is working on fixing it')
    await ctx.response.send_message(embed=embed,ephemeral=True)
    return
    
    api_response = runs_api_request(runid)
    json_response = json.dumps(api_response)
    data = json.loads(json_response)

    # Extract relevant information from runs with vehicle data
    vehicle_data = []
    for run in data['runs']:
        if run['vehicle_position']:
            vehicle_info = {
                'run_id': run['run_id'],
                'latitude': run['vehicle_position']['latitude'],
                'longitude': run['vehicle_position']['longitude'],
                'direction': run['vehicle_position']['direction'],
                'operator': run['vehicle_descriptor']['operator'],
                'description': run['vehicle_descriptor']['description']
            }
            vehicle_data.append(vehicle_info)
    for vehicle_info in vehicle_data:
        print(vehicle_info)
    
    embed = discord.Embed(title=f"Route Information - ", color=0x0e66ad)
    for vehicle_info in vehicle_data:
        embed.add_field(name="Train type:", value=vehicle_info["description"], inline=False)    
    
    await ctx.response.send_message(embed=embed)
    with open('logs.txt', 'a') as file:
                file.write(f"\n{datetime.datetime.now()} - user sent run search command with input {runid}")


# /search route BROKEN

@search.command(name="route", description="Show info about a tram or bus route")
@app_commands.describe(rtype = "What type of transport is this route?")
@app_commands.choices(rtype=[
        app_commands.Choice(name="Tram", value="1"),
        # app_commands.Choice(name="Metro Train", value="0"),
        app_commands.Choice(name="Bus", value="2"),
        # app_commands.Choice(name="VLine Train", value="3"),
        app_commands.Choice(name="Night Bus", value="4"),
])
@app_commands.describe(number = "What route number to show info about?")

async def route(ctx, rtype: str, number: int):    
    embed = discord.Embed(title='This command isn\'t working right now!', description='domino6658 is working on fixing it')
    await ctx.response.send_message(embed=embed,ephemeral=True)
    return
    
    try:
        json_info_str = route_api_request(number, rtype)
        json_info_str = json_info_str.replace("'", "\"")  # Replace single quotes with double quotes
        json_info = json.loads(json_info_str)
        
        channel = ctx.channel
        await ctx.response.send_message(f"Results for {number}:")
        # embed = discord.Embed(title=f"Bus routes matching `{line}`:", color=0xff8200)
        counter = 0
        for route in json_info['routes']:

            routes = json_info['routes']
            status = json_info['status']
            version = status['version']
            health = status['health']
        
        
            route = routes[counter]
            route_service_status = route['route_service_status']
            description = route_service_status['description']
            timestamp = route_service_status['timestamp']
            route_type = route['route_type']
            route_id = route['route_id']
            route_name = route['route_name']
            route_number = route['route_number']
            route_gtfs_id = route['route_gtfs_id']
            geopath = route['geopath']
            
             # disruption info
            disruptionDescription = ""
            try:
                disruptions = disruption_api_request(route_id)
                # print(disruptions)
                
                # Extracting title and description
                general_disruption = disruptions["disruptions"]["metro_bus"][0]
                disruptionTitle = general_disruption["title"]
                disruptionDescription = general_disruption["description"]


                
            except Exception as e:
                print(e)

            
            # disruption status:

             # Check if the route number is the one you want
            if route_number == str(number):
                # Create and send the embed only for the desired route number
                embed = discord.Embed(title=f"Route {route_number}:", color=getColor(rtype))
                embed.add_field(name="Route Name", value=f"{route_number} - {route_name}", inline=False)
                embed.add_field(name="Status Description", value=description, inline=False)
                if disruptionDescription:
                    embed.add_field(name="Disruption Info",value=disruptionDescription, inline=False)
                    
                await channel.send(embed=embed)
                with open('logs.txt', 'a') as file:
                    file.write(f"\n{datetime.datetime.now()} - user sent route search command with input {rtype}, {number}")
                                
            counter = counter + 1
                
    except Exception as e:
        await ctx.response.send_message(f"error:\n`{e}`\nMake sure you inputted a valid route number, otherwise, the bot is broken.")
        with open('logs.txt', 'a') as file:
                    file.write(f"\n{datetime.datetime.now()} - ERROR with user command - user sent route search command with input {rtype}, {number}")


# /search wongm

@search.command(name="wongm", description="Search Wongm's Rail Gallery")
@app_commands.describe(search="search")
async def line_info(ctx, search: str):
    channel = ctx.channel
    print(f"removing spaces in search {search}")
    spaces_removed = search.replace(' ', '%20')
    print(spaces_removed)
    url = f"https://railgallery.wongm.com/page/search/?s={spaces_removed}"
    await ctx.response.send_message(url)


# /search train

@search.command(name="train", description="Find trips for a specific Metro train")
@app_commands.describe(train="train")
async def search_train(ctx, train: str):
    channel = ctx.channel
    type = checkTrainType(train)
    print(f"TRAINTYPE {type}")
    if type == None:
        await ctx.response.send_message(f"Error: Train `{train.upper()}` not found")
        
    else:
        embed = discord.Embed(title=f"Info for {train.upper()}", color=0x0070c0)
        embed.add_field(name='Type:',value=type)
        embed.add_field(name='Set:',value=setNumber(train.upper()),inline=False)
        embed.set_thumbnail(url=getIcon(type))
        # embed.set_image(url=getImage(train.upper()))
    
        # additional embed fields:
        await ctx.response.send_message(embed=embed)

        # Run transportVicSearch in a separate thread
        loop = asyncio.get_event_loop()
        task = loop.create_task(transportVicSearch_async(ctx, train.upper()))
        await task

async def transportVicSearch_async(ctx: commands.Context, train):
    embed = discord.Embed(title=f"Current trips for {train.upper()}", color=0x0070c0)

    result = await asyncio.to_thread(transportVicSearch, train)  # find runs in a separate thread
    print(result)
    if result == 'none':
        embed = discord.Embed(title=f"No trips scheduled for {train.upper()}", color=0x0070c0)
        await ctx.channel.send(embed=embed)
    elif result == 'no location data':
        embed = discord.Embed(title=f"No location data found for {train.upper()}",description='Try again in a few minutes',color=0x0070c0)
        await ctx.channel.send(embed=embed)
    else:
        runs = result[0]
        location = result[1]
        departing = result[2]
        print("thing is a list")
        for i, run in enumerate(runs):
            embed.add_field(name=f"{i+1}. {run[1]} ({run[0]})", value=f'{run[2]}', inline=False)
        await ctx.channel.send(embed=embed)

        # tracking location of the train

        embed = discord.Embed(title=f"Current Location for {train.upper()}",description=runs[0][2], colour=0x0070c0)

        embed.add_field(name="Station:",value=location[0],inline=True)

        if location[2] == 'Now':
            embed.add_field(name="Arriving:",value='(Now) '+convert_to_unix_time(datetime.datetime.now()),inline=True)
        elif departing == True:
            embed.add_field(name="Departing:",value=convert_to_unix_time(datetime.datetime.now()+datetime.timedelta(minutes=int(location[2]))),inline=True)
        else:
            embed.add_field(name="Arriving:",value=convert_to_unix_time(datetime.datetime.now()+datetime.timedelta(minutes=int(location[2]))),inline=True)
            

        embed.add_field(name="",value="",inline=False)

        embed.add_field(name="Platform:",value='Platform '+location[1],inline=True)

        embed.add_field(name="Destination:",value=runs[0][1].split(' - ')[1],inline=True)

        await ctx.channel.send(embed=embed)

@search.command(name="rare-services", description="Search for rare services on all lines")
@app_commands.describe(line = "Line")
@app_commands.choices(line=[
        app_commands.Choice(name="Alamein", value="Alamein"),
        app_commands.Choice(name="Belgrave", value="Belgrave"),
        app_commands.Choice(name="Craigieburn", value="Craigieburn"),
        app_commands.Choice(name="Cranbourne", value="Cranbourne"),
        app_commands.Choice(name="Frankston", value="Frankston"),
        app_commands.Choice(name="Glen Waverley", value="Glen%20Waverley"),
        app_commands.Choice(name="Hurstbridge", value="Hurstbridge"),
        app_commands.Choice(name="Lilydale", value="Lilydale"),
        app_commands.Choice(name="Mernda", value="Mernda"),
        app_commands.Choice(name="Pakenham", value="Pakenham"),
        app_commands.Choice(name="Sandringham", value="Sandringham"),
        app_commands.Choice(name="Sunbury", value="Sunbury"),
        app_commands.Choice(name="Upfield", value="Upfield"),
        app_commands.Choice(name="Werribee", value="Werribee"),
])

async def search_rare_services(ctx, line: str = 'all'):
    channel = ctx.channel
    await ctx.response.send_message(f'Searching for rare services...')

    loop = bot.loop
    task = loop.create_task(search_rare_services_inthread(ctx,line))
    await task

async def search_rare_services_inthread(ctx,inputline):
    result = findRareServices(inputline)
    
    
    # await ctx.channel.send(result)
    # return

    if result in ['none' or None]:
        embed = discord.Embed(title=f'There was an error getting rare services')
        await ctx.channel.send(embed=embed)
        return
        
    if len(result) == 0:
        embed = discord.Embed(title=f'No rare services found')
        await ctx.channel.send(embed=embed)
        return
    

    embed = discord.Embed(title=f'{len(result)} Rare Service{"" if len(result) == 1 else "s"} found!')
    await ctx.channel.send(embed=embed)

    i = 0
    for trip in result:
        i += 1
        time = trip[0]
        desto = trip[1]
        set = trip[2]
        type = trip[3]
        line = trip[4]
        embed = discord.Embed(title=f'{i}. {desto} ({time})', color=lines_dictionary[line][1])
        embed.add_field(name='Line:',value=line)
        embed.add_field(name='Type:',value=type)
        embed.add_field(name='Set:',value=set,inline=False)
        embed.set_thumbnail(url=getIcon(type))
        await ctx.channel.send(embed=embed)






# /search station

@search.command(name="departures", description="Search for departures from a station")
@app_commands.describe(station="station")
@app_commands.autocomplete(station=metro_station_autocompletion)
async def search_departures(ctx, station: str, show_all: bool = False):
    channel = ctx.channel
    if station.title() not in metro_stations_list:
        await ctx.response.send_message(f'Please use the autocomplete function on this command!',ephemeral = True)
        return
    await ctx.response.send_message(f'Getting the next {"" if show_all else "10 "}departures...{" (This might take a minute)" if show_all else ""}')

    loop = bot.loop
    task = loop.create_task(search_departures_inthread(ctx,station,show_all))
    await task

async def search_departures_inthread(ctx,station,show_all):
    result = transportVicSearchStation(station,show_all)
    
    if result in ['none' or None]:
        embed = discord.Embed(title=f'There was an error getting {station.title()} Station\'s scheduled departures')
        await ctx.channel.send(embed=embed)
        return
        
    if len(result) == 0:
        embed = discord.Embed(title=f'{station.title()} Station has no scheduled departures')
        await ctx.channel.send(embed=embed)
        return
    
    if len(result) > 1:
        embed = discord.Embed(title=f'Next {len(result)} Departures for {station.title()} Station')
    else:
        embed = discord.Embed(title=f'Next {len(result)} Departure for {station.title()} Station')
    
    # check if show all departures
    if show_all:
        # create thread
        departuresthread = await ctx.channel.create_thread(
            name=f'Departures for {station.title()} Station',
            auto_archive_duration=60,
            type=discord.ChannelType.public_thread
        )
        
        # send reponse message
        await ctx.channel.send(f"Departures will be sent in <#{departuresthread.id}>")
        await departuresthread.send(embed=embed)
    else:
        await ctx.channel.send(embed=embed)
    i = 0
    for departure in result:
        i += 1
        try:
            embed = discord.Embed(title=f"Departure {i}",description='', colour=lines_dictionary[departure[1]][1])
            if departure[4] != None:
                car = departure[4].split('-')[0]
                type = checkTrainType(car)
                embed.add_field(name='Type:',value=type)
                embed.add_field(name='Set:',value=departure[4],inline=False)
                embed.set_thumbnail(url=getIcon(type))
            else:
                embed.add_field(name='Type:',value='Unknown')
                embed.add_field(name='Set:',value='Unknown',inline=False)

            
            
            # embed.add_field(name="Station:",value=location[0],inline=True)
            if departure[3] == 'Now':
                embed.add_field(name="Arriving:",value='(Now) '+convert_to_unix_time(datetime.datetime.now()),inline=True)
            else:
                embed.add_field(name="Arriving:",value=convert_to_unix_time(datetime.datetime.now()+datetime.timedelta(minutes=int(departure[3]))),inline=True)
                

            embed.add_field(name="Platform:",value='Platform '+departure[0],inline=True)

            embed.add_field(name="",value="",inline=False)

            embed.add_field(name="Line:",value=departure[1],inline=True)
            
            embed.add_field(name="Destination:",value=departure[2],inline=True)

            if show_all:
                await departuresthread.send(embed=embed)
            else:
                await ctx.channel.send(embed=embed)
        except IndexError:
            pass



# /game station-guesser
    
@games.command(name="station-guesser", description="Play a game where you guess what train station is in the photo.")
@app_commands.describe(rounds = "The number of rounds. Defaults to 1.", ultrahard = "Ultra hard mode.")
async def game(ctx, ultrahard: bool=False, rounds: int = 1):
    
    channel = ctx.channel
    async def run_game():

        # Check if a game is already running in this channel
        if channel in channel_game_status and channel_game_status[channel]:
            await ctx.response.send_message("A game is already running in this channel.", ephemeral=True )
            return
        if rounds > 25:
            await ctx.response.send_message("You can only play a maximum of 25 rounds!", ephemeral=True )
            return

        channel_game_status[channel] = True
        
        # Define the CSV file path
        if ultrahard:
            csv_file = 'utils/game/images/ultrahard.csv'
        else:
            csv_file = 'utils/game/images/guesser.csv'

        # Read the CSV file and store rows in a list
        rows = []
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                rows.append(row)

        # Remove the header row if present
        header = rows[0]
        data = rows[1:]

        for round in range(rounds):
            # Get a random row
            random_row = random.choice(data)

            # Extract data from the random row
            url = random_row[0]
            station = random_row[1]
            difficulty = random_row[2]
            credit = random_row[3]

            if ultrahard:
                embed = discord.Embed(title=f"Guess the station!", color=0xe52727, description=f"Type ! before your answer. You have 30 seconds to answer.\n\n**Difficulty:** `{difficulty.upper()}`")
            else:
                embed = discord.Embed(title=f"Guess the station!", description=f"Type ! before your answer. You have 30 seconds to answer.\n\n**Difficulty:** `{difficulty}`")
                if difficulty == 'Very Easy':
                    embed.color = 0x89ff65
                elif difficulty == 'Easy':
                    embed.color = 0xcaff65
                elif difficulty == 'Medium':
                    embed.color = 0xffe665
                elif difficulty == 'Hard':
                    embed.color = 0xffa665
                elif difficulty == 'Very Hard':
                    embed.color = 0xff6565
            
            embed.set_image(url=url)
            embed.set_footer(text=f"Photo by {credit}. DM @domino6658 to submit a photo")
            embed.set_author(name=f"Round {round+1}/{rounds}")

            # Send the embed message
            if round == 0:
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.channel.send(embed=embed)

            # Define a check function to validate user input
            def check(m):
                return m.channel == channel and m.author != bot.user and m.content.startswith('!')

            try:
                correct = False
                if ultrahard:
                    gameType = 'ultrahard'
                else:
                    gameType = 'guesser'
                
                
                while not correct:
                    # Wait for user's response in the same channel
                    user_response = await bot.wait_for('message', check=check, timeout=30.0)
                    
                    # Check if the user's response matches the correct station
                    if user_response.content[1:].lower() == station.lower():
                        if ultrahard:
                            await ctx.channel.send(f"{user_response.author.mention} guessed it correctly!")
                        else:
                            await ctx.channel.send(f"{user_response.author.mention} guessed it correctly! The answer was {station.title()}!")
                        correct = True
                        if ultrahard:
                            addLb(user_response.author.id, user_response.author.name, 'ultrahard')
                        else:
                            addLb(user_response.author.id, user_response.author.name, 'guesser')
                            
                    elif user_response.content.lower() == '!skip':
                        if user_response.author.id in [ctx.user.id,707866373602148363] :
                            await ctx.channel.send(f"Round {round+1} skipped.")
                            break
                        else:
                            await ctx.channel.send(f"{user_response.author.mention} you can only skip the round if you were the one who started it.")
                    elif user_response.content.lower() == '!stop':
                        if user_response.author.id in [ctx.user.id,707866373602148363] :
                            await ctx.channel.send(f"Game ended.")
                            return
                        else:
                            await ctx.channel.send(f"{user_response.author.mention} you can only stop the game if you were the one who started it.")    
                    else:
                        await ctx.channel.send(f"Wrong guess {user_response.author.mention}! Try again.")
                        if ultrahard:
                            addLoss(user_response.author.id, user_response.author.name, 'ultrahard')
                        else:
                            addLoss(user_response.author.id, user_response.author.name, 'guesser')
            except asyncio.TimeoutError:
                if ultrahard:
                    await ctx.channel.send(f"Times up. Answers are not revealed in ultrahard mode.")
                else:
                    await ctx.channel.send(f"Times up. The answer was ||{station.title()}||")
            finally:
                # Reset game status after the game ends
                channel_game_status[channel] = False

    # Run the game in a separate task
    asyncio.create_task(run_game())
    

# /stats leaderboard

@stats.command(name="leaderboard", description="Global leaderboards for the games.",)
@app_commands.describe(game="What game's leaderboard to show?")
@app_commands.choices(game=[
        app_commands.Choice(name="Station Guesser", value="guesser"),
        app_commands.Choice(name="Ultrahard Station Guesser", value="ultrahard"),
        app_commands.Choice(name="Station order game", value="domino"),
        ])

async def lb(ctx, game: str='guesser'):
    channel = ctx.channel
    leaders = top5(game)
    if leaders == 'no stats':
        await ctx.response.send_message('There is no data for this game yet!',ephemeral=True)
        return
    print(leaders)
    # Create the embed
    embed = discord.Embed(title=f"Top 7 players for {game}", color=discord.Color.gold())
    
    count = 1
    for item, number, losses in leaders:
        try:
            embed.add_field(name=f'{count}: {item}', value=f'Wins: {str(number)}\nLosses: {str(losses)}\nAccuracy: {str(round((number/(number+losses))*100, 1))}%', inline=False)
        except:
            embed.add_field(name=f'{count}: {item}', value=f'Wins: {str(number)}\nLosses: {str(losses)}', inline=False)
        count = count + 1
        
    await ctx.response.send_message(embed=embed)


# /games station-order

@games.command(name="station-order", description="A game where you list the stations before or after a station.")
@app_commands.describe(rounds = "The number of rounds. Defaults to 1.", direction = "The directions you are listing the stations in. Defaults to Up or Down.")
@app_commands.choices(
    direction=[
        app_commands.Choice(name="Up or Down", value='updown'),
        app_commands.Choice(name="Up", value='up'),
        app_commands.Choice(name="Down", value='down')
        ],
    )

async def stationordergame(ctx, direction: str = 'updown', rounds: int = 1):
    channel = ctx.channel
    async def run_game():
        # Check if a game is already running in this channel
        if channel in channel_game_status and channel_game_status[channel]:
            await ctx.response.send_message("A game is already running in this channel.", ephemeral=True )
            return
        if rounds > 25:
            await ctx.response.send_message("You can only play a maximum of 25 rounds!", ephemeral=True )
            return

        channel_game_status[channel] = True

        for round in range(rounds):
            # choose random number of stations
            numdirection = random.randint(2,5)

            # choose direction
            if direction == 'updown':
                direction1 = random.choice(['up','down'])
            else:
                direction1 = direction
            if direction1 == 'up':
                numdirection = numdirection*-1
            
            # choose random line
            line = None
            while line == None:
                line = linelist[random.randint(0,len(linelist)-1)]

            # choose random station
            if line == 'Flemington Racecourse':
                if numdirection == 5 or numdirection == -5:
                    numdirection = random.choice([-4,-3,-2,2,3,4])
            station = None
            while station == None:
                station = lines_dictionary[line][0][random.randint(0,len(lines_dictionary[line][0])-1)]
                if not 0 <= lines_dictionary[line][0].index(station)+numdirection <= len(lines_dictionary[line][0]):
                    station = None

            embed = discord.Embed(
                title=f"Which __**{numdirection if numdirection > 0 else numdirection*-1}**__ stations are __**{direction1}**__ from __**{station}**__ station on the __**{line} line**__?",
                description=f"**Answers must be in the correct order!** Answer using this format:\n!<station1>, <station2>{', <station3>' if numdirection >= 3 or numdirection <= -3 else ''}{', <station4>' if numdirection >= 4 or numdirection <= -4 else ''}{', <station5>' if numdirection >= 5 or numdirection <= -5 else ''}\n\n*Use !skip to skip to the next round.*",
                colour=lines_dictionary[line][1])
            embed.set_author(name=f"Round {round+1}/{rounds}")
            if round == 0:
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.channel.send(embed=embed)

            # Define a check function to validate user input
            def check(m): return m.channel == channel and m.author != bot.user and m.content.startswith('!')

            # get list of correct stations
            if numdirection > 0:
                correct_list = lines_dictionary[line][0][lines_dictionary[line][0].index(station)+1:lines_dictionary[line][0].index(station)+numdirection+1]
            else:
                correct_list = lines_dictionary[line][0][lines_dictionary[line][0].index(station)+numdirection:lines_dictionary[line][0].index(station)]
                correct_list.reverse()
            correct_list1 = [x.lower() for x in correct_list]

            # the actual input part
            try:
                correct = False
                while not correct:
                    # Wait for user's response in the same channel
                    user_response = await bot.wait_for('message', check=check, timeout=30.0)
                    response = user_response.content[1:].lower().split(',')
                    response = [x.strip() for x in response]


                    # Check if the user's response matches the correct station
                    if response == correct_list1:
                        await ctx.channel.send(f"{user_response.author.mention} guessed it correctly!")
                        addLb(user_response.author.id, user_response.author.name, 'domino')
                        
                        correct = True 
                    elif user_response.content.lower() == '!skip':
                        if user_response.author.id in [ctx.user.id,707866373602148363] :
                            await ctx.channel.send(f"Round {round+1} skipped. The answer was `{correct_list[0]}, {correct_list[1]}{f', {correct_list[2]}' if len(correct_list) >=3 else ''}{f', {correct_list[3]}' if len(correct_list) >=4 else ''}{f', {correct_list[4]}' if len(correct_list) >=5 else ''}`")
                            break
                        else:
                            await ctx.channel.send(f"{user_response.author.mention} you can only skip the round if you were the one who started it.")
                    elif user_response.content.lower() == '!stop':
                        if user_response.author.id in [ctx.user.id,707866373602148363] :
                            await ctx.channel.send(f"Game ended.")
                            return
                        else:
                            await ctx.channel.send(f"{user_response.author.mention} you can only stop the game if you were the one who started it.")
                    else:
                        await ctx.channel.send(f"Wrong guess {user_response.author.mention}! Try again.")
                        addLoss(user_response.author.id, user_response.author.name, 'domino')
                        
            except asyncio.TimeoutError:
                await ctx.channel.send(f"Times up. The answer was ||{correct_list[0]}, {correct_list[1]}{f', {correct_list[2]}' if len(correct_list) >=3 else ''}{f', {correct_list[3]}' if len(correct_list) >=4 else ''}{f', {correct_list[4]}' if len(correct_list) >=5 else ''}||")
            finally:
                # Reset game status down the game ends
                channel_game_status[channel] = False
            
    # Run the game in a separate task
    asyncio.create_task(run_game())


# /train-logs add

@trainlogs.command(name="add", description="Log a train you have been on")
@app_commands.describe(number = "Carrige Number", date = "Date in DD/MM/YYYY format", line = 'Train Line', start='Starting Station', end = 'Ending Station')
@app_commands.autocomplete(start=all_station_autocompletion)
@app_commands.autocomplete(end=all_station_autocompletion)
@app_commands.choices(line=[
        app_commands.Choice(name="Alamein", value="Alamein"),
        app_commands.Choice(name="Belgrave", value="Belgrave"),
        app_commands.Choice(name="Craigieburn", value="Craigieburn"),
        app_commands.Choice(name="Cranbourne", value="Cranbourne"),
        app_commands.Choice(name="Flemington Racecourse", value="Flemington Racecourse"),
        app_commands.Choice(name="Frankston", value="Frankston"),
        app_commands.Choice(name="Glen Waverley", value="Glen Waverley"),
        app_commands.Choice(name="Hurstbridge", value="Hurstbridge"),
        app_commands.Choice(name="Lilydale", value="Lilydale"),
        app_commands.Choice(name="Mernda", value="Mernda"),
        app_commands.Choice(name="Pakenham", value="Pakenham"),
        app_commands.Choice(name="Sandringham", value="Sandringham"),
        app_commands.Choice(name="Stony Point", value="Stony Point"),
        app_commands.Choice(name="Sunbury", value="Sunbury"),
        app_commands.Choice(name="Upfield", value="Upfield"),
        app_commands.Choice(name="Werribee", value="Werribee"),
        app_commands.Choice(name="Albury", value="Albury"),
        app_commands.Choice(name="Ballarat/Maryborough/Ararat", value="Ballarat/Maryborough/Ararat"),
        app_commands.Choice(name="Bendigo/Echuca/Swan Hill", value="Bendigo/Echuca/Swan Hill"),
        app_commands.Choice(name="Geelong/Warrnambool", value="Geelong/Warrnambool"),
        app_commands.Choice(name="Seymour/Shepparton", value="Seymour/Shepparton"),
        app_commands.Choice(name="Traralgon/Bairnsdale", value="Traralgon/Bairnsdale"),
        app_commands.Choice(name="Unknown", value="Unknown")
])

async def logtrain(ctx, number: str, line:str, date:str='today', start:str='N/A', end:str='N/A'):
    channel = ctx.channel
    print(date)
    async def log():
        print("logging the thing")

        # checking if date is valid
        savedate = date.split('/')
        if date.lower() == 'today':
            savedate = datetime.date.today()
        else:
            try:
                savedate = datetime.date(int(savedate[2]),int(savedate[1]),int(savedate[0]))
            except ValueError:
                await ctx.response.send_message(f'Invalid date: {date}\nMake sure to use a possible date.',ephemeral=True)
                return
            except TypeError:
                await ctx.response.send_message(f'Invalid date: {date}\nUse the form `dd/mm/yyyy`',ephemeral=True)
                return

        # checking if train number is valid
        set = setNumber(number.upper())
        if set == None:
            await ctx.response.send_message(f'Invalid train number: {number.upper()}',ephemeral=True)
            return
        type = checkTrainType(number.upper())

        # Add train to the list
        id = addTrain(ctx.user.name, set, type, savedate, line, start.title(), end.title())
        await ctx.response.send_message(f"Added {set} ({type}) on the {line} line on {savedate} from {start.title()} to {end.title()} to your file. (Log ID `#{id}`)")
        
                
    # Run in a separate task
    asyncio.create_task(log())
    

# /train-logs delete

@trainlogs.command(name='delete', description='Delete a logged trip. Defaults to the last logged trip.')
@app_commands.describe(id = "The ID of the log that you want to delete.")
async def deleteLog(ctx, id:str='LAST'):
    
    async def deleteLogFunction():
        if id[0] == '#':
            idformatted = id[1:].upper()
        else:
            idformatted = id.upper()

        if idformatted != 'LAST':
            if not is_hex(idformatted):
                cmds = await bot.tree.fetch_commands()
                for cmd in cmds:
                    if cmd.name == 'train-logs':
                        cmdid = cmd.id
                        await ctx.response.send_message(f'Invalid log ID entered: `{idformatted}`. You can find the ID of a log to delete by using </train-logs view:{cmdid}>.',ephemeral=True)
                        return
                
            
        dataToDelete = readRow(ctx.user.name, idformatted)
        if dataToDelete in ['no data at all','no data for user']:
            await ctx.response.send_message(f'You have no logs you can delete!',ephemeral=True)
            return
        elif dataToDelete == 'invalid id did not show up':
            cmds = await bot.tree.fetch_commands()
            for cmd in cmds:
                if cmd.name == 'train-logs':
                    cmdid = cmd.id
                    await ctx.response.send_message(f'Invalid log ID entered: `{idformatted}`. You can find the ID of a log to delete by using </train-logs view:{cmdid}>.',ephemeral=True)
                    return
        else:
            idformatted1 = deleteRow(ctx.user.name, idformatted)
            if idformatted == 'LAST':
                await ctx.response.send_message(f'Most recent log (`#{idformatted1}`) deleted. The data was:\n`{dataToDelete}`',ephemeral=True)
            else:
                await ctx.response.send_message(f'Log `#{idformatted}` deleted. The data was:\n`{dataToDelete}`',ephemeral=True)
            
    asyncio.create_task(deleteLogFunction())

    
# /train-logs view

vLineLines = ['Geelong/Warrnambool', 'Ballarat/Maryborough/Ararat', 'Bendigo/Echuca/Swan Hill','Albury', 'Seymour/Shepparton', 'Traralgon/Bairnsdale']

@trainlogs.command(name="view", description="View logged trips for a user")
@app_commands.describe(user = "Who do you want to see the data of?")
async def userLogs(ctx, user: discord.User=None):
    async def sendLogs():
        if user == None:
            userid = ctx.user
        else:
            userid = user
        
        try:
            file = discord.File(f'utils/trainlogger/userdata/{userid.name}.csv')
        except FileNotFoundError:
            if userid == ctx.user:
                await ctx.response.send_message("You have no trains logged!",ephemeral=True)
            else:
                await ctx.response.send_message("This user has no trains logged!",ephemeral=True)
            return
        print(userid.name)
        data = readLogs(userid.name)
        if data == 'no data':
            if userid == ctx.user:
                await ctx.response.send_message("You have no trains logged!",ephemeral=True)
            else:
                await ctx.response.send_message("This user has no trains logged!",ephemeral=True)
            return
    
        # create thread
        logsthread = await ctx.channel.create_thread(
            name=f'{userid.name}\'s Train Logs',
            auto_archive_duration=60,
            type=discord.ChannelType.public_thread
        )
        
        # send reponse message
        await ctx.response.send_message(f"Logs will be sent in <#{logsthread.id}>")
        await logsthread.send(f'# {userid.name}\'s CSV file', file=file)
        await logsthread.send(f'# {userid.name}\'s Train Logs')
        formatted_data = ""
        for sublist in data:
            if len(sublist) >= 7:  # Ensure the sublist has enough items
                image = None
                
                # thing to find image:
                hyphen_index = sublist[1].find("-")
                if hyphen_index != -1:
                    first_car = sublist[1][:hyphen_index]
                    print(f'First car: {first_car}')
                    image = getImage(first_car)
                    if image == None:
                        last_hyphen = sublist[1].rfind("-")
                        if last_hyphen != -1:
                            last_car = sublist[1][last_hyphen + 1 :]  # Use last_hyphen instead of hyphen_index
                            print(f'Last car: {last_car}')
                            image = getImage(last_car)
                            if image == None:
                                image = getImage(sublist[2])
                                print(f'the loco number is: {sublist[1]}')
                                
                #send in thread to reduce spam!
                thread = await ctx.channel.create_thread(name=f"{userid.name}'s logs")
                    # Make the embed
                if sublist[4] in vLineLines:
                    embed = discord.Embed(title=f"Log {sublist[0]}",colour=0x7e3e98)
                elif sublist[4] == 'Unknown':
                    embed = discord.Embed(title=f"Log {sublist[0]}")
                else:
                    embed = discord.Embed(title=f"Log {sublist[0]}",colour=lines_dictionary[sublist[4]][1])
                embed.add_field(name=f'Set', value="{} ({})".format(sublist[1], sublist[2]))
                embed.add_field(name=f'Line', value="{}".format(sublist[4]))
                embed.add_field(name=f'Date', value="{}".format(sublist[3]))
                embed.add_field(name=f'Trip Start', value="{}".format(sublist[5]))
                embed.add_field(name=f'Trip End', value="{}".format(sublist[6]))
                embed.set_thumbnail(url=image)

                await logsthread.send(embed=embed)
                # if count == 6:
                #     await ctx.channel.send('Max of 5 logs can be sent at a time. Use the csv option to see all logs')
                #     return
        
    asyncio.create_task(sendLogs())


# /train-logs stats

@trainlogs.command(name="stats", description="View stats for a logged user's trips.")
@app_commands.describe(stat='Type of stats to view', user='Who do you want to see the data of?')
@app_commands.choices(stat=[
    app_commands.Choice(name="Top Lines", value="lines"),
    app_commands.Choice(name="Top Stations", value="stations"),
    app_commands.Choice(name="Top Sets", value="sets"),
    app_commands.Choice(name="Top Dates", value="dates"),
    app_commands.Choice(name="Top Types", value="types"),
])
async def statTop(ctx: discord.Interaction, stat: str, user: discord.User = None):
    async def sendLogs():
        statSearch = stat
        if user == None:
            userid = ctx.user
        else:
            userid = ctx.user # temp cause the thing wont work fix later!
        data = topStats(userid.name, statSearch)

        embed = discord.Embed(title=f'Top {stat} for {userid.name}')
        for item in data:
            station, times = item.split(': ')
            embed.add_field(name=station, value=f"{times}", inline=False)
        
        await ctx.response.send_message(embed=embed)
    
    await sendLogs()


# /stats profile
    
@stats.command(name='profile', description="Shows a users trip log stats, and leaderboard wins")    
async def profile(ctx, user: discord.User = None):
    async def profiles():
        if user == None:
            username = ctx.user.name
        else:
            username = user.name
        embed = discord.Embed(title=f"{username}'s Profile")
        #games
        stats = fetchUserStats(username)
        
        if stats[0] != 'no stats':
            item, wins, losses = stats[0]
            embed.add_field(name='Station Guesser', value=f'Wins: {str(wins)}\nLosses: {str(losses)}\nAccuracy: {str(round((wins/(wins+losses))*100, 1))}%', inline=False)
        else:
            embed.add_field(name='Station Guesser', value='No data',inline=False)
        if stats[1] != 'no stats':
            item, wins, losses = stats[1]
            embed.add_field(name='Ultrahard Station Guesser', value=f'Wins: {str(wins)}\nLosses: {str(losses)}\nAccuracy: {str(round((wins/(wins+losses))*100, 1))}%', inline=False)
        else:
            embed.add_field(name='Ultrahard Station Guesser', value='No data',inline=False)
        if stats[2] != 'no stats':
            item, wins, losses = stats[2]
            embed.add_field(name='Station Order Guesser', value=f'Wins: {str(wins)}\nLosses: {str(losses)}\nAccuracy: {str(round((wins/(wins+losses))*100, 1))}%', inline=False)
        else:
            embed.add_field(name='Station Order Guesser', value='No data',inline=False)
        
        # train logger
        try:
            lines = topStats(username, 'lines')
            stations = topStats(username, 'stations')
            sets = topStats(username, 'sets')
            trains = topStats(username, 'types')
            dates = topStats(username, 'dates')
            embed.add_field(name='Train Log stats:', value=f'Top Line:  {lines[0]}\nTop Station:	{stations[0]}\nTop Train:	{trains[0]}\nTop Set:	{sets[0]}\nTop Date:    {dates[0]}')

        except FileNotFoundError:
            embed.add_field(name="Train Log Stats", value=f'{username} has no logged trips!')
        await ctx.response.send_message(embed=embed)
        
    await profiles()


# sync

@bot.command()
@commands.guild_only()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if ctx.author.id in [707866373602148363,780303451980038165]:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

# run bot
bot.run(BOT_TOKEN)