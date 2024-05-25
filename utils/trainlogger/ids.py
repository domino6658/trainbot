import csv
import os
import discord
import pandas as pd

def hextodec(hexnum):
    decnum = int(str(hexnum), 16) 
    return decnum

def dectohex(decnum):
    hexnum = hex(decnum)
    return hexnum[2:].upper()

def is_hex(s):
    try:
        int(str(s),16)
    except ValueError:
        return False
    else:
        return True

def addids():
    try:
        os.listdir('utils\\trainlogger\\userdata')
    except FileNotFoundError:
        print('no userdata folder')
        return 'no userdata folder'

    for filename in os.listdir('utils\\trainlogger\\userdata'):
        x = 0
        with open(f'utils/trainlogger/userdata/{filename}', 'r+', newline='') as file:
            data = file.readlines()
            for i in range(len(data)):
                x += 1
                data[i] = f'#{dectohex(x)},'+data[i]
            file.truncate(0)
            file.seek(0)
            file.writelines(data)
    return True