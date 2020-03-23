import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.subplots as subplots
import requests
from bs4 import BeautifulSoup
import datetime
import matplotlib.pyplot as plt

# # Using generic style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Instantiate app and suppress callbacks
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
server = app.server

def scrapeInfo(url,item,identifier,idName):
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"html.parser")
    table = soup.find(item,{identifier:idName})
    return table

def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%m-%d')
        return True
    except:
        return False

def getSAData():
    global SADF, maxTests,fig

    table = scrapeInfo('https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Africa', "table", "class",
                       "wikitable mw-collapsible")
    rows = []
    for element in table.find('tbody').find_all('tr'):
        rows.append(element.get_text().split('\n'))

    Date = [row[3] for row in rows if (len(row) > 3)]
    Date = [element for element in Date if validate(element) == True]
    Tests = [row[35] for row in rows if (len(row) > 35)]
    Tests = [element for element in Tests if (element.isdigit() or len(str(element)) == 0)]
    Total = [row[25] for row in rows if (len(row) > 25)]
    Total = [element for element in Total if (element.isdigit() or len(str(element)) == 0)]

    mapper = [{n: m} for n, m in list(zip(Date, Total))]
    SADF = pd.DataFrame(data=[d.values() for d in mapper], columns=['Total cases'],
                        index=[list(d.keys())[0] for d in mapper])
    SADF['Cumulative tests'] = Tests
    SADF.index.name = 'Date'
    SADF = SADF.replace('', np.nan)
    SADF = SADF.apply(pd.to_numeric)
    SADF['Daily tests'] = SADF['Cumulative tests'] - SADF['Cumulative tests'].shift(1)
    maxTests = 100
    SADF['Cases per {} tests'.format(maxTests)] = round((SADF['Total cases'] * maxTests) / SADF['Daily tests'], 3)
    fig = subplots.make_subplots()
    fig['layout'].update(height=500, title='Cases per 100 tests for South Africa as of {}'.format(SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                         xaxis_title="Date",
                         yaxis_title="Cases per 100 tests")
    fig['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    SADF = SADF.reset_index()
    SADF['Date'] = SADF['Date'].apply(lambda x: "2020-" + x)
    fig.append_trace({'x': SADF['Date'], 'y': SADF['Cases per {} tests'.format(maxTests)], 'type': 'bar', 'name': 'Cases per 100 tests'}, 1,1)
    print("Yes")
    fig.show()
getSAData()

app.layout =  html.Div([
        dbc.Form([
                    dbc.FormGroup(
                     [
                        dbc.Label("Population outside isolation", html_for="example-email-row"),
                        dbc.Input(id='pop', value=25000000,
                                  type='number',
                                  placeholder="Enter Population",
                            ),
                        ],className="mr-3",
                    ),
                    dbc.FormGroup(
                    [
                        dbc.Label("Number of days before recovery", html_for="example-email-row"),
                        dcc.Input(id='recDays', value=14, type='number',
                            ),
                        ],className="mr-3",
                    )],inline=True,
        ),
        dbc.Form([
                    dbc.FormGroup(
                    [
                        dbc.Label("Average infections a person passes during their sickness period above", html_for="example-email-row"),
                        dcc.Input(id='avgInfections', value=3, type='number',
                             ),
                        ],className="mr-3",
                    ),
                    dbc.FormGroup(
                    [
                        dbc.Label("Initial Infections", html_for="example-email-row"),
                        dcc.Input(id='initialInfections', value=85, type='number',
                              ),
                        ], className="mr-3",
                    )],inline=True,),html.Br(),html.Div([
    dcc.Graph(
    id='basic-interactions',config={'scrollZoom':True,'showTips':True}),html.Br(),html.H1(id='infected')]),
        html.Br(),html.Div([dcc.Graph(id='SA',figure=fig, config={'scrollZoom': True, 'showTips': True})])])

@app.callback([Output('basic-interactions','figure'),Output('infected','children')],[Input('pop','value'),
                                              Input('recDays','value'),Input('avgInfections','value'),Input('initialInfections','value')])
def runModel(Pop,recDays,avgInfections,initialInfections):
    if recDays and Pop and avgInfections:
        # Number of people self-isolating
        selfIsolating = Pop
        # Number of people susceptible
        S_0 = 1
        # Number of people infected
        I_0 = initialInfections/selfIsolating

        print('Initial Number of infected {}'.format(I_0 / S_0 * selfIsolating))

        # Number of people recovered
        R_0 = 0

        # Days to recovery
        recovDays = recDays
        # How many people the person infects every 2 weeks
        gamma = avgInfections/recDays
        # period of infectiousness is atleast 14 days (recovery)
        beta = 1/recDays

        # tau (time step)
        tau = 0.1

        t_max = 1000

        S = [S_0]
        I = [I_0]
        R = [R_0]
        t = [0]

        def function(S_0, I_0, R_0):
            S_dot = -gamma * S_0 * I_0
            I_dot = gamma * S_0 * I_0 - beta * I_0
            R_dot = beta * I_0
            return S_dot, I_dot, R_dot

        t_0 = 0

        while t_0 <= t_max:
            S_1 = S_0 + tau * function(S_0, I_0, R_0)[0]
            I_1 = I_0 + tau * function(S_0, I_0, R_0)[1]
            R_1 = R_0 + tau * function(S_0, I_0, R_0)[2]
            if round(R_1, 2) == 1:
                print('Time taken for everyone to recover {} days'.format(t_0))
                break
            S.append(S_1)
            I.append(I_1)
            R.append(R_1)
            t.append(t_0)
            S_0 = S_1
            I_0 = I_1
            R_0 = R_1
            t_0 += tau
        print('Peak infection at {} days with {} people infected at once'.format(round(np.argmax(I) * tau,3), round(max(I) * selfIsolating),3))
        stringy = 'Peak infection at {} days with {} people infected'.format(round(np.argmax(I) * tau,3), round(max(I) * selfIsolating))
        df= pd.DataFrame(data = list(zip(t,I)),columns=['Time','Infected'])
        df['Susceptible'] = S
        df['Recovered'] = R
        fig = subplots.make_subplots()
        fig['layout'].update(height=500, title='SIR Model evolution of Virus',title_x=0.5,
                         xaxis_title = "Days",
                         yaxis_title = "Population")
        fig['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
        fig.append_trace({'x': df['Time'], 'y': df['Infected']*selfIsolating, 'type': 'scatter', 'name': 'Infected'}, 1, 1)
        fig.append_trace({'x': df['Time'], 'y': df['Susceptible']*selfIsolating, 'type': 'scatter', 'name': 'Susceptible'}, 1, 1)
        fig.append_trace({'x': df['Time'], 'y': df['Recovered']*selfIsolating, 'type': 'scatter', 'name': 'Recovered'}, 1, 1)
        return [fig,stringy]
    else:
        return [{
            'data': [],'layout': {
        'height': 500,
                'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
            }
        },'None']

if __name__ == '__main__':
    app.run_server(debug=True,port=8030)



