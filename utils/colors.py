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
    if type == "Tram":
        return(0x78be20)
    if type in ["Bus" or "Night Bus"]:
        return(0xff8400)