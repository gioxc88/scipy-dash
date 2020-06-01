import dash
import dash_bootstrap_components as dbc

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True)
# server = app.server  # the Flask app
#napp.config['suppress_callback_exceptions'] = True

from . import layouts

app.layout = layouts.layout

from . import callbacks