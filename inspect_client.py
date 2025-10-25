from lnmarkets import rest

options = {
    'key': 'Zai8xehXFyl0JbIEBTGmP9cZ4knExRdbfb8Ki24ukR4=',
    'secret': 'N4tvsDZtpevqeWuQ1dJ2MpK6SGlJh0Ocm43kB3yHbF9agQkP0JURO8zA0U9DiUyGzQFAFYMGSOcYtEPli8mTJA==',
    'passphrase': '557569edb3fai',
    'network': 'testnet'
}

client = rest.LNMarketsRest(**options)
print(dir(client))
