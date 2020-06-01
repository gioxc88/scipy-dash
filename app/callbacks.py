import inspect

import dash
import dash_table
import numpy as np
import plotly.io as pio
import plotly.graph_objects as go

from dash.dependencies import Input, Output, State, MATCH, ALL
from dash_wrapper import dash_core_components as dcc
from dash_wrapper import dash_html_components as html
from dash_wrapper import dash_bootstrap_components as dbc

from scipy import stats

from . import app
from . import utils
from . import config


def get_params_list(dist):
    params = ['loc', 'scale']
    if isinstance(dist, str):
        dist = getattr(stats, dist)
    if isinstance(dist, stats.rv_continuous):
        if dist.shapes:
            more_params = [param.strip() for param in dist.shapes.split(',')]
            params.extend(more_params)
    return params


@app.callback(Output('more_params', 'children'),
              [Input({'name': 'dist', 'type': 'input'}, 'value')])
def update_params_list(dist):
    if dist is None:
        return
    params_name = get_params_list(dist)

    form = []

    for i, name in enumerate(params_name):
        addon = dbc.InputGroupAddon(name, addon_type="prepend")
        label = dbc.Label(name, width=2)
        input_ = dbc.Input(id={'name': name, 'type': 'input'}, type='number',
                           debounce=True)

        input_.value = None
        if name == 'scale':
            input_.min = 0

        elements = [label, dbc.Col(input_, width=8)]
        pair = dbc.FormGroup(elements, row=True)
        form.append(pair)

        # pair = dbc.InputGroup(elements, className="mb-1")
        # elements = [addon, input_]
        # form.append(dbc.Col(pair, width=11))

    form.append(dbc.FormText('fill the form and press enter to show the plot', color="secondary"))

    return html.Div(form)


@app.callback(Output('doc_frame', 'src'),
              [Input({'name': 'dist', 'type': 'input'}, 'value')])
def update_doc(dist):
    if dist is None:
        return 'about:blank'
    return f'{config.scipy_url}{dist}.html#scipy-stats-{dist}'


@app.callback(Output('doc_frame', 'hidden'),
              [Input({'name': 'dist', 'type': 'input'}, 'value')])
def show_frame(dist):
    return False


@app.callback(Output('plot', 'children'),
              [Input('hidden_pdf', 'children'),
               Input('hidden_cdf', 'children'),
               Input('switch', 'value')],
              prevent_initial_call=True)
def update_visible_plot(hidden_pdf, hidden_cdf, switch):
    if switch:
        return hidden_cdf
    else:
        return hidden_pdf


@app.callback(Output('hidden_pdf', 'children'),
              [Input({'type': 'input', 'name': ALL}, 'value'),
               Input('left_slider', 'value'),
               Input('right_slider', 'value'),
               Input('submit', 'n_clicks')],
              [State('hidden_pdf', 'children')],
              prevent_initial_call=True)
def update_hidden_pdf_plot(*args):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    args, lower_tail, upper_tail, n_clicks, children = args

    if not args or (len(args) == 1):
        # exit because argument list is empty or only the distribution has been passed
        return children

    if len(args) > 1 and (args[0] is None):
        return

    trigger_mask = trigger == 'submit'
    arg_maks = all([arg is not None for arg in args])

    if not (trigger_mask or arg_maks):
        # exit because either not all arguments have been filled or didnt press submit
        return children

    dist = getattr(stats, args[0])
    params_name = get_params_list(dist)
    if len(args[1:]) != len(params_name):
        return children

    params = {key: value for key, value in zip(params_name, args[1:])}
    if params['scale'] == 0:
        return


    lower_bound, upper_bound = dist.ppf([lower_tail, upper_tail], **params)

    x = np.linspace(lower_bound, upper_bound, 1000).round(4)
    y = dist.pdf(x, **params).round(4)

    layout = go.Layout(template='plotly_white',
                       title=dict(text='Probability density function', x=0.5, xanchor='center'))

    name = ', '.join([f'{key}: {value}' for key, value in params.items()])
    name = f'{dist.name}, {name}'

    trace = go.Scatter(x=x, y=y, name=name)

    if children is not None:
        figure = children['props']['figure']
        figure = go.Figure(figure)
        figure.add_trace(trace)

    else:
        figure = go.Figure(data=[trace], layout=layout)

    return dcc.Graph(figure=figure)


@app.callback([Output('hidden_cdf', 'children'),
               Output('table-col', 'children')],
              [Input({'type': 'input', 'name': ALL}, 'value'),
               Input('left_slider', 'value'),
               Input('right_slider', 'value'),
               Input('submit', 'n_clicks')],
              [State('hidden_cdf', 'children'),
               State('table-col', 'children')],
              prevent_initial_call=True)
def update_hidden_cdf_plot(*args):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    args, lower_tail, upper_tail, n_clicks, children, table_children = args

    if not args or (len(args) == 1):
        # exit because argument list is empty or only the distribution has been passed
        return children, table_children

    if len(args) > 1 and (args[0] is None):
        return None, None

    trigger_mask = trigger == 'submit'
    arg_maks = all([arg is not None for arg in args])

    if not (trigger_mask or arg_maks):
        # exit because either not all arguments have been filled or didnt press submit
        return children, table_children

    dist = getattr(stats, args[0])
    params_name = get_params_list(dist)
    if len(args[1:]) != len(params_name):
        return children, table_children

    params = {key: value for key, value in zip(params_name, args[1:])}
    if params['scale'] == 0:
        return None, None

    lower_bound, upper_bound = dist.ppf([lower_tail, upper_tail], **params)
    columns = ['name', 'mean', 'std', 'variance', 'skewness', 'kurtosis']

    name = ', '.join([f'{key}: {value}' for key, value in params.items()])
    name = f'{dist.name}, {name}'

    data = utils.dist_summary(dist(**params), name)

    data[1:] = data[1:].astype('float').round(2)
    data = data.to_dict()
    if table_children is None:
        table = dash_table.DataTable(columns=[{'name': col, 'id': col} for col in columns],
                                     data=[data])
    else:
        table_children = dash_table.DataTable(**table_children['props'])
        table_children.data.append(data)
        table = table_children

    x = np.linspace(lower_bound, upper_bound, 1000).round(4)
    y = dist.cdf(x, **params).round(4)

    layout = go.Layout(template='plotly_white',
                       title=dict(text='Cumulative distribution function', x=0.5, xanchor='center'))

    trace = go.Scatter(x=x, y=y, name=name)

    if children is not None:
        figure = children['props']['figure']
        figure = go.Figure(figure)
        figure.add_trace(trace)

    else:
        figure = go.Figure(data=[trace], layout=layout)

    return dcc.Graph(figure=figure), table


@app.callback(Output('switch', 'style'),
              [Input('plot', 'children')])
def show_switch(plot):
    if plot is None:
        return {'display': 'none'}
    else:
        return {}
