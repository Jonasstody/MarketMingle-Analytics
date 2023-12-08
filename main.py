#Streamlit & Components - add credits
import streamlit as st
from st_pages import Page, show_pages

#helper files
from data_loader import public, private
import general_worker as gw

#other
import pandas as pd


#GERNERAL 
#strucure (in the works): one respective file that handles the visuals for the subpage and helper files for background activity e.g. data pulls, building chart
#the code has all basic functionalities to add a secondary search for private companies incase the public company search does not return any results, at the moment not used due to time constraints

#credit html & css code mostly to chatgpt + add explanation why used rather than pure streamlit whenever used

#application will always start up in dark theme, change to light theme is possible, but will distort some of the graphics; 
#hard to implement/fix as streamlit is currently not able to provide the current theme through a python request, so no chance to change individual elements dynamically

st.set_page_config(layout='wide')

#initalize neccessary var
if 'search_input' not in st.session_state:
    st.session_state['search_input'] = 'n/a'
    
if 'ticker_symbol' or 'name' not in st.session_state:
    st.session_state['ticker_symbol'] = 'n/a'
    st.session_state['name'] = 'n/a'
    
if 'private_check_done' not in st.session_state:
    st.session_state['private_check_done'] = False

is_public = False
is_sus_private = False
is_private = False


#set subpages and link to respective files
show_pages([Page('main.py','Overview'),
            Page('financials.py','Financials'),
            Page('h2h.py','Head 2 Head')])


#remove border around form elements
remove_border_search = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(remove_border_search, unsafe_allow_html=True)


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
                st.rerun()
    
    #Main funciontality
    if is_public:
        st.session_state['name'] = name
        st.session_state['ticker'] = ticker
        st.session_state['private_check_done'] = False
        
        #profile section
        profile_container = st.container()
        #title
        profile_container.title(name)
        #description
        profile_container.write(public.get_comp_desc(ticker))
        
        profile_container.divider()
        #kpis
        hq_location, employee_count, website, sector, industry = profile_container.container().columns([1,1,1,1,1])
        profile_data = public.get_general_company_kpis(ticker)
        with hq_location:
            st.write(profile_data['HQ'])
            st.caption('Headquarter')
        with employee_count:
            st.write(profile_data['FTE'])
            st.caption('Full Time Employees')
        with website:
            website_link = profile_data['Website']
            try:
                website_text = website_link[website_link.find('www.')+4:]
            except:
                website_text = 'n/a'
            final_website_link = f'''<a href='{website_link}' style='color: white; text-decoration: none;'>{website_text}</a>'''
            st.markdown(final_website_link,unsafe_allow_html=True)
            st.caption('Website')
        with sector:
            st.write(profile_data['Sector'])
            st.caption('Sector')
        with industry:
            st.write(profile_data['Industry'])
            st.caption('Industry')
            
            
        st.divider() 
        #price section
        price_container = st.container()
        current_price_container, price_chart_container = price_container.columns([3,7])
        
        #current price
        current_price, p_change, quote_caption, current_price_table = public.get_current_price_data(ticker)
        try:
            if p_change >= 0:
                p_change_text = f'<font color="green">+{p_change}%</font>'
            else:
                p_change_text = f'<font color="red">{p_change}%</font>'
        except:
            p_change_text = f'<font color="white">n/a</font>'
        current_price_container.write(
            f'<span style="font-size: 56px; font-weight: bold;">{current_price}</span> <span style="font-size: 24px;">{p_change_text}</span>',
            unsafe_allow_html=True
        )

        current_price_container.caption(f'<p style="margin-top: -30px;">{quote_caption}</p>', unsafe_allow_html=True)
        
        current_price_container.dataframe(pd.DataFrame(current_price_table),hide_index=True,use_container_width=True)
        
        #price chart
        price_chart_container.subheader('Share Price Development')
        price_one_day, price_one_month, price_twelve_months, price_all_time = price_chart_container.tabs(['1 Day','1 Month','12 Months','All Time'])
        with price_one_day:
            public.get_hist_price_chart(ticker,'1d','1m')
        with price_one_month:
            public.get_hist_price_chart(ticker,'1mo','1h')
        with price_twelve_months:
            public.get_hist_price_chart(ticker,'1y','1d')
        with price_all_time:
            public.get_hist_price_chart(ticker,'max','5d')
            
            
        st.divider()
        #financials
        financials_container = st.container()
        financials_graph_container, key_stats_container = financials_container.columns([2,1])

        #graph & key stats
        financials_chart, info_text, helper_text = public.get_fin_chart(ticker,name)
        key_fin_stats, fin_currency = public.get_key_fin_stats(ticker)
        financials_graph_container.subheader('Financial Development',help=helper_text)
        with financials_graph_container:
            if isinstance(financials_chart,str):
                st.write(financials_chart)
            else:
                st.write(f'{info_text} of {fin_currency}')
                st.pyplot(financials_chart)

        key_stats_container.subheader('Key Stats')
        key_stats_container.dataframe(pd.DataFrame({'Indicator':key_fin_stats.keys(),'Value':key_fin_stats.values()},index=range(len(key_fin_stats))),
                                    hide_index=True)
        
        
        
        st.divider()

        top_inst_holders_container, leadership_container = st.columns([1.4,1])
        top_inst_holders_container.subheader('Top Institutional Holders',help='To isolate an item, double-click the name. To blend it out, single-click the name.')
        fig = public.get_top_inst_holders(ticker)
        try:
            top_inst_holders_container.plotly_chart(fig,use_container_width=True)
        except:
            top_inst_holders_container.write(fig)
            
        leadership_container.subheader('Company Leadership')
        leadership_container.dataframe(public.get_company_leadership(ticker),hide_index=True,use_container_width=True)
                
        st.divider()
        #10 recent news
        news_container = st.container()
        with news_container:
            st.subheader('Recent News')
            search = public.get_recent_news(ticker)
            try:
                for index, row in search.iterrows():
                    title = row['Title']
                    publisher = row['Publisher']
                    date = row['Date']
                    link = row['Link']
                    st.markdown(f'<a style="color: white;" href="{link}">{title} ({publisher}, {date})</a></span>', unsafe_allow_html=True)
            except:
                st.write(search)
        
    elif is_sus_private:
        st.session_state['name'] = 'n/a'
        st.session_state['ticker'] = 'n/a'
        if gw.check_if_private(st.session_state.search_input):
            st.session_state['private_check_done'] = True
        
    elif is_private:
        pass

    elif st.session_state.private_check_done:
        st.write('No company matching your search parameter has been found. Please try again.')
        

#catch if first search
else:
    with st.form(key='search_bar_start'):
        search_bar, search_button = st.columns([5,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                st.rerun()
