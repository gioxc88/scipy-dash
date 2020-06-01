import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True)
# server = app.server  # the Flask app
#napp.config['suppress_callback_exceptions'] = True

text = doc.get_doc('norm')

app.layout = html.Div(
    children=[
        html.Iframe(src='https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html')
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)


dist.
dist.mean()
dist.std()
def skewness(dist):
    try:
        result = dist.moment(3) / dist.std() ** 3
    except:
        return np.nan

def kurtosis(dist):
    try:
        result = dist.moment(4) / dist.std() ** 4
    except:
        result = np.nan
    return result
