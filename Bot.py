
import telebot
from cred import *
import requests
from bs4 import BeautifulSoup
import praw
import random
import os
from moviepy.editor import VideoFileClip
import redvid

from cred import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET

reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                        client_secret=REDDIT_CLIENT_SECRET,
                        user_agent='USER_AGENT')

API_TOKEN = TELEGRAM_BOT_API_KEY

bot = telebot.TeleBot(API_TOKEN)

def check_url_type(url):
    ext = os.path.splitext(url)[1]
    if ext in ['.jpg', '.jpeg', '.png']:
        return 'image'
    elif ext in ['.mp4', '.mov', '.avi']:
        return 'video'
    elif ext in ['.gif']:
        return 'gif'
    else:
        return 'website'


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    o='''
    Commands :
    /search subreddit : Search Subreddit
    /meme subreddit : random memes from subreddit
    /memeall subreddit : All memes from a subreddit
    /stop : Stop memeall command
    /clear :  clear bot's cache if slow
    '''
    bot.send_chat_action(chat_id=message.chat.id,action='typing')
    bot.send_message(chat_id=message.chat.id,text=o)
    
@bot.message_handler(commands=['search'])
def search(message):
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/search ", "").strip()
    subred = subred.lower()
    url = 'https://www.reddit.com/search/?q='+str(subred)
    result = requests.get(
        url, headers={'User-Agent': 'Bored programmer\'s bot'})
    src = result.content
    soup = BeautifulSoup(src, 'html.parser')
    links = soup.find_all('a')
    subs = set()
    for i in links:
        if "r/" in i.text:
            subs.add(str(i.text).strip())
    subs = list(subs)
    o = ""
    for i in range(len(subs)):
        o = o+str(i+1)+") "+subs[i]+'\n'
    bot.send_message(chat_id=message.chat.id, text=o)

@bot.message_handler(commands=['meme'])
def meme(message):
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/meme ", "").strip()
    subred = subred.lower()
    if subred == "/meme":
        subred = "memes"
    top = reddit.subreddit(subred).top(limit=100)
    random_sub = random.choice(list(top))
    out = ""
    if random_sub.title:
        out += random_sub.title+'\n'
    if random_sub.selftext:
        out += random_sub.selftext+'\n'
    if random_sub.author_flair_text:
        out += random_sub.author_flair_text+'\n'
    random_sub.url = random_sub.url.replace(".gifv", ".mp4")

    if check_url_type(random_sub.url) == 'image':
        r = requests.get(random_sub.url)
        photo = r.content
        bot.send_photo(message.chat.id, photo, caption=out)
    
    elif check_url_type(random_sub.url) == 'video':
        r = requests.get(random_sub.url)
        video = r.content
        bot.send_video(message.chat.id, video, caption=out)

    elif check_url_type(random_sub.url) == 'gif':
        r = requests.get(random_sub.url)
        h = r.headers
        if h['Content-Type'] == 'image/png' or h['Content-Type'] == 'image/jpg':
            return
        video = r.content
        g = open('temp.gif', 'wb')
        g.write(video)
        g.close()
        gif_clip = VideoFileClip('temp.gif')
        gif_clip.write_videofile('temp.mp4')
        f = open('temp.mp4', 'rb')
        bot.send_video(message.chat.id, f, caption=out)

    else:
        bot.send_message(chat_id=message.chat.id, text=out)

@bot.message_handler(commands=['memeall'])
def meme(message):
    print(message.chat.first_name, " :", message.text)
    subred = message.text.replace("/memeall ", "").strip()
    subred = subred.lower()
    if subred == "/meme":
        subred = "memes"
    top = reddit.subreddit(subred).top(limit=20)
    for random_sub in top:
        out = ""
        if random_sub.title:
            out += random_sub.title+'\n'
        if random_sub.selftext:
            out += random_sub.selftext+'\n'
        if random_sub.author_flair_text:
            out += random_sub.author_flair_text+'\n'
        random_sub.url = random_sub.url.replace(".gifv", ".mp4")
        print(random_sub.url)
        if check_url_type(random_sub.url) == 'image':
            r = requests.get(random_sub.url)
            photo = r.content
            bot.send_photo(message.chat.id, photo, caption=out)
        
        elif check_url_type(random_sub.url) == 'video':
            r = requests.get(random_sub.url)
            h = r.headers
            if h['Content-Type'] == 'image/png' or h['Content-Type'] == 'image/jpg':
                    continue
            video = r.content
            bot.send_video(message.chat.id, video, caption=out)
        
        elif check_url_type(random_sub.url) == 'gif':
            r = requests.get(random_sub.url)
            h = r.headers
            if h['Content-Type'] == 'image/png' or h['Content-Type'] == 'image/jpg':
                continue
            video = r.content
            g = open('temp.gif', 'wb')
            g.write(video)
            g.close()
            gif_clip = VideoFileClip('temp.gif')
            gif_clip.write_videofile('temp.mp4')
            f = open('temp.mp4', 'rb')
            bot.send_video(message.chat.id, f, caption=out)
            os.remove('temp.mp4')
        elif 'v.redd.it' in random_sub.url:
            downloader = redvid.Downloader(max_q=True)
            downloader.url = random_sub.url
            downloader.file_name = "temp.mp4"   
            downloader.filename = "temp.mp4"
            downloader.download()
            f = open('temp.mp4', 'rb')
            bot.send_video(message.chat.id, f, caption=out)
            os.remove('temp.mp4')
        else:
            out += random_sub.url+'\n'
            bot.send_message(chat_id=message.chat.id, text=out)

bot.infinity_polling()