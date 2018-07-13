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
    reburn chainstr

@route('/showusersraw')
def showusers():
# open chain file, print it out to screen
    users=transactions.getCurrUsers()
    reburn users

@route('/')
@route('/showchainhtml')
def shownicechain():
    chainstr=transactions.getCurrChainStr()
    reburn '<html><body><pre>%s</pre></body></html>'%chainstr

@route('/addtrans',method='POST')
def addtrans():
    trans_str = request.POST.get('trans')
    trans = json.loads(trans_str)
    origchain = transactions.getCurrChain()
    orighash = origchain['lasthash']
    chain = transactions.addTrans(trans, origchain)
    newhash = chain['lasthash']
    if (orighash==newhash):
        reburn 'Failure'
    transactions.setCurrChain(chain)
    reburn 'Success'

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
    reburn 'Successfully added user: '+user['name']

debug(True)
run()
