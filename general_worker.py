import yahooquery as yq
import json
import urllib

def check_if_public(search_input):
    try:
        response = urllib.request.urlopen(f'https://query2.finance.yahoo.com/v1/finance/search?q={search_input}')
        content = response.read()
        request = json.loads(content.decode('utf8'))['quotes'][0]
        name = request['shortname']
        symbol = request['symbol']
        return True, False, symbol, name
    except:
        return False, True, 'n/a', 'n/a'

def check_if_private(search_input):
    return False