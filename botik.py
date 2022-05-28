import telebot
from telebot import types

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import datetime
import time
from PIL import Image
import os


bot = telebot.TeleBot("1982576553:AAET9NY6gd_w5M_jozmCScW556WUWj8BmGM")
now = datetime.datetime.now()

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Новости')
    keyboard.row('Рейтинг', 'LIVE!')
    bot.send_message(message.chat.id, 'Здравствуй! Чем могу помочь? Узнайте всё что нужно вам по игре CS:GО прямо сейчас', reply_markup=keyboard)

@bot.message_handler(content_types = ['text'])
def get_text_messages(message):
    if message.text == 'Новости':
        url = "https://www.hltv.org"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        item = soup.find('div', class_ = 'standard-box standard-list')
        urls = []
        _newsName_spis = []
        _newsText_spis = []
        _newUrl_spis = []

        for n, i in enumerate(item, start = 1):
            newsName = i.find('div', class_ = 'newstext').text
            _newsName_spis.append(newsName)

        for i in item.findAll('a'):
            link = str(i.get('href'))
            urls.append(link)

        for slug in urls:
            newUrl = url + slug
            _newUrl_spis.append(newUrl)
            response = requests.get(newUrl)
            soup = BeautifulSoup(response.text, 'lxml')
            nextUrl = soup.find_all('div', class_='newsdsl')
            for n, i in enumerate(nextUrl, start = 1):
                newsText = i.find('p', class_='news-block').text
                _newsText_spis.append(newsText)

        for i in range(len(_newsName_spis)):
            bot.send_message(message.chat.id, f'{i+1}: {_newsName_spis[i]}\n\n{_newsText_spis[i]}..\n\n{_newUrl_spis[i]}\n\n')
            time.sleep(1)

    if message.text == 'Рейтинг':
        url = 'https://www.hltv.org/ranking/teams/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        item = soup.find_all('div', class_ = 'ranked-team standard-box')
        name_spis = []
        score_spis = []
        final_text = ''

        for n, i in enumerate(item, start = 1):
            rankingName = i.find('span', class_ = 'name').text
            rankingScore = i.find('span', class_ = 'points').text
            name_spis.append(rankingName)
            score_spis.append(rankingScore)
            if len(name_spis)>=5:
                break
        for i in range(5):
            final_text += f'#{i+1}: {name_spis[i]} --> {score_spis[i]}\n'
        bot.send_message(message.chat.id, f"На сегодняшний день {now.year}/{now.month}/{now.day} рейтинги команд такие...\n\n"+final_text+"\nВесь список и таблицу рейтинга можна увидеть по этой ссылке\n"+url)

    if message.text == 'LIVE!':
        url = 'https://www.hltv.org'
        r = requests.get(url+'/matches')
        soup = BeautifulSoup(r.text, 'lxml')
        item_1 = soup.find('div', class_ = 'liveMatchesContainer')
        item_2 = soup.find('div', class_ = 'upcomingMatchesSection')
        urls_upcoming = []
        urls_live = []
        live_links = []

        #live
        if item_1 != []:
            if not os.path.isdir(f'.\LIVE_banners\{str(message.chat.id)}'):
                os.mkdir(f'.\LIVE_banners\{str(message.chat.id)}')
            try: 
                for i in item_1.findAll('a', class_ = 'match a-reset'):
                    linkLive = str(i.get('href'))
                    urls_live.append(linkLive)

                for n, h in enumerate(urls_live, start = 1):
                    newUrl = url + h
                    name_spis = []
                    mapName_str = ''
                    teamName_spis = []
                    live_links.append(newUrl)
                    response = requests.get(newUrl)
                    soup1 = BeautifulSoup(response.text, 'lxml')
                    linkfind = soup1.find('div', class_ = 'stream-box hltv-live gtSmartphone-only')
                    mapsNamefind = soup1.find_all('div', class_ = 'mapholder')
                    teamNamefind1 = soup1.find('div', class_ = 'team1-gradient')
                    teamNamefind2 = soup1.find('div', class_ = 'team2-gradient')
            
                    for i in mapsNamefind:
                        mapName = i.find('div', class_ = 'mapname').text          
                        mapName_str += mapName + ' '
                    for j in (teamNamefind1, teamNamefind2):
                        for i in j:
                            teamName = i.find('div', class_ = 'teamName').text
                            teamName_spis.append(teamName)
                    for i in linkfind.findAll('a'):
                        global link_live_match
                        link_live_match = str(i.get('href'))
                    options = ChromeOptions()
                    options.headless = True
                    driver = webdriver.Chrome(options=options)
                    driver.get(newUrl)
                    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']"))).click()
                    element = driver.find_elements_by_class_name('match-page')
                    time.sleep(1)
                    
                    for elem in element:
                        elem.screenshot(f'.\LIVE_banners\{str(message.chat.id)}\{n}.png')
                        img = Image.open(rf'.\LIVE_banners\{str(message.chat.id)}\{n}.png')
                        size = img.size
                        width, height = img.size
                        img_crop = img.crop((0, 0, width, height-619))
                        img_crop.save(f'.\LIVE_banners\{str(message.chat.id)}\{n}.png')
                        bot.send_photo(message.chat.id, open(f'.\LIVE_banners\{str(message.chat.id)}\{n}.png', 'rb'), caption = f'{teamName_spis[0]} - {teamName_spis[1]}\n\nВыбранные карты: {mapName_str}\n\nСсылка на матч - {url+link_live_match}')
                        os.remove(f'.\LIVE_banners\{str(message.chat.id)}\{n}.png')
                    driver.quit()

            except:
                bot.send_message(message.chat.id, "В данный момент НЕТ никаких ОНЛАЙН-матчей, либо возникла какая-то ошибка!")

        
bot.polling(none_stop = True, interval = 0)

