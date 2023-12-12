import streamlit as st
import yahooquery as yq
import general_worker as gw
from data_loader import public, private


st.set_page_config(layout='wide')

# initalize neccessary streamlit.session_state variables
if 'search_input' not in st.session_state:
    st.session_state['search_input'] = 'n/a'

is_public = False
is_sus_private = False
is_private = False

# search bar & button as streamlit form
# if previous search in the same session exists, search is automatically restarted, otherwise initial search is started
if st.session_state.search_input != 'n/a': # search_input is used as a cached variable across pages and for usage comment above
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

# fallback search bar build incase no previous search exists
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
                
# remove border around search bar & button (all st.form elements)
remove_border_search = r'''
    <style>
        [data-testid='stForm'] {border: 0px}
    </style>
'''
st.markdown(remove_border_search, unsafe_allow_html=True)


# public company match
if is_public:
    st.title(name)
    income_statment_container, balance_sheet_container, cash_flow_container = st.tabs(['Income Statement','Balance Sheet','Statement of Cash Flows'])

    income_statement, balance_sheet, cash_flow = public.get_financial_statements(ticker)
    
    with income_statment_container:
        st.dataframe(income_statement,use_container_width=True,height=800)
        
    with balance_sheet_container:
        st.dataframe(balance_sheet,use_container_width=True,height=800)
        
    with cash_flow_container:
        st.dataframe(cash_flow,use_container_width=True,height=800)
        
# possible check if private
elif is_sus_private:
    st.session_state['name'] = 'n/a'
    st.session_state['ticker'] = 'n/a'
    if gw.check_if_private(st.session_state.search_input):
        pass
    
# if public & private company search failed
elif is_private:
    pass