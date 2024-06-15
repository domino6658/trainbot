def getServiceIcon(status):
    print(f"Line Status: {status}")
    if status == "Major Delays":
        return('https://files.catbox.moe/jqiu3q.png')
    if status == "Good Service":
        return('https://files.catbox.moe/iz0udh.png')
    if status == "Minor Delays":
        return('https://files.catbox.moe/1c9ivj.png')
    if status == "Suspended":
        return('https://files.catbox.moe/zxaz44.png')
    if status == "Planned Works":
        return('https://files.catbox.moe/mvjwvc.png')

def getColor(type):
    if type == "metro" or type == "0":
        return(0x0072ce)
    if type == "tram" or type == "1":
        return(0x78be20)
    if type == "bus" or type =="2":
        return(0xff8400)
    if type == "vline" or type =="3":
        return(0x8f1a95)