from utils import getConfig
import utils.trainInfo
config = getConfig.Config()
import utils.math
import utils.writeToFile
import typing
import json
import utils.findTrain
import utils.ptvApi
import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
from playsound import playsound
import traceback
import datetime

from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(float, [lon1, lat1, lon2, lat2])
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371000  # Radius of Earth in meters
    return c * r


bot = commands.Bot(command_prefix=config.bot.command_prefix, intents=discord.Intents.all())

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



stationscoords = {'Alamein Station': [-37.8683167, 145.079666], 'Ashburton Station': [-37.86197, 145.081345], 'Auburn Station': [-37.8224, 145.045837], 'Burnley Station': [-37.8275566, 145.007553], 'Burwood Station': [-37.8515625, 145.0805], 'Camberwell Station': [-37.8265648, 145.058685], 'East Richmond Station': [-37.8264046, 144.99707], 'Flagstaff Station': [-37.8119774, 144.955658], 'Flinders Street Station': [-37.81831, 144.966965], 'Glenferrie Station': [-37.8214645, 145.036438], 'Hartwell Station': [-37.8439827, 145.075562], 'Hawthorn Station': [-37.8218231, 145.0229], 'Melbourne Central Station': [-37.8099365, 144.9626], 'Parliament Station': [-37.8110542, 144.9729], 'Richmond Station': [-37.8240738, 144.990158], 'Riversdale Station': [-37.8315, 145.069641], 'Southern Cross Station': [-37.8179321, 144.951416], 'Willison Station': [-37.8357124, 145.0703], 'Bayswater Station': [-37.84173, 145.268143], 'Belgrave Station': [-37.9091, 145.355286], 'Blackburn Station': [-37.82007, 145.150009], 'Boronia Station': [-37.8604546, 145.284378], 'Box Hill Station': [-37.8192177, 145.121429], 'Canterbury Station': [-37.82449, 145.081223], 'Chatham Station': [-37.8243027, 145.088654], 'East Camberwell Station': [-37.8258934, 145.068192], 'Ferntree Gully Station': [-37.8817, 145.295258], 'Heatherdale Station': [-37.81884, 145.213547], 'Heathmont Station': [-37.82832, 145.244553], 'Laburnum Station': [-37.8207779, 145.1407], 'Mitcham Station': [-37.8180847, 145.192886], 'Nunawading Station': [-37.8204231, 145.175232], 'Ringwood Station': [-37.8156624, 145.229477], 'Tecoma Station': [-37.9081154, 145.343], 'Union Station': [-37.82312, 145.100281], 'Upper Ferntree Gully Station': [-37.8926735, 145.307526], 'Upwey Station': [-37.90369, 145.331329], 'Ascot Vale Station': [-37.77531, 144.921829], 'Broadmeadows Station': [-37.6830521, 144.919617], 'Coolaroo Station': [-37.661, 144.926056], 'Craigieburn Station': [-37.6018143, 144.943329], 'Essendon Station': [-37.75601, 144.9162], 'Glenbervie Station': [-37.7472153, 144.920944], 'Glenroy Station': [-37.7045326, 144.917221], 'Jacana Station': [-37.6951332, 144.915848], 'Kensington Station': [-37.7937775, 144.930527], 'Moonee Ponds Station': [-37.7657051, 144.919159], 'Newmarket Station': [-37.7873268, 144.928986], 'North Melbourne Station': [-37.807415, 144.942566], 'Oak Park Station': [-37.71795, 144.921509], 'Pascoe Vale Station': [-37.7307549, 144.928192], 'Roxburgh Park Station': [-37.6382332, 144.93541], 'Strathmore Station': [-37.74359, 144.927322], 'Armadale Station': [-37.8564529, 145.019333], 'Carnegie Station': [-37.88624, 145.058578], 'Caulfield Station': [-37.8774567, 145.042526], 'Clayton Station': [-37.9246826, 145.120529], 'Cranbourne Station': [-38.09954, 145.2806], 'Dandenong Station': [-37.9899673, 145.209732], 'Hawksburn Station': [-37.844593, 145.002136], 'Hughesdale Station': [-37.89425, 145.076431], 'Huntingdale Station': [-37.91102, 145.102371], 'Lynbrook Station': [-38.0573463, 145.249283], 'Malvern Station': [-37.86625, 145.0293], 'Merinda Park Station': [-38.0790024, 145.2635], 'Murrumbeena Station': [-37.8901978, 145.067383], 'Noble Park Station': [-37.9666252, 145.176331], 'Oakleigh Station': [-37.9003677, 145.088318], 'Sandown Park Station': [-37.9565, 145.162827], 'South Yarra Station': [-37.8384438, 144.99234], 'Springvale Station': [-37.9495125, 145.153458], 'Toorak Station': [-37.85077, 145.0139], 'Westall Station': [-37.93849, 145.13884], 'Yarraman Station': [-37.9782524, 145.1916], 'Bell Station': [-37.7455673, 145.000153], 'Clifton Hill Station': [-37.7886543, 144.995422], 'Collingwood Station': [-37.8045235, 144.993744], 'Croxton Station': [-37.7641, 144.997055], 'Epping Station': [-37.6521873, 145.031067], 'Hawkstowe Station': [-37.6229935, 145.0974], 'Jolimont-MCG Station': [-37.81653, 144.9841], 'Keon Park Station': [-37.6948662, 145.011887], 'Lalor Station': [-37.66585, 145.0172], 'Mernda Station': [-37.60255, 145.100876], 'Merri Station': [-37.7778435, 144.992981], 'Middle Gorge Station': [-37.644062, 145.092133], 'North Richmond Station': [-37.8103943, 144.9925], 'Northcote Station': [-37.7698631, 144.995285], 'Preston Station': [-37.7386742, 145.000534], 'Regent Station': [-37.7284, 145.002777], 'Reservoir Station': [-37.71689, 145.006989], 'Rushall Station': [-37.78322, 144.9924], 'Ruthven Station': [-37.7078972, 145.009521], 'South Morang Station': [-37.6491623, 145.067032], 'Thomastown Station': [-37.680336, 145.014282], 'Thornbury Station': [-37.7550468, 144.998581], 'Victoria Park Station': [-37.7991562, 144.994446], 'West Richmond Station': [-37.8149452, 144.991425], 'Aspendale Station': [-38.02722, 145.102158], 'Bentleigh Station': [-37.9174271, 145.036987], 'Bonbeach Station': [-38.06507, 145.120026], 'Carrum Station': [-38.0765038, 145.122833], 'Chelsea Station': [-38.05332, 145.116638], 'Cheltenham Station': [-37.9666519, 145.05455], 'Edithvale Station': [-38.0360641, 145.1073], 'Frankston Station': [-38.1429863, 145.12616], 'Glen Huntly Station': [-37.8897171, 145.042221], 'Highett Station': [-37.9484253, 145.04187], 'Kananook Station': [-38.12174, 145.135284], 'McKinnon Station': [-37.910305, 145.0383], 'Mentone Station': [-37.98297, 145.066], 'Moorabbin Station': [-37.93435, 145.036743], 'Mordialloc Station': [-38.006588, 145.087662], 'Ormond Station': [-37.90321, 145.039612], 'Parkdale Station': [-37.9930763, 145.076324], 'Patterson Station': [-37.9251442, 145.035461], 'Seaford Station': [-38.1040154, 145.128235], 'Southland Station': [-37.95876, 145.049118], 'Darling Station': [-37.8689575, 145.062943], 'East Malvern Station': [-37.87693, 145.0694], 'Gardiner Station': [-37.8532829, 145.051666], 'Glen Iris Station': [-37.8593063, 145.058228], 'Glen Waverley Station': [-37.8795, 145.162064], 'Heyington Station': [-37.83467, 145.022629], 'Holmesglen Station': [-37.8744, 145.090652], 'Jordanville Station': [-37.8736, 145.112091], 'Kooyong Station': [-37.8399277, 145.033554], 'Mount Waverley Station': [-37.87525, 145.128052], 'Syndal Station': [-37.87623, 145.14978], 'Tooronga Station': [-37.84937, 145.041733], 'Alphington Station': [-37.7783966, 145.03125], 'Darebin Station': [-37.7749634, 145.038483], 'Dennis Station': [-37.7791824, 145.00824], 'Diamond Creek Station': [-37.6732941, 145.158508], 'Eaglemont Station': [-37.7635841, 145.05394], 'Eltham Station': [-37.71355, 145.147827], 'Fairfield Station': [-37.7791748, 145.0169], 'Greensborough Station': [-37.70395, 145.108246], 'Heidelberg Station': [-37.7570763, 145.060684], 'Hurstbridge Station': [-37.6394, 145.192017], 'Ivanhoe Station': [-37.768898, 145.045425], 'Macleod Station': [-37.72601, 145.069153], 'Montmorency Station': [-37.7152977, 145.1215], 'Rosanna Station': [-37.7428741, 145.066147], 'Watsonia Station': [-37.7109528, 145.0838], 'Wattle Glen Station': [-37.6639671, 145.181625], 'Westgarth Station': [-37.7806168, 144.999237], 'Croydon Station': [-37.79544, 145.2806], 'Lilydale Station': [-37.75722, 145.34581], 'Mooroolbark Station': [-37.7847481, 145.312408], 'Ringwood East Station': [-37.81197, 145.2502], 'Beaconsfield Station': [-38.050827, 145.366074], 'Berwick Station': [-38.04041, 145.345718], 'Cardinia Road Station': [-38.07129, 145.43779], 'East Pakenham Station': [-38.0842857, 145.506317], 'Hallam Station': [-38.0177422, 145.269775], 'Narre Warren Station': [-38.02781, 145.30397], 'Officer Station': [-38.066143, 145.411], 'Pakenham Station': [-38.0806122, 145.486374], 'Balaclava Station': [-37.8694878, 144.993515], 'Brighton Beach Station': [-37.9264832, 144.989151], 'Elsternwick Station': [-37.88475, 145.0009], 'Gardenvale Station': [-37.8966942, 145.004166], 'Hampton Station': [-37.937973, 145.001465], 'Middle Brighton Station': [-37.9151344, 144.996292], 'North Brighton Station': [-37.9048843, 145.002609], 'Prahran Station': [-37.8495178, 144.989853], 'Ripponlea Station': [-37.8759079, 144.995239], 'Sandringham Station': [-37.95033, 145.004562], 'Windsor Station': [-37.8560524, 144.992035], 'Baxter Station': [-38.194046, 145.160522], 'Bittern Station': [-38.33739, 145.178024], 'Crib Point Station': [-38.36612, 145.204041], 'Hastings Station': [-38.30566, 145.185974], 'Leawarra Station': [-38.1520348, 145.139542], 'Morradoo Station': [-38.3540344, 145.1896], 'Somerville Station': [-38.22534, 145.176239], 'Stony Point Station': [-38.3742371, 145.221848], 'Tyabb Station': [-38.2598152, 145.1864], 'Albion Station': [-37.7776566, 144.8247], 'Diggers Rest Station': [-37.6270142, 144.719925], 'Footscray Station': [-37.8010864, 144.9032], 'Ginifer Station': [-37.760067, 144.811356], 'Keilor Plains Station': [-37.7292747, 144.793732], 'Middle Footscray Station': [-37.8025, 144.891479], 'South Kensington Station': [-37.7995338, 144.925476], 'St Albans Station': [-37.7448578, 144.800049], 'Sunbury Station': [-37.57909, 144.727325], 'Sunshine Station': [-37.7885361, 144.832886], 'Tottenham Station': [-37.7992554, 144.862946], 'Watergardens Station': [-37.7011261, 144.774185], 'West Footscray Station': [-37.8018036, 144.883987], 'Anstey Station': [-37.76124, 144.9607], 'Batman Station': [-37.7335243, 144.96283], 'Brunswick Station': [-37.76772, 144.9596], 'Coburg Station': [-37.74234, 144.963348], 'Fawkner Station': [-37.7146225, 144.960556], 'Flemington Bridge Station': [-37.7881355, 144.939316], 'Gowrie Station': [-37.700676, 144.958878], 'Jewell Station': [-37.7749825, 144.95871], 'Macaulay Station': [-37.7942619, 144.936172], 'Merlynston Station': [-37.7209358, 144.961319], 'Moreland Station': [-37.7544823, 144.961823], 'Royal Park Station': [-37.7811928, 144.9523], 'Upfield Station': [-37.6660767, 144.946747], 'Aircraft Station': [-37.8666039, 144.7608], 'Altona Station': [-37.86715, 144.829651], 'Hoppers Crossing Station': [-37.8832779, 144.700958], 'Laverton Station': [-37.8636932, 144.772614], 'Newport Station': [-37.8427124, 144.8836], 'Seaholme Station': [-37.8678436, 144.840958], 'Seddon Station': [-37.8090019, 144.89566], 'Spotswood Station': [-37.8306351, 144.885941], 'Werribee Station': [-37.8993835, 144.661118], 'Westona Station': [-37.8651657, 144.813492], 'Williams Landing Station': [-37.86987, 144.747452], 'Yarraville Station': [-37.81585, 144.889938], 'North Williamstown Station': [-37.85733, 144.889069], 'Williamstown Station': [-37.8677559, 144.905319], 'Williamstown Beach Station': [-37.8639832, 144.894485], 'Flemington Racecourse Station': [-37.7871971, 144.9076], 'Showgrounds Station': [-37.783474, 144.914261]}

async def metro_station_autocompletion(
    interaction: discord.Interaction,
    current: str
) -> typing.List[app_commands.Choice[str]]:
    if current == '':
        return [app_commands.Choice(name=station.rsplit(' Station',1)[0], value=station.rsplit(' Station',1)[0]) for station in list(stationscoords.keys())][:25]
    return [
        app_commands.Choice(name=station.rsplit(' Station',1)[0], value=station.rsplit(' Station',1)[0])
        for station in list(stationscoords.keys()) if current.lower() in station.lower()
    ][:25]
stations = [
    app_commands.Choice(name=station_name.rsplit(' Station',1)[0], value=station_name.rsplit(' Station',1)[0]) for station_name in list(stationscoords.keys())
]





def getEmojis(category):
    emojidict = {
        'Station': '<:trainstation:1329231167047733308>',
        'Level Crossing': '<:levelcrossing:1329230448018198540>',
        'Pedestrian Crossing': '<:pedestriancrossing:1329230476225024020>',
        'Bridge': '<:bridge:1329230328220614778>',
        'Footbridge': '<:footbridge:1329230364962590831>',
        'Other': '<:other:1329230517165490217>'
    }
    return emojidict[category]


@search.command(name='locations')
@app_commands.describe(station = "The closest station to your location.")
@app_commands.autocomplete(station=metro_station_autocompletion)
async def _locations(ctx: discord.Interaction, station: str):
    try:
        closest_coords = utils.math.find_closest_coordinates(stationscoords[station+" Station"],5)
    except KeyError:
        await ctx.response.send_message(f'Please use the autocomplete function on this command!',ephemeral = True)
        return

    embed = discord.Embed(title=f"5 Closest Trainspotting Locations to {station} Station",
                    colour=0x00b0f4)
    for i, entry in enumerate(closest_coords):
        category, name, description, lat, lon = entry[0]
        distance = entry[1]
        categories = category.split('-')
        categories = [getEmojis(cat) for cat in categories]
        emojis = '/'.join(categories)
        # if i % 2 == 0 and i != 0:
        #     embed.add_field(name='', value='', inline=False)
        embed.add_field(
            name=f"{i+1}. {emojis} __{name}__ - {distance:.0f}m away",
            value=f"**Type:** {category.replace('-','/')}\n **Description:** {description.replace('comma',',') if description != '' else '*No description*'}\n**Location:** [{float(lat):.4f}, {float(lon):.4f}](https://google.com/maps/place/{lat}+{lon})",
            inline=False
        )

    await ctx.response.send_message(embed=embed)





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
                # print(stop['stop_name'])
                if stop['stop_name'].lower() == f'{input_string.lower()} station':
                    stationId = stop['stop_id']
                    break
            if stationId != None:
                break
        
        data = utils.ptvApi.get(f'/v3/departures/route_type/0/stop/{stationId}?expand=All&max_results=1000')
        utils.writeToFile.write('a.json', json.dumps(data, indent=4, sort_keys=True))
        for run in list(data['runs'].keys()):
            if data['runs'][run]['vehicle_descriptor'] != None:
                
                for d in data['departures']:
                    if d['run_ref'] == run:
                        dtobj = datetime.datetime.strptime(d["scheduled_departure_utc"], "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(hours=11)
                        break
                type = utils.trainInfo.trainType(data['runs'][run]['vehicle_descriptor']['id'].split('-')[0])
                if type:
                    # if 'Comeng' in type:
                    print(f'{dtobj.strftime('%I:%M %p')} - {type}, {data["runs"][run]["vehicle_descriptor"]["id"]}')
            
        
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

