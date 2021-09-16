import dash_html_components as html
import dash_bootstrap_components as dbc 
import dash_core_components as dcc

# set up components
# buttons
start_button = html.Div(
    [
        dbc.Button(
            "Start the analysis!", id="start_button",
            className="m-2", n_clicks=0, color='info'
        ),
    ]
)


# empty graph
no_fig = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "Data will be displayed after the analysis",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 28
                }
            }
        ]
    }
}

# your idea message
your_fig = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "annotations": [
            {
                "text": "Here is room for more. <br>What data would you be interested in?",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 28
                }
            }
        ]
    }
}

description =  dbc.CardBody([
    html.Div('Find the perfect spot for generating solar power',style={'font-weight': 'bold'}),
    html.Div('''
    Welcome! You can use this site to analyse different 
    locations and find out, if they are suited for generating solar power. 
    This site will show you the optimal spots for high energy output or a maximum
    return on your investment.
    '''),
    html.Div('Get your personalized analysis',style={'font-weight': 'bold'}),
    html.Div('''
    Input your info and you will receive an analysis report tailored to your needs.
    '''),
    html.Div('About the inputs',style={'font-weight': 'bold'}),
    html.Div('''
    You can input three different types of information for now. The first one
    is the location you are interested in. This works with cities, regions or even 
    whole countries. The second one is the resolution of the map. Lower resolution are a 
    lot quicker but you can choose a higher resolution if you are interested in detailed
    data. The last input is the household size. Different household sizes lead to different 
    electricity needs. This will be taken into account for the analysis.
    '''),
    html.Div('''
    Check out the source code here: https://github.com/SoenkeMaibach/Solaranlagen
    '''),
])
        