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
    if type == 'EDI Comeng':
        return 'https://melbournesptgallery.weebly.com/uploads/1/9/9/4/19942089/edi-comeng-refurb-ptv-new-no-hand-rail_1_orig.png'
    if type == 'Alstom Comeng':
        return 'https://melbournesptgallery.weebly.com/uploads/1/9/9/4/19942089/alstom-comeng-refurb-ptv-new-without-hand-rails_orig.png'
    if type == 'Siemens Nexas':
        return 'https://melbournesptgallery.weebly.com/uploads/1/9/9/4/19942089/siemens-ptv_4_orig.png'
    if type == "X'Trapolis 100":
        return 'https://melbournesptgallery.weebly.com/uploads/1/9/9/4/19942089/x-trapolis-ptv_2_orig.png'
    if type == 'HCMT':
        return 'https://melbournesptgallery.weebly.com/uploads/1/9/9/4/19942089/hcmt-2_orig.png'
    if type == "Z":
        return 'https://files.catbox.moe/zkc4fz.png'
