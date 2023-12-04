import streamlit as st
import yahooquery as yq
import general_worker as gw


st.set_page_config(layout='wide')

#initalize neccessary var
if 'search_input' not in st.session_state:
    st.session_state['search_input'] = 'n/a'
    
if 'ticker_symbol' or 'name' not in st.session_state:
    st.session_state['ticker_symbol'] = 'n/a'
    st.session_state['name'] = 'n/a'

is_public = False
is_sus_private = False
is_private = False

#search bar & button as streamlit form
#if previous search in the same session exists, search is automatically restarted, otherwise initial search is started
if st.session_state.search_input != 'n/a': #search_input is used as a cached variable across pages and for usage comment above
    is_public, is_sus_private, ticker, name = gw.check_if_public(st.session_state.search_input)
    with st.form(key='seach_bar'):
        search_bar, search_button = st.columns([5,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',value=st.session_state.search_input,placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                is_public, is_sus_private, ticker, name = gw.check_if_public(search_name)

else:
    with st.form(key='search_bar_start'):
        search_bar, search_button = st.columns([5,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                is_public, is_sus_private, ticker, name = gw.check_if_public(search_name)
                
#remove border around search bar & button
remove_border_search = r'''
    <style>
        [data-testid='stForm'] {border: 0px}
    </style>
'''
st.markdown(remove_border_search, unsafe_allow_html=True)


#Main functionality
if is_public:
    st.title(name)
    income_statment_container, balance_sheet_container, cash_flow_container = st.tabs(['Income Statement','Balance Sheet','Statement of Cash Flows'])

    with income_statment_container:
        income_statement = yq.Ticker(ticker).income_statement().set_index('asOfDate').transpose()
        st.dataframe(income_statement,use_container_width=True,height=800)
        
    with balance_sheet_container:
        balance_sheet = yq.Ticker(ticker).balance_sheet().set_index('asOfDate').transpose()
        st.dataframe(balance_sheet,use_container_width=True,height=800)
        
    with cash_flow_container:
        cash_flow = yq.Ticker(ticker).cash_flow().set_index('asOfDate').transpose()
        st.dataframe(cash_flow,use_container_width=True,height=800)
        
elif is_sus_private:
    st.session_state['name'] = 'n/a'
    st.session_state['ticker'] = 'n/a'
    if gw.check_if_private(st.session_state.search_input):
        pass
    
elif is_private:
    pass