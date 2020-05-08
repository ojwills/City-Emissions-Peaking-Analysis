import dash
import dash_table
import dash_core_components as dcc 
import dash_html_components as html
from dash.dependencies import Input,Output,State
from datetime import datetime 
import plotly.graph_objs as go
import pandas as pd
import dash_auth 

#Import Bootsrap CSS extension
external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)

path = '/Users/oliverwills/Box/00_Live App Raw Data/Peaking Analysis/peaking_emissions_dashboard.xlsx'
df = pd.read_excel(path, sheet_name='DASHBOARD_Peak_Emissions')

#Set up data for peak emissions table
df2 = df[df['Peak year']==1]
df2 = df2[['City','Year','Emissions']]
df2['Emissions'] = df2['Emissions'].round()
df2.rename(columns={'Year':'Peak year','Emissions':'Peak Emissions'},inplace=True)
df2.sort_values('Peak year',inplace=True)

#Set up options for dropdown
options = []
for city in df['City'].unique():
     mydict = {}
     mydict['label'] = city
     mydict['value'] = city
     options.append(mydict)

app.layout = html.Div([html.Div([html.H1('C40 Peak Emissions Tracker')],style ={'padding-left':'40px','margin-top':'10px','margin-bottom':'20px'}),
                       html.Div([
                                html.H6('Select a city:')
                                  ],className = 'inline-block',style={'padding-left':'40px'}),
                       html.Div([
                                  html.Div([
                                            dcc.Dropdown(
                                            id='city_picker',
                                            options=options,
                                            value='Accra')
                                  ],className = 'inline-block col-2'),
                                ],className="row", style={'padding-left':'40px','margin-bottom':'20px'}),
                       
                       html.Div([
                               html.Div([
                                        html.H4(html.Div([html.Span(id='graph_title'),' Emissions (1990-2018)']))
                               ],className = 'inline-block col-4', style={'padding-left':'55px'}),
                               html.Div([
                                        html.H4(html.Div(['Emissions Status:',html.Span(id='peaking_status',style={'color':'#5DADE2'})]))
                                ],className = 'inline-block col-4',style={'text-align':'right','padding-right':'100px'}),
                               
                               html.Div([
                                        html.H4(html.Div(['Cities that have peaked:',html.Span(id='peaking_count',style={'color':'#5DADE2'})]))
                               ],className='inline-block col-4')
                           ],className = 'row'),
                        
                        html.Div([
                            html.H6(html.Div(['Data Source: ',html.Span(id='data_source',style={'color':'#A6ACAF'})]))
                        ],className = 'row',style={'margin-left':'40px'}),

                        html.Div([html.Div([
                                    html.Div([dcc.Graph(
                                              style={'height':'50vh','margin-bottom':0},
                                              id = 'my_graph',
                                              figure={'data':[go.Bar(x=df[df['City'] == 'Accra']['Year'],
                                              y=df[df['City'] == 'Accra']['Emissions'],
                                              marker={'color':'#5DADE2'})], 
                                             'layout':go.Layout(xaxis={'title':'Year'}, yaxis={'title':'Emissions / tCO2e'},margin={'t':0})}
                                            ),
                                            html.Div([
                                                      html.H5('Methodology'),
                                                      html.P("Peaking defines the point in time where a city's emissions switch from increasing to decreasing, and represents a critical turning point in achieveing the Paris Climate Change Agreement. This dashboard uses the following data sources to track whether C40 cities have peaked:"),
                                                      html.Ol([
                                                          html.Li(html.Div([html.Span('C40 GPC:',style={'font-weight':'bold'}),' Global Protocol for Community-Scale (GPC) emissions data reported to C40 and approved as GPC compliant.'])),
                                                          html.Li(html.Div([html.Span('City GPC:',style={'font-weight':'bold'}),' GPC emissions data published by cities through their website or elsewhere, but not reviewed by C40.'])),
                                                          html.Li(html.Div([html.Span('CDP GPC:',style={'font-weight':'bold'}),' GPC emisisons data reported by cities through Carbon Disclosure Project (CDP) questionaires.'])),
                                                          html.Li(html.Div([html.Span('All GPC considered:',style={'font-weight':'bold'}),' GPC emissions data combined from the above GPC sources in order of data quality to address data gaps.'])),
                                                          html.Li(html.Div([html.Span('Target other:',style={'font-weight':'bold'}),' Non-GPC emissions data reported by cities for baseline year reduction targets.'])),
                                                          html.Li(html.Div([html.Span('CDP other:',style={'font-weight':'bold'}),' Non-GPC data reported through CDP, but not reviewed by C40.'])),
                                                          html.Li(html.Div([html.Span('City other:',style={'font-weight':'bold'}),' Non-GPC data reported by cities through their website or elsewehre.'])),
                                                          html.Li(html.Div([html.Span('All non-GPC considered:',style={'font-weight':'bold'}),' Non-GPC emissions data combined from the above non-GPC sources in order of data quality to address data gaps.'])),
                                                      ]),
                                                    html.P(dcc.Markdown('For a full description of how data sources are selected and how peaking is determined please refer to the [methodology] (https://c40-production-images.s3.amazonaws.com/other_uploads/images/2084_Methodology_for_Peaking_Analysis_.original.docx?1559565995).')),
                                                    html.P(dcc.Markdown('To view the underlying data used in the dashboard please click [here] (https://c40-production-images.s3.amazonaws.com/other_uploads/images/2085_peaking_emissions_dashboard.original.xlsx?1559574441).')),
                                                   ],style={'margin-left':'50px','margin-right':'50px','font-family':'Arial, Helvetica, sans-serif','fontSize':14,'color':'dark-grey'})
                                            ],className="d-block col-8"),
                                    html.Div([dash_table.DataTable(
                                              id='my_table',
                                              columns = [{"name":i, "id":i} for i in df2.columns],
                                              data = df2.to_dict('records'),
                                              style_as_list_view = True,
                                              style_cell = {'font-family':'Arial, Helvetica, sans-serif','fontSize':14},
                                              style_header = {
                                                    'backgroundColour':'white',
                                                    },
                                              style_cell_conditional =[
                                                    {
                                                    'if':{'column_id':'City'},
                                                    'textAlign':'left',
                                                    }
                                                ],  
                                              )],className="col-4",style={'padding-right':'100px','font-family':'Arial, Helvetica, sans-serif'}),
                                    ],className="row"),
                        ])
                    ])

@app.callback(Output('peaking_status','children'),
              [Input('city_picker','value')])

def update_peak_status(city_name):
    status = ' ' + df[df['City'] == city_name]['Peak Status'].reset_index(drop=True).loc[0]
    return status

@app.callback(Output('peaking_count','children'),
              [Input('city_picker','value')])

def update_peak_count(city_name):
    count = ' ' + str(df[df['Peak year'] == 1]['Peak year'].sum())
    return count

@app.callback(Output('data_source','children'),
              [Input('city_picker','value')])

def update_data_source(city_name):
    data_source = df[df['City'] == city_name]['Protocol'].reset_index(drop=True).loc[0]
    return data_source

@app.callback(Output('graph_title','children'),
              [Input('city_picker','value')])

def update_graph_title(city_name):
    return city_name

@app.callback(Output('my_graph','figure'),
              [Input('city_picker','value')])

def update_bar_graph(city_name):
    figure={'data':[go.Bar(x=df[df['City'] == city_name]['Year'],
        y=df[df['City'] == city_name]['Emissions'],
        name = 'test',
        marker={'color':'#5DADE2'})],
        'layout':go.Layout(xaxis={'title':'Year'}, yaxis={'title':'Emissions / tCO2e', 'range':[0,df['Emissions'].max()]},margin={'t':0})}
    return figure

if __name__ == '__main__':
    app.run_server()
