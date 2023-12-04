#yahoo finance data
import yahooquery as yq
import yfinance as yf

#general
import pandas as pd
from datetime import datetime as dt
import toml

#openai 
from openai import OpenAI

#graphing
import matplotlib.pyplot as plt
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.express as px

class public():
    def get_comp_desc(ticker):
        try:
            desc = yq.Ticker(ticker).asset_profile[ticker]['longBusinessSummary']
        except:
            desc = 'n/a'
        return desc

    def get_general_company_kpis(ticker):
        needed_values = ['HQ','FTE','Website','Sector','Industry']
        search_values = ['city','fullTimeEmployees','website','sector','industry']
        search = yq.Ticker(ticker).summary_profile[ticker]
        return_dict = {}
        for needed_value, search_value in zip(needed_values,search_values):
            try:
                if needed_value == 'HQ':
                    city = search['city']
                    country = search['country']
                    return_dict[needed_value] = f'{city}, {country}'
                elif needed_value == 'FTE':
                    try:
                        return_dict[needed_value] = "{:,}".format(int(search[search_value]))[::-1].replace(',', "'")[::-1]
                    except:
                        return_dict[needed_value] = 'n/a'
                else:
                    return_dict[needed_value] = search[search_value]
            except:
                return_dict[needed_value] = 'n/a'
        return return_dict

    def get_current_price_data(ticker):
        needed_values = ['currency','Market Cap','exchange','date','time','current_price','change','Forward P/E','Beta (5y Monthly)','Dividend Yield (trailing)']
        search_values = ['currency','marketCap','exchangeName','regularMarketTime','regularMarketTime','regularMarketPrice','regularMarketChangePercent','forwardPE','beta','trailingAnnualDividendYield']
        search_one = yq.Ticker(ticker).summary_detail[ticker]
        search_two = yq.Ticker(ticker).price[ticker]
        if isinstance(search_one,str):
            search = search_two
        elif isinstance(search_two,str):
            search = search_one
        else:
            search = search_one | search_two
        base_dict = {}
        for needed_value, search_value in zip(needed_values,search_values):
            try:
                if needed_value == 'current_price':
                    base_dict[needed_value] = str(round(search[search_value],2))
                elif needed_value == 'change':
                    base_dict[needed_value] = round(search[search_value]*100,1)
                elif needed_value == 'date':
                    base_dict[needed_value] = dt.strptime(search[search_value],'%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')
                elif needed_value == 'time':
                    base_dict[needed_value] = dt.strptime(search[search_value],'%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')
                elif needed_value == 'Dividend Yield (trailing)':
                    p_dividend_yield_float = round(search[search_value]*100,1)
                    base_dict[needed_value] = f'{p_dividend_yield_float}%'
                elif needed_value == 'Beta (5y Monthly)':
                    base_dict[needed_value] = round(search['beta'],1)
                elif needed_value == 'Market Cap':
                    base_dict[needed_value] = "{:,}".format(int(search[search_value]))[::-1].replace(',', "'")[::-1]
                elif needed_value == 'Forward P/E':
                    base_dict[needed_value] = round(search[search_value],2)
                else:
                    base_dict[needed_value] = search[search_value]
            except:
                base_dict[needed_value] = 'n/a'
        
        p_exchange = base_dict['exchange']
        p_currency = base_dict['currency']
        p_date = base_dict['date']
        p_time = base_dict['time']
        quote_caption = f'{p_exchange} | {p_currency} | {p_date} | {p_time}'
        
        table = []
        for name in ['Market Cap','Forward P/E','Beta (5y Monthly)','Dividend Yield (trailing)']:
            value = base_dict[name]
            if name == 'Market Cap':
                name = f'Market Cap ({p_currency})'
            table.append({'Indicator':name,'Value':value})
        
        return base_dict['current_price'], base_dict['change'], quote_caption, table

    def get_hist_price_chart(ticker,timeframe,frequency):
        hist_data = pd.DataFrame(yf.Ticker(ticker).history(period=timeframe,interval=frequency)[['Close']]).to_dict('index')
        temp_hist_data = []
        for element in hist_data.keys():
            try:
                value = round(float(hist_data[element]['Close']),5)
                temp_hist_data.append({'time':int(element.timestamp())+3600,'value': value}) #time +3600 adds one hour - adjusts for daylight savings
            except:
                pass
        hist_data = temp_hist_data
        if timeframe in ['1d','1mo']:
            chartOptions = {
                "layout": {'textColor':'white',
                    "background": {
                        "type": 'solid',
                        "color": 'transparent'
                    }
                },
                "timeScale": {
                    "timeVisible": True,
                    "secondsVisible": False,
                },
            }
        else:
            chartOptions = {
                "layout": {'textColor':'white',
                    "background": {
                        "type": 'solid',
                        "color": 'transparent'
                    }
                }
            }

        seriesLineChart = [{
            "type": 'Line',
            "data": hist_data,
            "options": {'color':'rgb(229,61,62)'}
        }]

        renderLightweightCharts([
            {
                "chart": chartOptions,
                "series": seriesLineChart
            }
        ], timeframe)

    def get_fin_chart(ticker,company_name):
        try:
            df = yq.Ticker(ticker).income_statement()
            try:
                df = df[['asOfDate','TotalRevenue','NormalizedEBITDA','NetIncome']].set_index('asOfDate')
            except:
                try:
                    df = df[['asOfDate','TotalRevenue','EBITDA','NetIncome']].set_index('asOfDate')
                except:
                    df = df[['asOfDate','TotalRevenue','NetIncome']].set_index('asOfDate')
                    
            base_color = (16/256,18/256,23/256)
            accent_one = 'white'
            accent_two = (225/256,53/256,54/256)
            
            x_values = []
            y_values = []
            for index in df.index:
                x_values.append(f'FY {index.year}')
            x_values[len(x_values)-1] = 'LTM'

            if len(df.columns) == 2:
                for value in df.values:
                    if len(str(int(value[0]))) > 9:
                        revenue = round(value[0]/1000000000,1)
                        info_text = 'in billions'
                    elif len(str(int(value[0]))) > 6:
                        revenue = round(value[0]/1000000,1)
                        info_text = 'in millions'
                    elif len(str(int(value[0]))) > 3:
                        revenue = round(value[0]/1000,1)
                        info_text = 'in thousands'
                    y_values.append([revenue,round(float(value[1]/value[0]),3)])
                columns = ['Revenue','Net Profit Margin']
                final_df = pd.DataFrame(data=y_values,index=x_values,columns=columns)
                    
                fig, ax1 = plt.subplots()
                fig.patch.set_alpha(0)
                ax1.bar(final_df.index, final_df['Revenue'], color='none', edgecolor=accent_two, label='Revenue',width=0.15)
                ax1.set_facecolor('none')
                ax1.set_ylim(0, ax1.get_ylim()[1])
                ax2 = ax1.twinx()
                ax2.set_facecolor('none')
                ax2.plot(final_df.index, final_df['Net Profit Margin'], accent_one,linewidth=1, label='Net Profit Margin',linestyle='dashed',marker='o')
                ax2.set_ylim(ax2.get_ylim()[0], ax2.get_ylim()[1]*1.5)
                
                #next lines mostly chatgpt, credit?
                for x, y in zip(final_df.index, final_df['Net Profit Margin']):
                    ax2.annotate(f'{y*100:.1f}%', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', color=accent_one,bbox=dict(boxstyle='round,pad=0.5', edgecolor=accent_one, facecolor=base_color))
                
            else:
                for value in df.values:
                    if len(str(int(value[0]))) > 9:
                        revenue = round(value[0]/1000000000,1)
                        info_text = 'in billions'
                    elif len(str(int(value[0]))) > 6:
                        revenue = round(value[0]/1000000,1)
                        info_text = 'in millions'
                    elif len(str(int(value[0]))) > 3:
                        revenue = round(value[0]/1000,1)
                        info_text = 'in thousands'
                    y_values.append([revenue,round(float(value[1]/value[0]),3),round(float(value[2]/value[0]),3)])
                columns = ['Revenue','EBITDA Margin','Net Profit Margin']
                final_df = pd.DataFrame(data=y_values,index=x_values,columns=columns)
                    
                fig, ax1 = plt.subplots()
                fig.patch.set_alpha(0)
                ax1.bar(final_df.index, final_df['Revenue'], color='none', edgecolor=accent_two, label='Revenue',width=0.15)
                ax1.set_facecolor('none')
                ax1.set_ylim(0, ax1.get_ylim()[1])
                ax2 = ax1.twinx()
                ax2.set_facecolor('none')
                ax2.plot(final_df.index, final_df['EBITDA Margin'], accent_one,linewidth=1, label='EBITDA Margin',marker='o')
                ax2.plot(final_df.index, final_df['Net Profit Margin'], accent_one,linewidth=1, label='Net Profit Margin',linestyle='dashed',marker='o')
                ax2.set_ylim(ax2.get_ylim()[0], ax2.get_ylim()[1]*1.5)
                
                #next lines mostly chatgpt, credit?
                for x, y in zip(final_df.index, final_df['EBITDA Margin']):
                    ax2.annotate(f'{y*100:.1f}%', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', color=accent_one,bbox=dict(boxstyle='round,pad=0.5', edgecolor=accent_one, facecolor=base_color))
                for x, y in zip(final_df.index, final_df['Net Profit Margin']):
                    ax2.annotate(f'{y*100:.1f}%', (x, y), textcoords="offset points", xytext=(0, 10), ha='center', color=accent_one,bbox=dict(boxstyle='round,pad=0.5', edgecolor=accent_one, facecolor=base_color))

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            lines = lines1 + lines2
            labels = labels1 + labels2
            ax1.tick_params(axis='x', colors=accent_one)
            ax1.tick_params(axis='y', colors=accent_one)
            ax2.tick_params(axis='y', colors='none')
            ax2.spines['bottom'].set_color(accent_one)
            ax2.spines['top'].set_color(base_color)
            ax2.spines['right'].set_color(base_color)
            ax2.spines['left'].set_color(accent_one)
            plt.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, -0.1),frameon=False,labelcolor=accent_one,ncol=3)
            
            end_of_fin_year = df.index[0].strftime('%d.%m')
            end_of_ltm = df.index[len(df.index)-1].strftime('%d.%m.%y')
            helper_text = f'''{company_name}'s financial year ends on the {end_of_fin_year} of the respective year.
            Last Twelve Months (LTM) goes up to the {end_of_ltm}. The EBIDTA Margin is based on Adjusted EBITDA if available. The detailed financial statements can be found under the "Financials" tab.'''
        
        except:
            fig = 'Graph not available.'
            info_text = ''
            helper_text = 'n/a'
        return fig, info_text, helper_text

    def get_key_fin_stats(ticker):
        needed_values = ['Enterprise Value','EV/Revenue','EV/EBITDA','Debt/Equity','Quick Ratio','Current Ratio','Return on Assets','Return on Equity']
        search_values = ['enterpriseValue','enterpriseToRevenue','enterpriseToEbitda','debtToEquity','quickRatio','currentRatio','returnOnAssets','returnOnEquity']
        search_one = yq.Ticker(ticker).key_stats[ticker]
        search_two = yq.Ticker(ticker).financial_data[ticker]
        if isinstance(search_one,str):
            search = search_two
        elif isinstance(search_two,str):
            search = search_one
        else:
            search = search_one | search_two
        return_dict = {}
        for needed_value, search_value in zip(needed_values,search_values):
            try:
                if needed_value in ['Enterprise Value']:
                    try:
                        currency = search['financialCurrency']
                        return_dict[f'{needed_value} ({currency})'] = "{:,}".format(int(search[search_value]))[::-1].replace(',', "'")[::-1]
                    except:
                        return_dict[needed_value] = "{:,}".format(int(search[search_value]))[::-1].replace(',', "'")[::-1]
                elif needed_value in ['EV/Revenue','EV/EBITDA','Quick Ratio','Current Ratio']:
                    temp_value = round(search[search_value],2)
                    return_dict[needed_value] = f'{temp_value}x'
                elif needed_value in ['Debt/Equity','Return on Assets','Return on Equity']:
                    if needed_value == 'Debt/Equity':
                        temp_value = round(search[search_value],1)
                    else:
                        temp_value = round(search[search_value]*100,1)
                    return_dict[needed_value] = f'{temp_value}%'
            except:
                return_dict[needed_value] = 'n/a'
    
        try:
            return return_dict, search['financialCurrency']
        except:
            return return_dict, 'n/a'

    def get_top_inst_holders(ticker):
        try:
            inst_holders = yf.Ticker(ticker).get_institutional_holders()
        except:
            inst_holders = 'n/a'
            
        try:
            currency = yq.Ticker(ticker).financial_data[ticker]['financialCurrency']
        except:
            currency = 'n/a'
        
        def reformat_inst_holders_shares(share_count):
            return "{:,}".format(int(share_count))[::-1].replace(',', "'")[::-1]
        def reformat_inst_holders_date(date):
            return date.strftime('%d.%m.%Y')
        def reformat_inst_holders_out(perc):
            return round(perc*100,1)
        def reformat_inst_holders_value(value):
            value = "{:,}".format(int(value))[::-1].replace(',', "'")[::-1]
            return f'{value} {currency}'

        try:
            inst_holders['Shares'] = inst_holders['Shares'].apply(reformat_inst_holders_shares)
        except:
            pass
        try:
            inst_holders['Date Reported'] = inst_holders['Date Reported'].apply(reformat_inst_holders_date)
        except:
            pass
        try:
            inst_holders['% Out'] = inst_holders['% Out'].apply(reformat_inst_holders_out)
        except:
            pass
        try:
            inst_holders['Value'] = inst_holders['Value'].apply(reformat_inst_holders_value)
        except:
            pass
        
        try:
            sum_perc = 100-(inst_holders['% Out'].sum())
            inst_holders.loc[len(inst_holders.index)] = ['Rest','n/a','n/a',sum_perc,'n/a']
            fig = px.pie(inst_holders,values='% Out',names='Holder')
        except:
            fig = 'n/a'
        
        return fig

    def get_company_leadership(ticker):
        try:
            comp_officers = yq.Ticker(ticker).company_officers
        except:
            comp_officers = 'n/a'
        for item_to_drop in ['maxAge','yearBorn','fiscalYear','totalPay','exercisedValue','unexercisedValue']:
            try:
                comp_officers.drop(item_to_drop, axis=1, inplace=True)
            except:
                pass
        try:
            comp_officers.columns = ['Name','Age','Title']
        except:
            pass
            
        return comp_officers

    def get_recent_news(ticker):
        
        try:
            news = pd.DataFrame(yf.Ticker(ticker).get_news())
        except:
            news = 'n/a'
        for item_to_drop in ['uuid','type','thumbnail','relatedTickers']:
            try:
                news.drop(item_to_drop, axis=1, inplace=True)
            except:
                pass
            
        def reformat_time(time):
            return dt.fromtimestamp(time).strftime('%d.%m.%Y')
        
        try:
            news['providerPublishTime'] = news['providerPublishTime'].apply(reformat_time)
        except:
            pass

        try:
            news.columns = ['Title','Publisher','Link','Date']
        except:
            pass
        
        try:
            news = news[['Title','Publisher','Date','Link']]
        except:
            news =  'Not Available.'

        return news
    
    def get_ai_opinion(investor, ticker, company_name):
        try:
            if investor == 'buffet':
                name = 'Warren Buffet'
            elif investor == 'lynch':
                name = 'Peter Lynch'
            elif investor == 'graham':
                name = 'Benjamin Graham'
            
            fin_data = yq.Ticker(ticker).all_financial_data()
            general_pull = yq.Ticker(ticker).asset_profile[ticker]
            
            needed_values = ['HQ Country','Company Description','Industry','Sector','Number of Full Time Employees']
            search_values = ['country','longBusinessSummary','industry','sector','fullTimeEmployees']
            
            general_values = {}
            
            for needed_value, search_value in zip(needed_values,search_values):
                try:
                    general_values[needed_value] = general_pull[search_value]
                except:
                    pass
                
            #build request
            request_string = f'''Pretend to be the famous investor {name}, and consider the following general information 
            about the company {company_name}: {general_values} in combination with the following financial data: {fin_data}. 
            Stay in your role and give a short assessment about what you like and dislike about the company. 
            If the information seems insufficient still stay in role and give the best possible answer without 
            requesting more data or angles. Keep the answer to a maximum of 3 to 4 sentences and only provide your viewpoint in your role.
            Should it be impossible to return a proper answer return the following text and nothing else: {name} is currently
            stuck in a call, but will be back soon.'''
            
            #make request   
            response = OpenAI(api_key=toml.load('user_config.toml')['openai_api']['key']).chat.completions.create(
                messages=[
                    {'role': 'user',
                    'content': request_string}],
                model="gpt-3.5-turbo") 
            
        except:
            response = 'There was an error retrieving the answer. Please ensure that you provided the correct API key and that your OpenAI account has sufficient tokens.'
        return response
    
    def get_h2h_general(ticker):
        pull_one = yq.Ticker(ticker).summary_profile[ticker]
        pull_two = yq.Ticker(ticker).financial_data[ticker]
        if isinstance(pull_one,str):
            search = pull_two
        elif isinstance(pull_two,str):
            search = pull_one
        else:
            search = pull_one | pull_two
        needed_values = ['sector','industry','fullTimeEmployees','hq','financialCurrency','recommendationKey','esg_risk']
        return_dict = {}
        for value in needed_values:
            try:
                if value == 'hq':
                    return_dict[value] = f''' {search['city']},  {search['country']}'''
                elif value == 'esg_risk':
                    try:
                        data = yq.Ticker(ticker).esg_scores[ticker]
                        df_data = pd.DataFrame({'scores':['Environmental Risk', 'Social Risk', 'Governance Risk'],
                                                'start':[0, data['environmentScore'], data['socialScore']+data['environmentScore']],
                                                'end':[data['environmentScore'], data['socialScore']+data['environmentScore'], data['governanceScore']+data['socialScore']+data['environmentScore']],})
            
                        total = data['governanceScore']+data['socialScore']+data['environmentScore']

                        #vega lite chart eleement
                        chart = {'$schema':'https://vega.github.io/schema/vega-lite/v2.json',
                                'data':{'values':df_data.to_dict(orient='records')},
                                'layer':[{'mark':{'type':'bar', 'color':'red'},
                                        'encoding':{'y':{'field':'scores', 'type':'ordinal'},
                                                    'x':{'field':'start', 'type':'quantitative', 'scale':{'zero':False, 'domain':[0, 100]}},
                                                    'x2':{'field':'end', 'type':'quantitative', 'scale':{'zero':False, 'domain':[0, 100]}}}},
                                        {'mark':{'type':'rule', 'color':'red'},
                                        'encoding':{
                                            'x':{'field':'end', 'aggregate':'max'}, 
                                            'size':{'value':2},
                                            'strokeDash':{'value':[2,2]}}},
                                        {'mark':{'type':'text', 'align':'left', 'baseline':'middle', 'dx':5, 'color':'white'},
                                        'encoding':{'x':{'field':'end', 'aggregate':'max'},  
                                                    'text':{'value':f'Total ESG Risk:{str(round(total, 2))}'}}}],
                                'config':{'axis':{'titleFontSize':0}}}
                        
                        return_dict[value] = chart
                        
                    except:
                        return_dict[value] = 'n/a'
                        
                elif value == 'fullTimeEmployees':
                    return_dict[value] = "{:,}".format(int(search[value]))[::-1].replace(',', "'")[::-1]
                
                else:
                    return_dict[value] = search[value]
            except:
                return_dict[value] = 'n/a'
        return return_dict
    
    def build_h2h_relative_price_chart(ticker_init,ticker_h2h,timeframe,frequency):
        hist_data_init = pd.DataFrame(yf.Ticker(ticker_init).history(period=timeframe,interval=frequency)[['Close']]).to_dict('index')
        hist_data_h2h = pd.DataFrame(yf.Ticker(ticker_h2h).history(period=timeframe,interval=frequency)[['Close']]).to_dict('index')
        
        base_value_init = float(next(iter(hist_data_init.values()))['Close'])
        base_value_h2h = float(next(iter(hist_data_h2h.values()))['Close'])

        # Process and convert data to percentage values
        hist_data_init_percentage = [{'time': int(element.timestamp()) + 3600, 'value': round(float(data['Close']) / base_value_init * 100, 5)} for element, data in hist_data_init.items()]
        hist_data_h2h_percentage = [{'time': int(element.timestamp()) + 3600, 'value': round(float(data['Close']) / base_value_h2h * 100, 5)} for element, data in hist_data_h2h.items()]
        
        if timeframe in ['1d', '1mo']:
            chartOptions = {
                            "layout": {'textColor': 'white',
                                    "background": {
                                        "type": 'solid',
                                        "color": 'transparent'
                                    }
                                    },
                            "timeScale": {
                                "timeVisible": True,
                                "secondsVisible": False,
                            },
                            'mode': 2,
                            'rightPriceScale': {
                                'borderColor': 'rgba(197, 203, 206, 0.8)',
                                'mode': 2, 
                                'autoScale': True,
                                'scaleMargins': {
                                    'top': 0.1,
                                    'bottom': 0.1
                                },
                                'formatting': {
                                    'type': 'percent',
                                    'precision': 2,
                                },
                            },
                        }
        else:
            chartOptions = {
                "layout": {'textColor': 'white',
                        "background": {
                            "type": 'solid',
                            "color": 'transparent'
                        }
                        },
                'mode': 2,
                'rightPriceScale': {
                    'borderColor': 'rgba(197, 203, 206, 0.8)',
                    'mode': 2,  
                    'autoScale': True,
                    'scaleMargins': {
                        'top': 0.1,
                        'bottom': 0.1
                    },
                    'formatting': {
                        'type': 'percent',
                        'precision': 2,
                    },
                },
            }

        seriesLineChart = [{
            "type": 'Line',
            "data": hist_data_init_percentage,
            "options": {'color':'rgb(229,61,62)'}
        },
            {"type": 'Line',
            "data": hist_data_h2h_percentage,
            "options": {'color':'rgb(177,156,217)'}
        }]

        renderLightweightCharts([
            {
                "chart": chartOptions,
                "series": seriesLineChart
            }
        ], timeframe)
        
    def get_stock_movements_h2h(ticker_init, ticker_h2h):
        
        periods = [['1 Day','1d','1m'],
                    ['1 Month','1mo','1h'], 
                    ['6 Months','6mo','1h'],
                    ['YTD','ytd','1d'],
                    ['12 Months','1y','1d'],
                    ['5 Years','5y','1d'],
                    ['10 Years','10y','5d'],
                    ['20 Years','20y','5d'],
                    ['All Time','max','5d']]
        
        return_list = []
        
        for period in periods:
            
            try:
                history_init = yf.Ticker(ticker_init).history(period=period[1],interval=period[2])[['Close']]
                change_init = f'{round(((history_init.iloc[len(history_init)-1].iloc[0] / history_init.iloc[0].iloc[0]) - 1)*100,2)}%'
            except:
                change_init = 'n/a'
            
            try:
                history_h2h = yf.Ticker(ticker_h2h).history(period=period[1],interval=period[2])[['Close']]
                change_h2h = f'{round(((history_h2h.iloc[len(history_h2h)-1].iloc[0] / history_h2h.iloc[0].iloc[0]) - 1)*100,2)}%'
            except:
                change_h2h = 'n/a'
                
            return_list.append([period[0],change_init,change_h2h])
        
        return return_list
    
    def load_h2h_revenue_and_profitability_charts(ticker_init, ticker_h2h, name_init, name_h2h):
        inc_stmt_a_init = yq.Ticker(ticker_init).income_statement(trailing=False)[['asOfDate','currencyCode','periodType','TotalRevenue','NetIncome']]
        inc_stmt_a_init['asOfDate'] = inc_stmt_a_init['asOfDate'].dt.strftime('%d-%m-%Y')
        
        inc_stmt_a_h2h = yq.Ticker(ticker_h2h).income_statement(trailing=False)[['asOfDate','currencyCode','periodType','TotalRevenue','NetIncome']]
        inc_stmt_a_h2h['asOfDate'] = inc_stmt_a_h2h['asOfDate'].dt.strftime('%d-%m-%Y')
        
        inc_stmt_q_init = yq.Ticker(ticker_init).income_statement(frequency='q',trailing=False)[['asOfDate','currencyCode','periodType','TotalRevenue','NetIncome']]
        inc_stmt_q_init['asOfDate'] = inc_stmt_q_init['asOfDate'].dt.strftime('%d-%m-%Y')
        
        inc_stmt_q_h2h = yq.Ticker(ticker_h2h).income_statement(frequency='q',trailing=False)[['asOfDate','currencyCode','periodType','TotalRevenue','NetIncome']]
        inc_stmt_q_h2h['asOfDate'] = inc_stmt_q_h2h['asOfDate'].dt.strftime('%d-%m-%Y')

        def quarter_check(date_str):
            if date_str[:5] == '31-03':
                quarter = 'Q1'
            elif date_str[:5] == '30-06':
                quarter = 'Q2'
            elif date_str[:5] == '30-09':
                quarter = 'Q3'
            elif date_str[:5] == '31-12':
                quarter = 'Q4'
            return quarter

        end_fin_year_init = inc_stmt_a_init['asOfDate'].to_list()[0][:5].replace('-','.')
        end_fin_year_h2h = inc_stmt_a_h2h['asOfDate'].to_list()[0][:5].replace('-','.')

        #check for currency match, if no match. get conversion rate + set helper texts
        curr_init = inc_stmt_a_init['currencyCode'].iloc[0]
        curr_h2h = inc_stmt_a_h2h['currencyCode'].iloc[0]
        helper_text_one = f'''{name_init}'s financial year ends on the {end_fin_year_init} of the repective year. 
                                    {name_h2h}'s financial year ends on the {end_fin_year_h2h} of the repective year. '''
        if curr_init != curr_h2h:
            exchange_rate = yq.Ticker([f'{curr_init}{curr_h2h}=X']).quotes[f'{curr_init}{curr_h2h}=X']['regularMarketPrice']
            helper_text_two = f'As the companies denote their financials in different currencies, the results of {name_h2h} were adjusted at a current {curr_init}/{curr_h2h} rate of {exchange_rate} to match those of {name_init}.'
            helper_text_one = f'''{helper_text_one}{helper_text_two}'''
        else:
            exchange_rate = 1
            helper_text_two = ''

        #yearly revenue
        data_chart_one_a = []
        for element in inc_stmt_a_init['asOfDate'].to_list():
            period = f'FY {element[len(element)-2:]}'
            company = ticker_init
            revenue = int(inc_stmt_a_init.loc[inc_stmt_a_init['asOfDate']==element]['TotalRevenue'].iloc[0])
            data_chart_one_a.append({'Company':company,'Period':period,'Value':revenue})
            
        for element in inc_stmt_a_h2h['asOfDate'].to_list():
            period = f'FY {element[len(element)-2:]}'
            company = ticker_h2h
            revenue = int(inc_stmt_a_h2h.loc[inc_stmt_a_h2h['asOfDate']==element]['TotalRevenue'].iloc[0]/exchange_rate)
            data_chart_one_a.append({'Company':company,'Period':period,'Value':revenue})
        
        #quarterly revenue
        data_chart_one_q = []
        for element in inc_stmt_q_init['asOfDate'].to_list():
            quarter = quarter_check(element)
            period = f''''{element[len(element)-2:]} {quarter}'''
            company = ticker_init
            revenue = int(inc_stmt_q_init.loc[inc_stmt_q_init['asOfDate']==element]['TotalRevenue'].iloc[0])
            data_chart_one_q.append({'Company':company,'Period':period,'Value':revenue})
            
        for element in inc_stmt_q_h2h['asOfDate'].to_list():
            quarter = quarter_check(element)
            period = f''''{element[len(element)-2:]} {quarter}'''
            company = ticker_h2h
            revenue = int(inc_stmt_q_h2h.loc[inc_stmt_q_h2h['asOfDate']==element]['TotalRevenue'].iloc[0]/exchange_rate)
            data_chart_one_q.append({'Company':company,'Period':period,'Value':revenue})
        
        #annual net income
        data_chart_two_a = []
        for element in inc_stmt_a_init['asOfDate'].to_list():
            period = f'FY {element[len(element)-2:]}'
            company = ticker_init
            net_income = int(inc_stmt_a_init.loc[inc_stmt_a_init['asOfDate']==element]['NetIncome'].iloc[0])
            data_chart_two_a.append({'Company':company,'Period':period,'Value':net_income})
            
        for element in inc_stmt_a_h2h['asOfDate'].to_list():
            period = f'FY {element[len(element)-2:]}'
            company = ticker_h2h
            net_income = int(inc_stmt_a_h2h.loc[inc_stmt_a_h2h['asOfDate']==element]['NetIncome'].iloc[0]/exchange_rate)
            data_chart_two_a.append({'Company':company,'Period':period,'Value':net_income})
        
        
        #quarterly net income
        data_chart_two_q = []
        for element in inc_stmt_q_init['asOfDate'].to_list():
            quarter = quarter_check(element)
            period = f''''{element[len(element)-2:]} {quarter}'''
            company = ticker_init
            net_income = int(inc_stmt_q_init.loc[inc_stmt_q_init['asOfDate']==element]['NetIncome'].iloc[0])
            data_chart_two_q.append({'Company':company,'Period':period,'Value':net_income})
            
        for element in inc_stmt_q_h2h['asOfDate'].to_list():
            quarter = quarter_check(element)
            period = f''''{element[len(element)-2:]} {quarter}'''
            company = ticker_h2h
            net_income = int(inc_stmt_q_h2h.loc[inc_stmt_q_h2h['asOfDate']==element]['NetIncome'].iloc[0]/exchange_rate)
            data_chart_two_q.append({'Company':company,'Period':period,'Value':net_income})
            
        def build_chart(data):
            chart = {"data": {"values": data},
                    "mark": "bar",
                    "encoding": {"column": {"field": "Period", "header": {"orient": "bottom",'title':None}},
                                "y": {"field": "Value", "type": "quantitative", "axis": {"title": None}},
                                "x": {"field": "Company", "axis": {"title": None}, 'sort':None},
                                "color": {"field": "Company",'legend':None}, 'scale':None},
                    "config": {"view": {"stroke": "transparent"},
                    "range": {"category": ["rgb(229,61,62)", "rgb(177,156,217)"]}}}
            return chart
        
        chart_one_a = build_chart(data_chart_one_a)
        chart_one_q = build_chart(data_chart_one_q)
        chart_two_a = build_chart(data_chart_two_a)
        chart_two_q = build_chart(data_chart_two_q)
        
        return chart_one_a, chart_one_q, chart_two_a, chart_two_q, helper_text_one, helper_text_two, curr_init
        
        
    def get_h2h_fin_ratios(ticker_init,ticker_h2h):
        data_init, curr_init = public.get_key_fin_stats(ticker_init)
        data_h2h, curr_h2h = public.get_key_fin_stats(ticker_h2h)

        return_list = []
        for element_init, element_h2h in zip(data_init,data_h2h):
            if element_init[:16] == 'Enterprise Value':
                pass
            else:
                return_list.append([data_init[element_init],element_init,data_h2h[element_h2h]])
        return return_list
    
    def get_earnings_chart_h2h(ticker_init,ticker_h2h):
        data_init = yq.Ticker(ticker_init).earnings[ticker_init]['earningsChart']['quarterly']
        data_h2h = yq.Ticker(ticker_h2h).earnings[ticker_h2h]['earningsChart']['quarterly']
        
        consolidated_data = []
        for element in data_init:
            if element['actual'] > element['estimate']:
                caption = 'beat'
            elif element['actual'] == element['estimate']:
                caption = ''
            else:
                caption = 'miss'
            consolidated_data.append({'company':ticker_init.upper(),'id':f'{ticker_init.upper()} Actual','type':'Actual','timeframe':element['date'],'value':element['actual'],'caption':caption})
            consolidated_data.append({'company':ticker_init.upper(),'id':f'{ticker_init.upper()} Estimate','type':'Estimate','timeframe':element['date'],'value':element['estimate']})
        
        for element in data_h2h:
            if element['actual'] > element['estimate']:
                caption = 'beat'
            elif element['actual'] == element['estimate']:
                caption = ''
            else:
                caption = 'miss'
            consolidated_data.append({'company':ticker_h2h.upper(),'id':f'{ticker_h2h.upper()} Actual','type':'Actual','timeframe':element['date'],'value':element['actual'],'caption':caption})
            consolidated_data.append({'company':ticker_h2h.upper(),'id':f'{ticker_h2h.upper()} Estimate','type':'Estimate','timeframe':element['date'],'value':element['estimate']})
            
        consolidated_data = pd.DataFrame(consolidated_data)    

        color_map = {f'{ticker_init.upper()} Actual':'rgb(229,61,62)',
                    f'{ticker_init.upper()} Estimate':'rgb(255,173,174)',
                    f'{ticker_h2h.upper()} Actual':'rgb(177,156,217)',
                    f'{ticker_h2h.upper()} Estimate':'rgb(207,196,227)'}
        
        fig = px.scatter(consolidated_data, x='timeframe', y='value', color='id', symbol='type',
                text='caption', hover_name='id',color_discrete_map=color_map)

        fig.update_traces(textposition='bottom right')
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
        fig.update_layout(xaxis=dict(title_text=''),yaxis=dict(title_text='Earnings per Share'))
        fig.update_layout(legend=dict(title_text='',itemsizing='constant'))

        return fig

class private():
    
    def example():
        pass