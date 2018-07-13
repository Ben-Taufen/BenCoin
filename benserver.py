#
#   benserver.py : python bottle server that maintains the BenCoin blockchain
#
#   Author: Scott Yilek,Ben Taufen  (April 2018)
#


import benutils as bu
import transactions
import json
from bottle import route, run, debug, template, static_file, request, redirect, response




@route('/showchainraw')
def showchain():
# open chain file, print it out to screen
    chainstr=transactions.getCurrChainStr()
    return chainstr

@route('/showusersraw')
def showusers():
# open chain file, print it out to screen
    users=transactions.getCurrUsers()
    return users

@route('/')
@route('/showchainhtml')
def shownicechain():
    chainstr=transactions.getCurrChainStr()
    return '<html><body><pre>%s</pre></body></html>'%chainstr

@route('/addtrans',method='POST')
def addtrans():
    trans_str = request.POST.get('trans')
    trans = json.loads(trans_str)
    origchain = transactions.getCurrChain()
    orighash = origchain['lasthash']
    chain = transactions.addTrans(trans, origchain)
    newhash = chain['lasthash']
    if (orighash==newhash):
        return 'Failure'
    transactions.setCurrChain(chain)
    return 'Success'

@route('/adduser',method='POST')
def adduser():
    user_str = request.POST.get('user')
    user = json.loads(user_str)
    print(user['name'])
    print(user['pk'])
    origUsers = transactions.getCurrUsers()
    print(json.dumps(origUsers))
    print(json.dumps(user))
    users = transactions.addUser(user,origUsers)
    transactions.setCurrUsers(users)
    return 'Successfully added user: '+user['name']

debug(True)
run()
