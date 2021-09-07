import dash_html_components as html
import dash_bootstrap_components as dbc 
import dash_core_components as dcc

# set up components
# buttons
start_button = html.Div(
    [
        dbc.Button(
            "Start the analysis!", id="start_button",
            className="mr-2", n_clicks=0, color='info'
        ),
        html.Span(id="example-output", style={"verticalAlign": "middle"}, children='fix the start button'),
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