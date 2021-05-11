import pandas as pd
import plotly.graph_objects as go
from stories.models import Corridor, CorridorIntake 
from django.db.models import Q

#World Thematic Map
country_code_dict = {
    'Aruba':'ABW',
    'Afghanistan':'AFG',
    'Angola':'AGO',
    'Anguilla':'AIA',
    'Åland Islands':'ALA',
    'Albania':'ALB',
    'Andorra':'AND  ',
    'United Arab Emirates':'ARE',
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
    'United Kingdom':'GBR',
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
    'United States of America':'USA',
    'USA':'USA',
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

def world_choropleth_map_intake (year):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))


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
        df_intake.columns = ['corridor_id', 'intake', 'date']
        df = pd.merge(df_corridor,df_intake,on=['corridor_id'],how="outer",indicator=True)
        df =df.drop(['corridor_id'], axis = 1)
        df = df.groupby(['load_country']).sum().reset_index()
        df = df[df['intake']> 0] # filter values that are more than zero

        df['code'] = df['load_country'].map(country_code_dict,'ignore')
        fig = go.Figure(data=go.Choropleth(
            locations = df['code'],
            z = df['intake'],
            text = df['load_country'],
            colorscale = 'Blues',
            autocolorscale=False,
            reversescale=True,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '',
            colorbar_title = 'Crude Intake (Tons)',
        ))

        fig.update_layout(
            title_text='Crude Intake by Country',
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
        print(intake.head(50))
        df =  pd.merge(intake,lvh,on=['commodity_id'],how="inner",indicator=True)
        print(df.head(50))
        df = df.groupby(['name']).sum().reset_index()
        print(df.head(10))
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


def horizontal_bar_intake(year):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','load_country'))
    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

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

def piechart_intake(year):
    df_corridor = pd.DataFrame.from_records(Corridor.objects.all().values('corridor_id','discharge_port'))
    df_intake =   pd.DataFrame.from_records(
        CorridorIntake.objects.filter(Q(date__year=year), Q(commodity=66)| Q(commodity=54)|Q(commodity=22)|Q(commodity=77)).values('corridor','intake','date'))

    if df_intake.empty:
       fig = go.Figure()
       fig.update_layout(
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