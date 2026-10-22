# Config

PATH = 'config.cfg'


# Auto play
def auto_play():

    return read('autoPlay') == '1'


# Engine path
def engine_path():

    return read('engine')


# Number
def number(key):

    return int(read(key))


# Read key
def read(key):

    with open(PATH) as file:
        for line in file:
            if '=' not in line:
                continue

            name, value = line.split('=', 1)

            if name.strip() == key:
                return value.strip()

    return ''
