import streamlit as st
import general_worker as gw
from data_loader import public

import pandas as pd

# GENERAL
# In the H2H section we refer to the initial company (input on the left/used on the other pages) either as the kpi in combination 
# with init (e.g. ticker_init) or without any markings (e.g. ticker); for the other company (on the right) we always add a h2h (e.g. ticker_h2h)

# layout
st.set_page_config(layout='wide')

# initalize neccessary streamlit.session_state variables
if 'search_input' not in st.session_state:
    st.session_state['search_input'] = 'n/a'

# same for h2h company
if 'search_input_h2h' not in st.session_state:
    st.session_state['search_input_h2h'] = 'n/a'

# start up values for search order
# not neccessary for current structure but allow later implementation for secondary search
is_public = False
is_sus_private = False
is_private = False

is_public_h2h = False
is_sus_private_h2h = False
is_private_h2h = False

# search input exists for both companies
if st.session_state.search_input != 'n/a' and st.session_state.search_input_h2h != 'n/a':
    # check for both companies
    is_public, is_sus_private, ticker, name = gw.check_if_public(st.session_state.search_input)
    is_public_h2h, is_sus_private_h2h, ticker_h2h, name_h2h = gw.check_if_public(st.session_state.search_input_h2h)
    
    # form with two user input fields and a button 
    with st.form(key='search_bar'):
        search_bar, search_bar_h2h, search_button = st.columns([3,3,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',value=st.session_state.search_input,placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_bar_h2h:
            search_name_h2h = st.text_input(label='search_bar_h2h',value=st.session_state.search_input_h2h,placeholder='Compared to?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start',use_container_width=True)
            if isclick:
                # upon button click/form submit, the search inputs are entered into session_state and then the page is fully rerun
                st.session_state.search_input = search_name
                st.session_state.search_input_h2h = search_name_h2h
                st.rerun()

    # public company match
    if is_public and is_public_h2h:
        
        # Headers with company names;
        st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 2; text-align: left;"><h2>{name}</div>
                    <div style="flex: 1; text-align: center;"></div> 
                    <div style="flex: 2; text-align: right;"><h2>{name_h2h}</div>
                </div>
                ''', unsafe_allow_html=True) 
        # 3 columns on purpose, gives option to adjust design by adding more distance in the middle
        
        # helper function that utilizes html to align one kpi to the left, add a custom, centralized text and a second kpi aligned to the right 
        def build_h2h_row(content_left,category,content_right,category_weight=1):
            st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 2; text-align: left;">{content_left}</div>
                    <div style="flex: {category_weight}; text-align: center; color: gray">{category}</div>
                    <div style="flex: 2; text-align: right;">{content_right}</div>
                </div>
                ''', unsafe_allow_html=True)
        
        # Structure in tabs
        general_tab, stock_tab, financial_tab = st.tabs(['General Company Information','Stock Performance','Financial Standing'])
        
        # General Company Information Tab
        with general_tab:
            # header
            st.subheader('General Company Information')
            # extra spaces
            st.markdown('<div><br></div>',unsafe_allow_html=True)
            
            # retrieve data to put h2h
            data_init = public.get_h2h_general(ticker)
            data_h2h = public.get_h2h_general(ticker_h2h)
            # put into collective dict, with the category as key and the two kpis as values in a list
            general_content = {'Industry':[data_init['industry'],data_h2h['industry']],
                            'Sector':[data_init['sector'],data_h2h['sector']],
                            'Full Time Employees':[data_init['fullTimeEmployees'],data_h2h['fullTimeEmployees']],
                            'Headquarter Location':[data_init['hq'],data_h2h['hq']],
                            'Analyst Recommendation':[data_init['recommendationKey'],data_h2h['recommendationKey']],
                            'ESG Risk':[data_init['esg_risk'],data_h2h['esg_risk']]}
            
            #go through elements of dict
            for kpi in general_content.keys():
                #special case for ESG as it is a graph
                if kpi == 'ESG Risk':
                    left_graph, category, right_graph = st.columns([2,1,2])
                    category.markdown(f'''
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1; text-align: center; color: gray">{'ESG Risk'}</div>
                    </div>''', unsafe_allow_html=True)
                    
                    # helpers for layout to align helper text to middle 
                    help_one, help_two, help_three = category.columns([3,1,3]) 
                    # helper text explaining ESG score
                    help_two.markdown('',help='''Sustainalytics' ESG Risk Ratings assess the degree to which a company's 
                                    enterprise business value is at risk driven by environmental, social and governance 
                                    issues. The rating employs a two-dimensional framework that combines an assessment of 
                                    a company's exposure to industry-specific material ESG issues with an assessment of how 
                                    well the company is managing those issues. The final ESG Risk Ratings scores are a measure 
                                    of unmanaged risk on an absolute scale of 0-100, with a lower score signaling less unmanaged
                                    ESG Risk.''')
                    try:
                        left_graph.vega_lite_chart(general_content[kpi][0],use_container_width=True)
                    except:
                        left_graph.write('n/a')
                    try:
                        right_graph.vega_lite_chart(general_content[kpi][1],use_container_width=True)
                    except:
                        right_graph.write('n/a')
                
                else:
                    # use helper funtion from above to build rows and add divider below each
                    build_h2h_row(general_content[kpi][0],kpi,general_content[kpi][1],1)
                    st.divider()
        
        # Stock Performance Tab
        with stock_tab:
            # header
            st.subheader('Stock Performance')
            # extra space
            st.markdown('<div><br></div>',unsafe_allow_html=True)
            
            # layout row one
            current_price_container, related_kpis_container = st.columns([1,1])
            
            # display of current price data in almost similar style to the current price in main.py
            # difference is that info i.e. exchange etc. is split into two rows due to space constraints
            with current_price_container:
                price_init, price_splitter, price_h2h = st.columns([3,1,3])
                # price info of init company
                # data for this and next section (current_price_table for next section)
                current_price, p_change, quote_caption, current_price_table = public.get_current_price_data(ticker)
                try:
                    if p_change >= 0:
                        p_change_text = f'<font color="green">+{p_change}%</font>'
                    else:
                        p_change_text = f'<font color="red">{p_change}%</font>'
                except:
                    p_change_text = f'<font color="white">n/a</font>'
                price_init.write(
                    f'<span style="font-size: 30px; font-weight: bold;">{current_price}</span> <span style="font-size: 16px;">{p_change_text}</span>',
                    unsafe_allow_html=True)
                
                price_init.caption(f'<p style="margin-top: -25px;">{quote_caption[:quote_caption.find("|")+quote_caption[quote_caption.find("|")+1:].find("|")]}</p>', unsafe_allow_html=True)
                price_init.caption(f'<p style="margin-top: -25px;">{quote_caption[quote_caption.find("|")+1:][quote_caption[quote_caption.find("|")+1:].find("|")+2:]}</p>', unsafe_allow_html=True)
                
                # price info of h2h company
                # data for this and next section (current_price_table_h2h for next section)
                current_price_h2h, p_change_h2h, quote_caption_h2h, current_price_table_h2h = public.get_current_price_data(ticker_h2h)
                try:
                    if p_change_h2h >= 0:
                        p_change_text_h2h = f'<font color="green">+{p_change_h2h}%</font>'
                    else:
                        p_change_text_h2h = f'<font color="red">{p_change_h2h}%</font>'
                except:
                    p_change_text_h2h = f'<font color="white">n/a</font>'
                price_h2h.write(
                    f'<span style="font-size: 30px; font-weight: bold;">{current_price_h2h}</span> <span style="font-size: 16px;">{p_change_text_h2h}</span>',
                    unsafe_allow_html=True)
                
                price_h2h.caption(f'<p style="margin-top: -25px;">{quote_caption_h2h[:quote_caption_h2h.find("|")+quote_caption_h2h[quote_caption_h2h.find("|")+1:].find("|")]}</p>', unsafe_allow_html=True)
                price_h2h.caption(f'<p style="margin-top: -25px;">{quote_caption_h2h[quote_caption_h2h.find("|")+1:][quote_caption_h2h[quote_caption_h2h.find("|")+1:].find("|")+2:]}</p>', unsafe_allow_html=True)
                
                price_splitter.header('|')
                
            # table Market Cap, Forward P/E, Beta (5y Monthly) and Dividend Yield (trailing)'
            with related_kpis_container:
                for item_init, item_h2h in zip(current_price_table,current_price_table_h2h):
                    build_h2h_row(item_init['Value'],item_init['Indicator'],item_h2h['Value'],3)
            
            st.divider()
            
            # second row
            # Historical price chart (relative) and past perfromance over predefined periods
            price_chart_container, past_performance_container = st.columns([2.5,1])
            # build charts for 1 Day, 1 Month, 1 Year, 5 Years and the max available data
            with price_chart_container:
                one_day, one_month, one_year, five_year, all_time = st.tabs(['1 Day','1 Month','12 Months','5 Years','All Time'])
                with one_day:
                    public.build_h2h_relative_price_chart(ticker,ticker_h2h,'1d','1m')
                with one_month:
                    public.build_h2h_relative_price_chart(ticker,ticker_h2h,'1mo','1h')
                with one_year:
                    public.build_h2h_relative_price_chart(ticker,ticker_h2h,'1y','1d')
                with five_year:
                    public.build_h2h_relative_price_chart(ticker,ticker_h2h,'5y','1d')
                with all_time:
                    public.build_h2h_relative_price_chart(ticker,ticker_h2h,'max','5d')

                #legend for the graph
                st.markdown(
                            f"<div style='text-align: center;'>"
                            f"<span style='display: inline-block; margin-right: 10px; height: 10px; width: 10px; border-radius: 50%; background-color: rgb(229,61,62);'></span>"
                            f"{name}"
                            f"<span style='display: inline-block; margin-left: 20px; margin-right: 10px; height: 10px; width: 10px; border-radius: 50%; background-color: rgb(177,156,217);'></span>"
                            f"{name_h2h}"
                            f"</div>", unsafe_allow_html=True)
            
            # past performance in table; visuallized as df
            with past_performance_container:
                elements = pd.DataFrame(public.get_stock_movements_h2h(ticker, ticker_h2h),columns=['Timespan',ticker,ticker_h2h])
                st.dataframe(elements,hide_index=True,use_container_width=True)
                
        
        # Financial Standing Tab
        with financial_tab:
            # header
            st.subheader('Financial Standing')
            # extra space
            st.markdown('<div><br></div>',unsafe_allow_html=True)
            
            # layout row one: 2 sections with Revenue and Net Income, both available annualy & quarterly
            # incase the companies currencies do not match, the financials of the h2h company will be converted to match the inti company using the current exchange rate
            revenue_container, profitability_container = st.columns([1,1])
        
            # get chart data
            chart_a_rev, chart_q_rev, chart_a_inc, chart_q_inc, helper_text_rev, helper_text_inc, fin_curr = public.load_h2h_revenue_and_profitability_charts(ticker,ticker_h2h,name,name_h2h)
            
            # build content
            with revenue_container:
                annual_rev_container, quarterly_rev_conatainer = st.tabs(['Annual Revenue','Quarterly Revenue'])
                
                with annual_rev_container:
                    st.markdown(f'in {fin_curr}',help=helper_text_rev)
                    st.vega_lite_chart(chart_a_rev)
                    
                with quarterly_rev_conatainer:
                    if helper_text_inc != '':
                        st.markdown(f'in {fin_curr}',help=helper_text_inc)
                    else:
                        st.markdown(f'in {fin_curr}')
                    st.vega_lite_chart(chart_q_rev)
                    
            with profitability_container:
                annual_prof_container, quarterly_prof_container = st.tabs(['Annual Net Income','Quarterly Net Income'])
                
                with annual_prof_container:
                    st.markdown(f'in {fin_curr}',help=helper_text_rev)
                    st.vega_lite_chart(chart_a_inc)
                    
                with quarterly_prof_container:
                    if helper_text_inc != '':
                        st.markdown(f'in {fin_curr}',help=helper_text_inc)
                    else:
                        st.markdown(f'in {fin_curr}')
                    st.vega_lite_chart(chart_q_inc)
            
            
            st.divider()
            
            # second row: key ratios (Enterprise Value, EV/Revenue, EV/EBITDA, Debt/Equity, Quick Ratio, Current Ratio, Return on Assets, Return on Equity) and past earnings estimates vs. actuals 
            ratios_container, helper, earnings_container = st.columns([1,0.2,2])
            
            with ratios_container:
                st.markdown('<div><br><br></div>',unsafe_allow_html=True)
                data = public.get_h2h_fin_ratios(ticker,ticker_h2h)
                for element in data:
                    build_h2h_row(element[0],element[1],element[2],3)
                    
            with earnings_container:
                st.plotly_chart(public.get_earnings_chart_h2h(ticker,ticker_h2h),use_container_width=True)
        
    
    elif is_sus_private or is_sus_private_h2h:
        #once either company is probably private, both are handled as private; therefore data for both is collected from crunchbase: possible as crunchbase also has public companies in its register and plus as it simplifies the h2h comparison
        #check if private companies match
        if gw.check_if_private(st.session_state.search_input):
            is_private = True
        if gw.check_if_private(st.session_state.search_input_h2h):
            is_private_h2h = True
            
        # build if private company search yields result for both companies
        if is_private and is_private_h2h:
            pass
        
        # Error messages if companies can't be found
        elif is_private:
            st.write('''Comparison company can't be found. Please try  different input.''')
        elif is_private_h2h:
            st.write('''Base company can't be found. Please try  different input.''')
        else:
            st.write('Neither company can be found. Please try different inputs.')


# startup search bars, if either or both inputs are missing

# init company has public company match, h2h company doesn't
elif st.session_state.search_input != 'n/a': 
    with st.form(key='search_bar_start'):
        search_bar, search_bar_h2h, search_button = st.columns([3,3,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',value=st.session_state.search_input,placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_bar_h2h:
            search_name_h2h = st.text_input(label='search_bar_h2h',placeholder='Compared to?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                st.session_state.search_input_h2h = search_name_h2h
                st.rerun()

# h2h company has public company match, init company doesn't
elif st.session_state.search_input_h2h != 'n/a': 
    with st.form(key='search_bar_start'):
        search_bar, search_bar_h2h, search_button = st.columns([3,3,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_bar_h2h:
            search_name_h2h = st.text_input(label='search_bar_h2h',value=st.session_state.search_input_h2h,placeholder='Compared to?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                st.session_state.search_input_h2h = search_name_h2h
                st.rerun()

# neither input matched
else:
    with st.form(key='search_bar_start'):
        search_bar, search_bar_h2h, search_button = st.columns([3,3,1])
        with search_bar:
            search_name = st.text_input(label='search_bar',placeholder='What Company are you looking for?',label_visibility='collapsed')
        with search_bar_h2h:
            search_name_h2h = st.text_input(label='search_bar_h2h',placeholder='Compared to?',label_visibility='collapsed')
        with search_button:
            isclick = st.form_submit_button('Start Search',use_container_width=True)
            if isclick:
                st.session_state.search_input = search_name
                st.session_state.search_input_h2h = search_name_h2h
                st.rerun()