from playsound import playsound
from io import BytesIO
import discord
from discord.ext import commands
import datetime
from hashlib import sha1
import hmac
from dotenv import dotenv_values
import os
import json
import requests
import asyncio
import aiohttp
import traceback
from PIL import Image, ImageDraw

import utils
import utils.trainInfo
import utils.math
import utils.parseTimestamp
import utils.ptvApi
import utils.writeToFile
from utils import getConfig

config = getConfig.Config()

class Train(object):
    def __init__(self, carriage: str):
        self.carriage = carriage
        self.carriage = carriage.upper()
        self.type = None
        self.set = None
        
        self.running = None
        
        self.runs = []
        self.currentRun = None
        self.runRef = None
        self.runDestination = None
        self.runOrigination = None
        self.runLine = None
        
        self.runStartUtc = None
        self.runEndUtc = None
        self.runStartLocal = None
        self.runEndLocal = None
        self.runDelta = None
        
        self.isAtStation = None
        self.distanceToStation = None
        self.stationInfo = None
        self.stationId = None
        self.stationName = None
        
        self.stationLatitude = None
        self.stationLongitude = None
        self.runLatitude = None
        self.runLongitude = None
        
        self.map = None
        self.image = None
        
        
        
        # self.main()
    
    async def main(self, interaction: discord.Interaction):
        try:
            trainType = utils.trainInfo.trainType(self.carriage)
            if trainType == None:
                return None
            else:
                self.type = trainType
            
            
            carriageRunRefs = []
            trainLines = utils.trainInfo.trainLines(trainType)
            
            
            routesData = utils.ptvApi.get('/v3/routes?route_types=0')
            routesData = routesData['routes']
            
        
            
            validRoutes = []
            for route in routesData:
                if route['route_name'] in trainLines:
                    validRoutes.append(route)


            async def process_route(session, route, carriageRunRefs):
                routeName = route['route_name']
                print('Checking',routeName,'...')
                routeId = route['route_id']
                
                routeData = await utils.ptvApi.get_async(session, f'/v3/runs/route/{routeId}?expand=All')
                if routeData:
                    for run in routeData['runs']:
                        if run['vehicle_descriptor']:
                            runCarriages = run['vehicle_descriptor']['id'].split('-')
                            for runCarriage in runCarriages:
                                if runCarriage.lower() == self.carriage.lower():
                                    carriageRunRefs.append(run['run_ref'])
                                    print(f'Found! {run["run_ref"]} {routeName}')
                                    break

            async def getcarriageRunRefs(carriageRunRefs, routesData):
                
                async with aiohttp.ClientSession() as session:
                    if routesData:
                        tasks = [process_route(session, route, carriageRunRefs) for route in routesData]
                        await asyncio.gather(*tasks)
                        return
                    else:
                        print('No routes found')
            
            
            loop = asyncio.get_event_loop()
            def callback(future):
                if future.exception():
                    print(future.exception())
                    
                async def getRunsInfo(carriageRunRefs):
                
                    async def getRunInfo(carriageRunRef):
                        runInfo = await utils.ptvApi.get_async(session, f'/v3/pattern/run/{carriageRunRef}/route_type/0?expand=All&include_skipped_stops=true&include_geopath=true&include_advertised_interchange=true')
                        self.runs.append(runInfo)
                        
                    async with aiohttp.ClientSession() as session:
                        tasks = [getRunInfo(carriageRunRef) for carriageRunRef in carriageRunRefs]
                        await asyncio.gather(*tasks)
                        return
                
                def callback2(future):
                    try:
                        if future.exception():
                            print(future.exception())
                        if self.runs == []:
                            embed = discord.Embed(title=f"{self.type} ({self.carriage.upper()})",
                                                colour=0x3d7ce1)

                            embed.add_field(name="Type:",
                                            value=self.type,
                                            inline=True)
                            embed.add_field(name="Set:",
                                            value=self.set,
                                            inline=True)
                            embed.add_field(name="",
                                            value="",
                                            inline=False)
                            embed.add_field(name=f"{self.carriage.upper()} is not running a service right now.",
                                            value="",
                                            inline=True)

                            thumbnail = discord.File(fp=utils.trainInfo.pathsdict[self.type], filename='thumbnail.png')
                            embed.set_thumbnail(url='attachment://thumbnail.png')
                    
                            loop.create_task(interaction.followup.send(file=thumbnail,embed=embed))
                            return
                        for carriageRunInfo in self.runs:
                            # print(list(carriageRunInfo.keys()))
                            # print(str(json.dumps(carriageRunInfo['departures'][0], indent=4, sort_keys=True)))
                            first = carriageRunInfo['departures'][0]['estimated_departure_utc']
                            if first == None:
                                first = carriageRunInfo['departures'][0]['scheduled_departure_utc']
                            
                            last = carriageRunInfo['departures'][-1]['estimated_departure_utc']
                            if last == None:
                                last = carriageRunInfo['departures'][-1]['scheduled_departure_utc']
                                
                            firstStopDtObj = utils.parseTimestamp.parse_timestamp(first)
                            
                            lastStopDtObj = utils.parseTimestamp.parse_timestamp(last)
                            nowUtcDtObj = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                            # print(delta)
                            print('now', nowUtcDtObj)
                            print('start', firstStopDtObj)
                            print('end', lastStopDtObj)
                            print(nowUtcDtObj > firstStopDtObj)
                            print(nowUtcDtObj < lastStopDtObj)
                            if nowUtcDtObj > firstStopDtObj and nowUtcDtObj < lastStopDtObj:
                                self.currentRun = carriageRunInfo
                                self.runStartUtc = firstStopDtObj
                                self.runEndUtc = lastStopDtObj
                                self.runRef = list(self.currentRun['runs'].keys())[0]
                                break
                        
                        self.set = self.currentRun['runs'][self.runRef]['vehicle_descriptor']['id']
                        self.runLatitude = self.currentRun['runs'][self.runRef]['vehicle_position']['latitude']
                        self.runLongitude = self.currentRun['runs'][self.runRef]['vehicle_position']['longitude']
                        self.runLine = self.currentRun['routes'][list(self.currentRun['routes'].keys())[0]]['route_name']
                        self.runDestination = self.currentRun['runs'][self.runRef]['destination_name']
                        self.runOrigination = self.currentRun['stops'][str(self.currentRun['departures'][0]['stop_id'])]['stop_name']
                        if self.currentRun['runs'][self.runRef]['direction_id'] == 1:
                            self.runDestination = 'Flinders Street'
                        else:
                            self.runOrigination = 'Flinders Street'
                        self.runStartLocal = self.runStartUtc + datetime.datetime.now(datetime.timezone.utc).astimezone().utcoffset()
                        self.runEndLocal = self.runEndUtc + datetime.datetime.now(datetime.timezone.utc).astimezone().utcoffset()
                        
                        # utils.writeToFile.write('routes.json', json.dumps(self.currentRun, indent=4, sort_keys=True))
                        
                        self.running = False
                        for departure in self.currentRun['departures']:
                            if departure['at_platform']:
                                self.stationInfo = departure
                                self.isAtStation = False
                                self.running = True
                                break
                            if departure['estimated_departure_utc'] != None:
                                departureTime = utils.parseTimestamp.parse_timestamp(departure['estimated_departure_utc'])
                            else:
                                departureTime = utils.parseTimestamp.parse_timestamp(departure['scheduled_departure_utc'])
                            
                            print(departureTime)
                            print(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))
                            
                                
                            if departureTime > datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None):
                                self.stationInfo = departure
                                self.isAtStation = False
                                delta = departureTime - datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                                self.runDelta = delta
                                print('this awgwaergned')
                                print(type(departureTime), type(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)), type(delta), type(self.runDelta))
                                print('this definitely happened')
                                self.running = True
                                
                                print('bigger')
                                print()
                                break
                            else:
                                print('smaller')
                                print()
                        
                        if not self.running:
                            print(f'{self.carriage.upper()} is not running.')
                            # print(json.dumps(self.currentRun['departures'], indent=4, sort_keys=True))
                            
                            return
                            
                        self.stationId = str(self.stationInfo['stop_id'])
                        self.stationName = self.currentRun['stops'][self.stationId]['stop_name']
                        self.stationLatitude = self.currentRun['stops'][self.stationId]['stop_latitude']
                        self.stationLongitude = self.currentRun['stops'][self.stationId]['stop_longitude']
                        self.map = f'https://www.google.com/maps/search/{self.runLatitude},{self.runLongitude}/'
                        self.image = f'https://maps.googleapis.com/maps/api/staticmap?center={self.runLatitude},{self.runLongitude}&map_id=3b4527fbc6823f42&zoom=15&size=1000x1000&key={config.google_api_key}'
                        response = requests.get(self.image)

                        # with open('map.png', 'wb') as f:
                        #     f.write(response.content)
                        


                        image = Image.open('map.png')
                        draw = ImageDraw.Draw(image)
                        
                        width, height = image.size
                        center_x, center_y = width // 2, height // 2
                        overlay_size = 50
                        overlay_x1 = center_x - overlay_size // 2
                        overlay_y1 = center_y - overlay_size // 2

                        overlay = Image.open(utils.trainInfo.pathsdict[self.type])
                        
                        image = image.convert('RGBA')
                        overlay = overlay.convert('RGBA') 
                        
                        overlay = overlay.resize((50, int(overlay.size[1]*(50/overlay.size[0]))), Image.Resampling.LANCZOS)
                        
                        image.paste(overlay, (overlay_x1, overlay_y1), mask=overlay)
                        
                        print(f'\nType: {self.type}')
                        print(f'Set: {self.set}')
                        print(f'Line: {self.runLine}')
                        print(f'Destination: {self.runDestination}')
                        print(f'Origin: {self.runOrigination}')
                        print(f'Time: {self.runStartLocal.strftime("%I:%M %p")} to {self.runEndLocal.strftime("%I:%M %p")}')
                        print(f'Map: {self.map}')
                        
                        print(f'Image: {self.image}')
                        if self.isAtStation:
                            print(f'Now at: {self.stationName}')
                        else:
                            print(f'Next station: {self.stationName}')
                            print(f'Distance to next station: {utils.math.haversine(self.runLatitude, self.runLongitude, self.stationLatitude, self.stationLongitude):.2f}km')
                            minutes, seconds = divmod(self.runDelta.seconds, 60)
                            print(f'Time to next station: {minutes}m {seconds:02d}s')
                            
                        with BytesIO() as image_binary:
                            image.save(image_binary, 'PNG')
                            image_binary.seek(0)
                            picture = discord.File(fp=image_binary, filename='image.png')
                            
                        embed = discord.Embed(title=f"{self.type} ({self.carriage.upper()})",
                                            colour=0x3d7ce1)

                        embed.add_field(name="Type:",
                                        value=self.type,
                                        inline=True)
                        embed.add_field(name="Set:",
                                        value=self.set,
                                        inline=True)
                        embed.add_field(name="",
                                        value="",
                                        inline=False)
                        embed.add_field(name="Line:",
                                        value=self.runLine,
                                        inline=False)
                        embed.add_field(name="Origin:",
                                        value=f"{self.runOrigination} ({self.runStartLocal.strftime("%I:%M %p")})",
                                        inline=True)
                        embed.add_field(name="Destination:",
                                        value=f"{self.runDestination} ({self.runEndLocal.strftime("%I:%M %p")})",
                                        inline=True)
                        if self.isAtStation:
                            embed.add_field(name="Now at:",
                                            value=self.stationName,
                                            inline=True)
                            embed.add_field(name="Location:",
                                            value=f"[Google Maps]({self.map})",
                                            inline=True)
                        else:
                            embed.add_field(name="Next station:",
                                            value=self.stationName,
                                            inline=True)
                            embed.add_field(name="Location:",
                                            value=f"[Google Maps]({self.map})",
                                            inline=True)
                            embed.add_field(name="",
                                            value="",
                                            inline=False)
                            embed.add_field(name="Distance to next station:",
                                            value=f"{utils.math.haversine(self.runLatitude, self.runLongitude, self.stationLatitude, self.stationLongitude):.2f}km",
                                            inline=True)
                            embed.add_field(name="Time to next station:",
                                            value=f"{minutes}m {seconds:02d}s",
                                            inline=True)

                        embed.set_image(url="attachment://image.png")

                        thumbnail = discord.File(fp=utils.trainInfo.pathsdict[self.type], filename='thumbnail.png')
                        
                        embed.set_thumbnail(url="attachment://thumbnail.png")
                
                        loop.create_task(interaction.followup.send(files=[picture, thumbnail], embed=embed))
                    except Exception as e:
                        print(type(e).__name__)
                        print(str(e))
                        print(traceback.format_exc())
                        playsound('misc/sounds/error.mp3')
                
                task = loop.create_task(getRunsInfo(carriageRunRefs))
                task.add_done_callback(callback2)
            
            task = loop.create_task(getcarriageRunRefs(carriageRunRefs, validRoutes))
            task.add_done_callback(callback)
        # print(carriageRunRefs)
        except Exception as e:
            pass
        
        
        
        
        #get current run more info
        
            
            
            
