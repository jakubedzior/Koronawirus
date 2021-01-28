import datetime
import pandas as pd
from time import sleep
import glob
import os
from selenium import webdriver
import webbrowser
import pyperclip
from pynput.keyboard import Key, Controller


def await_new_copy():
    clipboard_old = pyperclip.paste()
    while True:
        sleep(1)
        clipboard_new = pyperclip.paste()
        if clipboard_old != clipboard_new:
            return clipboard_new


def await_url_change(link, driver):
    while True:
        sleep(1)
        url_new = driver.current_url
        if link != url_new:
            return url_new


def check_url(driver):
    url = driver.current_url
    if url[:-5] == 'https://archive.vn/' or \
       url[:-5] == 'https://archive.vn/wip/':
        return url[-5:]
    else:
        return None


def insert_coma(number):
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


def front_zero(date):
    if date[0] == '0':
        date = date[1:]
        return date
    else:
        return date


def create_day(previous_data, date, source_code, links=None):

    try:
        driver.find_element_by_xpath(
            '//*[@id="layers"]/div/div[2]/div/div/div/div[2]/div').click()
    except:
        pass

    new_date = date + datetime.timedelta(days=1)
    print(f'\nEnter data for: {new_date}:')

    data = {'Quarantined': 0,
            'Monitored': 0,
            'Recovered': 0,
            'Confirmed': 0,
            'Deaths': 0,
            'Tested': 0,
            'Recovered daily': 0,
            'Confirmed daily': 0,
            'Deaths daily': 0,
            'Active': 0}

    for category, _ in zip(data, range(6)):
        data[category] = int(input(f'{category}: '))

    data['Recovered daily'] = data['Recovered'] - previous_data['Recovered']
    data['Confirmed daily'] = data['Confirmed'] - previous_data['Confirmed']
    data['Deaths daily'] = data['Deaths'] - previous_data['Deaths']
    data['Active'] = previous_data['Active'] + \
        data['Confirmed daily'] - \
        data['Recovered daily'] - \
        data['Deaths daily']

    previous_data_archive = {'Deaths': 0,
                             'Recovered': 0,
                             'Confirmed': 0,
                             'Active': 0}
    previous_data_archive['Deaths'] = previous_data['Deaths']
    previous_data_archive['Recovered'] = previous_data['Recovered']
    previous_data_archive['Confirmed'] = previous_data['Confirmed']
    previous_data_archive['Active'] = previous_data['Active']

    previous_data['Deaths'] = data['Deaths']
    previous_data['Recovered'] = data['Recovered']
    previous_data['Confirmed'] = data['Confirmed']
    previous_data['Active'] = data['Active']

    for entry in data:
        data[entry] = insert_coma(data[entry])

    if links == None:
        print('\nPlease copy links to clipboard.')

        links = [await_new_copy() for i in range(3)]

    new_date_space = new_date.strftime('%d %B %Y')
    new_date_space = front_zero(new_date_space)
    new_date_dash = new_date.strftime('%Y-%m-%d')

    today = datetime.date.today()
    today_date_dash = today.strftime('%Y-%m-%d')

    refs = []
    for tweet in links:
        ref = f'<ref>{{{{Cite news|date={new_date_dash}|title=Tweet|url={tweet}|url-status=live|quote=Dzienny raport o #koronawirus.}}}}</ref>'
        refs.append(ref)

    print()
    while True:
        next_ = input('Next day (n), Finish (f), Correct (c): ')
        if next_ in ['n', 'f', 'c']:
            break

    if next_ == 'c':
        create_day(previous_data_archive, new_date - datetime.timedelta(days=1),
                   source_code, links=links)

    if len(source_code) > 1:
        source_code += '\n'

    source_code += f"""\
|-
|{new_date_space}
|{data["Quarantined"]}
|{data["Monitored"]}
|{data["Tested"]}
|{data["Confirmed daily"]}
|{data["Confirmed"]}
|{data["Active"]}
|{data["Recovered daily"]}
|{data["Deaths daily"]}
|
|{refs[0]}{refs[1]}{refs[2]}"""

    if next_ == 'f':
        source_code += f"""
|- class="sortbottom"
|'''Total'''
|N/A
|N/A
|{data["Tested"]}<!-- tests -->
|N/A
|{data["Confirmed"]}{{{{efn|+ at least 1000 unofficial cases, sources: [https://www.jsw.pl/media/wydarzenia/artykul/kolejne-przypadki-zachorowan], [https://twitter.com/martalena123/status/1268818898314502144]}}}}<!-- total lab-confirmed -->
|N/A<!-- total active cases -->
|'''{data['Recovered']}'''<!-- total recovered -->
|'''{data['Deaths']}'''<!-- total official deaths -->
|'''9'''<!-- total unofficial deaths -->"""

        pyperclip.copy(source_code)
        webbrowser.open(
            'https://en.wikipedia.org/w/index.php?title=Template:COVID-19_pandemic_data/Poland_medical_cases&action=edit')

    if next_ == 'n':
        create_day(previous_data, new_date, source_code)


list_of_files = glob.glob(
    'csv/*.csv')
latest_file = max(list_of_files, key=os.path.getmtime)

file = pd.read_csv(latest_file)

date = file['Date'].tolist()[-1]

date = date.split('.')
date = date[2] + '-' + date[1] + '-' + date[0]
date = datetime.date.fromisoformat(date)

print(f'Latest update on {date}')

previous_data = {'Deaths': 0,
                 'Recovered': 0,
                 'Confirmed': 0,
                 'Active': 0}

previous_data['Deaths'] = file['Deaths (total)'].tolist()[-1]
previous_data['Recovered'] = file['Recovered (total)'].tolist()[-1]
previous_data['Confirmed'] = file['Confirmed (total)'].tolist()[-1]
previous_data['Active'] = file['Active (total)'].tolist()[-1]

source_code = ''
tweeter_url = 'https://twitter.com/MZ_GOV_PL'

keyboard = Controller()
keyboard.press(Key.cmd)
keyboard.press(Key.right)
keyboard.release(Key.cmd)
keyboard.release(Key.right)

driver = webdriver.Chrome()
driver.get(tweeter_url)

keyboard.press(Key.cmd)
keyboard.press(Key.left)
keyboard.release(Key.cmd)
keyboard.release(Key.left)

create_day(previous_data, date, source_code)
