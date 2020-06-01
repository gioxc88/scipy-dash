from scipy import stats

# from dash_wrapper.dash_custom_components import Row, Col
from dash_wrapper import dash_html_components as html
from dash_wrapper import dash_core_components as dcc
from dash_wrapper import dash_bootstrap_components as dbc
from dash_wrapper import dash_daq as daq
from dash_wrapper.dash_bootstrap_components import Row, Col

from plotly import graph_objects as go

from . import app
from . import config

drop_down_options = [{'label': d, 'value': d} for d in dir(stats) if isinstance(getattr(stats, d), stats.rv_continuous)]
dropdown = dcc.Dropdown(id={'name': 'dist', 'type': 'input'},
                        options=drop_down_options,
                        placeholder='select a distribution',
                        className='mt-3')
dropdown_form = dbc.FormGroup([dropdown, dbc.FormText('click x to clear', color="secondary")])

lower = (
        dbc.FormGroup(row=True) *
            dbc.Label("left tail", className='mr-2') @
            dbc.Col() *
                dcc.Slider(id='left_slider', value=0.005,
                           min=0.001, max=0.1, step=0.001,
                           tooltip={'always_visible': False, 'placement': 'bottom'})
)

upper = (
        dbc.FormGroup(row=True) *
        dbc.Label("right tail", className='mr-1') @
        dbc.Col() *
            dcc.Slider(id='right_slider', value=0.995,
                       min=0.9, max=0.999, step=0.001,
                       tooltip={'always_visible': False, 'placement': 'bottom'})
)

layout = \
    (
        html.Div(className='container') *
            Row(id='logo') *
                html.H1('Scipy Dash') /
            Row() *
                html.H5('by gioxc88') @
                html.A(href=config.linkedin_url, target="_blank") *
                    html.Img(src=app.get_asset_url(str(config.linkedin_png.relative_to(config.assets_path))),
                             className='img-responsive ml-3',
                             height=20) /
                html.A(href=config.github_url, target="_blank") *
                    html.Img(src=app.get_asset_url(str(config.github_png.relative_to(config.assets_path))),
                             className='img-responsive ml-3',
                             height=20) %
            Row() *
                Col(id='params', width=3) *
                    dropdown_form @
                    lower @
                    upper @
                    html.Div(id='more_params', className="mt-1") @
                    dbc.Button("Plot", id='submit', color="primary", className="mt-3", style={'display': 'none'}) @
                    html.A(href='', target="_blank") /
                Col(id='doc_col', width=dict(size=7,  offset=2)) *
                    html.Div(className='embed-responsive embed-responsive-16by9') *
                        html.Iframe(id='doc_frame', src='about:blank', className='embed-responsive-item', hidden=True) %
            Row(className="mt-3", justify='start') *
                Col(width=dict(size=1, offset=1)) *
                    daq.ToggleSwitch(id='switch',
                        label='PDF / CDF',
                        labelPosition='bottom',
                        style={'display': 'none'},
                        className='mt-2') %
            Row() *
                Col(id='plot-col') *
                    html.Div(id='plot') %
            Row(className="mb-2", justify="center") *
                Col(id='table-col', width=8) %

            html.Div(id='hidden_pdf', style={'display': 'none'}) @
            html.Div(id='hidden_cdf', style={'display': 'none'})
    )
