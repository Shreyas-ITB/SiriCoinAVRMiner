import json
import serial
import requests
from time import sleep
import colorama
from colorama import Fore
from pythonping import ping
import configparser
import os
from os import path, mkdir

colorama.init(autoreset=True)
def address(addr):
    if len(addr) < 42:
        print(f"[SC] {Fore.RED}Error Invalid SiriCoin Address Please Enter a valid one from metamask")
    else:
        print(f"[SC] {Fore.GREEN}Valid SiriCoin Address Proceeding..")

node = ("1.0 Public Beta Release")
miner = ("1.0 Public Beta Release")

CONFIG_DIR = "config"
wallet = ""
port = ""

def startMining():
    print(f"""
    {Fore.BLUE}SiriCoin CryptoCurrency AVR Miner 2021-2022
    {Fore.BLUE}AVR Algorithm: DataHash Created by Shreyas-ITB
    {Fore.BLUE}Simplest AVR Job Ever For Arduinos...
    {Fore.YELLOW}Discord Server: https://discord.gg/6EGmgNWD9R
    {Fore.MAGENTA}DataHashNode Version: {Fore.YELLOW}{node}
    {Fore.MAGENTA}SiriCoin AVRMiner Version: {Fore.YELLOW}{miner}
    {Fore.GREEN}Your SiriCoin Address: {wallet}
    """)
    sleep(3)
    print (f"[SYS] {Fore.GREEN}Starting SiriCoin AVRMiner. With DataHash Algorithm.")
    sleep(3)
    while True:
        try:
            ser  = serial.Serial(f"{port}", baudrate=115200, timeout=2.5)
            print(f"[AVR] {Fore.GREEN}Successfully Connected to AVR Device")
            sleep(2)
            print(f"[SYS] {Fore.YELLOW}Requesting Job from DataHash-Node")
            sleep(2)
            try:
                req = requests.get("https://00de-2401-4900-1f20-64ba-a4c4-b962-9cdc-bb5d.ngrok.io/createData")
                print(f"[SYS] {Fore.GREEN}Successfully Connected to DataHashNode")
                sleep(2)
                data = {}
                data["operation"] = f"{req.text}"
                data = json.dumps(data) + "*"
                print(f"[SYS] {Fore.GREEN}Got Master Hash From DataHashNode")
                sleep(2)
                print(f"[SYS] {Fore.YELLOW}Sending Job to AVR: " + data)
                ser.write(data.encode('ascii'))
                ser.flush()
                try:
                    incoming = ser.readline().decode("utf-8")
                    avrdata = requests.post(f"https://00de-2401-4900-1f20-64ba-a4c4-b962-9cdc-bb5d.ngrok.io/acceptjob/{incoming}")
                    print(f"[AVR] {Fore.GREEN}The Hash has been Solved by the AVR Device")
                    sleep(3)
                    print(f"[SYS] {Fore.YELLOW}Sending SolvedHash From AVR device to Node")
                    sleep(3)
                    print(f"[AVR] {Fore.BLUE}{avrdata.text}")
                    sleep(2)  
                    p=ping('00de-2401-4900-1f20-64ba-a4c4-b962-9cdc-bb5d.ngrok.io')
                    print(f"""
[Node] {Fore.MAGENTA}DataHash Algo Works a bit different The Lower the Hashrate the Faster You recieve jobs.
{Fore.MAGENTA}Your AVR's Average Hashrate: {p.rtt_avg_ms}H/s
{Fore.MAGENTA}Your AVR's Max Hashrate: {p.rtt_max_ms}H/s
{Fore.MAGENTA}Your AVR's Min Hashrate: {p.rtt_min_ms}H/s
                    """)
                except Exception as e:
                    print(e)
                    pass
                ser.close()
            except requests.exceptions.ConnectionError:
                print(f"[SYS] {Fore.RED}Error Connecting To AVR DataHash Node Retrying in 3 seconds")
                sleep(3)
        except serial.SerialException:
            print(f"[AVR] {Fore.RED}Error Connecting to AVR device Retrying in 3 seconds")
            sleep(3)

if __name__ == "__main__":
    if not path.exists(CONFIG_DIR):
        mkdir(CONFIG_DIR)

    if os.path.exists(CONFIG_DIR + '/settings.cfg'):
        config = configparser.ConfigParser()
        config.read(CONFIG_DIR + '/settings.cfg')
        wallet = config['settings']['address']
        address(wallet)
        port = config['settings']['port1']
        print(f"[SC] {Fore.GREEN}Found Config File...")
        
        startMining()
    else:
        print(f"[SC] {Fore.RED}No Config File Found...")
        wallet = input(f"[SC] {Fore.GREEN} Please Enter Your SiriCoin Address: ")
        address(wallet)
        sleep(2)
        port = input(f"[SYS] {Fore.YELLOW} Please enter your Arduino Com Port: ")
        sleep(2)

        config = configparser.ConfigParser()
        config.add_section('settings')
        config.set('settings', 'address', wallet)
        config.set('settings', 'port1', port)
        with open(CONFIG_DIR + '/settings.cfg', 'w') as configfile:
            config.write(configfile)

        startMining()