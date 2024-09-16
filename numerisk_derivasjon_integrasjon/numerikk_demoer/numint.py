import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widget
from IPython.display import display 


def make_stem_segments(n, xn):
    """
    Create list of line segments from x and y coordinates, in the correct format
    for LineCollection: an array of the form numlines x (points per line) x 2 (x
    and y) array
    """

    points = np.array([n, xn]).T.reshape(-1, 1, 2)
    start_points = np.array([n, np.zeros(len(n))]).T.reshape(-1, 1, 2)

    segments = np.concatenate([start_points, points], axis=1)
    return segments


def get_vertices(x, y):
    """
    Convert regular plot coordinates (x, y) to vertices of a polygon
    """
    verts = np.array([x, y]).T.reshape(-1, 2)
    verts = np.vstack(([[x[0], 0]], verts, [[x[-1], 0]]))
    return verts


class NumIntDemo:
    """
    Generates an interactive plot showing the mechanismis of numerical integration.

    Parameters
    ------------
    func: callable
        Function or lambda function representing a one-dimensional mathematical 
        function y = f(x).

    xlim: tuple
        x axis range. Interactive demo will be confined to the numerical range
        xlim[0] <= x <= xlim[1]

    fig_num: int, optional
        Figure number. If specified, closes any active figure before opening new
        figure

    figsize: tuple, optional
        Dimensions of the interactive figure

    Example
    ------------
    Illustrate numerical differentiation of the function f(x) = x^3-2*x^2 +1 for x-values
    0 <= x <= 2.

    >>> def f(x):
    >>>     y = x**3 - 2*x**2 + 1
    >>>     return y

    >>> NumIntDemo(f, xlim = (0, 2) , fig_num = 1, figsize = (8, 6))

    """
    def __init__(self, func: callable, xlim: tuple , fig_num: int = None, figsize: tuple = (8,6)):
        plt.close(fig_num)
        # Static member variables
        self.fig = plt.figure(fig_num, figsize=figsize)
        self.res = 201
        self.f = func
        self.x_vals = np.linspace(xlim[0], xlim[1], self.res)

        # Dynamic member variables
        self.method = "trapezoidal"
        self.N = 7 # Antall delintervall
        self.h = (xlim[1]-xlim[0])/self.N
        self.x_n = np.linspace(xlim[0], xlim[1], self.N+1)
        self.x_m = np.linspace(xlim[0], xlim[1], self.N+1)

        # Set up initial plots
        ax1 = plt.subplot(1,1,1)
        ax1.plot(self.x_vals, self.f(self.x_vals), label="$f(x)$")
        self.y_range = ax1.get_ylim()
        ax1.set_xlabel(r"$x$")
        ax1.set_ylabel(r"$y=f(x)$")
        ax1.grid(True)
        ax1.set_xlim([xlim[0], xlim[-1]])

        self.borders = ax1.stem(self.x_n, # 
                                    self.f(self.x_n), # Nullsampler
                                    linefmt='C1--', # Linjestil stolper
                                    markerfmt='oC3', # Punktstil for stem-markere. Default er 'o' (stor prikk)
                                    basefmt='black' # Farge på y=0 aksen
                                    )
        self.borders.baseline.set_linewidth(0.5)
        self.borders.markerline.set_markersize(0)

        self.points, = ax1.plot(self.x_m, 
                                self.f(self.x_m),
                                'C1o',
                                linewidth=0.0, 
                                markersize=6, 
                               label = r"$f(a + m \cdot h)$")

        self.approx_curve, = ax1.plot(self.x_vals,
                                      self.f_approx_trapezoidal(), 
                                      'C1')
        self.approx_area = ax1.fill_between(self.x_vals,
                                            self.approx_curve.get_ydata(), 
                                            color='C1', 
                                            alpha=0.2, 
                                            label=r"$\approx \int_{a}^{b}f(x)dx$")
        ax1.legend()
        self.ax1 = ax1
        self.fig.tight_layout()

        # Set up widget panel
        N_input = widget.BoundedIntText(value=self.N,
                                          min=1,
                                          max=20,
                                          step=1,
                                          description=r'N',
                                          disabled=False,
                                          style = {'description_width': 'initial'},
                                          layout=widget.Layout(width='30%'),
                                          continuous_update=True
                                          )
        
        method_input = widget.Dropdown(options=['trapezoidal', "simpson's"],
                                       value='trapezoidal',
                                       description='Integration Method:',
                                       style = {'description_width': 'initial'},
                                       layout=widget.Layout(width='30%'),
                                       disabled=False
                                       )

        self.layout = widget.HBox([N_input, method_input])
        N_input.observe(self.on_N_change, names="value")
        method_input.observe(self.update_method, names="value")
        out = widget.Output()
        display(self.layout, out)

    def update_method(self, change):
        self.method = change["new"]
        self.update_integration()

    def on_N_change(self, inputChange):
        self.N = inputChange["new"]
        self.x_n = np.linspace(self.x_vals[0], self.x_vals[-1], self.N+1)
        self.update_integration()

    def update_integration(self):
        if self.method == "trapezoidal":
            self.x_m = self.x_m = np.linspace(self.x_vals[0], self.x_vals[-1], self.N+1)
            self.h = (self.x_vals[-1] - self.x_vals[0])/self.N
        elif self.method == "simpson's":
            self.x_m = self.x_m = np.linspace(self.x_vals[0], self.x_vals[-1], self.N*2+1)
            self.h = (self.x_vals[-1] - self.x_vals[0])/(2*self.N)
        else:
            raise Exception("Unrecognized integration method!")
        self.update_points()
        self.update_borders()
        self.update_polygon()
        
    def f_approx_trapezoidal(self):
        y = np.zeros(self.res)
        fx_n = self.points.get_ydata()
        stop = 0
        
        for i in range(self.N):
            start = stop
            stop=np.searchsorted(self.x_vals, self.x_m[i+1])
            f_a = fx_n[i]
            f_b = fx_n[i+1]
            a = (f_b - f_a)/self.h
            b = f_a - a*self.x_m[i]
            y[start:stop] = a*self.x_vals[start:stop]+b

        y[-1] = self.f(self.x_vals[-1])
        return y
        
    def f_approx_simpson(self):
        y = np.zeros(self.res)
        fx_m = self.points.get_ydata()
        stop = 0
        
        for i in range(self.N):
            x_i = self.x_m[i*2:i*2+3]
            M = np.array([[x_i[0]**2, x_i[0], 1],
                          [x_i[1]**2, x_i[1], 1],
                          [x_i[2]**2, x_i[2], 1]])
            (A, B, C) = np.linalg.solve(M, fx_m[i*2:i*2+3])
            
            start = stop
            stop = np.searchsorted(self.x_vals, self.x_n[i+1])

            y[start:stop] = A*self.x_vals[start:stop]**2+B*self.x_vals[start:stop] + C

        y[-1] = self.f(self.x_vals[-1])
        return y
        
    def update_points(self):
        self.points.set_xdata(self.x_m)
        self.points.set_ydata(self.f(self.x_m))
        
    def update_borders(self):
        y_n = self.f(self.x_n)
        segments = make_stem_segments(self.x_n, y_n)
        self.borders.stemlines.set_segments(segments)
        self.borders.markerline.set_xdata(self.x_n)
        self.borders.markerline.set_ydata(y_n)
        self.borders.baseline.set_xdata([self.x_vals[0], self.x_vals[-1]])
        self.borders.baseline.set_ydata([0, 0])

    def update_polygon(self):
        if self.method == "trapezoidal":
            y = self.f_approx_trapezoidal()
        elif self.method == "simpson's":
            y = self.f_approx_simpson()
        else:
            raise Exception("unrecognized integration method")
        self.approx_curve.set_ydata(y)
        verts = get_vertices(self.x_vals, y)
        self.approx_area.set_verts([verts])
