import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, callback, Output, Input
import numpy as np
from string import Template

E_a = 0.5 #Activate energy
T_ref = 298.15 
t = Template('./data/$file')

app = Dash()

app.layout = [
    html.H1('Battery performance'),
    dcc.Dropdown(['00001.csv','00003.csv', '00005.csv', '00006.csv'], '00001.csv', id='dropdown-selection'),
    html.H4('Battery impedance'),
    dcc.Graph(id='battery-impedance'),
    html.H4('Electrolyte resistance'),
    dcc.Graph(id='r_electrolyte'),
    html.H4('Charge transfer resistance'),
    dcc.Graph(id='r_ct')
]

@callback(
    Output('battery-impedance', 'figure'),
    Output('r_electrolyte', 'figure'),
    Output('r_ct', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    data = pd.read_csv(t.substitute({'file':value}))

    data['Battery_Impedance'] = data['Voltage_measured'] / data['Current_measured'].replace(0, np.nan)
    R0 = data['Battery_Impedance'].mean()
    data['Temperature_measured'] = data['Temperature_measured'] + 273.15 #Convert to Kelvin

    data['R_Electrolyte'] =  R0 * np.exp(E_a * ((1 / T_ref) - (1 / data['Temperature_measured'])))
    data['R_Charge_Transfer'] = (data['Voltage_measured'] - data['Current_measured']*data['R_Electrolyte'])/data['Current_measured'].replace(0, np.nan)

    return px.line(data,x='Time', y='Battery_Impedance'), px.line(data,x='Time', y='R_Electrolyte'), px.line(data,x='Time', y='R_Charge_Transfer')


if __name__ == "__main__":
    app.run(debug=True)