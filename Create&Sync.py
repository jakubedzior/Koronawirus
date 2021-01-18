from github import Github
from datetime import datetime, timedelta
import glob
import os
from pathlib import Path
from time import sleep

from Comparison import Comparison
from Prediction_comparison import Prediction_comparison
from Clear import Clear


def Git_commands():
    print('Leveling repositories...')
    orig_path = os.getcwd()
    os.chdir(git_path)
    os.system('git fetch')
    os.system('git add -A')
    os.system('git commit -m "photo"')
    os.system('git push')
    os.chdir(orig_path)


def get_dates(type_, repo):

    print('Getting dates...')

    uploaded = []
    try:
        for year_content in repo.get_contents(f'Results'):
            path = year_content.path
            year = path.split('/')[-1]
            try:
                for month_content in repo.get_contents(f'Results/{year}'):
                    path = month_content.path
                    month = path.split('/')[-1]
                    try:
                        for file_content in repo.get_contents(f'Results/{year}/{month}/{type_}'):
                            uploaded.append(file_content.path[-14:-4])
                    except:
                        continue
            except:
                continue
    except:
        pass

    uploaded_datetime = [datetime.strptime(u, '%d.%m.%Y') for u in uploaded]
    if len(uploaded_datetime) == 0:
        oldest_uploaded = input(
            'No uploads found. Enter initial date (dd.mm.yyyy): ')
        oldest_uploaded = datetime.strptime(oldest_uploaded, '%d.%m.%Y')
        oldest_uploaded = oldest_uploaded - timedelta(1)
    else:
        oldest_uploaded = min(uploaded_datetime)

    list_of_files = glob.glob('csv/*.csv')
    latest_file = max(list_of_files, key=os.path.getmtime)
    latest_data = latest_file[-19:-9]
    latest_data = datetime.strptime(latest_data, '%d.%m.%Y')

    delta = latest_data - oldest_uploaded
    delta = delta.days
    if delta < 0:
        delta = 0

    all_since_oldest = []
    for i in range(delta):
        all_since_oldest.append((oldest_uploaded + timedelta(1 + i)))

    dates_datetime = list(set(all_since_oldest) - set(uploaded_datetime))
    dates_datetime.sort()

    dates = [datetime.strftime(d, '%d.%m.%Y') for d in dates_datetime]

    return dates


# path to your github repository
git_path = 'C:/Users/jakub/Desktop/Programming/GitHub/Koronawirus'

g = Github(os.environ.get('github_access_token'))
repo = g.get_user().get_repo('Koronawirus')

types = [('Standard', 'Comparison'),
         ('With predictions', 'Prediction_comparison')]

for folder, filename in types:
    dates = get_dates(folder, repo)
    # dates = ['06.03.2020', '15.04.2020']

    if len(dates) == 0:
        print(f'{filename} folder is up to date.')

    for date in dates:
        print(f'\nCreating {filename} for {date}:')
        if not os.path.isfile(f'png/{filename}.{date}.png'):
            if filename == 'Comparison':
                try:
                    Comparison(date)
                except:
                    print('Can\'t create a plot.\n')
                    continue
            elif filename == 'Prediction_comparison':
                try:
                    Prediction_comparison(date)
                except:
                    print('Can\'t create a plot.\n')
                    continue

        sleep(1)
        print('Moving file...')
        date_datetime = datetime.strptime(date, '%d.%m.%Y')
        year = date_datetime.strftime('%Y')
        month = date_datetime.strftime('%B')

        new_path = f'{git_path}/Results/{year}/{month}/{folder}'
        Path(new_path).mkdir(parents=True, exist_ok=True)
        os.replace(f'png/{filename}.{date}.png', f'{new_path}/{date}.png')
    print('\n')

Git_commands()
Clear()
