import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import glob
import os
from pathlib import Path
import pandas as pd


def Comparison(the_date=None):

    class Data:
        objects = []

        def __init__(self, raw, color_bar, color_plot, title, order):
            self.raw = raw
            self.average = None
            self.color_bar = color_bar
            self.color_plot = color_plot
            self.title = title
            self.order = order

            Data.objects.append(self)

        def round_(self, ofsurr_):
            if ofsurr_ % 2 == 0:
                ofsurr_ += 1
            new_data = [None for x in range(int((ofsurr_ - 1) / 2))]
            for i in range(len(self.raw) - ofsurr_ + 1):
                average_variable = 0
                for j in range(ofsurr_):
                    average_variable += self.raw[ofsurr_ - 1 + i - j]
                average_variable /= ofsurr_
                average_variable = round(average_variable, 3)
                new_data.append(average_variable)
            new_data += [None for x in range(int((ofsurr_ - 1) / 2))]
            self.average = new_data

        def fix_mistake(self, index):
            if len(self.raw) < index + 2:
                return
            number_original = self.raw[index]
            number_new = (self.raw[index - 1] + self.raw[index + 1]) / 2
            mistake = number_new - number_original

            self.raw[index] = number_new
            all_before_index = 0
            for i, each in enumerate(self.raw):
                if i >= index:
                    break
                all_before_index += each
            fine_fraction = 1 - mistake / all_before_index
            for i, each in enumerate(self.raw):
                if i >= index:
                    break
                self.raw[i] = each * fine_fraction

    print('Getting data...')

    list_of_files = glob.glob('csv/*.csv')
    latest_file = max(list_of_files, key=os.path.getmtime)

    if the_date != None:
        latest_date = latest_file[-19:-9]
        latest_date = datetime.strptime(latest_date, '%d.%m.%Y')
        the_date = datetime.strptime(the_date, '%d.%m.%Y')

        delta = latest_date - the_date
        delta = delta.days
        if delta == 0:
            delta = None
        else:
            delta = -delta
    else:
        delta = None

    file = pd.read_csv(latest_file)

    active = Data(
        raw=file['Active (total)'].tolist()[:delta],
        color_bar='#EAD2AE',
        color_plot='orange',
        title='\nŁączna ilość osób chorujących każdego dnia',
        order=1,
    )
    confirmed = Data(
        raw=file['Confirmed (daily)'].tolist()[:delta],
        color_bar='#FBBAA0',
        color_plot='firebrick',
        title='\nNowo wykryte przypadki zarażeń każdego dnia',
        order=2,
    )
    deaths = Data(
        raw=file['Deaths (daily)'].tolist()[:delta],
        color_bar='#D8D8D8',
        color_plot='dimgray',
        title='\nPrzypadki śmiertelne każdego dnia',
        order=3,
    )
    recovered = Data(
        raw=file['Recovered (daily)'].tolist()[:delta],
        color_bar='#B9EBC9',
        color_plot='olivedrab',
        title='\nWyzdrowienia każdego dnia',
        order=4,
    )
    tested = Data(
        raw=file['Tested (daily)'].tolist()[:delta],
        color_bar='#C5E7F0',
        color_plot='lightseagreen',
        title='\nIlość przeprowadzonych testów każdego dnia',
        order=5,
    )
    quarantined = Data(
        raw=file['Quarantined (daily)'].tolist()[:delta],
        color_bar='#AED0EA',
        color_plot='royalblue',
        title='\nOsoby objęte kwarantanną każdego dnia',
        order=6,
    )
    dates_raw = file['Date'].tolist()[:delta]

    tested.fix_mistake(160)

    for obj in Data.objects:
        obj.round_(7)

    print('Creating plots...')

    my_dpi = 100
    plt.figure(figsize=(2100 / my_dpi, 2970 / my_dpi), dpi=my_dpi)
    plt.style.use('seaborn-poster')

    sides = ['top', 'right', 'left']
    formatter = mdates.DateFormatter("%Y-%m-%d")
    locator = mdates.MonthLocator()
    dates = [datetime.strptime(d, '%d.%m.%Y').date() for d in dates_raw]

    for obj in Data.objects:
        plt.subplot(6, 1, obj.order)
        ax = plt.gca()
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(locator)
        plt.tick_params(labelright=True)
        for side in sides:
            ax.spines[side].set_visible(False)
        ax.grid(zorder=0, color='gainsboro', linewidth=0.6)
        ax.bar(dates, obj.raw, width=0.7, align='center',
               color=obj.color_bar, zorder=3)
        ax.plot(dates, obj.average, '-.', color=obj.color_plot, zorder=4)
        plt.title(obj.title)

    plt.tight_layout()
    # plt.subplots_adjust(hspace=0.7)

    Path("png").mkdir(parents=True, exist_ok=True)
    plt.savefig(f'png/Comparison.{dates_raw[-1]}.png')

    plt.close('all')


if __name__ == '__main__':
    Comparison()
    list_of_files = glob.glob('png/*.png')
    latest_file = max(list_of_files, key=os.path.getmtime)
    os.system(latest_file)
