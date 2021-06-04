import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

#World Thematic Map
country_code_dict = {
    'Aruba':'ABW',
    'Afghanistan':'AFG',
    'Angola':'AGO',
    'Anguilla':'AIA',
    'Åland Islands':'ALA',
    'Albania':'ALB',
    'Andorra':'AND  ',
    'United Arab Emirates':'ARE',
    'Argentina':'ARG ',
    'Armenia':'ARM ',
    'American Samoa':'ASM',
    'Antarctica':'ATA',
    'French Southern Territories':'ATF',
    'Antigua and Barbuda':'ATG',
    'Australia':'AUS',
    'Austria':'AUT',
    'Azerbaijan':'AZE',
    'Burundi':'BDI',
    'Belgium':'BEL',
    'Benin':'BEN',
    'Bonaire, Sint Eustatius and Saba':'BES',
    'Burkina Faso':'BFA',
    'Bangladesh':'BGD',
    'Bulgaria':'BGR',
    'Bahrain':'BHR',
    'Bahamas':'BHS',
    'Bosnia and Herzegovina':'BIH',
    'Saint Barthélemy':'BLM',
    'Belarus':'BLR',
    'Belize':'BLZ',
    'Bermuda':'BMU',
    'Bolivia':'BOL',
    'Brazil':'BRA',
    'Barbados':'BRB',
    'Brunei Darussalam':'BRN',
    'Bhutan':'BTN',
    'Bouvet Island':'BVT',
    'Botswana':'BWA',
    'Central African Republic':'CAF',
    'Canada':'CAN',
    'Cocos (Keeling) Islands':'CCK',
    'Switzerland':'CHE',
    'Chile':'CHL',
    'China':'CHN',
    'Côte d\'Ivoire':'CIV',
    'Cameroon':'CMR',
    'Congo, Rep.':'COD',
    'Congo':'COG',
    'Cook Islands':'COK',
    'Colombia':'COL',
    'Comoros':'COM',
    'Cabo Verde':'CPV',
    'Costa Rica':'CRI',
    'Cuba':'CUB',
    'Curaçao':'CUW',
    'Christmas Island':'CXR',
    'Cayman Islands':'CYM',
    'Cyprus':'CYP',
    'Czechia':'CZE',
    'Germany':'DEU',
    'Djibouti':'DJI',
    'Dominica':'DMA',
    'Denmark':'DNK',
    'Dominican Republic':'DOM',
    'Algeria':'DZA',
    'Ecuador':'ECU',
    'Egypt, Arab Rep.':'EGY',
    'Eritrea':'ERI',
    'Western Sahara':'ESH',
    'Spain':'ESP',
    'Estonia':'EST',
    'Ethiopia':'ETH',
    'Finland':'FIN',
    'Fiji':'FJI',
    'Falkland Islands (Malvinas)':'FLK',
    'France':'FRA',
    'Faroe Islands':'FRO',
    'Micronesia (Federated States of)':'FSM',
    'Gabon':'GAB',
    'Georgia':'GEO',
    'Guernsey':'GGY',
    'Ghana':'GHA',
    'Gibraltar':'GIB',
    'Guinea':'GIN',
    'Guadeloupe':'GLP',
    'Gambia':'GMB',
    'Guinea-Bissau':'GNB',
    'Equatorial Guinea':'GNQ',
    'Greece':'GRC',
    'Grenada':'GRD',
    'Greenland':'GRL',
    'Guatemala':'GTM',
    'French Guiana':'GUF',
    'Guam':'GUM',
    'Guyana':'GUY',
    'Hong Kong SAR, China':'HKG',
    'Heard Island and McDonald Islands':'HMD',
    'Honduras':'HND',
    'Croatia':'HRV',
    'Haiti':'HTI',
    'Hungary':'HUN',
    'Indonesia':'IDN',
    'Isle of Man':'IMN',
    'India':'IND',
    'British Indian Ocean Territory':'IOT',
    'Ireland':'IRL',
    'Iran, Islamic Rep.':'IRN',
    'Iraq':'IRQ',
    'Iceland':'ISL',
    'Israel':'ISR',
    'Italy':'ITA',
    'Jamaica':'JAM',
    'Jersey':'JEY',
    'Jordan':'JOR',
    'Japan':'JPN',
    'Kazakhstan':'KAZ',
    'Kenya':'KEN',
    'Kyrgyzstan':'KGZ',
    'Cambodia':'KHM',
    'Kiribati':'KIR',
    'Saint Kitts and Nevis':'KNA',
    'Korea, Republic of':'KOR',
    'Kuwait':'KWT',
    'Lao PDR':'LAO',
    'Lebanon':'LBN',
    'Liberia':'LBR',
    'Libya':'LBY',
    'St. Lucia':'LCA',
    'Liechtenstein':'LIE',
    'Sri Lanka':'LKA',
    'Lesotho':'LSO',
    'Lithuania':'LTU',
    'Luxembourg':'LUX',
    'Latvia':'LVA',
    'Macao SAR, China':'MAC',
    'Saint Martin (French part)':'MAF',
    'Morocco':'MAR',
    'Monaco':'MCO',
    'Moldova, Republic of':'MDA',
    'Madagascar':'MDG',
    'Maldives':'MDV',
    'Mexico':'MEX',
    'Marshall Islands':'MHL',
    'North Macedonia':'MKD',
    'Mali':'MLI',
    'Malta':'MLT',
    'Myanmar':'MMR',
    'Montenegro':'MNE',
    'Mongolia':'MNG',
    'Northern Mariana Islands':'MNP',
    'Mozambique':'MOZ',
    'Mauritania':'MRT',
    'Montserrat':'MSR',
    'Martinique':'MTQ',
    'Mauritius':'MUS',
    'Malawi':'MWI',
    'Malaysia':'MYS',
    'Mayotte':'MYT',
    'Namibia':'NAM',
    'New Caledonia':'NCL',
    'Niger':'NER',
    'Norfolk Island':'NFK',
    'Nigeria':'NGA',
    'Nicaragua':'NIC',
    'Niue':'NIU',
    'Netherlands':'NLD',
    'Norway':'NOR',
    'Nepal':'NPL',
    'Nauru':'NRU',
    'New Zealand':'NZL',
    'Oman':'OMN',
    'Pakistan':'PAK',
    'Panama':'PAN',
    'Pitcairn':'PCN',
    'Peru':'PER',
    'Philippines':'PHL',
    'Palau':'PLW',
    'Papua New Guinea':'PNG',
    'Poland':'POL',
    'Puerto Rico':'PRI',
    'Korea, Dem. Rep.':'PRK',
    'Portugal':'PRT',
    'Paraguay':'PRY',
    'Palestine, State of':'PSE',
    'French Polynesia':'PYF',
    'Qatar':'QAT',
    'Réunion':'REU',
    'Romania':'ROU',
    'Russian Federation':'RUS',
    'Rwanda':'RWA',
    'Saudi Arabia':'SAU',
    'Sudan':'SDN',
    'Senegal':'SEN',
    'Singapore':'SGP',
    'South Georgia and the South Sandwich Islands':'SGS',
    'Saint Helena, Ascension and Tristan da Cunha':'SHN',
    'Svalbard and Jan Mayen':'SJM',
    'Solomon Islands':'SLB',
    'Sierra Leone':'SLE',
    'El Salvador':'SLV',
    'San Marino':'SMR',
    'Somalia':'SOM',
    'Saint Pierre and Miquelon':'SPM',
    'Serbia':'SRB',
    'South Sudan':'SSD',
    'Sao Tome and Principe':'STP',
    'Suriname':'SUR',
    'Slovakia':'SVK',
    'Slovenia':'SVN',
    'Sweden':'SWE',
    'Eswatini':'SWZ',
    'Sint Maarten (Dutch part)':'SXM',
    'Seychelles':'SYC',
    'Syrian Arab Republic':'SYR',
    'Turks and Caicos Islands':'TCA',
    'Chad':'TCD',
    'Togo':'TGO',
    'Thailand':'THA',
    'Tajikistan':'TJK',
    'Tokelau':'TKL',
    'Turkmenistan':'TKM',
    'Timor-Leste':'TLS',
    'Tonga':'TON',
    'Trinidad and Tobago':'TTO',
    'Tunisia':'TUN',
    'Turkey':'TUR',
    'Tuvalu':'TUV',
    'Taiwan, China':'TWN',
    'Tanzania, United Republic of':'TZA',
    'Uganda':'UGA',
    'Ukraine':'UKR',
    'United States Minor Outlying Islands':'UMI',
    'Uruguay':'URY',
    'United States':'USA',
    'United Kingdom':'GBR',
    'Uzbekistan':'UZB',
    'Holy See':'VAT',
    'Saint Vincent and the Grenadines':'VCT',
    'Venezuela (Bolivarian Republic of)':'VEN',
    'Virgin Islands (British)':'VGB',
    'Virgin Islands (U.S.)':'VIR',
    'Viet Nam':'VNM',
    'Vanuatu':'VUT',
    'Wallis and Futuna':'WLF',
    'Samoa':'WSM',
    'Yemen':'YEM',
    'South Africa':'ZAF',
    'Zambia':'ZMB',
    'Zimbabwe':'ZWE',
}

def world_choropleth_map_intake (df_corridor, df_intake):
    if df_intake.empty:
       fig = go.Figure()
       fig.update_layout(
            title_text='Crude Intake by Country',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake.columns = ['corridor_id', 'intake','commodity','date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_country']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero

        df['code'] = df['load_country'].map(country_code_dict,'ignore')
        fig = go.Figure(data=go.Choropleth(
            locations = df['code'],
            z = df['intake'],
            text = df['load_country'],
            colorscale = 'Oranges',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='white',
            marker_line_width=0.8,
            colorbar_tickprefix = '',
            colorbar_title = 'Crude Intake (Tons)',
        ))

        fig.update_layout(
            title_text='Color Map of Crude Intake by Country',
            width=950,
            height=530,
            font=dict(
                size=18,
                ),
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            annotations = [dict(
                x=0.55,
                y=0.1,
                xref='paper',
                yref='paper',
                text='',
                showarrow = False
            )]
        )

    return fig
    
def intake_corridor_barplot(intake, lvh):
    if intake.empty:
         barplot = go.Figure()
         barplot.update_layout(
                            title='Total Intake per Commodity',
                            width = 500,
                            height = 500,
                            annotations = [
                                {   
                                    "text": "Not Data",
                                    "xref": "paper",
                                    "yref": "paper",
                                    "showarrow": False,
                                    "font": {"size": 28}
                                }
                            ]
                        )
    else:
        intake.columns = ['commodity_id', 'intake']
        df =  pd.merge(intake,lvh,on=['commodity_id'],how="inner",indicator=True)
        df = df.groupby(['name']).sum().reset_index()
        '''
        data = list(CorridorIntake.objects.values_list('commodity').annotate(Sum('intake'))) #Return a tumple of (commodity, sum)
        x_data, y_data = [list(c) for c in zip(*data)] #Separete x and y data by commodity and sum(intake)
        #x_data = [str(int) for int in x_data]

        x_data = [CommodityLvh.objects.values_list('name').filter(commodity_id=int)[0][0] for int in x_data] #Query returns a tuple Queryset[(name, )] 
        '''
        barplot = go.Figure([go.Bar(x=df['name'], y=df['intake'],
                            name='test',
                            opacity=0.8, marker_color='blue')])

        barplot.update_layout(
                            title='Total Intake per Commodity',
                            width = 500,
                            height = 500,
                            font=dict(
                                size=18,
                                ),
                            )
    
    return barplot

def horizontal_bar_intake(df_corridor, df_intake):

    if df_intake.empty:
       barplot = go.Figure()
       barplot.update_layout(
            title_text='Crude Intake by Country',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_country']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero
        top_ten = df.nlargest(10,'intake')

        barplot = go.Figure([go.Bar(y=top_ten['load_country'], x=top_ten['intake'],
                        name='test',
                        orientation='h',
                        opacity=0.8, marker_color='blue')])

        barplot.update_layout(
                        title='Total Intake per Country',
                        width = 950,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
    return barplot

def horizontal_bar_intake_load_port(df_corridor, df_intake):

    if df_intake.empty:
       barplot = go.Figure()
       barplot.update_layout(
            title_text='Total Intake by Load Port [Mtons]',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df['location'] =  df['load_port'] +' (' +df['load_country'] + ')'
        df = df.groupby(['location']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero
       
        top_ten = df.nlargest(10,'intake')

        barplot = go.Figure([go.Bar(y=top_ten['location'], x=top_ten['intake'],
                        name='test',
                        orientation='h',
                        opacity=0.8, marker_color='blue')])

        barplot.update_layout(
                        title='Total Intake by Load Port [Mtons]',
                        width = 1050,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
        return barplot

def piechart_intake(df_corridor, df_intake):

    if df_intake.empty:
       piechart = go.Figure()
       piechart.update_layout(
            title_text='Total Intake per Discharge Port',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['discharge_port']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero

        total_sum = df['intake'].sum()
        df['percentage'] = df['intake'].apply(lambda x: (x/total_sum).round(4)*100)

        piechart = go.Figure([go.Pie(labels=df['discharge_port'], values=df['percentage'],
                        name='test',
                        textinfo='label+percent',
                        insidetextorientation='radial'
                       )])

        piechart.update_layout(
                        title='Total Intake per Discharge Port',
                        width = 950,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
    return piechart

def world_choropleth_map_risk (total_risk_df):
   
    if total_risk_df.empty:
       fig = go.Figure()
       fig.update_layout(
            title_text='Energy Risk',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        total_risk_df['code'] = total_risk_df['country'].map(country_code_dict,'ignore')
        fig = go.Figure(data=go.Choropleth(
            locations = total_risk_df['code'],
            z = total_risk_df['risk'],
            text = total_risk_df['country'],
            colorscale = 'Reds',
            autocolorscale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '',
            colorbar_title = 'Energy Risk [Mtoe]',
        ))

        fig.update_layout(
            title_text='Energy Risk',
            width=950,
            height=600,
            font=dict(
                 size=18,
                ),
            geo=dict(
                showframe=False,
                showcoastlines=False,
                projection_type='equirectangular'
            ),
            annotations = [dict(
                x=0.55,
                y=0.1,
                xref='paper',
                yref='paper',
                text='',
                showarrow = False
            )]
        )

    return fig

def group_bar_intake_country(corridor_df, intake_df, intake_previous_df, year):
    if intake_df.empty:
       fig = go.Figure()
       fig.update_layout(
            title_text='Total Intake by Load Country [Mtons]',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )

    elif intake_previous_df.empty:
        intake_df = intake_df.drop(['commodity'], axis= 1)
        intake_df.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(corridor_df,intake_df,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_country']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero
        top_ten = df.nlargest(10,'intake')

        fig = go.Figure(data=[
        go.Bar(name=year, x=df['load_country'], y=df['intake']),
        ])

        fig.update_layout(
        barmode='group',
        title='Total Intake by Load Country [Mtons]',
        width = 1100,
        height = 600,
        font=dict(
            size=18,
            ),
        )

    else:
        intake_df = intake_df.drop(['commodity'], axis= 1)
        intake_df.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(corridor_df,intake_df,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_country']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero
        top_ten = df.nlargest(10,'intake')

        intake_previous_df = intake_previous_df.drop(['commodity'], axis= 1)
        intake_previous_df.columns = ['corridor_id', 'intake', 'date']
        df_last = pd.merge(corridor_df,intake_previous_df,on=['corridor_id'],how="outer",indicator=True)
        df_last =df_last.drop(['corridor_id'], axis = 1)
        df_last = df_last.groupby(['load_country']).sum().reset_index()

        new_df = pd.merge(top_ten,df_last,on=['load_country'],how="left",indicator=True)
        fig = go.Figure(data=[
        go.Bar(name=year, x=new_df['load_country'], y=new_df['intake_x']),
        go.Bar(name=year-1, x=new_df['load_country'], y=new_df['intake_y'])
        ])
        # Change the bar mode
        fig.update_layout(
            barmode='group',
            title='Total Intake by Load Country [Mtons]',
            width = 1100,
            height = 600,
            font=dict(
                size=18,
                ),
            )
            

    return fig

def piechart_intake_load_country(df_corridor, df_intake):

    if df_intake.empty:
       piechart = go.Figure()
       piechart.update_layout(
            title_text='Shares of Crude Intake by Load Port',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_port']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero

        total_sum = df['intake'].sum()
        df['percentage'] = df['intake'].apply(lambda x: (x/total_sum).round(4)*100)
        df = df.sort_values(by=['intake'],ascending=False)
        top_ten = df.nlargest(7,'intake')
        rest_intake = df.iloc[7:].sum()
        top_ten = top_ten.append({'load_port': 'Others', 'intake': rest_intake['intake'], 'percentage': rest_intake['percentage']}, ignore_index=True)
        
        piechart = go.Figure([go.Pie(labels=top_ten['load_port'], values=top_ten['percentage'],
                        name='test',
                        textinfo='label+percent',
                        insidetextorientation='radial'
                       )])

        piechart.update_layout(
                        title='Shares of Crude Intake by Load Port',
                        width = 950,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
    return piechart
    
def bar_plot_oil_dicharge_port (df_corridor, df_intake):
    if df_intake.empty:
       barplot = go.Figure()
       barplot.update_layout(
            title_text='Total Intake by Discharge Port [Mtons]',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['discharge_port']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero
       
        top_ten = df.nlargest(10,'intake')

        barplot = go.Figure([go.Bar(x=top_ten['discharge_port'], y=top_ten['intake'],
                        name='test',
                        opacity=0.8, marker_color='blue')])

        barplot.update_layout(
                        title='Total Intake by Discharge Port [Mtons]',
                        width = 1050,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
        return barplot

def piechart_discharge_port_oil(df_corridor, df_intake):
    if df_intake.empty:
       piechart = go.Figure()
       piechart.update_layout(
            title_text='Shares of Crude Intake by Discharge Port',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        df_intake = df_intake.drop(['commodity'], axis= 1)
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['discharge_port']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero

        total_sum = df['intake'].sum()
        df['percentage'] = df['intake'].apply(lambda x: (x/total_sum).round(4)*100)
        df = df.sort_values(by=['intake'],ascending=False)
        top_ten = df.nlargest(7,'intake')
        rest_intake = df.iloc[7:].sum()
        top_ten = top_ten.append({'discharge_port': 'Others', 'intake': rest_intake['intake'], 'percentage': rest_intake['percentage']}, ignore_index=True)
        
        piechart = go.Figure([go.Pie(labels=top_ten['discharge_port'], values=top_ten['percentage'],
                        name='test',
                        textinfo='label+percent',
                        insidetextorientation='radial'
                       )])

        piechart.update_layout(
                        title='Shares of Crude Intake by Discharge Port',
                        width = 950,
                        height = 600,
                        font=dict(
                            size=18,
                            ),
                        )
    
    return piechart

def stack_bar_chart_commodity(df_corridor, df_intake, df_lvh):
    if df_intake.empty:
        fig = go.Figure()
        fig.update_layout(
            title_text='Intake Commodity by Discharge Port',
            width=1100,
            height=700,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:

        df_intake.columns = ['corridor_id', 'intake','commodity_id','date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="inner",indicator=False)
        df = df.drop(['load_country','load_port','date','corridor_id'], axis= 1)
        df = pd.merge(df,df_lvh, on=['commodity_id'], how='outer', indicator=True)
        df = df.groupby(['discharge_port','name']).sum().reset_index() 
        data = [go.Bar(name=group, x=dfg['discharge_port'], y=dfg['intake']) for group, dfg in df.groupby(by='name')]

        # plot the figure
        fig = go.Figure(data)
        fig.update_layout(
            barmode='stack', 
            title='Intake Commodity by Discharge Port',
            width = 1050,
            height = 750,
            font=dict(
                size=18,
                ),
            #xaxis_title='Name',
            #yaxis=dict(tickformat="%",)
            
            )
    
    return fig
    
def sunburst_commodity_dp(df_corridor, df_intake, df_lvh):
    if df_intake.empty:
        fig = go.Figure()
        fig.update_layout(
            title_text='Intake Commodity by Discharge Port',
            width=1100,
            height=700,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:

        df_intake.columns = ['corridor_id', 'intake','commodity_id','date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="inner",indicator=False)
        df = df.drop(['load_country','load_port','date','corridor_id'], axis= 1)
        df = pd.merge(df,df_lvh, on=['commodity_id'], how='outer', indicator=True)
        df = df.groupby(['discharge_port','name']).sum().reset_index()

        fig = px.sunburst(df, path=['name', 'discharge_port'], values='intake', width=1100, height=800)
        fig.update_layout(
            title = 'Share of Commodity by Port',
            font_size = 20,
        )
        fig.update_traces(textinfo="label+percent entry")
    return fig

def group_bar_risk_country_oil(total_risk_df):
    if total_risk_df.empty:
       fig = go.Figure()
       fig.update_layout(
            title_text='Total Risk by Load Country',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )

    else:
        fig = go.Figure(data=[
        go.Bar(name='Energy Risk [Mtoe]', x=total_risk_df['Country'], y=total_risk_df['Energy Risk [Mtoe]']),
        go.Bar(name='Intake [Mtons]', x=total_risk_df['Country'], y=total_risk_df['Intake [Mtoe]'])
        ])
        # Change the bar mode
        fig.update_layout(
            barmode='group',
            title='Total Risk by Load Country',
            width = 1100,
            height = 750,
            font=dict(
                size=18,
                ),
            )
            

    return fig

def piechart_risk_country_oil(total_risk_df):
    if total_risk_df.empty:
       piechart = go.Figure()
       piechart.update_layout(
            title_text='Shares of Risk by Load Country',
            width=950,
            height=600,
            xaxis =  { "visible": False },
            yaxis = { "visible": False },
            annotations = [
                {   
                    "text": "Not Data for the selected Date. Please Select Another",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {
                        "size": 28
                    }
                }
            ]
        )
    else:
        top_ten = total_risk_df.nlargest(10, 'Energy Risk [Mtoe]')
        piechart = go.Figure([go.Pie(labels=top_ten['Country'], values=top_ten['Share Risk [%]'],
                        name='test',
                        textinfo='label+percent',
                        insidetextorientation='radial'
                       )])

        piechart.update_layout(
                        title='Shares of Risk by Load Country',
                        width = 1100,
                        height = 750,
                        font=dict(
                            size=18,
                            ),
                        )
    
    return piechart