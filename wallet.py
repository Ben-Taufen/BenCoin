#!/usr/bin/python

# dictionaries to strings using json
import json

# to send requests to server
import requests

# for command-line arguments
import sys

# all the crypto sbuff is here
import benutils as bu

import transactions



######### YOUR CODE HERE ############
def getPrevMine():
    r = requests.get('http://127.0.0.1:8080/showchainraw')
    chain = r.json();
    return transactions.findLastMined(chain)

def writeKeysToFile(keys, name):
    pk = keys[0]
    sk = keys[1]
    name = name.lower();
    f = open('./keys/'+name+'pk.txt','w')
    f.write(pk)
    f.close()
    f = open('./keys/'+name+'sk.txt','w')
    f.write(sk)
    f.close()
    return


#get name by stripping arg
def getName(nameFile):
    nameLen = len(nameFile)-6;
    name = nameFile[0];
    name = name.upper();
    return name + nameFile[1:nameLen]


#gets all other names user can pay to
def getOtherNames(name):
    r = requests.get('http://127.0.0.1:8080/showusersraw')
    users_json = r.json();
    users = users_json['users']
    list = []
    names = ''
    for i in range(len(users)):
        if name != users[i]['name']:
            if len(names)>0:
                names = names + ", " + users[i]['name']
            else:
                names = users[i]['name']
    return names

def getAvailCoins(pk,chain):
    #returns all available coins in order of largest to smallest value
    coins = [];
    hashPk = bu.sha256(pk)
    blocks = chain["blocks"]
    for i in range(len(blocks)):
        for j in range(len(blocks[i]["transactions"]["outs"])):
            if blocks[i]["transactions"]["outs"][j]["recipient"]==hashPk:
                if transactions.isAvailCoin((i,j),chain):
                    value = blocks[i]["transactions"]["outs"][j]["value"]
                    coin = {'value':value,'transid':i,'outnum':j}
                    insert = False
                    for k in range(len(coins)):
                        if value >= coins[k]["value"]:
                            if(insert==False):
                                coins.insert(k,coin)
                                insert = True
                    if insert == False:
                        coins.append(coin);
    return coins

def getPkByName(name,userlist):
    users = userlist['users']
    for i in range(len(users)):
        if(users[i]['name']==name):
            return users[i]['pk']
    return ''

def calcTotalCoins(pk):
    r = requests.get('http://127.0.0.1:8080/showchainraw')
    chain = r.json();
    value = 0
    coins = getAvailCoins(pk,chain)
    for i in range(len(coins)):
        value += coins[i]["value"];
    print('You have ' + str(value) + ' BenCoins available.')
    return value

if len(sys.argv) == 1:
    ans = raw_input("Would you like to create an account? (Y or N): ")
    if(ans == 'y') or (ans == 'Y'):
        newName = raw_input("Enter your name: ")
        newKeys = bu.keygen(1024)
        writeKeysToFile(newKeys,newName)
        user = {'name':newName,'pk':newKeys[0]}

        r = requests.post('http://127.0.0.1:8080/adduser', data = {'user':json.dumps(user,sort_keys=True)})

        print("Account created for "+newName+". ")
        sys.argv.append(newName.lower()+'pk.txt')
        sys.argv.append(newName.lower()+'sk.txt')




    else:
        print("Please send your public and secret key as arguments. Now quitting.")
        exit(1)

if len(sys.argv) > 3:
    print("Wrong number of arguments. Please use the format:\n./wallet.py pkfilename skfilename\nFor example:\n./wallet.py alicepk.txt alicesk.txt")
    exit(1)

try:
    f = open('./keys/'+sys.argv[2],'r')
    sk = f.read()
    f.close()
except:
    print("invalid sk file.")
    exit(1)

try:
    f = open('./keys/'+sys.argv[1],'r')
    pk = f.read()
    f.close()
except:
    print("invalid pk file.")
    exit(1)


users = transactions.getCurrUsers();
print(users)
name = getName(sys.argv[1]);
if(name!=getName(sys.argv[2])):
    print('Public key user does not match secret key user. \nNow exiting...')
    exit(1)
otherNames = getOtherNames(name)

print('Welcome, ' + name + '.')

action = ''
person = ''
while action != 'quit':
    value = calcTotalCoins(pk)

    action = raw_input('What would you like to do? (pay, mine, quit): ')
    if action == 'pay':
        #pay
        person = raw_input('Who would you like to pay to? (' + otherNames + '): ')
        sendToPk = getPkByName(person,users)
        amt = 0
        sufficientFunds = False
        while sufficientFunds == False:
            amt = input('How much would you like to pay (must be an integer): ')
            if amt <= value:
                sufficientFunds = True
            else:
                sufficientFunds = False
                print("You do not have enough BenCoin to pay " + person + " "+str(amt) + ". You have " + str(value) + " BenCoin available to use.")
        print('Building transaction...')
        #generate inlist
        r = requests.get('http://127.0.0.1:8080/showchainraw')
        chain = r.json();
        coins = getAvailCoins(pk,chain)
        payAmount = coins[0]['value']
        coinIndex = 0
        inlist = []
        inlist.append(buple((coins[coinIndex]['transid'],coins[coinIndex]['outnum'])))
        while(payAmount<amt) and (coinIndex < len(coins)):
            coinIndex = coinIndex + 1
            payAmount += coins[coinIndex]['value']
            inlist.append(buple((coins[coinIndex]['transid'],coins[coinIndex]['outnum'])))

        #generate pklist and amtlist
        pklist = []
        amtlist = []
        if(payAmount > amt):
            pklist = [sendToPk,pk]
            balance = payAmount - amt
            amtlist = [amt,balance]
        else:
            pklist = [sendToPk]
            amtlist = [amt]

        trans = transactions.genPay(pk,sk, inlist, pklist, amtlist)
        r=requests.post('http://127.0.0.1:8080/addtrans', data = {'trans':json.dumps(trans,sort_keys=True)})
        print(r.text)

    elif action == 'mine':
        print('Mining...')
        prevmine = getPrevMine()
        trans = transactions.genMined(pk,prevmine)
        r = requests.post('http://127.0.0.1:8080/addtrans', data = {'trans':json.dumps(trans,sort_keys=True)})
        if(r.text=='Failure'):
            print('Mine failed... Someone already mined with that prevmine. Please try again.')
        else:
            print('Success!')
    elif action == 'quit':
        #do nothing
        print('Quitting.')
    else:
        print('Invalid input. Please enter either pay, mine, or quit.')
