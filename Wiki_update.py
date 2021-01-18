from bs4 import BeautifulSoup
import urllib.request
import datetime
from pathlib import Path
import pandas as pd
from time import sleep


def Wiki_update():

    print('Downloading data...')

    # Create target folder if doesn't exist
    Path("csv").mkdir(
        parents=True, exist_ok=True)

    # Get first table from wiki
    url = 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/Poland_medical_cases'
    try:
        thepage = urllib.request.urlopen(url)
    except urllib.error.URLError:
        print("Turn on internet connection!")
        sleep(3)
        exit()
    soup = BeautifulSoup(thepage, "html.parser")
    table = soup.find_all('table', class_="wikitable")[0]

    # Create dictionary model
    alldata = {'Date': [],
               'Quarantined (daily)': [],
               'Monitored (daily)': [],
               'Tested (total)': [],
               'Confirmed (daily)': [],
               'Confirmed (total)': [],
               'Active (total)': [],
               'Recovered (daily)': [],
               'Deaths (daily)': []
               }

    # Get out of any nested loops if necessary
    class GetOutOfLoops(Exception):
        pass

    # Cut out annotations if necessary
    def cut_sqbr(cell):
        open_sqbr = cell.index('[')
        close_sqbr = cell.index(']')
        cell = cell[:open_sqbr] + cell[close_sqbr + 1:]

        if '[' in cell:
            return cut_sqbr(cell)
        return cell

    # Cut out comas in numbers if necessary
    def cut_coma(cell):
        coma = cell.index(',')
        cell = cell[:coma] + cell[coma + 1:]

        if ',' in cell:
            return cut_coma(cell)
        return cell

    # Save table to created dictionary
    try:
        for row_index, record in enumerate(table.findAll('tr')):
            # Skip first 4 rows of table
            if row_index < 5:
                continue

            for data, key in zip(record.findAll('td'), alldata):
                cell = data.text[:-1]

                # Quit when realised that table content has ended
                if cell == 'Total':
                    raise GetOutOfLoops

                cell = list(cell)
                # Cut out annotations
                if '[' in cell:
                    cell = cut_sqbr(cell)
                # Cut out comas in numbers
                if ',' in cell:
                    cell = cut_coma(cell)

                cell = ''.join(cell)
                alldata[key].append(cell)
    except GetOutOfLoops:
        pass

    # Change all dates format
    months = [['January',   '01'],
              ['February',  '02'],
              ['March',     '03'],
              ['April',     '04'],
              ['May',       '05'],
              ['June',      '06'],
              ['July',      '07'],
              ['August',    '08'],
              ['September', '09'],
              ['October',   '10'],
              ['November',  '11'],
              ['December',  '12']]
    for date_index, date in enumerate(alldata['Date']):
        date = date.replace(' ', '.')

        for month in months:
            date = date.replace(month[0], month[1])

        alldata['Date'][date_index] = date

    # Get today's date
    today = datetime.date.today()
    today = today.strftime('%d.%m.%Y')

    # Change table data day format
    for index, date in enumerate(alldata['Date']):
        if len(date.split('.')[0]) == 1:
            date = list(date)
            date.insert(0, '0')
            date = ''.join(date)
            alldata['Date'][index] = date

    # Delete last table row if it's today's
    final_date = alldata['Date'][-1]
    # if alldata['Date'][-1] == today:
    #     for key in alldata:
    #         alldata[key].pop(-1)
    #     final_date = alldata['Date'][-1]

    # Save all data to new csv file
    df = pd.DataFrame(alldata)
    df.to_csv(f'csv/Wikidata.{final_date}.csv', index=False, header=True)


Wiki_update()
