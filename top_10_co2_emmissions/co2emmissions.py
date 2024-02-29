#import necessary libraries
import pandas as pd
import dash
from dash import Input, Output, dcc, html
import plotly.express as px
import numpy as np


#store the df_esg file into a dataframe
file = "https://raw.githubusercontent.com/Ale3isk/esg/main/df_esg.csv"
df_esg = pd.read_csv(file)

#we define a years variable so that we have the range of years from 1961 to 2021
years = list(map(str,range(1960,2022)))

#we will extract the part of the dataframe which contains the CO2 emmissions in kilotons
df_co2 = df_esg[df_esg['indicator'] == 'CO2 emissions (kt)']

#we will remove all the columns for which the sum of nan values for CO2 emmissions is equal to the total count of the column.
for i in years:
    count = 0
    for value in df_co2[i]:
        if np.isnan(value):
            count+=1
    if count == len(df_co2[i]):
        df_co2.drop([i], axis = 1, inplace = True)

#drop duplicates
df_co2 = df_co2.drop_duplicates()
#remove "Unnamed: 0" columns
df_co2.drop(['Unnamed: 0'], axis = 1, inplace = True)
#reset the index
df_co2.reset_index(inplace = True)

#we will create a new dataframe for all countries for which we have data and separate them from the countries
#for which there's no data

#re-define the years variable so as to include the updated array of years of our dataframe.
years = list(map(str,range(1990,2019)))

newdf_co2 = df_co2.dropna(subset = years, how = 'all')
#change the name of the United Kingdom to UK as the string occupies a lot of space
newdf_co2.loc[67,'country'] = 'UK'

# initiate a dash app
app = dash.Dash(__name__)

# create the layout and add the app components that will be displayed in the web browser,
app.layout = html.Div(
    children=[html.H1("10 most CO2 emmitting countries and global emmissions from 1990-2019 in (CO2 Gt)",
                      style={'textAlign': 'center', 'color': '#503D36',
                             'font-size': 40}  # header
                      ),
              html.Br(),
              dcc.Input(id='input-yr',
                        min=1990,
                        max=2019,
                        type='number',
                        value="1990",

                        style={
                            'width': '80%',  # set width as 80%
                            'padding': '3px',  # set padding as 3px
                            'fontsize': '20px',  # set font size as 20px
                            'textAlignLast': 'center'  # set text-align-last as center
                        }
                        ),
              html.Div([

                  html.Div([
                      dcc.Graph(id='bar-plot')
                  ], style={'display': 'inline-block', 'width': '55%'}),
                  html.Div([
                      dcc.Graph(id='bar-plot2')
                  ], style={'display': 'inline-block', 'width': '44%'}),
              ]
              ),

              html.Div([
                  html.Div([
                      dcc.Graph(id='pie-plot')

                  ])
              ])

              ]
    )


# Add controls to build the interaction
@app.callback(
    [Output(component_id='bar-plot', component_property='figure'),
     Output(component_id='pie-plot', component_property='figure'),
     Output(component_id='bar-plot2', component_property='figure')],
    [Input(component_id='input-yr', component_property='value')])
def get_graph(entered_year):
    # select data
    df_plot = newdf_co2[[str(entered_year), 'country']]

    # top 10 emmitting countries for that year
    g1 = newdf_co2.nlargest(10, str(entered_year))
    # convert kilotons to gigatons divide by a million as there are a million kilotons in one gigaton
    g1[str(entered_year)] = g1[str(entered_year)] / 1000000

    # plot the graph
    fig1 = px.bar(g1,
                  x='country',
                  y=str(entered_year),
                  labels={'country': 'Country',
                          str(entered_year): 'CO2 (Gt)'},
                  title="Top 10 emmitting countries in year " + str(entered_year) + " in CO2 Gigatons")

    fig1.update_layout()

    # select data
    g2 = newdf_co2[years].sum(axis=0).reset_index().rename(columns={"index": 'year', 0: 'volume'})
    # convert kilotons to gigatons divide by a million as there are a million kilotons in one gigaton
    g2['volume'] = g2['volume'] / 1000000
    g2['volume'] = g2['volume'].apply(lambda x: round(x,2))

    fig2 = px.line(g2,
                   x='year',
                   y='volume',
                   labels={'year': 'Year',
                           'volume': 'Amount'},
                   title='Global emmissions in CO2 Gigatons')
    fig2.update_layout()

    g3 = newdf_co2.groupby('continent')[str(entered_year)].sum().reset_index()
    g3[str(entered_year)] = (g3[str(entered_year)] / 1000000).apply(lambda x: round(x, 2))

    fig3 = px.pie(g3, 'continent',
                  str(entered_year),
                  title='Pie plot of CO2 emmissions per continent in Gigatons in year ' + str(entered_year))

    return fig1, fig2, fig3


# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
