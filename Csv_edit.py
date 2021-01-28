import csv
import glob
import os
from time import sleep
import pandas as pd


def int_each(list_):

    for i, each in enumerate(list_):
        list_[i] = int(each)
    return list_


def get_latest(both=False):

    list_of_files = glob.glob(
        'csv/*.csv')
    latest_file = max(list_of_files, key=os.path.getmtime)

    if not both:
        return latest_file
    else:
        if latest_file[-8:] == 'edit.csv':
            orig_file = latest_file[0:-8]
            orig_file += 'csv'
            edit_file = latest_file
        else:
            orig_file = latest_file
            edit_file = latest_file[0: -3]
            edit_file += 'edit.csv'
        return orig_file, edit_file


def clean():

    orig_file, edit_file = get_latest(both=True)

    with open(orig_file, 'r') as f_read, open(edit_file, 'w+', newline='') as f_write:
        reader = csv.reader(f_read)
        writer = csv.writer(f_write)

        for i, row in enumerate(reader):

            for j, cell in enumerate(row):
                if cell == '':
                    cell = 0

                if j == 3 and i == 7:
                    cell = 1005
                elif j == 3 and i == 16:
                    cell = 6696
                elif j == 1 and i == 32:
                    cell = 176705
                elif j == 2 and i == 32:
                    cell = 49422
                # elif j == 4 and i == 148:
                #     cell = 2114778

                row[j] = cell

            writer.writerow(row)


def add_delta_column(from_, to_):

    file = pd.read_csv(get_latest())
    date = file['Date'][len(file['Date'])-1]

    data = file[from_].tolist()
    new_data = [0]
    for i, arg in enumerate(data):
        if i != 0:
            new_arg = arg - old_arg
            new_data.append(new_arg)
        old_arg = arg

    file[to_] = new_data

    file.to_csv(f'csv/Wikidata.{date}.edit.csv', index=False)


def add_total_column(from_, to_):

    file = pd.read_csv(get_latest())
    date = file['Date'][len(file['Date']) - 1]

    data = file[from_].tolist()
    new_data = [data[0]]
    for i in range(len(data) - 1):
        new_data.append(new_data[i] + data[i + 1])

    file[to_] = new_data

    file.to_csv(f'csv/Wikidata.{date}.edit.csv', index=False)


def add_average(from_, to_, ofsurr_):

    file = pd.read_csv(get_latest())
    date = file['Date'][len(file['Date']) - 1]

    data = file[from_].tolist()
    new_data = [0 for x in range(ofsurr_ - 1)]
    for i in range(len(data) - ofsurr_ + 1):
        average_variable = 0
        for j in range(ofsurr_):
            average_variable += data[ofsurr_ - 1 + i - j]
        average_variable /= ofsurr_
        average_variable = round(average_variable, 3)
        new_data.append(average_variable)

    file[to_ + f' of {ofsurr_}'] = new_data

    file.to_csv(f'csv/Wikidata.{date}.edit.csv', index=False)


def sort():

    file = pd.read_csv(get_latest())
    date = file['Date'][len(file['Date']) - 1]

    file.to_csv(f'csv/Wikidata.{date}.edit.csv', index=False,
                columns=[
                    'Date',
                    'Monitored (daily)',
                    'Quarantined (daily)',
                    'Tested (daily)',
                    'Tested (total)',
                    'Recovered (daily)',
                    'Recovered (total)',
                    'Deaths (daily)',
                    'Deaths (total)',
                    'Confirmed (daily)',
                    'Confirmed (total)',
                    'Active (daily)',
                    'Active (total)'
                ])


print('Editing data...')
clean()
add_delta_column('Tested (total)', 'Tested (daily)')
add_delta_column('Active (total)', 'Active (daily)')
add_total_column('Deaths (daily)', 'Deaths (total)')
add_total_column('Recovered (daily)', 'Recovered (total)')
sort()
# add_delta_column('Active (daily)', 'Active (daily) growth')
# add_delta_column('Confirmed (daily)', 'Confirmed (daily) growth')
# add_average('Active (daily) growth', 'Active (daily) growth average', 10)
# add_average('Confirmed (daily) growth', 'Confirmed (daily) growth average', 10)


def print_date():
    file = pd.read_csv(get_latest())
    date = file['Date'].tolist()[-1]
    print(f'Latest update on {date}')


print_date()
sleep(1)
