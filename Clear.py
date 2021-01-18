import glob
import os
from time import sleep


def Clear():
    directories = ['csv', 'png', 'gif']

    amount = 0

    for dir_ in directories:
        list_of_files = glob.glob(f'{dir_}/*')
        quantity = len(list_of_files)
        if quantity > 10:
            quantity -= 10
        else:
            continue
        for i in range(quantity):
            oldest_file = min(list_of_files, key=os.path.getmtime)
            os.remove(oldest_file)
            list_of_files.remove(oldest_file)

            amount += 1

    print(f'Removed {amount} file(s).')
    sleep(2)


if __name__ == '__main__':
    Clear()
