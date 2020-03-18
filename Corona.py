import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.subplots as subplots

# # Using generic style sheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Instantiate app and suppress callbacks
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
server = app.server

def makeDash():
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
    id='basic-interactions',config={'scrollZoom':True,'showTips':True}),html.Br(),html.H1(id='infected')])])
    return app.layout

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
    makeDash()
    app.run_server(debug=True)
