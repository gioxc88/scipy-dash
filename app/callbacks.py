import ast
import inspect

from functools import partial

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
              [Input('dist', 'value')])
def update_params_list(dist):
    if dist is None:
        return
    params_name = get_params_list(dist)

    form = []

    for i, name in enumerate(params_name):
        addon = dbc.InputGroupAddon(name, addon_type="prepend")
        label = dbc.Label(name, width=2)
        input_ = dbc.Input(id={'name': name, 'type': 'param'}, type='number',
                           debounce=True, key=f'{dist}-{name}')

        input_.value = None
        if name == 'scale':
            input_.min = 0

        # elements = [label, dbc.Col(input_, width=8)]
        # pair = dbc.FormGroup(elements, row=True)
        # form.append(pair)

        elements = [addon, input_]
        pair = dbc.InputGroup(elements, className="mb-2")
        form.append(dbc.Col(pair, width=11))

    form.append(dbc.FormText('fill the form and press enter to show the plot', color="secondary"))

    return html.Div(form)


@app.callback(Output('doc_frame', 'src'),
              [Input('dist', 'value')])
def update_doc(dist):
    if dist is None:
        return 'about:blank'
    return f'{config.scipy_url}{dist}.html#scipy-stats-{dist}'


@app.callback(Output('doc_frame', 'hidden'),
              [Input('dist', 'value')])
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
              [Input({'type': 'param', 'name': ALL}, 'value')],
              [State('dist', 'value'),
               State('left_slider', 'value'),
               State('right_slider', 'value'),
               State('hidden_pdf', 'children')],
              prevent_initial_call=True)
def update_hidden_pdf_plot(*args):
    ctx = dash.callback_context
    return update_plot(ctx, 'pdf', *args)


@app.callback(Output('hidden_cdf', 'children'),
              [Input({'type': 'param', 'name': ALL}, 'value')],
              [State('dist', 'value'),
               State('left_slider', 'value'),
               State('right_slider', 'value'),
               State('hidden_cdf', 'children')],
              prevent_initial_call=True)
def update_hidden_cdf_plot(*args):
    ctx = dash.callback_context
    return update_plot(ctx, 'cdf', *args)


@app.callback(Output('switch', 'style'),
              [Input('plot', 'children')])
def show_switch(plot):
    if plot is None:
        return {'display': 'none'}
    else:
        return {}


def update_plot(context, fun, *args):
    params, dist, lower_tail, upper_tail, children = args

    result = proceed(context, dist, params, children)
    if isinstance(result, tuple) and isinstance(result[0], stats._distn_infrastructure.rv_frozen):
        dist, name = result
    else:
        return result

    lower_bound, upper_bound = dist.ppf([lower_tail, upper_tail])

    x = np.linspace(lower_bound, upper_bound, 1000).round(4)
    y = getattr(dist, fun)(x).round(4)

    title = 'Probability density function' if fun == 'pdf' else 'Cumulative distribution function'
    layout = go.Layout(template='plotly_white',
                       title=dict(text=title, x=0.5, xanchor='center'))

    trace = go.Scatter(x=x, y=y, name=name)

    if children is not None:
        figure = children['props']['figure']
        figure = go.Figure(figure)
        figure.add_trace(trace)

    else:
        figure = go.Figure(data=[trace], layout=layout)

    return dcc.Graph(figure=figure)


@app.callback(Output('table-col', 'children'),
              [Input({'type': 'param', 'name': ALL}, 'value')],
              [State('dist', 'value'),
               State('table-col', 'children')],
              prevent_initial_call=True)
def update_table(*args):
    ctx = dash.callback_context
    params, dist, children = args

    result = proceed(ctx, dist, params, children)
    if isinstance(result, tuple) and isinstance(result[0], stats._distn_infrastructure.rv_frozen):
        dist, name = result
    else:
        return result

    data = utils.dist_summary(dist, name)
    data[1:] = data[1:].astype('float').round(4)

    if children is None:
        table = dash_table.DataTable(columns=[{'name': col, 'id': col} for col in data.index],
                                     data=[data.to_dict()])
    else:
        table = dash_table.DataTable(**children['props'])
        table.data.append(data.to_dict())

    return table


def proceed(context, dist, params, children):
    params_name = [ast.literal_eval(key.split('.')[0]).get('name') for key in context.inputs if key.startswith('{')]

    if not dist:
        return

    params_maks = all([param is not None for param in params])
    if not params_maks or not params:
        # exit because not all parameters have been filled or parameter is empty list
        return children

    params_dict = {key: value for key, value in zip(params_name, params)}
    dist = getattr(stats, dist)(**params_dict)

    name = ', '.join([f'{key}: {value}' for key, value in params_dict.items()])
    name = f'{dist.dist.name}, {name}'

    if params_dict['scale'] == 0:
        return

    return dist, name
