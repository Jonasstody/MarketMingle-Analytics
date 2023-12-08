import yahooquery as yq
from time import sleep

def check_if_public(search_input):
    search = yq.search(search_input)
    try:
        ticker_symbol = search['quotes'][0]['symbol']
        long_name  = search['quotes'][0]['longname']
        return True, False, ticker_symbol, long_name
    except:
        sleep(0.5)
        try:
            search = yq.search(search_input)
            ticker_symbol = search['quotes'][0]['symbol']
            long_name  = search['quotes'][0]['longname']
            return True, False, ticker_symbol, long_name
        except:
            return False, True, 'n/a', 'n/a'

def check_if_private(search_input):
    return False