import os
from textwrap import dedent
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dash import no_update
from dash.dependencies import Input, Output, State
import plotly.express as px
import openai


def Header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("dash-logo.png"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


# Load data
df = pd.read_csv('wait_times.csv', low_memory=False)
df['datetime']=pd.to_datetime(df['datetime'])
#df = px.data.gapminder()

# Authentication
openai.api_key = os.getenv("OPENAI_KEY")


# Define the prompt
prompt = """
Our dataframe "df" only contains the following columns: country, continent, year, life expectancy (lifeExp), population (pop), GDP per capita (gdpPercap), the ISO alpha, the ISO numerical.

**Description**: The life expectancy in Oceania countries throughout the years.

**Code**: ```px.line(df.query("continent == 'Oceania'"), x='year', y='lifeExp', color='country', log_y=False, log_x=False)```


**Description**: The GDP per capita in India throughout the years.

**Code**: ```px.line(df.query("continent == 'Asia'" and "country=='India'"), x='year', y='lifeExp', color='country', log_y=False, log_x=False)```
"""


prompt="""
Our dataframe "df" only contains the following columns: the datetime, the wait time for the dinosaur ride (wait_dinosaur), the park for the dinosaur ride (park_dinosaur), the date (DATE), the wait time for the Expedition Everest ride (wait_expedition_everest), the park for the expedition everest ride (park_expedition_everest), the day of the week (DAYOFWEEK) where sunday=1, the day of the year (DAYOFYEAR) where 1/1 = 1 and 12/31 = 365, the week of the year (WEEK), the month of the year (MONTH) where January = 1, the year (YEAR), the season (SEASON) which can be ['CHRISTMAS PEAK'  'CHRISTMAS' 'WINTER' 'MARTIN LUTHER KING JUNIOR DAY' 'PRESIDENTS WEEK' 'SPRING' 'EASTER' 'MEMORIAL DAY' 'SUMMER BREAK' 'JULY 4TH' 'SEPTEMBER LOW' 'FALL' 'COLUMBUS DAY' 'HALLOWEEN' 'JERSEY WEEK' 'THANKSGIVING' 'MARDI GRAS'], and the day of the month (DAYOFMONTH).


**Description**: What is the average wait time for the dino ride in June of 2018

**Code**: ```px.scatter(x=[0],y=[df[(df['YEAR']==2018)&(df['MONTH']==6)]['wait_dinosaur'].mean(), size=6])```


**Description**: Plot the wait time for saturdays in may for the everest ride

**Code**: ```px.scatter(df[(df['DAYOFWEEK']==7) & (df['MONTH']==5)],x='datetime',y='wait_expedition_everest',size=6)```


**Description**: Plot the wait time for the dino ride on January 1st from 15 - 18:20pm over time

**Code**: ```px.scatter(df[(df['DAYOFYEAR']==1) & (df['datetime'].dt.hour>=15) &  (df['datetime'].dt.hour<=18) & (df['datetime'].dt.minute<=20)], x='datetime',y='wait_dinosaur',)```

"""

# Create
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

content_style = {"height": "475px"}

chat_input = dbc.InputGroup(
    [
        dbc.Input(
            id="input-text", placeholder="Tell GPT-3 what you want to generate..."
        ),
        dbc.InputGroupAddon(
            dbc.Button("Submit", id="button-submit", color="primary"),
            addon_type="append",
        ),
    ]
)
output_graph = [
    dbc.CardHeader("Plotly Express Graph"),
    dbc.CardBody(dbc.Spinner(dcc.Graph(id="output-graph", style={"height": "425px"}))),
]
output_code = [
    dbc.CardHeader("GPT-3 Conversation Interface"),
    dbc.CardBody(
        dbc.Spinner(dcc.Markdown("", id="conversation-interface")),
        style={"height": "725px"},
    ),
]

explanation = f"""
*GPT-3 can generate Plotly graphs from a simple description of what you want, and it
can even modify what you have previously generated!
Here we load a dataset of wait times for rides at Disney and give the following prompt to GPT-3:*

{prompt}
"""
explanation_card = [
    dbc.CardHeader("What am I looking at?"),
    dbc.CardBody(dcc.Markdown(explanation)),
]

left_col = [dbc.Card(output_graph), html.Br(), dbc.Card(explanation_card)]

right_col = [dbc.Card(output_code), html.Br(), chat_input]

app.layout = dbc.Container(
    [
        Header("Dash GPT-3 Line Charts Update", app),
        html.Hr(),
        dbc.Row([dbc.Col(left_col, md=7), dbc.Col(right_col, md=5)]),
    ],
    fluid=True,
)


@app.callback(
    [
        Output("output-graph", "figure"),
        Output("conversation-interface", "children"),
        Output("input-text", "value"),
    ],
    [Input("button-submit", "n_clicks"), Input("input-text", "n_submit")],
    [State("input-text", "value"), State("conversation-interface", "children")],
)
def generate_graph(n_clicks, n_submit, text, conversation):
    if n_clicks is None and n_submit is None:
        default_fig = px.line(
            df[(df['YEAR']>=2018) & (df['MONTH']==6)],
            x="datetime",
            y="wait_dinosaur",
            log_y=False,
            log_x=False,
        )
        return default_fig, dash.no_update, dash.no_update

    conversation += dedent(
        f"""
    **Description**: {text}

    **Code**:"""
    )

    #print('Prompt',prompt)
    #print('Conversation',conversation)
    gpt_input = (prompt + conversation).replace("```", "").replace("**", "")
    print('gpt_input',gpt_input)
    print("-" * 40)

    response = openai.Completion.create(
        engine="davinci",
        prompt=gpt_input,
        max_tokens=200,
        stop=["Description:", "Code:"],
        temperature=0,
        top_p=1,
        n=3,
    )

    output = response.choices[0].text.strip()

    conversation += f" ```{output}```\n"

    #print('output',output)
    #print('conversation',conversation)
    #print('-'*60)

    try:
        fig = eval(output)
    except Exception as e:
        fig = px.line(title=f"Exception: {e}. Please try again!")

    return fig, conversation, ""


if __name__ == "__main__":
    app.run_server(debug=True)
