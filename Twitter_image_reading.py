import datetime
from pathlib import Path
import pandas as pd
from time import sleep
import csv
import glob
import os
import sys
from selenium import webdriver
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import webbrowser
import pyperclip
from pynput.mouse import Button, Controller as mController
from pynput.keyboard import Key, Controller as kController, Listener
from urllib.request import urlretrieve
from pyautogui import locateOnScreen

from ImageOperations import *


def awaitNewCopy():
    clipboard_old = pyperclip.paste()
    while True:
        sleep(1)
        clipboard_new = pyperclip.paste()
        if clipboard_old != clipboard_new:
            return clipboard_new


def insertComa(number):
    number_list = list(str(number))
    lenght = len(number_list)
    comas = lenght // 3
    reminder = lenght % 3

    if reminder == 0:
        skip = True
        comas -= 1
    else:
        skip = False

    for i in range(comas):
        number_list.insert(reminder + i + i*3 + (3 if skip else 0), ',')
    return ''.join(number_list)


def frontZero(date):
    if date[0] == '0':
        date = date[1:]
        return date
    else:
        return date


def retrieveNums(string):
    string = string[string.find('/') - 12:string.find('/') + 10]
    string = string.split('/')

    while True:
        if not string[0][0].isnumeric():
            string[0] = string[0][1:]
        else:
            break
    while True:
        index = string[0].find(' ')
        if index == -1:
            break
        string[0] = string[0][:index] + string[0][index + 1:]

    while True:
        if not string[1][-1].isnumeric():
            string[1] = string[1][:-1]
        else:
            break
    while True:
        index = string[1].find(' ')
        if index == -1:
            break
        string[1] = string[1][:index] + string[1][index + 1:]

    return int(string[0]), int(string[1])


def on_release(key):
    global decision
    try:
        if key.char == '1':
            decision = (1, 0)
        if key.char == '2':
            decision = (2, 0)
        if key.char == '-':
            decision = (-2, decision[0])
        if key.char == '0':
            decision = (-3, 0)
    except AttributeError:  # special key
        if key == Key.tab:
            decision = (-1, 0)
    listener.stop()


data_template = {
    'Quarantined': 0,
    'Monitored': 0,
    'Recovered': 0,
    'Confirmed': 0,
    'Deaths': 0,
    'Tested': 0,
    'Recovered daily': 0,
    'Confirmed daily': 0,
    'Deaths daily': 0,
    'Active': 0
}
final_data = {}


list_of_files = glob.glob(
    'csv/*.csv')
latest_file = max(list_of_files, key=os.path.getmtime)

file = pd.read_csv(latest_file)

date = file['Date'].tolist()[-1]
date = date.split('.')
date = date[2] + '-' + date[1] + '-' + date[0]
date = datetime.date.fromisoformat(date)

final_data[-1] = {'Deaths': 0,
                  'Recovered': 0,
                  'Confirmed': 0,
                  'Active': 0}
final_data[-1]['Deaths'] = file['Deaths (total)'].tolist()[-1]
final_data[-1]['Recovered'] = file['Recovered (total)'].tolist()[-1]
final_data[-1]['Confirmed'] = file['Confirmed (total)'].tolist()[-1]
final_data[-1]['Active'] = file['Active (total)'].tolist()[-1]


mouse = mController()
keyboard = kController()
with keyboard.pressed(Key.cmd):
    keyboard.press(Key.right)
    keyboard.release(Key.right)

new_date = date + datetime.timedelta(days=1)

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
LOGGER.setLevel(logging.WARNING)
driver = webdriver.Chrome(options=options)
driver.get(
    f'https://twitter.com/search?q=(%23koronawirus)%20(from%3AMZ_GOV_PL)%20since%3A{new_date}%20-filter%3Areplies&src=typed_query&f=live')

with keyboard.pressed(Key.cmd):
    keyboard.press(Key.left)
    keyboard.release(Key.left)

try:
    driver.find_element_by_xpath(
        '//*[@id="layers"]/div/div[2]/div/div/div/div[2]/div').click()
except:
    pass


source_code = ''
image_adresses = []
url_adresses = []
url_adresses_text = []
temp_data = []
decision = (0, 0)

print('''\
Instructions:

On the 1st website:
press 1 on an image to copy it's credentials,
press 2 on post's date to copy it's link,
press 0 to reset previous command,
press tab to continue the next website.

On the 2nd website:
select text and press either 1, 2 or tab to copy numbers embedeed in it.
''')

while True:
    with Listener(on_release=on_release) as listener:
        listener.join()
    if decision[0] == 1:
        mouse.press(Button.right)
        mouse.release(Button.right)
        sleep(0.05)
        keyboard.press('o')  # get image adress
        keyboard.release('o')
        sleep(0.05)
        image_adresses.append(pyperclip.paste())
        sleep(0.05)

        mouse.press(Button.right)
        mouse.release(Button.right)
        sleep(0.05)
        keyboard.press('e')  # get link adress
        keyboard.release('e')
        sleep(0.05)
        url_adresses.append(pyperclip.paste())
    if decision[0] == 2:
        mouse.press(Button.right)
        mouse.release(Button.right)
        sleep(0.05)
        keyboard.press('e')  # get link adress
        keyboard.release('e')
        sleep(0.05)
        url_adresses_text.append(pyperclip.paste())
    if decision[0] == -1:
        break
    if decision[0] == -2:
        if decision[1] == 1:
            image_adresses.pop(0)
            url_adresses.pop(0)
        if decision[1] == 3:
            url_adresses_text.pop(0)
    if decision[0] == -3:
        url_adresses = []
        url_adresses_text = []
days = int(len(image_adresses) / 2)

driver.get(
    f'https://twitter.com/search?q=%22wszystkie%20pozytywne%20przypadki%2Fw%20tym%20osoby%20zmar%C5%82e%22%20(from%3AMZ_GOV_PL)%20since%3A{new_date}%20filter%3Areplies%20-filter%3Alinks&src=typed_query&f=live')
while True:
    with Listener(on_release=on_release) as listener:
        listener.join()
    if decision[0] in [-1, 1, 2]:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        sleep(0.05)
        temp_data.append(retrieveNums(pyperclip.paste()))
    if decision[0] == -2:
        temp_data.pop(0)
    if decision[0] == -3:
        temp_data = []
    if len(temp_data) == days:
        break


driver.close()
print('Processing data...')

for i, adress in enumerate(image_adresses):
    index = adress.find('jpg')
    adress = adress[:index] + 'png' + adress[index + 3:]
    adress = adress[:-5] + '4096x4096'
    image_adresses[i] = adress

for i, adress in enumerate(url_adresses):
    url_adresses[i] = adress[:-8]


def latestFile(extension):
    list_of_files = glob.glob(f'*{extension}')
    return max(list_of_files, key=os.path.getmtime)


class template:
    scale = 1  # 680 / 2500

    def __init__(self, pos, size):
        self.pos = (int(self.scale * pos[0]), int(self.scale * pos[1]))
        self.size = (int(self.scale * size[0]), int(self.scale * size[1]))


params = {
    0: {
        "Quarantined": template((350, 1000), (600, 200)),
        "Monitored": template((1100, 1000), (600, 200)),
        "Recovered": template((1850, 1000), (600, 200))
    },
    1: {
        "Tested": template((50, 850), (500, 200))
    }
}


class Count:

    def __init__(self, _list, start=0):
        if isinstance(_list, range):
            _list = list(_list)
        self.index = start
        self.list = _list

        self.current = self.list[self.index]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self.current = self.list[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1
        return self.current

    def __repr__(self):
        return self.current

    def __str__(self):
        return str(self.current)

    def previous(self):
        self.index -= 1
        if self.index == -1:
            raise IndexError('Can\'t go back anymore.')


os.chdir(os.getcwd() + '\\Image recognition')

iterator = Count(range(days))
for day in iterator:
    final_data[day] = data_template.copy()

    try:
        for param in params:
            urlretrieve(image_adresses[2*day + param], 'picture.png')
            convertImage('picture.png', 220)
            template = latestFile('.png')

            for key in params[param]:
                scaleImage(template, 2500, 1407)
                cropImage(template, params[param]
                          [key].pos, params[param][key].size)
                number = readNumber(
                    'temp.png', ('nums_1' if param == 0 else 'nums_4'))
                final_data[day][key] = number
    except:
        print('Trying again...')
        iterator.previous()
        continue

    os.remove(template)
    os.remove('temp.png')

    final_data[day]['Confirmed'] = temp_data[day][0]
    final_data[day]['Deaths'] = temp_data[day][1]

    final_data[day]['Recovered daily'] = final_data[day]['Recovered'] - \
        final_data[day - 1]['Recovered']
    final_data[day]['Confirmed daily'] = final_data[day]['Confirmed'] - \
        final_data[day - 1]['Confirmed']
    final_data[day]['Deaths daily'] = final_data[day]['Deaths'] - \
        final_data[day - 1]['Deaths']
    final_data[day]['Active'] = final_data[day - 1]['Active'] + \
        final_data[day]['Confirmed daily'] - \
        final_data[day]['Recovered daily'] - \
        final_data[day]['Deaths daily']

    new_date_space = new_date.strftime('%d %B %Y')
    new_date_space = frontZero(new_date_space)
    new_date_dash = new_date.strftime('%Y-%m-%d')

    today = datetime.date.today()
    today_date_dash = today.strftime('%Y-%m-%d')

    refs = []
    for i in range(2):
        refs.append(
            f'<ref>{{{{Cite news|date={new_date_dash}|title=Tweet|url={url_adresses[2*day+i]}|url-status=live|quote=Dzienny raport o #koronawirus.}}}}</ref>')
    refs.append(
        f'<ref>{{{{Cite news|date={new_date_dash}|title=Tweet|url={url_adresses_text[day]}|url-status=live|quote=Dzienny raport o #koronawirus.}}}}</ref>')

    if len(source_code) > 1:
        source_code += '\n'

    source_code += f"""\
|-
|{new_date_space}
|{insertComa(final_data[day]["Quarantined"])}
|{insertComa(final_data[day]["Monitored"])}
|{insertComa(final_data[day]["Tested"])}
|{insertComa(final_data[day]["Confirmed daily"])}
|{insertComa(final_data[day]["Confirmed"])}
|{insertComa(final_data[day]["Active"])}
|{insertComa(final_data[day]["Recovered daily"])}
|{insertComa(final_data[day]["Deaths daily"])}
|
|{refs[0]}{refs[1]}{refs[2]}"""

    if day + 1 == days:
        source_code += f"""
|- class="sortbottom"
|'''Total'''
|N/A
|N/A
|{insertComa(final_data[day]["Tested"])}<!-- tests -->
|N/A
|{insertComa(final_data[day]["Confirmed"])}{{{{efn|+ at least 1000 unofficial cases, sources: [https://www.jsw.pl/media/wydarzenia/artykul/kolejne-przypadki-zachorowan], [https://twitter.com/martalena123/status/1268818898314502144]}}}}<!-- total lab-confirmed -->
|N/A<!-- total active cases -->
|'''{insertComa(final_data[day]["Recovered"])}'''<!-- total recovered -->
|'''{insertComa(final_data[day]["Deaths"])}'''<!-- total official deaths -->
|'''9'''<!-- total unofficial deaths -->"""

    print(f'Day {new_date} completed!')
    new_date = new_date + datetime.timedelta(1)

pyperclip.copy('|- class="sortbottom"')
webbrowser.open(
    'https://en.wikipedia.org/w/index.php?title=Template:COVID-19_pandemic_data/Poland_medical_cases&action=edit')

while True:
    page = locateOnScreen('Wiki_pic.png')
    if page is not None:
        break

with keyboard.pressed(Key.ctrl):
    keyboard.press('f')
    keyboard.release('f')
    keyboard.press('v')
    keyboard.release('v')
sleep(5)

pyperclip.copy(source_code)
