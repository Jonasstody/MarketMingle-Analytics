import yahooquery as yq

def check_if_public(search_input):
    # initial check, if search input can be attributed to a publicly listed company
    # close matches, name inputs & ticker inputs are possible
    search = yq.search(search_input)
    try:
        ticker_symbol = search['quotes'][0]['symbol']
        long_name  = search['quotes'][0]['longname']
        return True, False, ticker_symbol, long_name
    except:
        return False, True, 'n/a', 'n/a'

def check_if_private(search_input):
    # possibility to implement search for private company
    # currently returns false to skip (the non-existent) page build up for private companyies
    return False
