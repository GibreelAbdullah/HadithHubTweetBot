from PIL import Image, ImageFont, ImageDraw
import textwrap
import tweepy
import requests
import os

def getsize(text, font, direction):
    left, top, right, bottom = font.getbbox(text, direction=direction)
    return right - left, bottom - top

def generateImage():
    my_image = Image.open("HadithBackground.png")
    
    r = requests.get(os.environ['url']) # append ?l=216 at the end for length of hadith

    font = ImageFont.truetype(
        'NotoNaskhArabic-Regular.ttf', 42)
    imageWidth = 1200

    araHadith = r.json()[0][0]
    engHadith = r.json()[0][1]
    reference = r.json()[0][2]
    link = r.json()[0][3]
    gradings = r.json()[0][4]
    gradingList = gradings.replace("::", " - ").split(' && ')
    image_editable = ImageDraw.Draw(my_image)

    para = textwrap.wrap(araHadith, width=100)
    current_h, pad = 400, 10

    for line in reversed(para):
        w, h = getsize(line, font=font, direction='rtl')
        image_editable.text(((imageWidth - w) / 2, current_h), line, font=font)
        current_h -= h + pad

    font = ImageFont.truetype(
        'RobotoCondensed-Light.ttf', 42)
    para = textwrap.wrap(engHadith, width=65)
    current_h, pad = 600, 10

    for line in para:
        w, h = getsize(line, font=font, direction='rtl')
        image_editable.text(((imageWidth - w) / 2, current_h), line, font=font)
        current_h += h + pad

    font = ImageFont.truetype(
        'RobotoCondensed-Light.ttf', 35)

    for i in range(len(gradingList)):
        if(i%2==1):
            w, h = getsize(gradingList[i], font=font, direction='rtl')
            image_editable.text((1180 - w, current_h),gradingList[i], font=font)
        else:
            current_h = current_h+100
            image_editable.text((20, current_h),gradingList[i], font=font)

    w, h = getsize(reference, font=font, direction='rtl')
    image_editable.text(((imageWidth - w) / 2, 20), reference, font=font)

    w, h = getsize(link, font=font, direction='rtl')
    image_editable.text(((imageWidth - w) / 2, 1120), link, font=font)

    my_image.save("/tmp/result.png", "PNG")
    return link

def get_twitter_conn_v1(api_key, api_secret, access_token, access_token_secret) -> tweepy.API:
    """Get twitter conn 1.1"""

    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(
        access_token,
        access_token_secret,
    )
    return tweepy.API(auth)

def get_twitter_conn_v2(api_key, api_secret, access_token, access_token_secret) -> tweepy.Client:
    """Get twitter conn 2.0"""

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )

    return client

# if __name__ == "__main__":
def lambda_handler(event, context):
    link = generateImage()

    api_key = os.environ['api_key']
    api_secret = os.environ['api_secret']
    access_token = os.environ['access_token']
    access_token_secret = os.environ['access_token_secret']

    client_v1 = get_twitter_conn_v1(api_key, api_secret, access_token, access_token_secret)
    client_v2 = get_twitter_conn_v2(api_key, api_secret, access_token, access_token_secret)

    media_path = "/tmp/result.png"
    media = client_v1.media_upload(filename=media_path)
    media_id = media.media_id

    client_v2.create_tweet(text="Read Ahadith in Arabic, Bengali, English, French, Indonesian, Tamil, Urdu, Turkish, Russian \n{}".format(link), media_ids=[media_id])