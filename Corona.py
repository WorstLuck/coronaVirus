import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.subplots as subplots
from bs4 import BeautifulSoup
import datetime
import requests

r = requests.get('https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Africa')
soup = BeautifulSoup(r.content, "html.parser")
table = soup.find("table", {"class": "wikitable"})

# # Using generic style sheet
external_stylesheets =[dbc.themes.SIMPLEX]

# Instantiate app and suppress callbacks
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
server = app.server


def validate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%m-%d')
        return True
    except:
        return False


def getSAData():
    global SADF, maxTests, fig, fig2, fig3, fig4, fig5

    rows = []

    for element in table.find('tbody').find_all('tr'):
        rows.append(element.get_text().split('\n'))
    Date = [row[1] for row in rows if (len(row) > 3)]
    Date = [element for element in Date if validate(element) == True]
    Tests = [row[33] for row in rows if (len(row) > 35)]
    Tests = [element for element in Tests if (element.isdigit() or len(str(element)) == 0)]
    Total = [row[25] for row in rows if (len(row) > 25)]
    new = []
    for element in Total:
        if element.isdigit():
            pass
        else:
            for element2 in element:
                if element2.isdigit() == False:
                    element = element.replace(element2, '')
        new.append(element)
    Total = [element for element in new if element!='']
    print(len(Date),len(Tests),len(Total))
    mapper = [{n: m} for n, m in list(zip(Date, Total))]
    SADF = pd.DataFrame(data=[d.values() for d in mapper], columns=['Total cases'],
                        index=[list(d.keys())[0] for d in mapper])
    SADF['Total cases'] = SADF['Total cases'].astype(float)
    SADF['Daily cases'] = SADF['Total cases'] - SADF['Total cases'].shift(1)
    SADF['Cumulative tests'] = Tests
    SADF.index.name = 'Date'
    SADF = SADF.replace('', np.nan)
    SADF = SADF.apply(pd.to_numeric)
    SADF['Daily tests'] = SADF['Cumulative tests'] - SADF['Cumulative tests'].shift(1)
    maxTests = 100
    SADF['Cases per {} tests'.format(maxTests)] = round((SADF['Daily cases'] * maxTests) / SADF['Daily tests'], 3)
    SADF = SADF.replace([np.inf, -np.inf], np.nan)
    print(SADF)
    fig = subplots.make_subplots()
    fig['layout'].update(height=500, title='Cases per 100 tests for South Africa as of {}'.format(
        SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                         xaxis_title="Date",
                         yaxis_title="Cases per 100 tests")
    fig['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    SADF = SADF.reset_index()
    SADF['Date'] = SADF['Date'].apply(lambda x: "2020-" + x)
    fig.append_trace({'x': SADF['Date'], 'y': SADF['Cases per {} tests'.format(maxTests)], 'type': 'bar',
                      'name': 'Cases per 100 tests'}, 1, 1)
    fig.append_trace({'x': SADF['Date'], 'y': SADF['Cases per {} tests'.format(maxTests)], 'type': 'scatter',
                      'name': 'Cases per 100 tests'}, 1, 1)
    fig2 = subplots.make_subplots()
    fig2['layout'].update(height=500, title='Daily cases reported in South Africa as of {}'.format(
        SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                          xaxis_title="Date",
                          yaxis_title="Daily cases reported")
    fig2['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    fig2.append_trace({'x': SADF['Date'], 'y': SADF['Daily cases'], 'type': 'bar', 'name': 'Daily cases'}, 1, 1)
    fig2.append_trace({'x': SADF['Date'], 'y': SADF['Daily cases'], 'type': 'scatter', 'name': 'Daily cases'}, 1, 1)
    fig3 = subplots.make_subplots()
    fig3['layout'].update(height=500, title='Daliy tests reported in South Africa as of {}'.format(
        SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                          xaxis_title="Date",
                          yaxis_title="Daily tests reported")
    fig3['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    fig3.append_trace({'x': SADF['Date'], 'y': SADF['Daily tests'], 'type': 'bar', 'name': 'Daily tests'}, 1, 1)
    fig3.append_trace({'x': SADF['Date'], 'y': SADF['Daily tests'], 'type': 'scatter', 'name': 'Daily tests'}, 1, 1)
    fig4 = subplots.make_subplots()
    fig4['layout'].update(height=500, title='Total cases reported in South Africa as of {}'.format(
        SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                          xaxis_title="Date",
                          yaxis_title="Total cases reported")
    fig4['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    fig4.append_trace({'x': SADF['Date'], 'y': SADF['Total cases'], 'type': 'bar', 'name': 'Total cases'}, 1, 1)
    fig4.append_trace({'x': SADF['Date'], 'y': SADF['Total cases'], 'type': 'scatter', 'name': 'Total cases'}, 1, 1)
    fig5 = subplots.make_subplots()
    fig5['layout'].update(height=500, title='Total tests reported in South Africa as of {}'.format(
        SADF.reset_index()['Date'].tail(1).item()), title_x=0.5,
                          xaxis_title="Date",
                          yaxis_title="Total tests reported")
    fig5['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
    fig5.append_trace({'x': SADF['Date'], 'y': SADF['Cumulative tests'], 'type': 'bar', 'name': 'Total tests'}, 1, 1)
    fig5.append_trace({'x': SADF['Date'], 'y': SADF['Cumulative tests'], 'type': 'scatter', 'name': 'Total tests'}, 1, 1)

getSAData()

input_style = {'textAlign':'center','width':'auto'}
result_style = {'textAlign':'center','fontWeight': 'bold','borderStyle': 'groove','borderColor': '#eeeeee','borderWidth': '1px'}
label_font = {'textAlign':'center'}
app.layout = dbc.Container([dbc.Container([
    dbc.Row([
        dbc.Col([dbc.Label("Population outside isolation",style=label_font)],width={'size':2,"offset":1}),
        dbc.Col([dbc.Label("Number of days before recovery",style=label_font)],width={'size':2}),
        dbc.Col([dbc.Label("Infections a person passes before recovery",style=label_font)],width={'size':2}),
        dbc.Col([dbc.Label("Simulated Worlds for stochastic model",style=label_font)],width={'size':2}),
        dbc.Col([dbc.Label("Initial Infections",style=label_font)],width={'size':2})]),
    dbc.Row([
        dbc.Col([
                dbc.Input(id='pop', value=99,
                          type='number',style=input_style
                          )
                        ],width={'size':2,"offset":1}
                    ),
        dbc.Col([
                dbc.Input(id='recDays', value=14, type='number',style=input_style
                          ),
                        ],width=2
                    ),
        dbc.Col([
                dbc.Input(id='avgInfections', value=3, type='number',style=input_style
                          )
                        ],width=2
                    ),
        dbc.Col([
                dbc.Input(id='worlds', value=3, type='number',style=input_style
                         )
                        ],width=2
                    ),
        dbc.Col([
                dbc.Input(id='initialInfections', value=85, type='number',style=input_style
                          ),
                        ],width={'size':2,"offset":-1}
                    )])],fluid=True),
        html.Br(),
    dbc.Container([
        html.H1(id='infected',style = result_style)],fluid=True),
    dbc.Container([
        html.Br(),
        html.Div([
        dcc.Graph(
            id='basic-interactions', config={'scrollZoom': True, 'showTips': True})]),
        html.Br(),
        html.Div([dcc.Graph(
            id='basic-interactions2', config={'scrollZoom': True, 'showTips': True})]),
    html.Br(), html.Div([dcc.Graph(id='SA', figure=fig, config={'scrollZoom': True, 'showTips': True})]),
    html.Br(), html.Div([dcc.Graph(id='DailyCases', figure=fig2, config={'scrollZoom': True, 'showTips': True})]),
    html.Br(), html.Div([dcc.Graph(id='Dailytests', figure=fig3, config={'scrollZoom': True, 'showTips': True})]),
    html.Br(), html.Div([dcc.Graph(id='TotCases', figure=fig4, config={'scrollZoom': True, 'showTips': True})]),
    html.Br(), html.Div([dcc.Graph(id='TotTests', figure=fig5, config={'scrollZoom': True, 'showTips': True})])],fluid=True)],fluid=True)


@app.callback([Output('basic-interactions', 'figure'), Output('infected', 'children'),Output('basic-interactions2', 'figure')], [Input('pop', 'value'),
                                                                                                                                 Input('recDays', 'value'),
                                                                                                                                 Input('avgInfections','value'),
                                                                                                                                 Input('initialInfections','value'),
                                                                                                                                 Input('worlds','value')
                                                                                                                                 ])
def runModel(Pop, recDays, avgInfections, initialInfections,worlds):
    if recDays and Pop and avgInfections and initialInfections:
        def runRegular(recDays,Pop,avgInfections,initialInfections):
            global fig,stringy
            # Number of people self-isolating
            selfIsolating = Pop
            # Number of people susceptible
            S_0 = Pop - initialInfections
            # Number of people infected
            I_0 = initialInfections

            print('Initial Number of infected {}'.format(I_0 / S_0))

            # Number of people recovered
            R_0 = 0

            # Days to recovery
            recovDays = recDays
            # How many people the person infects every 2 weeks
            gamma = avgInfections / recDays
            # period of infectiousness is atleast 14 days (recovery)
            beta = 1 / recDays

            # tau (time step)
            tau = 1

            t_max = 1000

            S = [S_0]
            I = [I_0]
            R = [R_0]
            t = [0]

            def function(S_0, I_0, R_0):
                S_dot = -gamma * S_0/Pop * I_0
                I_dot = gamma * S_0/Pop * I_0 - beta * I_0
                R_dot = beta * I_0
                return S_dot, I_dot, R_dot

            t_0 = 0

            while t_0 <= t_max:
                S_1 = S_0 + tau * function(S_0, I_0, R_0)[0]
                I_1 = I_0 + tau * function(S_0, I_0, R_0)[1]
                R_1 = R_0 + tau * function(S_0, I_0, R_0)[2]
                if I_1 < 1:
                    break
                S.append(S_1)
                I.append(I_1)
                R.append(R_1)
                t.append(t_0)
                S_0 = S_1
                I_0 = I_1
                R_0 = R_1
                t_0 += tau
            print('Peak infection at {} days with {} people infected at once'.format(round(np.argmax(I) * tau, 3),
                                                                                     round(max(I)), 3))
            stringy = 'On average, peak infection at {} days with {} people infected at once'.format(round(np.argmax(I) * tau, 3),
                                                                                 round(max(I)))
            df = pd.DataFrame(data=list(zip(t, I)), columns=['Time', 'Infected'])
            df['Susceptible'] = S
            df['Recovered'] = R
            fig = subplots.make_subplots()
            fig['layout'].update(height=500, title='SIR Model evolution of Virus', title_x=0.5,
                                 xaxis_title="Days",
                                 yaxis_title="Population")
            fig['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
            fig.append_trace(
                {'x': df['Time'], 'y': df['Susceptible'], 'type': 'scatter', 'name': 'Susceptible'}, 1, 1)
            fig.append_trace({'x': df['Time'], 'y': df['Infected'], 'type': 'scatter', 'name': 'Infected'},
                             1, 1)
            fig.append_trace(
                {'x': df['Time'], 'y': df['Recovered'], 'type': 'scatter', 'name': 'Recovered'}, 1, 1)
        runRegular(recDays,Pop,avgInfections,initialInfections)
        if Pop <= 10000:
            def stochasticModel(Pop, recDays, avgInfections, initialInfections,worlds):
                global fig_stoch
                fig_stoch = subplots.make_subplots()
                fig_stoch['layout'].update(height=500, title='Stochastic SIR Model evolution of Virus', title_x=0.5,
                                           xaxis_title="Days",
                                           yaxis_title="Population")
                fig_stoch['layout']['margin'] = {'l': 20, 'b': 30, 'r': 10, 't': 50}
                for i in range(0, worlds):
                    # int; total population
                    N = Pop
                    # maximum elapsed time
                    T = 1000

                    # start time
                    t = 0.0

                    # recovery days
                    recDays = 14

                    # rate of infection after contact
                    _alpha = avgInfections / recDays

                    # rate of cure
                    _beta = 1 / recDays

                    # initial infected population
                    n_I = initialInfections

                    # susceptible population, set recovered to zero
                    n_S = N - n_I
                    n_R = 0

                    # Initialize results list
                    SIR_data = []
                    SIR_data.append((t, n_S, n_I, n_R))

                    # Main loop
                    while t < T:
                        if n_I == 0:
                            break
                        w1 = _alpha * n_S / N * n_I
                        w2 = _beta * n_I
                        W = w1 + w2
                        dt = np.random.exponential(1 / W)
                        t = t + dt
                        if np.random.uniform(0, 1) < w1 / W:
                            n_S = n_S - 1
                            n_I = n_I + 1
                        else:
                            n_I = n_I - 1
                            n_R = n_R + 1

                        SIR_data.append((t, n_S, n_I, n_R))
                    S = [y[1] for y in SIR_data]
                    I = [y[2] for y in SIR_data]
                    R = [y[3] for y in SIR_data]
                    t = [y[0] for y in SIR_data]
                    df_stoch = pd.DataFrame(data=list(zip(t, I)), columns=['Time', 'Infected'])
                    df_stoch['Susceptible'] = S
                    df_stoch['Recovered'] = R
                    print(df_stoch)
                    if i == 0:
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Susceptible'], mode="lines", row=1, col=1,name='Susceptible',marker=dict(size=20, color='blue'))
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Infected'], mode="lines", row=1, col=1,name='Infected',marker=dict(size=20, color='red'),fillcolor='red')
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Recovered'], mode="lines", row=1, col=1,name='Recovered',marker=dict(size=20, color='green'),fillcolor='green')
                    else:
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Susceptible'], mode="lines", row=1, col=1,name='Susceptible',marker=dict(size=20, color='blue'),showlegend=False)
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Infected'], mode="lines", row=1, col=1,name='Infected',marker=dict(size=20, color='red'),showlegend=False,fillcolor='red')
                        fig_stoch.add_scatter(x=df_stoch['Time'], y=df_stoch['Recovered'], mode="lines", row=1, col=1,name='Recovered',showlegend=False,marker=dict(size=20, color='green'),fillcolor='green')
            stochasticModel(Pop, recDays, avgInfections, initialInfections, worlds)
        else:
            return [fig,stringy,{
            'data': [], 'layout': {
                'height': 500,
                'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
            }
        }]
        return [fig,stringy,fig_stoch]
    else:
        return [{
            'data': [], 'layout': {
                'height': 500,
                'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
            }
        }, 'None',{
            'data': [], 'layout': {
                'height': 500,
                'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10}
            }
        }]


if __name__ == '__main__':
    app.run_server(debug=True, port=8030)



