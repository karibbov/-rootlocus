import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from root_locus import *
import flask
import os
from random import randint

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, server=server,  external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Root Locus'),
    html.Div('''GH transfer function is equal to Numerator / Denominator'''),
    html.Div(["Numerator: ",
              dcc.Input(id='num', value='x^2 + 4*x', type='text')]),
    html.Div(["Denominator: ",
              dcc.Input(id='denom', value='x^4 + 2*x^3 + 4*x**2', type='text')]),

    html.Div('''Set window boundaries to show the plot'''),
    html.Div(["X axis bounds\n", "Lowest x:",
              dcc.Input(id='x_low', value='-10', type='number'),
              "Highest x:",
              dcc.Input(id='x_up', value='10', type='number')]),

    html.Div(["Y axis bounds\n", "Lowest y:",
              dcc.Input(id='y_low', value='-10', type='number'),
              "Highest y:",
              dcc.Input(id='y_up', value='10', type='number')]),

    html.Div('''Specify maximum K value and step between each K value to plot the root locus'''),
    html.Div(["Maximum K value:",
              dcc.Input(id='K_max', value='100', type='number'),
              "K step:",
              dcc.Input(id='K_step', value='0.5', type='number')]),

    html.Button(id='plot-button', n_clicks=0, children='Plot'),
    html.Div(children='''
        Hover to see corresponding K-gain values.
    '''),

    dcc.Graph(
        id='graph'
    )


])

@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input('plot-button', 'n_clicks')],
    [State(component_id='num', component_property='value'),
     State(component_id='denom', component_property='value'),
     State(component_id='x_low', component_property='value'),
     State(component_id='x_up', component_property='value'),
     State(component_id='y_low', component_property='value'),
     State(component_id='y_up', component_property='value'),
     State(component_id='K_max', component_property='value'),
     State(component_id='K_step', component_property='value')])
def update_plot(submit, num_expr, denom_expr, x_low, x_up, y_low, y_up, k_max, k_step):
    x_low = float(x_low)
    x_up = float(x_up)
    y_low = float(y_low)
    y_up = float(y_up)
    k_max = float(k_max)
    k_step = float(k_step)

    num = parse_polynomial(num_expr)
    denom = parse_polynomial(denom_expr)

    GH = transfer_function(num, denom)

    # create a list of evenly spaced gains
    gains = np.linspace(0.0, k_max, num=int(k_max/k_step))
    fig = root_locus(GH, gains, x_low=x_low, x_up=x_up, y_low=y_low, y_up=y_up)
    return fig


if __name__ == '__main__':
    app.server.run(debug=False)