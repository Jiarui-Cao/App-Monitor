import pandas as pd
from dash import  dcc, Input, Output, html, dash_table
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import time
from datetime import datetime
import requests
from collections import OrderedDict

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
    # Output(component_id='ts_graph_1', component_property='style'),
    [Input('dropdown_ts', 'value')])
def plot_ts_graph_1(metric):
    # if not metric:
    #     return None, {'display': 'none'}
    # else:
    if metric:
        print("LOL")
        fig = px.line(x=[1, 2, 3, 4], y=[1, 4, 9, 16], title='LOL')
        fig.update_layout(
            xaxis_title='X',
            yaxis_title='Y'
        )
        # fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])    
        return fig
        # return fig, {'display': 'block', "margin": 20}
    

# @app.callback(Output('spyder', 'figure'),
#               [Input('dropdown', 'value')])
# def update_spyder(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     # Use similar method to search through documentidentifier for lithium
#     org = org[['ActualThemes','V2Tone']]
#     org_closed = pd.concat([org, org.iloc[[0]]], ignore_index=True)
#     fig=px.line_polar(org_closed,r='V2Tone',theta='ActualThemes')
#     return fig


# layout=dbc.Container([
#     html.Div([
#         dcc.Dropdown(id='dropdown_misc', options = misc_list, placeholder="Select Miscellaneous Metric", style={'display': 'inline-block'}),
#         dcc.Dropdown(id='dropdown_counter', options = counter_list, placeholder="Select Counter Metric", style={'display': 'inline-block'})]),
#     html.Div([
#         dcc.Graph(id='')
#     ])
#     html.Div([
#         dcc.Dropdown(id='dropdown_ts', options = ts_list, placeholder="Select Time Series Metric")]),
    # html.Div([
    #     dcc.Graph(id='spyder24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='spyder',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='scatter24', style={'display': 'inline-block','height':'1000px'}),
    #     dcc.Graph(id='scatter',style={'display': 'inline-block','height':'1000px'})]),
    # html.Div([
    #     dcc.Graph(id='groupedscatter24', style={'display': 'inline-block','height':'1000px'}),
    #     dcc.Graph(id='groupedscatter',style={'display': 'inline-block','height':'1000px'})]),
    # html.Div([
    #     dcc.Graph(id='freqhist24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='freqhist',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='avghist24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='avghist',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='heatmap24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='heatmap',style={'display': 'inline-block'})]),
    # html.Div([
    #     html.Div(id='table24',style={'display': 'inline-block'}),
    #     html.Div(id='table',style={'display': 'inline-block'})]),
    # html.Div([
    #     html.Div(id='tableurl24',style={'display': 'inline-block'}),
    #     html.Div(id='tableurl',style={'display': 'inline-block'})]),
    # html.Div([
    #     html.Div(id='companyurl24',style={'display': 'inline-block'}),
    #     html.Div(id='companyurl',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='themegraph24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='themegraph',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='stackedbar24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='stackedbar',style={'display': 'inline-block'})])
    # ])

# @app.callback(Output('spyder', 'figure'),
#               [Input('dropdown', 'value')])
# def update_spyder(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     # Use similar method to search through documentidentifier for lithium
#     org = org[['ActualThemes','V2Tone']]
#     org_closed = pd.concat([org, org.iloc[[0]]], ignore_index=True)
#     fig=px.line_polar(org_closed,r='V2Tone',theta='ActualThemes')
#     return fig

# @app.callback(Output('spyder24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_spyder24(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes','V2Tone']]
#     org_closed = pd.concat([org, org.iloc[[0]]], ignore_index=True)
#     fig=px.line_polar(org_closed,r='V2Tone',theta='ActualThemes')
#     return fig


# @app.callback(Output('scatter', 'figure'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     fig = px.scatter(x=output.V2Tone, y=output.Themes)
#     return fig

# @app.callback(Output('scatter24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_scatter24(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     fig = px.scatter(x=output.V2Tone, y=output.Themes)
#     return fig

# @app.callback(Output('groupedscatter', 'figure'),
#               [Input('dropdown', 'value')])
# def update_spyder(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes','V2Tone']]
#     fig = px.scatter(x=org.V2Tone, y=org.ActualThemes)
#     return fig

# @app.callback(Output('groupedscatter24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_spyder24(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes','V2Tone']]
#     fig = px.scatter(x=org.V2Tone, y=org.ActualThemes)
#     return fig

# @app.callback(Output('freqhist', 'figure'),
#               [Input('dropdown', 'value')])
# def update_freqhist(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output=output['Themes']
#     fig = px.histogram(output,x='Themes').update_xaxes(categoryorder="total descending")
#     return fig

# @app.callback(Output('freqhist24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_freqhist24(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output=output['Themes']
#     fig = px.histogram(output,x='Themes').update_xaxes(categoryorder="total descending")
#     return fig

# @app.callback(Output('avghist', 'figure'),
#               [Input('dropdown', 'value')])
# def update_avghist(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output=output.groupby('Themes', as_index=False).mean()
#     output.sort_values(by=['V2Tone'],inplace=True)
#     fig = px.bar(output, x='Themes', y='V2Tone')
#     return fig

# @app.callback(Output('avghist24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_avghist24(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output=output.groupby('Themes', as_index=False).mean()
#     output.sort_values(by=['V2Tone'],inplace=True)
#     fig = px.bar(output, x='Themes', y='V2Tone')
#     return fig

# @app.callback(Output('heatmap', 'figure'),
#               [Input('dropdown', 'value')])
# def update_heatmap(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output['new']=output['V2Tone'].astype(str)+output['Themes']
#     c1=output[output['V2Tone'].between(-100, -5, inclusive='both')].drop('Themes',axis=1)
#     c2=output[output['V2Tone'].between(-4.99, -4, inclusive='both')].drop('Themes',axis=1)
#     c3=output[output['V2Tone'].between(-3.99, -3, inclusive='both')].drop('Themes',axis=1)
#     c4=output[output['V2Tone'].between(-2.99, -2, inclusive='both')].drop('Themes',axis=1)
#     c5=output[output['V2Tone'].between(-1.99, -1, inclusive='both')].drop('Themes',axis=1)
#     c6=output[output['V2Tone'].between(-0.99, 0, inclusive='both')].drop('Themes',axis=1)
#     c7=output[output['V2Tone'].between(0.01, 1, inclusive='both')].drop('Themes',axis=1)
#     c8=output[output['V2Tone'].between(1.01, 2, inclusive='both')].drop('Themes',axis=1)
#     c9=output[output['V2Tone'].between(2.01, 3, inclusive='both')].drop('Themes',axis=1)
#     c10=output[output['V2Tone'].between(3.01, 4, inclusive='both')].drop('Themes',axis=1)
#     c11=output[output['V2Tone'].between(4.01, 5, inclusive='both')].drop('Themes',axis=1)
#     c12=output[output['V2Tone'].between(5, 100, inclusive='both')].drop('Themes',axis=1)
#     c1.rename(columns={"V2Tone": 'Lesser than -5'},inplace=True)
#     c2.rename(columns={"V2Tone": '-5 to -4'},inplace=True)
#     c3.rename(columns={"V2Tone": '-4 to -3'},inplace=True)
#     c4.rename(columns={"V2Tone": '-3 to -2'},inplace=True)
#     c5.rename(columns={"V2Tone": '-2 to -1'},inplace=True)
#     c6.rename(columns={"V2Tone": '-1 to 0'},inplace=True)
#     c7.rename(columns={"V2Tone": '0.01 to 1'},inplace=True)
#     c8.rename(columns={"V2Tone": '1.01 to 2'},inplace=True)
#     c9.rename(columns={"V2Tone": '2.01 to 3'},inplace=True)
#     c10.rename(columns={"V2Tone": '3.01 to 4'},inplace=True)
#     c11.rename(columns={"V2Tone": '4.01 to 5'},inplace=True)
#     c12.rename(columns={"V2Tone": 'Greater than 5'},inplace=True)
#     output=output.merge(c1, on='new',how='left')
#     output=output.merge(c2, on='new',how='left')
#     output=output.merge(c3, on='new',how='left')
#     output=output.merge(c4, on='new',how='left')
#     output=output.merge(c5, on='new',how='left')
#     output=output.merge(c6, on='new',how='left')
#     output=output.merge(c7, on='new',how='left')
#     output=output.merge(c8, on='new',how='left')
#     output=output.merge(c9, on='new',how='left')
#     output=output.merge(c10, on='new',how='left')
#     output=output.merge(c11, on='new',how='left')
#     output=output.merge(c12, on='new',how='left')
#     output=output.drop(['V2Tone','new'],axis=1).set_index('Themes')
#     fig = px.imshow(output,text_auto=True,aspect='auto',color_continuous_scale=["red", "green"])
#     return fig

# @app.callback(Output('heatmap24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_heatmap(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output['new']=output['V2Tone'].astype(str)+output['Themes']
#     c1=output[output['V2Tone'].between(-100, -5, inclusive='both')].drop('Themes',axis=1)
#     c2=output[output['V2Tone'].between(-4.99, -4, inclusive='both')].drop('Themes',axis=1)
#     c3=output[output['V2Tone'].between(-3.99, -3, inclusive='both')].drop('Themes',axis=1)
#     c4=output[output['V2Tone'].between(-2.99, -2, inclusive='both')].drop('Themes',axis=1)
#     c5=output[output['V2Tone'].between(-1.99, -1, inclusive='both')].drop('Themes',axis=1)
#     c6=output[output['V2Tone'].between(-0.99, 0, inclusive='both')].drop('Themes',axis=1)
#     c7=output[output['V2Tone'].between(0.01, 1, inclusive='both')].drop('Themes',axis=1)
#     c8=output[output['V2Tone'].between(1.01, 2, inclusive='both')].drop('Themes',axis=1)
#     c9=output[output['V2Tone'].between(2.01, 3, inclusive='both')].drop('Themes',axis=1)
#     c10=output[output['V2Tone'].between(3.01, 4, inclusive='both')].drop('Themes',axis=1)
#     c11=output[output['V2Tone'].between(4.01, 5, inclusive='both')].drop('Themes',axis=1)
#     c12=output[output['V2Tone'].between(5, 100, inclusive='both')].drop('Themes',axis=1)
#     c1.rename(columns={"V2Tone": 'Lesser than -5'},inplace=True)
#     c2.rename(columns={"V2Tone": '-5 to -4'},inplace=True)
#     c3.rename(columns={"V2Tone": '-4 to -3'},inplace=True)
#     c4.rename(columns={"V2Tone": '-3 to -2'},inplace=True)
#     c5.rename(columns={"V2Tone": '-2 to -1'},inplace=True)
#     c6.rename(columns={"V2Tone": '-1 to 0'},inplace=True)
#     c7.rename(columns={"V2Tone": '0.01 to 1'},inplace=True)
#     c8.rename(columns={"V2Tone": '1.01 to 2'},inplace=True)
#     c9.rename(columns={"V2Tone": '2.01 to 3'},inplace=True)
#     c10.rename(columns={"V2Tone": '3.01 to 4'},inplace=True)
#     c11.rename(columns={"V2Tone": '4.01 to 5'},inplace=True)
#     c12.rename(columns={"V2Tone": 'Greater than 5'},inplace=True)
#     output=output.merge(c1, on='new',how='left')
#     output=output.merge(c2, on='new',how='left')
#     output=output.merge(c3, on='new',how='left')
#     output=output.merge(c4, on='new',how='left')
#     output=output.merge(c5, on='new',how='left')
#     output=output.merge(c6, on='new',how='left')
#     output=output.merge(c7, on='new',how='left')
#     output=output.merge(c8, on='new',how='left')
#     output=output.merge(c9, on='new',how='left')
#     output=output.merge(c10, on='new',how='left')
#     output=output.merge(c11, on='new',how='left')
#     output=output.merge(c12, on='new',how='left')
#     output=output.drop(['V2Tone','new'],axis=1).set_index('Themes')
#     fig = px.imshow(output,text_auto=True,aspect='auto',color_continuous_scale=["red", "green"])
#     return fig

# @app.callback(Output('table', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     print(org.to_dict('records'))
#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
#     )
#     return table
#     # fig = go.Figure(data=[go.Table(
#     # header=dict(values=list(org.columns)),
#     # cells=dict(values=[org.ActualThemes, org.V2Tone, org.DocumentIdentifier],height=60))])
#     # return fig

# @app.callback(Output('table24', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
#     )
#     return table

# @app.callback(Output('tableurl', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     org=org['DocumentIdentifier']
#     org=org.to_frame()
#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-top':'20px','margin-left':'70px'}
#     )
#     return table

# @app.callback(Output('tableurl24', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     org=org['DocumentIdentifier']
#     org=org.to_frame()
#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-top':'20px','margin-left':'70px'}
#     )
#     return table

# # URL contains companies names only
# @app.callback(Output('companyurl', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     input_val = input_value.split()
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     org=org[org["DocumentIdentifier"].str.contains(input_val[0])]
#     org=org['DocumentIdentifier']
#     org=org.to_frame()

#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-top':'20px','margin-left':'70px'}
#     )
#     return table

# @app.callback(Output('companyurl24', 'children'),
#               [Input('dropdown', 'value')])
# def update_scatter(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     input_val = input_value.split()
#     org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
#     org=org.sort_values(by=['V2Tone'])
#     org=org[org["DocumentIdentifier"].str.contains(input_val[0])]
#     org=org['DocumentIdentifier']
#     org=org.to_frame()

#     table = dash.dash_table.DataTable(
#         data=org.to_dict('records'),
#         columns=[{'name': i, 'id': i} for i in org.columns],
#         fixed_rows={'headers': True},
#         style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
#         style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-top':'20px','margin-left':'70px'}
#     )
#     return table


# @app.callback(Output('themegraph', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stsfig(input_value):
#     org = data_15[data_15['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes', 'V2Tone', 'dates']]
#     new = org['ActualThemes'].str.split(',', expand=True).stack()
#     vals = new.index.get_level_values(level=0)
#     org = org.drop(columns=['ActualThemes']).loc[vals]
#     output = pd.DataFrame()
#     output['V2Tone'] = org['V2Tone']
#     output['Date'] = org['dates']
#     output['Themes'] = new.values
#     fig = px.line(output, x="Date", y="V2Tone", color='Themes')
#     return fig

# @app.callback(Output('themegraph24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stsfig(input_value):
#     org = newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes', 'V2Tone', 'dates']]
#     new = org['ActualThemes'].str.split(',', expand=True).stack()
#     vals = new.index.get_level_values(level=0)
#     org = org.drop(columns=['ActualThemes']).loc[vals]
#     output = pd.DataFrame()
#     output['V2Tone'] = org['V2Tone']
#     output['Date'] = org['dates']
#     output['Themes'] = new.values
#     output = output.sort_values('Date')
#     fig = px.line(output, x="Date", y="V2Tone", color='Themes',markers=True)
#     return fig

# @app.callback(Output('stackedbar', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stackedbar(input_value):
#     curr=newdata24['dates'][0]
#     prev=curr-pd.Timedelta('0 days 00:15:00')
#     org = newdata24[newdata24['dates'].isin([curr, prev])]
#     org = org[org['Organizations'].apply((lambda x: input_value in x))]
#     org = org[['ActualThemes', 'V2Tone', 'dates']]
#     new = org['ActualThemes'].str.split(',', expand=True).stack()
#     vals = new.index.get_level_values(level=0)
#     org = org.drop(columns=['ActualThemes']).loc[vals]
#     output = pd.DataFrame()
#     output['V2Tone'] = org['V2Tone']
#     output['dates'] = org['dates']
#     output['Themes'] = new.values
#     d1 = output[output['dates'].isin([curr])].groupby('Themes', as_index=False).mean()
#     d1['dates'] =  curr
#     d2 = output[output['dates'].isin([prev])].groupby('Themes', as_index=False).mean()
#     d2['dates'] = prev
#     new = pd.concat([d1, d2])
#     fig = px.bar(new, x="dates", y="V2Tone", color='Themes',
#               hover_data=['Themes'], barmode='stack')
#     return fig

# @app.callback(Output('stackedbar24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stackedbar(input_value):
#     org=newdata24[newdata24['Organizations'].apply((lambda x: input_value in x))]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     vals=new.index.get_level_values(level=0)
#     org=org.drop(columns=['ActualThemes']).loc[vals]
#     output=pd.DataFrame()
#     output['V2Tone']=org
#     output['Themes']=new.values
#     output=output.groupby('Themes', as_index=False).mean()
#     output.sort_values(by=['V2Tone'],inplace=True)
#     output['col'] = 'Themes'
#     fig = px.bar(output, x="col", y="V2Tone", color='Themes',
#             hover_data=['Themes'], barmode = 'stack')
#     return fig


if __name__ == '__main__':
    app.run_server(port = 8000, debug=True)
