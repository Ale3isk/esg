#import necessary libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

#import the csv file from github https://raw.githubusercontent.com/Ale3isk/esg/main/df_esg.csv
df_esg = pd.read_csv("https://raw.githubusercontent.com/Ale3isk/esg/main/df_esg.csv")

#we will create a list of the years that we need mapping each year as a string
years = [i for i in map(str, range(1990,2019))]

#filter the main dataframe by extracting all rows with the relevant indicators
new_df = df_esg[df_esg['ind'].isin(["EN.ATM.CO2E.PC",
                                     "EN.ATM.METH.PC",
                                     "EN.ATM.NOXE.PC",
                                     "NY.GDP.MKTP.KD.ZG",
                                    "EG.FEC.RNEW.ZS",
                                    "NY.ADJ.DRES.GN.ZS",
                                    "NY.ADJ.DFOR.GN.ZS",
                                    "AG.LND.FRST.ZS"])].reset_index()

#drop all year columns from 1960 up to 1989 as the World Bank dataset does not include any date for these years
new_df = new_df.drop(['index','Unnamed: 0',"iso3",'group','pillar'], axis = 1).drop(list(map(str,range(1960,1990))),axis = 1).reset_index()

# we will delete all years for which there is no data for any of our environmental indicators
# create a list of the indicators
indicators = ["EN.ATM.CO2E.PC",
              "EN.ATM.METH.PC",
              "EN.ATM.NOXE.PC",
              "NY.GDP.MKTP.KD.ZG",
              "EG.FEC.RNEW.ZS",
              "NY.ADJ.DRES.GN.ZS",
              "NY.ADJ.DFOR.GN.ZS"
              "AG.LND.FRST.ZS"]

# iterate through each year
for year in years:

    # for each year we set the variable count as 0
    count = 0

    # iterate through each indicator on each year
    for indicator in indicators:

        # if the sum of all NaN values in the series of the corresponding year and indicator
        # is equal to the length of the series then we add +1 in the count variable
        # the inner for loop will iterate across all indicators doing the same check
        if pd.isna(new_df[new_df['ind'] == indicator][year]).sum() == new_df[new_df['ind'] == indicator].shape[0]:
            count += 1

    # if the count of the resulting inner loop is equal to the length of the indicators list
    # then we delete the column as there's no data for any indicator in that year.
    if count == len(indicators):
        new_df.drop([year], axis=1, inplace=True)

#let's delete the year 2021 as well as our indicators do not have any data in that column
new_df.drop(['index','2021'], axis = 1,inplace = True)

#create a list of the dataframe's indexes.
rows = list(new_df.index)

#reverse the list so that we can iterate inversely and be able to execute the for loop without resulting errors.
rows.reverse()

# loop through the list of rows
for row in rows:
    # set the count variable to 0 on each outer loop
    count = 0

    # loop through each row and the years 1990 to 2018
    for value in new_df.loc[row, '1990':'2018']:
        # if a value is NaN
        if pd.isna(value):
            # add 1 to the count variable
            count += 1
    # if the resulting value of the count variable is equal to 36 (the length of each row) then that means that
    # the row contains nan values and therefore we will delete it.
    if count == len(new_df.loc[row, '1990':'2018']):
        # if the sum of nan values equals the length of the row, delete the row and repeat the loop
        new_df.drop(row, inplace=True)

#reset the index
new_df.reset_index(inplace = True)

#delete the column "index" which was created after resetting the index
new_df.drop(['index'],axis = 1, inplace = True)

#delete columns corresponding to years 2019 and 2020
new_df.drop(['2019','2020'],axis = 1, inplace = True)

#redefine the years from 1990 to 2018
years = list(map(str,range(1990,2019)))

#check if there are duplicates and remove any:
if new_df.shape[0] != new_df.drop_duplicates().shape[0]:
    new_df = new_df.drop_duplicates()

# create a dash application
app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': 'black', 'color': '#7FFF00', 'width': '100%'}, children=[

    html.H1(children='A comparative depiction of environmental data (World Bank Data)', style={'textAlign': 'center'}),

    html.H1('Country | Sub-region | Continent', style={'textAlign': 'center'}),

    dcc.RadioItems(options=['country',
                            'sub-region',
                            'continent'
                            ],
                   value='country',
                   id='controls-and-radio-item',
                   inline=True,
                   ),

    dcc.RadioItems(options=['Year',
                            'All years'
                            ],
                   value='Year',
                   id='controls-and-radio-item2',
                   inline=True
                   ),

    dcc.Dropdown(id='dropdown-selection',
                 style={

                     'width': '99.8%',  # set width as 80%
                     'padding': '3px',  # set padding as 3px
                     'fontsize': '20px',  # set font size as 20px
                     'textAlignLast': 'center',  # set text-align-last as center
                     'backgroundColor': 'black',  # set background color as black
                     'color': 'black'  # set text color as white
                 }

                 ),

    dcc.Dropdown(id='Year',
                 options=[{'label': year, 'value': year} for year in new_df[years].columns],
                 placeholder='select-year',
                 style={

                     'width': '99.8%',  # set width as 80%
                     'padding': '3px',  # set padding as 3px
                     'fontsize': '20px',  # set font size as 20px
                     'textAlignLast': 'center',  # set text-align-last as center
                     'backgroundColor': 'black',  # set background color as black
                     'color': 'black'  # set text color as white
                 }

                 ),

    html.Div([
        html.Div(id='output-container',
                 className='chart-grid',
                 style={'display': 'flex'})
    ])

]
                      )


@app.callback(
    Output('dropdown-selection', 'options'),
    [Input('controls-and-radio-item', 'value')]
)
def update_dropdown(selected_option):
    if selected_option == 'country':
        return [{'label': country, 'value': country} for country in sorted(new_df['country'].unique())]

    elif selected_option == 'sub-region':
        return [{'label': sub_region, 'value': sub_region} for sub_region in sorted(new_df['sub-region'].unique())]
    elif selected_option == 'continent':
        return [{'label': continent, 'value': continent} for continent in sorted(new_df['continent'].unique())]


@app.callback(
    Output(component_id='Year', component_property='disabled'),
    Input(component_id='controls-and-radio-item2', component_property='value')
)
def update_period(selected_option):
    if selected_option == 'Year':
        return False
    else:
        return True


@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-selection', component_property='value'),
     Input(component_id='Year', component_property='value')])
def update_output(option, year):
    light_green_color = '#7FFF00'  # HEX color code for light green

    # OPTION 1: USER SELECTS COUNTRY AND YEAR

    if option in new_df['country'].unique() and year in years:

        # --------------------------------------------------------------------------------------
        # GRAPH NO 1: EMMISSIONS DATA PER YEAR FOR SELECTED COUNTRY AND YEAR
        # --------------------------------------------------------------------------------------

        # get the dataframe for the country and the year
        my_check = new_df[new_df['country'] == option].set_index('indicator')[year].transpose().reset_index()

        my_check.head()

        # get the piece of the dataframe for the emmissions indicators
        my_check = my_check[my_check['indicator'].isin(["CO2 emissions (metric tons per capita)",
                                                        "Methane emissions (metric tons of CO2 equivalent per capita)",
                                                        "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"])]

        # we will change the x labels' names
        xlabels = ["CO2", "Methane", "Nitrous oxide"]

        # set the plot
        figure1 = px.bar(my_check,
                         x="indicator",
                         y=year,
                         labels={"indicator": "Indicator", year: "Metric tons per capita"},
                         title=f"Bar plot of Greenhous Gasses Emmissions per capita for {option}"
                         )

        # Update x-axis labels
        figure1.update_xaxes(tickvals=[0, 1, 2], ticktext=xlabels)

        # Update layout to change background color and label color
        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Greenhouse Gas Emissions in {option} per capita for ' + year, 'x': 0.5}
            # Add title and align it to the center
        })

        # Update traces to change bar color
        light_green_color = '#7FFF00'  # HEX color code for light green
        figure1.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure1.update_yaxes(range=[0, my_check[year].max() + 2])  # update y axes limits range

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # --------------------------------------------------------------------------------------
        # GRAPH NO 2 TOP 10 COUNTRIES CO2 EMMISSIONS PER CAPITA FOR SELECTED YEAR
        # --------------------------------------------------------------------------------------

        my_check2 = new_df.set_index('indicator')[[year, 'country']].reset_index()

        my_check2 = my_check2[my_check2['indicator'].isin(["CO2 emissions (metric tons per capita)",
                                                           "Methane emissions (metric tons of CO2 equivalent per capita)",
                                                           "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"])]

        g1 = my_check2[my_check2['indicator'] == "CO2 emissions (metric tons per capita)"].nlargest(10, year)

        figure2 = px.bar(g1,
                         x="country",
                         y=year,
                         title="Top 10 countries CO2 emmissions metric tons per capita for " + year,
                         labels={'country': 'Country',
                                 year: 'Metric tons per capita'
                                 }
                         )

        # Update layout to change background color and label color
        figure2.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': 'Top 10 countries CO2 emmissions per capita for ' + year, 'x': 0.5}
        })  # Add title and align it to the center

        # Update traces to change bar color
        light_green_color = '#7FFF00'  # HEX color code for light green
        figure2.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure2.update_yaxes(range=[0, g1[year].max() + 7])  # update y axes limits range\

        # set the first dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # --------------------------------------------------------------------------------------
        # GRAPH NO 3 TOP 10 COUNTRIES METHANE EMMISSIONS (CO2 METRIC TONS EQUIVALENT PER CAPITA)
        # --------------------------------------------------------------------------------------

        my_check3 = new_df.set_index('indicator')[[year, 'country']].reset_index()

        g2 = my_check3[
            my_check3['indicator'] == "Methane emissions (metric tons of CO2 equivalent per capita)"].nlargest(10, year)

        figure3 = px.bar(g2,
                         x="country",
                         y=year,
                         title="Top 10 countries methane emmissions per capita for " + year,
                         labels={'country': 'Country',
                                 year: 'Metric tons of CO2 equivalent per capita'
                                 }
                         )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': 'Top 10 countries methane emmissions per capita for ' + year, 'x': 0.5}
        })  # Add title and align it to the center

        # Update traces to change bar color
        light_green_color = '#7FFF00'  # HEX color code for light green
        figure3.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure3.update_yaxes(range=[0, g2[year].max() + 5])  # update y axes limits range\

        # set the first dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # -----------------------------------------------------------------------------------------------
        # GRAPH NO 4 TOP 10 COUNTRIES NITROUS OXIDE EMMISSIONS (METRIC TONS OF CO2 EQUIVALENT PER CAPITA)
        # -----------------------------------------------------------------------------------------------

        my_check4 = new_df.set_index('indicator')[[year, 'country']].reset_index()

        g3 = my_check4[
            my_check4['indicator'] == "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"].nlargest(10,
                                                                                                                     year)

        figure4 = px.bar(g3,
                         x="country",
                         y=year,
                         title=f"Top 10 countries nitrous oxide emissions per capita for " + year,
                         labels={'country': 'Country',
                                 year: 'Metric tons of CO2 equivalent per capita'
                                 }
                         )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Top 10 countries nitrus oxide emmissions per capita for ' + year, 'x': 0.5}
        })  # Add title and align it to the center

        # Update traces to change bar color
        light_green_color = '#7FFF00'  # HEX color code for light green
        figure4.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure4.update_yaxes(range=[0, g3[year].max() + 5])  # update y axes limits range

        # set the first dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        # -----------------------------------------------------------------------------------------------
        # RETURN THE GRAPHS
        # -----------------------------------------------------------------------------------------------

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]

    # OPTION 2: USER SELECTS SUB-REGION AND YEAR
    elif option in new_df['sub-region'].unique() and year in years:

        # --------------------------------------------------------------------------------------
        # GRAPH NO 1: TOP 10 CO2 EMMISSIONS DATA PER SUB-REGION PER YEAR
        # --------------------------------------------------------------------------------------

        my_check1 = new_df[(new_df['sub-region'] == option) & (
                    new_df['indicator'] == "CO2 emissions (metric tons per capita)")].set_index('indicator')[
            ['country', year]].nlargest(10, year)

        if len(my_check1['country']) < 10:

            title1 = f"{my_check1.index[0]} in {option}<br> for {year}"

        else:

            title1 = f"Top 10 {option} in {my_check1.index[0]}<br> in {year}"

        figure1 = px.bar(my_check1,
                         x='country',
                         y=year,
                         title=title1,
                         labels={'country': 'Country', year: "Metric tons per capita"
                                 }
                         )

        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': title1, 'x': 0.5}
        })  # Add title and align it to the center

        figure1.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure1.update_yaxes(range=[0, my_check1[year].max() + 5])  # update y axes limits range

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # --------------------------------------------------------------------------------------
        # GRAPH NO 2: TOP 10 COUNTRIES GDP GROWTH (ANNUAL %) PER SUB-REGION AND YEAR
        # --------------------------------------------------------------------------------------

        my_check2 = \
        new_df[(new_df['sub-region'] == option) & (new_df['indicator'] == "GDP growth (annual %)")].set_index(
            'indicator')[['country', year]].nlargest(10, year)

        if len(my_check2['country']) < 10:

            title2 = f"{my_check2.index[0]} in {option} for {year}"

        else:

            title2 = f"Top 10 countries in {option} in {my_check2.index[0]} in {year}"

        figure2 = px.bar(my_check2,
                         x='country',
                         y=year,
                         title=title2,
                         labels={'country': 'Country', year: "GDP growth (annual %)"
                                 }
                         )

        figure2.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': title2, 'x': 0.5}
        })  # Add title and align it to the center

        figure2.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure2.update_yaxes(range=[-5, my_check2[year].max() + 5])  # update y axes limits range

        # set the second dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # -----------------------------------------------------------------------------------------------------------------------
        # GRAPH NO 3: TOP 10 COUNTRIES RENEWABLE ENERGY CONSUMPTION (% OF TOTAL FINAL ENERGY CONSUMPTION) PER SUB-REGION AND YEAR
        # -----------------------------------------------------------------------------------------------------------------------

        my_check3 = new_df[(new_df['sub-region'] == option) & (new_df[
                                                                   'indicator'] == "Renewable energy consumption (% of total final energy consumption)")].set_index(
            'indicator')[['country', year]].nlargest(10, year)

        if len(my_check3['country']) < 10:
            title3 = f"Renewable energy consumption in<br> {option} for {year}"

        else:
            title3 = f"{option} Top 10 in renewable energy consumption<br> in {year}"

        figure3 = px.bar(my_check3,
                         x='country',
                         y=year,
                         title=title3,
                         labels={'country': 'Country', year: '% of total energy consumption'
                                 }
                         )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': title3, 'x': 0.5}
        })  # Add title and align it to the center

        figure3.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure3.update_yaxes(range=[0, my_check3[year].max() + 5])  # update y axes limits range

        # set the third dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # ------------------------------------------------------------------------------------
        # GRAPH NO 4: TOP 10 COUNTRIES NET FOREST DEPLETION (% OF GNI) PER SUB-REGION AND YEAR
        # ------------------------------------------------------------------------------------

        my_check4 = new_df[(new_df['sub-region'] == option) & (
                    new_df['indicator'] == "Adjusted savings: net forest depletion (% of GNI)")].set_index('indicator')[
            ['country', year]].nlargest(10, year)

        if len(my_check4['country']) < 10:
            title4 = f"Net forest depletion in {option}<br> for {year}"

        else:
            title4 = f"{option} Top 10 in<br> net forest depletion {year}"

        figure4 = px.bar(my_check4,
                         x='country',
                         y=year,
                         title=title4,
                         labels={'country': 'Country', year: '(% of GNI)'
                                 }
                         )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': title4, 'x': 0.5}
        })  # Add title and align it to the center

        figure4.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure4.update_yaxes(range=[-5, my_check4[year].max() + 5])  # update y axes limits range

        # set the fourth dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        # -----------------------------------------------------------------------------------------------
        # RETURN THE GRAPHS
        # -----------------------------------------------------------------------------------------------

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]

    # OPTION 3: USER SELECTS CONTINENT AND YEAR

    elif option in new_df['continent'].unique() and year in years:

        # ------------------------------------------------------------------------------------
        # GRAPH NO 1: TOP 10 COUNTRIES CO2 EMMISSIONS PER CONTINENT FOR SELECTED YEAR
        # ------------------------------------------------------------------------------------

        # create a dataframe where the chosen continent and year are selected. We also filter by indicator to get the CO2 emmissions
        my_check1 = new_df[(new_df['continent'] == option) & (
                    new_df['indicator'] == "CO2 emissions (metric tons per capita)")].set_index("indicator")[
            [year, 'country']].nlargest(10, year)

        figure1 = px.bar(my_check1,
                         x='country',
                         y=year,
                         title=f"{option}: CO2 emmissions Top 10 in {year}",
                         labels={'country': 'Country', year: "Metric tons per capita"
                                 }
                         )

        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f"{option}: CO2 emmissions Top 10 in {year}", 'x': 0.5}
            # Add title and align it to the center
        })

        figure1.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure1.update_yaxes(range=[0, my_check1[year].max() + 20])  # update y axes limits range

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # ------------------------------------------------------------------------------------
        # GRAPH NO 2: CUMULATIVE GHG EMMISSIONS PER CONTINENT FOR SELECTED YEAR
        # ------------------------------------------------------------------------------------

        # create a new dataframe where we filter by the necessary indicators
        my_check2 = new_df[new_df['indicator'].isin(["CO2 emissions (metric tons per capita)",
                                                     "Methane emissions (metric tons of CO2 equivalent per capita)",
                                                     "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"])]

        # group by continent and indicator and sum the values for the corresponding year for each indicator
        grouped_my_check2 = my_check2.groupby(['continent', 'indicator'])[year].sum()

        # re-asign table to a dataframe and reset the index
        grouped_my_check2 = pd.DataFrame(grouped_my_check2).reset_index()

        # create a pivot table with continent as the index, indicator as the column and the values for each indicator and reset the index
        grouped_my_check2 = grouped_my_check2.pivot(index='continent', columns='indicator', values=year).reset_index()

        # create a figure object
        figure2 = px.bar(grouped_my_check2,
                         x='continent',
                         y=["CO2 emissions (metric tons per capita)",
                            "Methane emissions (metric tons of CO2 equivalent per capita)",
                            "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"
                            ],

                         color_discrete_map={'CO2 emissions (metric tons per capita)': 'white',
                                             'Methane emissions (metric tons of CO2 equivalent per capita)': '#7FFF00',
                                             'Nitrous oxide emissions (metric tons of CO2 equivalent per capita)': 'yellow'}
                         )

        # Update layout
        figure2.update_layout({'plot_bgcolor': 'black',  # Change background color to black
                               'paper_bgcolor': 'black',  # Change plot area color to black
                               'font': {'color': 'white'},  # Change label color to white
                               },
                              title='Cumulative GHG emmissions in all continents ',
                              xaxis_title='Continent',
                              yaxis_title='Metric tons per capita*',
                              yaxis=dict(titlefont=dict(size=18), tickfont=dict(size=14)))

        # Add sub-note annotation
        figure2.add_annotation(xref='paper',
                               yref='paper',
                               x=0.5,
                               y=-0.3,
                               text='*Values for Methane and Nitrus Oxide emmissions correspond to metric tons of CO2 equivalent per capita',
                               showarrow=False,
                               font=dict(size=12)
                               )

        # figure2.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure2.update_yaxes(range=[0, my_check2[year].max() + 500])  # update y axes limits range

        # set the second dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # -----------------------------------------------------------------------------------------------
        # GRAPH NO 3: TOP 10 COUNTRIES RENEWABLE ENERGY CONSUMPTION (% OF TOTAL FINAL ENERGY CONSUMPTION)
        # -----------------------------------------------------------------------------------------------

        # Renewable energy consumption (% of total final energy consumption)

        my_check3 = new_df[(new_df['ind'] == "EG.FEC.RNEW.ZS") & (new_df['continent'] == option)][
            [year, 'country']].nlargest(10, year)

        figure3 = px.bar(my_check3,
                         x='country',
                         y=year,
                         title=f"{option}: Renewable energy consumption<br> in {year}",
                         labels={'country': 'Country', year: "(% of total final energy consumption)"
                                 }
                         )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f"{option}: Renewable energy consumption<br> in {year}", 'x': 0.5}
            # Add title and align it to the center
        })

        figure3.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure3.update_yaxes(range=[0, 100])  # update y axes limits range

        # set the third dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # -----------------------------------------------------------------------------------------------
        # GRAPH NO 4: TOP 10 COUNTRIES ADJUSTED SAVINGS: NATURAL RESOURCES DEPLETION (% OF GNI)
        # -----------------------------------------------------------------------------------------------

        # Adjusted savings: natural resources depletion (% of GNI)

        my_check4 = new_df[(new_df['ind'] == "NY.ADJ.DRES.GN.ZS") & (new_df['continent'] == option)][
            [year, 'country']].nlargest(10, year)

        figure4 = px.bar(my_check4,
                         x='country',
                         y=year,
                         title=f"{option}: Top 10 Adjusted Savings:<br>Natural Resources Depletion in {year}",
                         labels={'country': 'Country', year: "(% of GNI)"
                                 }
                         )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f"{option}: Top 10 Adjusted Savings:<br>Natural Resources Depletion in {year}", 'x': 0.5}
            # Add title and align it to the center
        })

        figure4.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure4.update_yaxes(range=[0, 40])  # update y axes limits range

        # set the fourth dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        # -----------------------------------------------------------------------------------------------
        # RETURN THE GRAPHS
        # -----------------------------------------------------------------------------------------------

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]


    # OPTION 4: USER SELECTS COUNTRY AND ALL YEARS

    elif option in new_df['country'].unique() and year not in years:

        # --------------------------------------------------------------------------------------
        # GRAPH NO 1: EVOLUTION OF GHG EMMISSIONS PER CAPITA THROUGHOUT THE YEARS
        # --------------------------------------------------------------------------------------

        # create a series of all CO2 metric tons per capita values across all years. Reset the index.
        my_check1 = \
        new_df[(new_df['country'] == option) & (new_df['indicator'].isin(["CO2 emissions (metric tons per capita)",
                                                                          "Methane emissions (metric tons of CO2 equivalent per capita)",
                                                                          "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)"]))][
            years].reset_index()

        # drop the "index" column
        my_check1.drop('index', axis=1, inplace=True)

        # transpose the series
        my_check1 = my_check1.T

        # reset the index
        my_check1.reset_index(inplace=True)

        # rename the columns
        my_check1.rename(columns={"index": "Year", 0: "Value"}, inplace=True)

        # convert the year column in data type int to modify the x limits of the plot
        my_check1['Year'] = my_check1['Year'].astype(int)

        # make a dataframe variable to use for plotting
        my_check1 = pd.DataFrame(my_check1)

        my_check1.rename(columns={'Value': 'CO2 emissions (metric tons per capita)',
                                  1: 'Methane emissions (metric tons of CO2 equivalent per capita)',
                                  2: 'Nitrous oxide emissions (metric tons of CO2 equivalent per capita)'},
                         inplace=True)

        # create a figure
        figure1 = px.line(my_check1,  # the dataframe
                          x='Year',  # the years will be on the x-axis
                          y=['CO2 emissions (metric tons per capita)',
                             'Methane emissions (metric tons of CO2 equivalent per capita)',
                             'Nitrous oxide emissions (metric tons of CO2 equivalent per capita)'],
                          # the values for each gas will be on the y axis
                          labels={'value': 'Metric tons'},  # change the label for the y axis
                          markers=True  # show markers on each point
                          )

        # Define shortened labels for the legend
        short_labels = {'CO2 emissions (metric tons per capita)': 'CO2',
                        'Methane emissions (metric tons of CO2 equivalent per capita)': 'Methane',
                        'Nitrous oxide emissions (metric tons of CO2 equivalent per capita)': 'Nitrous oxide'}

        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Greenhouse Gas emmissions per capita<br> in {option} [1990-2018]', 'x': 0.5},
            # Add title and align it to the center
            'legend': {'title': {'text': 'Gas'}, 'traceorder': 'normal', 'itemsizing': 'constant', 'itemwidth': 50},
            # Update the legend properties
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        # Update legend labels
        for trace in figure1.data:
            trace.name = short_labels[trace.name]

        figure1.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure1.update_xaxes(
            range=[my_check1['Year'].min() - 0.5, my_check1['Year'].max() + 0.5])  # Change the lims of the x axis

        # Show all years on x-axis
        figure1.update_xaxes(tickmode='linear', tick0=my_check1['Year'].min(), dtick=1)

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # -------------------------------------------------------------------------------------------
        # GRAPH NO 2: EVOLUTION OF RENEWABLE ENERGY CONSUMPTION (% OF TOTAL FINAL ENERGY CONSUMPTION)
        # -------------------------------------------------------------------------------------------

        # Create a Series with the relevant indicator and the country of choice
        my_check2 = new_df[(new_df['country'] == option) & (
                    new_df['indicator'] == "Renewable energy consumption (% of total final energy consumption)")][
            years].reset_index()

        # Drop the index column
        my_check2.drop('index', axis=1, inplace=True)

        # Transpose the series
        my_check2 = my_check2.T

        # Rename the columns
        my_check2.rename(columns={'index': 'year', 0: 'value'},
                         inplace=True
                         )

        # make a dataframe variable to use for plotting
        my_check2 = pd.DataFrame(my_check2)

        # reset the index
        my_check2.reset_index(inplace=True)

        # rename the index column
        my_check2.rename(columns={'index': 'year'}, inplace=True)

        # convert the year column in data type int to modify the x limits of the plot
        my_check2['year'] = my_check2['year'].astype(int)

        # set the figure
        figure2 = px.bar(my_check2,
                         x='year',
                         y='value',
                         labels={'value': '% of total final energy consumption'}
                         )

        figure2.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Renewable energy consumption<br> in {option} [1990-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure2.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure2.update_xaxes(range=[my_check2['year'].min() - 0.5, my_check2['year'].max() + 0.5])

        # Show all years on x-axis
        figure2.update_xaxes(tickmode='linear', tick0=my_check2['year'].min(), dtick=1)

        # set the second dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # -------------------------------------------------------------------------------------------
        # GRAPH NO 3: EVOLUTION OF GDP ANNUAL GROWTH
        # -------------------------------------------------------------------------------------------

        # Create a Series with the relevant indicator and the country of choice
        my_check3 = new_df[(new_df['country'] == option) & (new_df['indicator'] == "GDP growth (annual %)")][
            years].reset_index()

        # drop the "index" column
        my_check3.drop('index', axis=1, inplace=True)

        # transpose the series
        my_check3 = my_check3.T

        # reset the index
        my_check3.reset_index(inplace=True)

        # rename the columns
        my_check3.rename(columns={"index": "Year", 0: "Value"}, inplace=True)

        # convert the year column in data type int to modify the x limits of the plot
        my_check3['Year'] = my_check3['Year'].astype(int)

        # make a dataframe variable to use for plotting
        my_check3 = pd.DataFrame(my_check3)

        figure3 = px.line(my_check3,
                          x='Year',
                          y='Value',
                          labels={'value': 'Annual change (%)'},
                          markers=True
                          )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'GDP growth in {option} [1980-2018]', 'x': 0.5},  # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure3.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure3.update_xaxes(range=[my_check3['Year'].min() - 0.5, my_check3['Year'].max() + 0.5])

        # Show all years on x-axis
        figure3.update_xaxes(tickmode='linear', tick0=my_check3['Year'].min(), dtick=1)
        figure3.update_yaxes(range=[my_check3['Value'].min() - 1.5, my_check3['Value'].max() + 5])

        # set the third dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # -------------------------------------------------------------------------------------------
        # GRAPH NO 4: EVOLUTION OF ADJUSTED SAVINGS: NATURAL RESOURCES DEPLETION (% of GNI)
        # -------------------------------------------------------------------------------------------

        # Create a Series with the relevant indicator and the country of choice
        my_check4 = new_df[(new_df['country'] == option) & (new_df['indicator'] == "Forest area (% of land area)")][
            years].reset_index()

        # drop the "index" column
        my_check4.drop('index', axis=1, inplace=True)

        # transpose the series
        my_check4 = my_check4.T

        # reset the index
        my_check4.reset_index(inplace=True)

        # rename the columns
        my_check4.rename(columns={"index": "Year", 0: "Value"}, inplace=True)

        # convert the year column in data type int to modify the x limits of the plot
        my_check4['Year'] = my_check4['Year'].astype(int)

        # make a dataframe variable to use for plotting
        my_check4 = pd.DataFrame(my_check4)

        figure4 = px.line(my_check4,
                          x='Year',
                          y='Value',
                          labels={'Value': '% of land area'},
                          markers=True
                          )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Forest area in {option} [1980-2018]', 'x': 0.5},  # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure4.update_traces(marker_color=light_green_color)  # Change bar color to light green
        figure4.update_xaxes(range=[my_check4['Year'].min() - 0.5, my_check4['Year'].max() + 0.5])
        figure4.update_yaxes(range=[my_check4['Value'].min() - 1.5, my_check4['Value'].max() + 5])

        # Show all years on x-axis
        figure4.update_xaxes(tickmode='linear', tick0=my_check4['Year'].min(), dtick=1)

        # set the fourth dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]

    # OPTION 5: USER SELECTS SUB-REGION AND ALL YEARS

    elif option in new_df['sub-region'].unique() and year not in years:

        # ------------------------------------------------------------------------------------------------------
        # GRAPH NO 1: EVOLUTION OF CUMULATIVE CO2 EMMISSIONS PER CAPITA THROUGHOUT THE YEARS FOR ALL SUB-REGIONS
        # ------------------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check1 = new_df[new_df['indicator'] == "CO2 emissions (metric tons per capita)"]

        # group the dataframe by sub-region - sum the CO2 emmissions per capita per sub-region
        my_check1 = my_check1.groupby('sub-region')[years].sum().reset_index()

        # re-asign table to a dataframe and reset the index
        my_check1 = pd.DataFrame(my_check1)

        # transpose the datafrafe
        my_check1 = my_check1.T

        # change the name of the columns
        my_check1.columns = my_check1.iloc[0, :]

        # remove the first row which is not necessary
        my_check1 = my_check1.loc['1990':, :]

        # reset the index to put the years back as a column
        my_check1.reset_index(inplace=True)

        # rename the index column to 'year'
        my_check1.rename(columns={"index": 'year'}, inplace=True)

        # change the data type of the year column to modify the x axis limits while plotting
        my_check1['year'] = my_check1['year'].astype(int)

        # take the values of all sub-regions for plotting
        subregions = my_check1.columns[1:]

        # plot the line graph
        figure1 = px.line(my_check1,
                          x='year',
                          y=subregions,
                          labels={'value': 'Metric Tons per Capita'},
                          markers=True
                          )

        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': 'Comparison of cumulative CO2 emmissions<br> for all sub-regions [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure1.update_xaxes(range=[my_check1['year'].min() - 0.5, my_check1['year'].max() + 0.5])

        # Show all years on x-axis
        figure1.update_xaxes(tickmode='linear', tick0=my_check1['year'].min(), dtick=1)

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # --------------------------------------------------------------------------------------
        # GRAPH NO 2: EVOLUTION OF CO2 EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # --------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check2 = new_df[
            (new_df['sub-region'] == option) & (new_df['indicator'] == "CO2 emissions (metric tons per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check2 = my_check2.set_index('country')[years].T

        # set the name of the columns to None
        my_check2.columns.name = None

        # reset the index
        my_check2.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check2.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check2['year'] = my_check2['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check2.columns[1:]

        figure2 = px.line(my_check2,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons per Capita', 'year': 'Year'}
                          )

        figure2.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'CO2 emmissions in {option}<br>All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure2.update_xaxes(range=[my_check2['year'].min() - 0.5, my_check2['year'].max() + 0.5])

        # Show all years on x-axis
        figure2.update_xaxes(tickmode='linear', tick0=my_check2['year'].min(), dtick=1)

        # set the second dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # -------------------------------------------------------------------------------------------
        # GRAPH NO 3: EVOLUTION OF METHANE EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # -------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check3 = new_df[(new_df['sub-region'] == option) & (
                    new_df['indicator'] == "Methane emissions (metric tons of CO2 equivalent per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check3 = my_check3.set_index('country')[years].T

        # set the name of the columns to None
        my_check3.columns.name = None

        # reset the index
        my_check3.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check3.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check3['year'] = my_check3['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check3.columns[1:]

        figure3 = px.line(my_check3,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons of CO2 Equivalent<br> per Capita', 'year': 'Year'}
                          )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Methane emmissions in {option}<br> All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure3.update_xaxes(range=[my_check3['year'].min() - 0.5, my_check3['year'].max() + 0.5])

        # Show all years on x-axis
        figure3.update_xaxes(tickmode='linear', tick0=my_check3['year'].min(), dtick=1)

        # set the third dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # ------------------------------------------------------------------------------------------------
        # GRAPH NO 4: EVOLUTION OF NITRUS OXIDE EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # ------------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check4 = new_df[(new_df['sub-region'] == 'Southern Europe') & (
                    new_df['indicator'] == "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check4 = my_check4.set_index('country')[years].T

        # set the name of the columns to None
        my_check4.columns.name = None

        # reset the index
        my_check4.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check4.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check4['year'] = my_check4['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check4.columns[1:]

        figure4 = px.line(my_check4,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons of CO2 equivalent in<br> per Capita', 'year': 'Year'}
                          )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Nitrus oxide emmissions in {option}<br> All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure4.update_xaxes(range=[my_check4['year'].min() - 0.5, my_check4['year'].max() + 0.5])

        # Show all years on x-axis
        figure4.update_xaxes(tickmode='linear', tick0=my_check4['year'].min(), dtick=1)

        # set the fourth dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]

    # OPTION 6: USER SELECTS CONTINENT AND ALL YEARS

    elif option in new_df['continent'].unique() and year not in years:

        # ------------------------------------------------------------------------------------------------------
        # GRAPH NO 1: EVOLUTION OF CUMULATIVE CO2 EMMISSIONS PER CAPITA THROUGHOUT THE YEARS FOR ALL CONTINENTS
        # ------------------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check1 = new_df[new_df['indicator'] == "CO2 emissions (metric tons per capita)"]

        # group the dataframe by sub-region - sum the CO2 emmissions per capita per sub-region
        my_check1 = my_check1.groupby('continent')[years].sum().reset_index()

        # re-asign table to a dataframe and reset the index
        my_check1 = pd.DataFrame(my_check1)

        # transpose the datafrafe
        my_check1 = my_check1.T

        # change the name of the columns
        my_check1.columns = my_check1.iloc[0, :]

        # assign a None value to the columns name
        my_check1.columns.name = None

        # reset the index to put the years back as a column
        my_check1.reset_index(inplace=True)

        # rename the index column to 'year'
        my_check1.rename(columns={"index": 'year'}, inplace=True)

        # remove the first row from the dataset
        my_check1 = my_check1.iloc[1:, :]

        # change the data type of the year column to modify the x axis limits while plotting
        my_check1['year'] = my_check1['year'].astype(int)

        # take the values of all sub-regions for plotting
        continents = my_check1.columns[1:]

        figure1 = px.line(my_check1,
                          x='year',
                          y=continents,
                          markers=True,
                          labels={'value': 'Cumulative Metric Tons <br>of CO2 per Capita', 'year': 'Year'}
                          )

        figure1.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': 'Comparison of cumulative CO2 emmissions<br> for all continents [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure1.update_xaxes(range=[my_check1['year'].min() - 0.5, my_check1['year'].max() + 0.5])

        # Show all years on x-axis
        figure1.update_xaxes(tickmode='linear', tick0=my_check1['year'].min(), dtick=1)

        # set the first dcc graph object
        R_chart1 = dcc.Graph(figure=figure1)

        # --------------------------------------------------------------------------------------
        # GRAPH NO 2: EVOLUTION OF CO2 EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # --------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check2 = new_df[
            (new_df['continent'] == option) & (new_df['indicator'] == "CO2 emissions (metric tons per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check2 = my_check2.set_index('country')[years].T

        # set the name of the columns to None
        my_check2.columns.name = None

        # reset the index
        my_check2.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check2.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check2['year'] = my_check2['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check2.columns[1:]

        figure2 = px.line(my_check2,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons per Capita', 'year': 'Year'}
                          )

        figure2.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'CO2 emmissions in {option}<br>All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure2.update_xaxes(range=[my_check2['year'].min() - 0.5, my_check2['year'].max() + 0.5])

        # Show all years on x-axis
        figure2.update_xaxes(tickmode='linear', tick0=my_check2['year'].min(), dtick=1)

        # set the second dcc graph object
        R_chart2 = dcc.Graph(figure=figure2)

        # -------------------------------------------------------------------------------------------
        # GRAPH NO 3: EVOLUTION OF METHANE EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # -------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check3 = new_df[(new_df['continent'] == option) & (
                    new_df['indicator'] == "Methane emissions (metric tons of CO2 equivalent per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check3 = my_check3.set_index('country')[years].T

        # set the name of the columns to None
        my_check3.columns.name = None

        # reset the index
        my_check3.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check3.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check3['year'] = my_check3['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check3.columns[1:]

        figure3 = px.line(my_check3,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons of <br>CO2 Equivalent per Capita', 'year': 'Year'}
                          )

        figure3.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Methane emmissions in {option}<br>All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure3.update_xaxes(range=[my_check3['year'].min() - 0.5, my_check3['year'].max() + 0.5])

        # Show all years on x-axis
        figure3.update_xaxes(tickmode='linear', tick0=my_check3['year'].min(), dtick=1)

        # set the third dcc graph object
        R_chart3 = dcc.Graph(figure=figure3)

        # ------------------------------------------------------------------------------------------------
        # GRAPH NO 4: EVOLUTION OF NITRUS OXIDE EMMISSIONS PER CAPITA THROUGHOUT THE YEARS (ALL COUNTRIES)
        # ------------------------------------------------------------------------------------------------

        # retrieve only the relevant indicator (CO2 emmissions per capita)
        my_check4 = new_df[(new_df['continent'] == option) & (
                    new_df['indicator'] == "Nitrous oxide emissions (metric tons of CO2 equivalent per capita)")]

        # set the country as index and select the years columns then transpose the dataframe
        my_check4 = my_check4.set_index('country')[years].T

        # set the name of the columns to None
        my_check4.columns.name = None

        # reset the index
        my_check4.reset_index(inplace=True)

        # rename the column 'index' to 'year'
        my_check4.rename(columns={'index': 'year'}, inplace=True)

        # change the data type of the year column to int to change the x axis limits in plotting
        my_check4['year'] = my_check4['year'].astype(int)

        # get the countries from the dataframe
        countries = my_check4.columns[1:]

        figure4 = px.line(my_check4,
                          x='year',
                          y=countries,
                          markers=True,
                          labels={'value': 'Metric Tons of<br>CO2 Equivalent per Capita', 'year': 'Year'}
                          )

        figure4.update_layout({
            'plot_bgcolor': 'black',  # Change background color to black
            'paper_bgcolor': 'black',  # Change plot area color to black
            'font': {'color': 'white'},  # Change label color to white
            'title': {'text': f'Nitrus oxide emmissions in {option}<br>All Countries [1980-2018]', 'x': 0.5},
            # Add title and align it to the center
            'xaxis': {'tickangle': 45}  # Rotate x-axis labels by 45 degrees
        })

        figure4.update_xaxes(range=[my_check4['year'].min() - 0.5, my_check4['year'].max() + 0.5])

        # Show all years on x-axis
        figure4.update_xaxes(tickmode='linear', tick0=my_check4['year'].min(), dtick=1)

        # set the fourth dcc graph object
        R_chart4 = dcc.Graph(figure=figure4)

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)])
        ]


if __name__ == '__main__':
    app.run_server(debug=True)