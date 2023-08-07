import telebot
from telebot import types

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import datetime
import time
from PIL import Image
import os
from dotenv import dotenv_values

if os.environ.get("TELEBOT_TOKEN"):
    TElEBOT_TOKEN=os.environ.get("TELEBOT_TOKEN")
else:
    TElEBOT_TOKEN=dotenv_values(".env").get("TELEBOT_TOKEN")
bot = telebot.TeleBot(TElEBOT_TOKEN)
now = datetime.datetime.now()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
}

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Новости')
    keyboard.row('Рейтинг', 'LIVE!')
    bot.send_message(message.chat.id, 'Привіт! Чим можу допомогти? Дізнайтесь все що Вам потрібно по грі CS:GО прямо зараз', reply_markup=keyboard)


@bot.message_handler(content_types = ['text'])
def get_text_messages(message):
    if message.text == 'Новости':
        url = "https://www.hltv.org"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.findAll('a', class_ = 'newsline')[:5]
        
        count = 1
        for i in items:
            newsName = i.find('div', class_ = 'newstext').text
            newUrl = url + i.get("href")
            
            item_r = requests.get(newUrl, headers=headers)
            item_soup = BeautifulSoup(item_r.text, 'lxml')
            newsText = item_soup.find('p', class_='news-block').text
            
            
            bot.send_message(message.chat.id, f'{count}: {newsName}\n\n{newsText}..\n\n{newUrl}\n\n')
            count += 1            


    if message.text == 'Рейтинг':
        url = 'https://www.hltv.org/ranking/teams/'
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        items = soup.find_all('div', class_ = 'ranked-team standard-box')[:5]
        
        final_text = ''

        for n, i in enumerate(items, start = 1):
            rankingName = i.find('span', class_ = 'name').text
            rankingScore = i.find('span', class_ = 'points').text
            final_text += f'#{n}: {rankingName} --> {rankingScore}\n'
            
        bot.send_message(message.chat.id, f"На сьогодняшній день {now.year}/{now.month}/{now.day} рейтинги команд такі...\n\n"+final_text+"\nВесь список и таблицу рейтинга можна увидеть по этой ссылке\n"+url)


    if message.text == 'LIVE!':
        url = 'https://www.hltv.org'

        bot.send_message(message.chat.id, f"Секундочку...")

        options = uc.ChromeOptions() 
        options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = uc.Chrome(service=Service(ChromeDriverManager().install()), use_subprocess=True, options=options)
        driver.get(url+'/matches')
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        live_matches_container = soup.find('div', class_ = 'liveMatchesContainer')

        #live
        if live_matches_container:
            if not os.path.isdir(f'.\LIVE_banners\{str(message.chat.id)}'):
                os.mkdir(f'.\LIVE_banners\{str(message.chat.id)}')
            try: 
                for i in live_matches_container.findAll('a', class_ = 'match a-reset'):
                    newUrl = url + i.get('href')
                    driver.get(newUrl)
                    soup_item = BeautifulSoup(driver.page_source, 'lxml')
                    
                    link_item = soup_item.find('div', class_ = 'stream-box hltv-live gtSmartphone-only').find("a").get('href')
                    map_names = '\n  '.join([x.text.strip() for x in soup_item.findAll('div', class_ = 'map-name-holder')])
                    teams_name = [x.text for x in soup_item.findAll('div', class_ = 'teamName')]

                    try:
                        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']"))).click()
                        time.sleep(1)
                    except:
                        pass
                    
                    element = driver.find_element(By.CLASS_NAME, "teamsBox")
                    element.screenshot(f'.\LIVE_banners\{str(message.chat.id)}\{1}.png')
                    with open(f'.\LIVE_banners\{str(message.chat.id)}\{1}.png', 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, caption = f'{teams_name[0]} - {teams_name[1]}\n\nОбрані карти:\n  {map_names}\n\nПосилання на матч - {url}{link_item}')

                    os.remove(f'.\LIVE_banners\{str(message.chat.id)}\{1}.png')    

                bot.send_message(message.chat.id, f"Це всі LIVE-матчі на даний момент")
                driver.quit()

            except Exception as e:
                print(e)
                bot.send_message(message.chat.id, "Виникла якась помилка!")
        else:
            bot.send_message(message.chat.id, "В даний момент НЕМАЄ ніяких ОНЛАЙН-матчів!")

        
bot.polling(none_stop = True, interval = 0)

