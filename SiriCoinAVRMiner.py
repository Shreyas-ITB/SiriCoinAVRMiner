# Based https://github.com/Shreyas-ITB/SiriCoinPCMiner
import time, importlib, json, serial
from web3.auto import w3
from eth_account.account import Account
from eth_account.messages import encode_defunct
from time import sleep
from termcolor import colored
import os.path 
import configparser
from threading import Thread
from rich import print
from pypresence import Presence
import pypresence
import time
import serial.tools.list_ports
import sys


#define all managers
ArduinoManager = ("[cyan][AVRM][/cyan]")
SystemManager = ("[cyan][SYSM][/cyan]")
NodeManager = ("[cyan][NODEM][/cyan]")
InfoManager = ("[cyan][INFOM][/cyan]")

#time job
temptime = 20

self_lastBlock = ""


def print_colored( strtext, strcolor ):
    print(colored(strtext, strcolor))

class ConfigFile(object):
    def __init__(self):
        self.config_file_name = "Config\config.ini"
        self.config_object = configparser.ConfigParser()
        self.userinfo = {}
    
    def read(self):
        self.config_object["USERINFO"] = { "walletaddr": "", "ports": []}
        if (os.path.exists(self.config_file_name) is False):
            self.write()
        self.config_object.read(self.config_file_name)            
        self.userinfo = self.config_object["USERINFO"]
                
    def write(self):
        with open(self.config_file_name, "w") as conf:
            self.config_object.write(conf)

class SignatureManager(object):
    def __init__(self):
        self.verified = 0
        self.signed = 0
    
    def signTransaction(self, private_key, transaction):
        message = encode_defunct(text=transaction["data"])
        transaction["hash"] = w3.soliditySha3(["string"], [transaction["data"]]).hex()
        _signature = w3.eth.account.sign_message(message, private_key=private_key).signature.hex()
        signer = w3.eth.account.recover_message(message, signature=_signature)
        sender = w3.toChecksumAddress(json.loads(transaction["data"])["from"])
        if (signer == sender):
            transaction["sig"] = _signature
            self.signed += 1
        return transaction
        
    def verifyTransaction(self, transaction):
        message = encode_defunct(text=transaction["data"])
        _hash = w3.soliditySha3(["string"], [transaction["data"]]).hex()
        _hashInTransaction = transaction["hash"]
        signer = w3.eth.account.recover_message(message, signature=transaction["sig"])
        sender = w3.toChecksumAddress(json.loads(transaction["data"])["from"])
        result = ((signer == sender) and (_hash == _hashInTransaction))
        self.verified += int(result)
        return result

class SiriCoinMiner(object):
    def __init__(self, NodeAddr, RewardsRecipient):
        # self.chain = BeaconChain()
        self.requests = importlib.import_module("requests")
        
        self.node = NodeAddr
        self.signer = SignatureManager()
        self.difficulty = 1
        self.target = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        self.lastBlock = ""
        self.rewardsRecipient = w3.toChecksumAddress(RewardsRecipient)
        self.priv_key = w3.solidityKeccak(["string", "address"], ["SiriCoin Will go to MOON - Just a disposable key", self.rewardsRecipient])
        
        self.nonce = 0
        self.acct = w3.eth.account.from_key(self.priv_key)
        self.messages = b"null"
        
        self.timestamp = int(time.time())
        _txs = self.requests.get(f"{self.node}/accounts/accountInfo/{self.acct.address}").json().get("result").get("transactions")
        self.lastSentTx = _txs[len(_txs)-1]
        self.refresh()
    
    def refresh(self):
        info = self.requests.get(f"{self.node}/chain/miningInfo").json().get("result")
        self.target = info["target"]
        self.difficulty = info["difficulty"]
        self.lastBlock = info["lastBlockHash"]
        _txs = self.requests.get(f"{self.node}/accounts/accountInfo/{self.acct.address}").json().get("result").get("transactions")
        self.lastSentTx = _txs[len(_txs)-1]
        self.timestamp = int(time.time())
        self.nonce = 0
    
    def submitBlock(self, blockData):
        data = json.dumps({"from": self.acct.address, "to": self.acct.address, "tokens": 0, "parent": self.lastSentTx, "blockData": blockData, "epoch": self.lastBlock, "type": 1})
        tx = {"data": data}
        tx = self.signer.signTransaction(self.priv_key, tx)
        self.refresh()
        txid = self.requests.get(f"{self.node}/send/rawtransaction/?tx={json.dumps(tx).encode().hex()}").json().get("result")[0]
        sbmtblck = colored(f"[yellow]{blockData['miningData']['proof']}[/yellow]")
        printingtxt = colored(f"[white]Mined a block {sbmtblck}[/white]")
        print(SystemManager, printingtxt)
        print(colored(f"[green]Submitted in transaction {txid}[/green]"))
        return txid

    def beaconRoot(self):
        messagesHash = w3.keccak(self.messages)
        bRoot = w3.soliditySha3(["bytes32", "uint256", "bytes32","address"], [self.lastBlock, self.timestamp, messagesHash, self.rewardsRecipient]) # parent PoW hash (bytes32), beacon's timestamp (uint256), hash of messages (bytes32), beacon miner (address)
        return colored(f"{bRoot.hex()}", "green")

    def formatHashrate(self, hashrate):
        if hashrate < 1000:
            return f"{round(hashrate, 2)}H/s"
        elif hashrate < 1000000:
            return f"{round(hashrate/1000, 2)}kH/s"
        elif hashrate < 1000000000:
            return f"{round(hashrate/1000000, 2)}MH/s"
        elif hashrate < 1000000000000:
            return f"{round(hashrate/1000000000, 2)}GH/s"
            
    def startMining(self, indexThread, serial_port ):
        while True:
            try:
                global self_lastBlock
                ser  = serial.Serial(f"{serial_port}", baudrate=115200, timeout=2.5)
                time.sleep(1)
                contxt = (f"[green]AVRD{indexThread} successfully connected on {serial_port}![/green]")
                print(ArduinoManager, contxt)
                proof = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"            
                while True:
                    self.refresh()
                    if (self_lastBlock != self.lastBlock):
                        self_lastBlock = self.lastBlock
                        print("")
                        lstblck = (f"[yellow]{self.lastBlock}[/yellow]")
                        trgt = (f"[yellow]{self.target}[/yellow]")
                        diff = (f"[blue]{self.difficulty}[/blue]")
                        serverts = (f"[yellow]{self.timestamp}[/yellow]")
                        lstxt = (f"[magenta]LastBlock : {lstblck}[/magenta]")
                        trgtxt = (f"[magenta]TargetBlock : {trgt}[/magenta]")
                        difftxt = (f"[magenta]CurrentDiff : {diff}[/magenta]")
                        timestamp = (f"[magenta]NodeTimeStamp : {serverts}[/magenta]")
                        print(NodeManager, lstxt)
                        print(NodeManager, trgtxt)
                        print(NodeManager, difftxt)
                        print(NodeManager, timestamp)
                        print("")
                    bRoot = self.beaconRoot()
                    ddata = f"{bRoot},{self.target},{temptime}\n"
                    ser.flush()
                    ser.write(ddata.encode('ascii'))
                    recebido = ""
                    tempo_decorrido = temptime
                    q_bytes = 0
                    self.nonce = 0
                    tinicial = time.time()
                    while (time.time() - tinicial) < (temptime * 2):
                        if (ser.in_waiting>0):
                            byte_lido = ser.read()
                            q_bytes = q_bytes + 1
                            if (byte_lido == b'\n'):
                                ress = recebido.split(',')
                                try:
                                    self.nonce = int(ress[0].rstrip())
                                    tempo_decorrido = round(int(ress[1].rstrip()) * 0.000001)
                                    proof = ress[2].rstrip()
                                except:
                                    invld = (f"{recebido}")
                                    dat = (f"Invalid Data: {invld}")
                                    print(ArduinoManager, dat)
                                recebido = ""
                                measurehash = (f"[yellow]AVRD{indexThread} Measuring AVR Hashrate..[/yellow]")
                                print(SystemManager, measurehash)
                                measuredhash = (f"[blue]AVRD{indexThread} Hashing.. at the hashrate of : {self.formatHashrate((self.nonce / tempo_decorrido))}[/blue]")
                                print(ArduinoManager, measuredhash)
                                if (q_bytes>32):
                                    print(f"bRoot: {bRoot}")
                                    self.submitBlock({"miningData" : {"miner": self.rewardsRecipient,"nonce": self.nonce,"difficulty": self.difficulty,"miningTarget": self.target,"proof": proof}, "parent": self.lastBlock,"messages": self.messages.hex(), "timestamp": self.timestamp, "son": "0000000000000000000000000000000000000000000000000000000000000000"})
                                q_bytes = 0
                                break
                            else:
                                recebido = recebido + byte_lido.decode("utf-8")
            except serial.SerialException:
                    errtxt = (f"[red]AVRD{indexThread} got disconnected! Please connect it back.. Retrying in 5sec[/red]")
                    print(ArduinoManager, errtxt)
                    sleep(5)                        
                

if __name__ == "__main__":
    try:
        print("[yellow]Trying to start Discord RPC...[/yellow]")
        #Read config
        open("Config\config.ini", "r")
        open("Config\confignames.txt", "r")
        try:
            rpc = Presence("972449607235821569")
            rpc.connect()   
            #Read config
            open("Config\config.ini", "r")
            print("[green]Got Config Data from the ConfigFiles.. Proceeding Further..[/green]")
            config_local = ConfigFile();
            config_local.read()
            usraddr = config_local.userinfo["walletaddr"]
            minead = (f"[blue]{usraddr}[/blue]")
            print(f"[green]Started mining for SiriUser {minead}[/green]")
            readfile = open("Config\confignames.txt", "r")
            getinfo = readfile.readline()
            rpc.update(state=f"Board(s): {getinfo}", details="Mining SiriCoin with my AVRs", large_image="smallimage", small_image="logo", start=time.time())
            print("[green]Successfully Established Discord RPC..[/green]")
            serialPorts = config_local.userinfo["ports"].split(',')
            addr = config_local.userinfo["walletaddr"]
            index = 0
            for port in serialPorts:
                miner = SiriCoinMiner("http://47.250.59.81:5005/", usraddr)
                Thread(target=miner.startMining, args=(index, port)).start()
                index += 1
        except pypresence.exceptions.DiscordNotFound or pypresence.exceptions.DiscordError:
            print("[red]Couldnt Start Discord RPC Proceeding...[/red]")
            #Read config
            open("Config\config.ini", "r")
            print("[green]Got Config Data from the ConfigFiles.. Proceeding Further..[/green]")
            config_local = ConfigFile();
            config_local.read()
            usraddr = config_local.userinfo["walletaddr"]
            minead = (f"[blue]{usraddr}[/blue]")
            print(f"[green]Started mining for SiriUser {minead}[/green]")
            serialPorts = config_local.userinfo["ports"].split(',')
            addr = config_local.userinfo["walletaddr"]
            index = 0
            for port in serialPorts:
                miner = SiriCoinMiner("http://47.250.59.81:5005/", usraddr)
                Thread(target=miner.startMining, args=(index, port)).start()
                index += 1      
    except FileNotFoundError:
        print("[red]No Config file found. Creating a new one in ConfigDir..[/red]")
        config_local = ConfigFile();
        config_local.read()
        print("[blue]Please Choose your COM port from the below list..[/blue]")
        sleep(1)
        print("")
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            print("Detected Ports - {}: {} [{}]".format(port, desc, hwid))
        print("")
        print(f"{InfoManager} [yellow]If 'Detected Ports' say nothing, Then your AVR Devices are not connected or Your Computer is not recognising it. Please Check and Restart the miner..[/yellow]")
        serialPort = input("Enter your AVR Serial Port(s) Seperated by comma without space (i.e COM3,COM4): ")
        if ( serialPort != "" ):
            config_local.userinfo["ports"] = serialPort
        minerAddr = input("Enter your SiriCoin address Starts with (0x): ")
        if ( minerAddr != "" ):
            config_local.userinfo["walletaddr"] = minerAddr
        config_local.write()
        nameavrs = open("Config\confignames.txt", "w")
        avrnames = input("Enter the name of one AVR device which you are trying to mine on (Please enter the name little shorter): ")
        nameavrs.write(avrnames)
        print("[green]Config Saved Successfully..[/green]")
        sleep(2)
        print("[yellow]Please Restart the miner.[/yellow] [red]in the next 10 seconds...[/red]")
        sleep(5)
