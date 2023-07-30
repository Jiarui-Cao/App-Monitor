import pandas as pd
from dash import  dcc, Input, Output, html, dash_table
import dash
import plotly.express as px
import plotly.graph_objects as go
import time
import requests

api_url = "http://127.0.0.1:5000"

r = requests.get(api_url + "/metric_names/misc")
misc_list = r.json()

r = requests.get(api_url + "/metric_names/counter")
counter_list = r.json()

r = requests.get(api_url + "/metric_names/time_series")
ts_list = r.json()


r = requests.get(api_url + "/data/misc")
df_misc = pd.DataFrame(r.json(), columns=['ID', 'Metric', 'Value', 'Unit'])

r = requests.get(api_url + "/data/counter")
df_counter = pd.DataFrame(r.json(), columns=['ID', 'Metric', 'Value', 'Unit'])

r = requests.get(api_url + "/data/time_series")
df_ts = pd.DataFrame(r.json(), columns=['ID', 'Time', 'Metric', 'Value', 'Unit'])
df_ts['Time'] = df_ts['Time'].apply(lambda x: time.asctime(time.gmtime(x)))


df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'margin-left': 'auto', 'margin-right': 'auto', 
              'background-color': '#222222',
              'padding': 10,
              'boarder-spacing': 50,
              'border': '1px solid black',
              'textAlign': 'center',
              'cell-padding': 5})

def generate_datatable(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        style_cell={'textAlign': 'center', 'padding': '5px'},
        style_data={
            'color': colors['text'],
            'backgroundColor': '#555555'
        },
        style_header={
            'backgroundColor': '#222222',
            'fontWeight': 'bold'
        },
    )

# fig = px.scatter(df, x="time", y="life expectancy",
#                  size="population", color="continent", hover_name="country",
#                  log_x=True, size_max=60)

######################################
### Create Dashboard Visualization ###
######################################

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Application Performance Monitor',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'padding-top': 20,
        }
    ),

    html.Div(children='AUM Dashboard: A web application for AUM data.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div(children=[
        html.Label('dropdown_misc', style = {'color': colors['text']}),
        dcc.Dropdown(id='dropdown_misc', options=misc_list, placeholder='Select Miscellaneous Metric'),

        html.Br(),
        html.Label('dropdown_counter', style = {'color': colors['text']}),
        dcc.Dropdown(id='dropdown_counter', options=counter_list, placeholder='Select Counter Metric'),

        html.Br(),
        html.Label('dropdown_ts', style = {'color': colors['text']}),
        dcc.Dropdown(id='dropdown_ts', options=ts_list, placeholder='Select Time Series Metric'),
    ], style={'padding': 20, 'flex': 1}),

    html.Div(children=[
        html.Br(),
        html.Label('Time Series Resolution Slider',  style = {'color': colors['text'], 'padding': 10}),
        dcc.Slider(
            min=0,
            max=10,
            marks={i: f'Time Interval {i}' if i == 1 else str(i) for i in range(1, 10)},
            value=5,
        ),
    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[
        html.Div(children=[
            html.H2(id='text1', children='[Select Misc Metric]'),
            html.Div(id='misc_table_1', children=[]),

            html.Br(),
            html.H2(id='text2', children='[Select Counter Metric]'),
            html.Div(id='counter_table_1', children=[]),
        ], style={'textAlign': 'center', 'flex': '50%'}),

        html.Div(children=[
            html.H2(id='text3', children='[Select Time Series Metric]'),
            html.Div([
                dcc.Graph(id='ts_graph_1', 
                          figure=go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])]),
                          style={'display': 'inline-block', "margin": 20}),
            ])
        ], style={'textAlign': 'center', 'flex': '50%'}),

    ], style={'display': 'flex', 'flex-direction': 'row', 'color': colors['text']}),

    html.Div(children=[
        html.H3(children='All Miscellaneous Metrics', style={'textAlign': 'center'}),
        generate_datatable(df_misc),

        html.Br(),
        html.H3(children='All Counter Metrics', style={'textAlign': 'center'}),
        generate_datatable(df_counter),

        html.Br(),
        html.H3(children='All Time Series Metrics', style={'textAlign': 'center'}),
        generate_datatable(df_ts),
    ], style={'color': colors['text'], 'margin-left': 200, 'margin-right': 200})
])

app = dash.Dash(__name__)
server = app.server
app.layout=layout


@app.callback(
    Output(component_id='text1', component_property='children'),
    Output(component_id='text1', component_property='style'),
    [Input(component_id='dropdown_misc', component_property='value')])
def update_output_div(input_value):
    if not input_value:
        return '[ Pleaset Select Miscellaneous Metric ]', {}
    else:
        return f'{input_value}', {'font-size': 40}


@app.callback(
    Output(component_id='text2', component_property='children'),
    Output(component_id='text2', component_property='style'),
    [Input(component_id='dropdown_counter', component_property='value')])
def update_output_div(input_value):
    if not input_value:
        return '[ Pleaset Select Counter Metric ]', {}
    else:
        return f'{input_value}', {'font-size': 40}


@app.callback(
    Output(component_id='text3', component_property='children'),
    Output(component_id='text3', component_property='style'),
    [Input(component_id='dropdown_ts', component_property='value')])
def update_output_div(input_value):
    if not input_value:
        return '[ Pleaset Select Time Series Metric ]', {}
    else:
        return f'Time Series Graph of [{input_value}]', {'font-size': 30}


@app.callback(
    Output(component_id='misc_table_1', component_property='children'),
    Output(component_id='misc_table_1', component_property='style'),
    [Input(component_id='dropdown_misc', component_property='value')])
def show_hide_element(metric):
    if not metric:
        return None, {'display': 'none'}
    else:
        print(metric)
        r = requests.get(api_url + f"/data/misc/{metric}")
        df = pd.DataFrame(r.json(), columns=['ID', 'Metric', 'Value', 'Unit'])
        return generate_datatable(df), {'display': 'block', 'margin': 40}


@app.callback(
    Output(component_id='counter_table_1', component_property='children'),
    Output(component_id='counter_table_1', component_property='style'),
    [Input(component_id='dropdown_counter', component_property='value')])
def show_hide_element_2(metric):
    if not metric:
        return None, {'display': 'none'}
    else:
        print(metric)
        r = requests.get(api_url + f"/data/counter/{metric}")
        df = pd.DataFrame(r.json(), columns=['ID', 'Metric', 'Value', 'Unit'])
        return generate_datatable(df), {'display': 'block', 'margin': 40}


@app.callback(
    Output('ts_graph_1', 'figure'),
    [Input('dropdown_ts', 'value')])
def plot_ts_graph_1(metric):
    if metric:
        data = requests.get(api_url + f"/data/time_series/{metric}").json()
        data = pd.DataFrame(data, columns=['id', 'time', 'metric', 'value', 'unit'])
        data['time'] = pd.to_datetime(data['time'], unit='s')
        data.set_index('time', inplace=True)
        print(data)
        fig = px.line(data[['value']])
        fig.update_layout(
            xaxis_title='Time',
            yaxis_title=f'Value (unit = {data.iloc[0,3]})'
        )
    else:
        fig=go.Figure()
    return fig
    

if __name__ == '__main__':
    app.run_server(port = 8000, debug=True)
