import numpy as np
import plotly.graph_objects as go
import math
import sympy


def parse_polynomial(expr: str):
    """ Gets coefficients of the polynomial from symbolic expression.
    Args:
        expr: symbolic expression for the polynomial. e.g. 'x^3 + 2*x**2 - 2*x + 1' or '(x + 3)*(x^2 - x + 1)'
    Returns:
        coeffs: 1D numpy array of coefficients of the polynomial in decreasing powers
    """

    poly = sympy.polys.polytools.poly_from_expr(expr)[0]
    size = poly.degree() + 1
    coeffs = np.zeros(size)
    x = sympy.symbols('x')

    for c in poly.coeffs():
        coeffs[size - poly.degree() - 1] = c
        poly = poly - c*x**poly.degree()

    return coeffs

def transfer_function(num, denom):
    """Simple transfer function
    Args:
      num: coefficients of the zeros [coeff_n, coeff_(n-1), ..., coeff_0]
      denom: coefficients of the poles: [coeff_n, coeff_(n-1), ..., coeff_0]
    Returns:
      tf: 2D numpy array [num, denom]
    """
    num = np.poly1d(num)
    denom = np.poly1d(denom)
    tf = np.array((num, denom))
    return tf


def compute_roots(tf, gains):
    """Computes the roots of the characteristic equation of the closed-loop system
    of a given transfer function for a list of gain parameters.
    Concretely, given TF = zeros/poles, and a gain value K, we solve for the
    characteristic equation roots, that is the roots of poles + (K * zeros).
    To avoid change in the order of the characteristic equation K must be different
    from zero when Order(zeros) > Order(poles).
    Args:
    tf: transfer function.
    gains: list of gains.
    Returns:
    roots: numpy array containing the roots for each gain in gains.
    """
    num, denom = tf[0], tf[1]
    # num_roots = len(np.roots(denom))
    roots = []

    for gain in gains:
        if gain == 0:
            # ensure order of the characteristic equation doesn't change
            # gain = np.nextafter(np.float32(0), np.float32(1))
            gain = 0.001
        ch_eq = denom + gain*num
        ch_roots = np.roots(ch_eq)
        # ch_roots.sort()
        roots.append(ch_roots)

    # convert final roots list into array
    roots = np.vstack(roots)

    return roots


def root_locus(tf, gains, **kwargs):
    num, denom = tf[0], tf[1]
    zeros = np.roots(num)
    poles = np.roots(denom)


    # number of asymptotes
    k = len(poles) - len(zeros)
    # origin of asymptotes
    s = 0
    if k != 0:
        s = (np.sum(poles) - np.sum(zeros)) / k
    # angle of asymptotes
    k = np.abs(k)
    asymptote_angle = [180*(2*i + 1)/k for i in range(k)]

    roots = compute_roots(tf, gains)

    fig = go.Figure()
    # plot roots
    real_values = np.real(roots)
    imag_values = np.imag(roots)

    for r, i in zip(real_values.T, imag_values.T):
        fig.add_trace(go.Scatter(x=r, y=i, mode='lines+markers'))

    fig.update_traces(hovertext=gains, hoverinfo='text')

    # plot asymptotes
    s_r = np.real(s)
    s_i = np.imag(s)
    M = 100
    for alpha in asymptote_angle:
        tr_r = s_r + round(M*math.cos(math.pi*alpha/180))
        tr_i = s_i + round(M*math.sin(math.pi*alpha/180))

        fig.add_trace(go.Scatter(x=[s_r, tr_r], y=[s_i, tr_i], mode='lines',
                                 line=dict(color='grey', width=1, dash='dash'),
                                 name='{}° asymptote line'.format(alpha)))

    # plot zeros and poles
    fig.add_trace(go.Scatter(x=np.real(zeros), y=np.imag(zeros), mode='markers',
                             marker=dict(symbol='circle-open', size=12, color='cyan'),
                             name='zeros'))
    fig.add_trace(go.Scatter(x=np.real(poles), y=np.imag(poles), mode='markers',
                             marker=dict(symbol='x-thin-open', size=12, color='red'),
                             name='poles'))

    x = sympy.symbols('x')
    k = sympy.symbols('k', constant=True)

    title = sympy.Poly(denom, x) + k*sympy.Poly(num, x)
    fig.update_layout(title='Root locus for characteristic equ: {}'.format(title))

    # adjust view boundaries
    x_low = kwargs.pop('x_low', -10)
    y_low = kwargs.pop('y_low', -10)
    x_up = kwargs.pop('x_up', 10)
    y_up = kwargs.pop('y_up', 10)
    fig.update_layout(xaxis=dict(range=[x_low, x_up], title='Real'),
                      yaxis=dict(range=[y_low, y_up], title='Imaginary'))
    return fig


if __name__ == "__main__":
    # open loop transfer function
    num = parse_polynomial('(x^2 + 2)*(x)')
    denom = parse_polynomial('x**3 - 2 + 3*x')
    GH = transfer_function(num, denom)

    # create a list of evenly spaced gains
    gains = np.linspace(0.0, 100.0, num=1000)
    fig = root_locus(GH, gains)
    fig.write_html('tmp.html', auto_open=True)
