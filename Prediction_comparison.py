import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta
import glob
import os
from pathlib import Path
import pandas as pd


def Prediction_comparison(the_date=None):

    new_to_predict = 30
    average_to_display = 7  # default value that can be changed for each plot

    class Data:

        objects = []

        def __init__(self, raw, color_bar, color_plot, title, order, new_average_to_display=None):
            self.raw = raw
            self.color_bar = color_bar
            self.color_plot = color_plot
            self.color_pred = color_plot
            self.title = title
            self.order = order

            if new_average_to_display != None:
                self.average_to_display = new_average_to_display
            else:
                self.average_to_display = average_to_display

            self.dates = {'tidied': [], 'predicted': []}

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
            return new_data

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

        def predict(self, av_list, pr_list, smooth=True):

            def smoothen(list_, step=2, start=0):

                valid_values = []
                for i in range(len(list_) - start):
                    if i % step + start == 0:
                        valid_values.append(list_[i])

                new_list = []
                for i in range(len(valid_values) - 1):
                    new_list.append(valid_values[i])
                    move = (valid_values[i+1] - valid_values[i]) / step
                    for j in range(step - 1):
                        new_value = valid_values[i] + move * (j + 1)
                        new_list.insert(1+step*i+j, new_value)

                new_list.append(valid_values[-1])
                for i in range(start):
                    new_list.insert(i, list_[i])
                return new_list

            def dirivative_II(list_, start):
                first = list_[start]
                second = list_[start + 1]
                third = list_[start + 2]

                dirivative_I_1 = second / first
                dirivative_I_2 = third / second
                dirivative_II = (dirivative_I_1 + dirivative_I_2) / 2
                return dirivative_II

            def find_third_of_dirivative_II(list_, start, dirivative_II):
                first = list_[start]
                second = list_[start + 1]

                third = 2 * dirivative_II * second - second**2 / first
                return third

            final_pred = [0 for x in range(
                new_to_predict + 1 + 2 * int((av_list[-1]-1)/2))]

            for av in av_list:
                for pr in pr_list:

                    list_ = self.round_(av)

                    dir_II = 0
                    for i in range(pr - 1):
                        dir_II += dirivative_II(list_, -(pr - 1 + i))
                    dir_II /= pr - 1

                    pred = list_[-2:]
                    for i in range(new_to_predict + int((av_list[-1]-1)/2)):
                        pred.append(
                            find_third_of_dirivative_II(pred, i, dir_II))
                    pred.pop(0)

                    if smoothen == True:
                        pred = smoothen(pred, step=2, start=0)

                    for i, each in enumerate(pred):
                        final_pred[i + int((av - 1) / 2)] += each

                    if av == av_list[-1] and pr == pr_list[-1]:
                        final_pred = final_pred[int(
                            (av_list[-1]-1)/2): -int((av_list[-1]-1)/2)]
                        for i, each in enumerate(final_pred):
                            final_pred[i] /= len(av_list) * len(pr_list)
                        final_pred = smoothen(final_pred, step=2, start=0)
                        return final_pred[:new_to_predict + 1]

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

    tested.fix_mistake(160)

    for obj in Data.objects:
        obj.average = obj.round_(obj.average_to_display)
        obj.prediction = obj.predict(av_list=[3, 5, 7, 9, 11], pr_list=[
            5, 6, 7, 8, 9, 10, 11, 12, 13])
        obj.prediction1 = obj.predict(
            av_list=[3, 5, 7], pr_list=[5, 6, 7, 8, 9])
        obj.prediction2 = obj.predict(
            av_list=[7, 9, 11], pr_list=[9, 10, 11, 12, 13])

    dates = file['Date'].tolist()[:delta]
    dates_datetime = [datetime.strptime(d, '%d.%m.%Y').date() for d in dates]

    for obj in Data.objects:
        obj.dates['predicted'].append(datetime.strptime(
            dates[-int((obj.average_to_display - 1) / 2)], '%d.%m.%Y'))
        for i in range(new_to_predict):
            new_day = obj.dates['predicted'][i] + timedelta(days=1)
            obj.dates['predicted'].append(new_day)

    print('Creating plots...')

    my_dpi = 100
    plt.figure(figsize=(2100 / my_dpi, 2970 / my_dpi), dpi=my_dpi)
    plt.style.use('seaborn-poster')

    sides = ['top', 'right', 'left']
    formatter = mdates.DateFormatter("%Y-%m-%d")
    locator = mdates.MonthLocator()

    for obj in Data.objects:
        plt.subplot(6, 1, obj.order)
        ax = plt.gca()
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(locator)
        plt.tick_params(labelright=True)
        for side in sides:
            ax.spines[side].set_visible(False)
        ax.grid(zorder=0, color='gainsboro', linewidth=0.6)
        ax.bar(dates_datetime, obj.raw, width=0.6, align='center',
               color=obj.color_bar, zorder=3, alpha=0.9)
        ax.plot(dates_datetime[:-int((obj.average_to_display - 1) / 2)],
                obj.average, '-.', color=obj.color_plot, zorder=5)
        ax.plot(obj.dates['predicted'], obj.prediction,
                ':', color=obj.color_pred, zorder=4)
        # ax.plot(obj.dates['predicted'], obj.prediction1, ':', color=obj.color_pred, zorder=4)
        # ax.plot(obj.dates['predicted'], obj.prediction2, ':', color=obj.color_pred, zorder=4)
        ax.fill_between(obj.dates['predicted'][int((obj.average_to_display-1)/2):], obj.prediction1[int((obj.average_to_display-1)/2):],
                        obj.prediction[int((obj.average_to_display - 1) / 2):], color=obj.color_bar, alpha=0.5, zorder=2)
        ax.fill_between(obj.dates['predicted'][int((obj.average_to_display-1)/2):], obj.prediction[int((obj.average_to_display-1)/2):],
                        obj.prediction2[int((obj.average_to_display-1)/2):], color=obj.color_bar, alpha=0.5, zorder=2)
        plt.axvline(x=dates_datetime[-1]+timedelta(days=1),
                    zorder=6, color='#999999', linewidth=1.5)
        plt.title(obj.title)

    plt.tight_layout()
    # plt.subplots_adjust(hspace=0.7)

    Path("png").mkdir(parents=True, exist_ok=True)
    plt.savefig(f'png/Prediction_comparison.{dates[-1]}.png')

    plt.close('all')


if __name__ == '__main__':
    Prediction_comparison()
    list_of_files = glob.glob('png/*.png')
    latest_file = max(list_of_files, key=os.path.getmtime)
    os.system(latest_file)
