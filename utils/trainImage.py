import requests

# THIS IS DIFFRNT TO THE ONE USED IN THE TRAIN PHOTO COMMAND!
# THIS ONE ONLY RETURNS THE FIRST IMAGE AND ALSO REQUIRS CORRECT FORMATTING!!
def getImage(number):
    photo_url = f"https://railway-photos.xm9g.xyz/photos/{number}.jpg"

    # Make a HEAD request to check if the photo exists
    URLresponse = requests.head(photo_url)
    if URLresponse.status_code == 200:
        return(photo_url)


def getIcon(type):
    cleaned_type = type.replace(' ', '-').replace("'", '')
    url = f"https://xm9g.xyz/discord-bot-assets/MPTB/{cleaned_type}.png"
    return(url)
