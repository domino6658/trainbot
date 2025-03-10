def trainType(number):
    car = str(number).upper()
    try:
        if car.endswith("M"):
            car = car.rstrip(car[-1])
            try:
                car = int(car)
            except:
                return None
            if car >= 561 and car <= 680:
                return "Alstom Comeng"
            elif car >= 301 and car <= 468:
                return "EDI Comeng"
            elif car >= 471 and car <= 554:
                return "EDI Comeng"
            elif car >= 1 and car <= 288:
                return "X'Trapolis 100"
            elif car >= 851 and car <= 986:
                return "X'Trapolis 100"
            elif car >= 701 and car <= 844:
                return "Siemens Nexas"
            elif car >= 9001 and int(car) <= 9070 or int(car) >= 9101 and int(car) <= 9170 or int(car) >= 9201 and int(car) <= 9270 or int(car) >= 9301 and int(car) <= 9370 or int(car) >= 9701 and int(car) <= 9770 or int(car) >= 9801 and int(car) <= 9870 or int(car) >= 9901 and int(car) <= 9970:
                return "HCMT"
            else:
                return None
        elif car.endswith("T"):
    
            car = car.rstrip(car[-1])
            try:
                car = int(car)
            except:
                return None
            if car >= 1131 and car <= 1190:
                return "Alstom Comeng"
            elif car >= 1001 and car <= 1084:
                return "EDI Comeng"
            elif car >= 1086 and car <= 1127:
                return "EDI Comeng"
            elif car >= 1301 and car <= 1444:
                return "X'Trapolis 100"
            elif car >= 1626 and car <= 1693:
                return "X'Trapolis 100"
            elif car >= 851 and car <= 986:
                return "X'Trapolis100"
            elif car >= 2501 and car <= 2572:
                return "Siemens Nexas"
            else:
                return None
        else:
            try:
                car = int(car)
            except:
                return None
            
            if car >= 9001 and int(car) <= 9070 or int(car) >= 9101 and int(car) <= 9170 or int(car) >= 9201 and int(car) <= 9270 or int(car) >= 9301 and int(car) <= 9370 or int(car) >= 9701 and int(car) <= 9770 or int(car) >= 9801 and int(car) <= 9870 or int(car) >= 9901 and int(car) <= 9970:
                return "HCMT"
            
        if car.startswith("N"):
            car = car.lstrip("N")
            try:
                car = int(car)
            except:
                return f"Train type not found for {number}"
            if 451 <= car <= 475:
                return "N Class"

            if car >= 451 and car <= 475:
                return "N Class"
            else:
                return None
            
        if car.startswith("K"):
            return("K Class")
        
        if car.startswith("Y"):
            return("Y Class")
        
        if car.startswith("TRAIN"):
            return("Error: TrainID sent")
            
        elif int(car) >= 9001 and int(car) <= 9070 or int(car) >= 9101 and int(car) <= 9170 or int(car) >= 9201 and int(car) <= 9270 or int(car) >= 9301 and int(car) <= 9370 or int(car) >= 9701 and int(car) <= 9770 or int(car) >= 9801 and int(car) <= 9870 or int(car) >= 9901 and int(car) <= 9970:
            return "HCMT"
        elif (1100 <= int(car) <= 1228) or (1230 <= int(car) <= 1328) or (1330 <= int(car) <= 1392) or (int(car) == 1399) or (1593 <= int(car) <= 1598) or (2100 <= int(car) <= 2132) or (2134 <= int(car) <= 2141) or (2200 <= int(car) <= 2232) or (2234 <= int(car) <= 2241) or (2300 <= int(car) <= 2332) or (2334 <= int(car) <= 2341):
            return "VLocity"
        elif (7001 <= int(car) <= 7022):
            return "Sprinter"

        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
    return None


trains_on_lines = {
    "Alamein":["X'Trapolis 100"],
    "Belgrave":["X'Trapolis 100"],
    "Craigieburn":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Cranbourne":["HCMT"],
    "Frankston":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"],
    "Glen Waverley":["X'Trapolis 100"],
    "Hurstbridge":["X'Trapolis 100"],
    "Lilydale":["X'Trapolis 100"],
    "Mernda":["X'Trapolis 100"],
    "Pakenham":["HCMT"],
    "Sandringham":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Sunbury":["Alstom Comeng","EDI Comeng","Siemens Nexas","HCMT"],
    "Upfield":["Alstom Comeng","EDI Comeng","Siemens Nexas"],
    "Werribee":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"],
    "Williamstown":["Alstom Comeng","EDI Comeng","Siemens Nexas","X'Trapolis 100"]
}

def trainLines(type):
    lines = []
    for line, trains in trains_on_lines.items():
        if type in trains:
            lines.append(line)
    return lines

pathsdict = {
    "X'Trapolis 100": 'misc/icons/xtrapolis.png',
    "Alstom Comeng": 'misc/icons/alstomcomeng.png',
    "EDI Comeng": 'misc/icons/edicomeng.png',
    "Siemens Nexas": 'misc/icons/siemens.png',
    "HCMT": 'misc/icons/hcmt.png',
}