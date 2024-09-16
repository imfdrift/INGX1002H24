import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import HBox, VBox, Layout
import ipywidgets as widget

class NumDiffDemo:
    """
    Generates an interactive plot showing the mechanismis of numerical
    differentiation. 
    
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
    
    >>> NumDiffDemo(f, xlim = (0, 2) , fig_num = 1, figsize = (8, 6))
    
    """
    def __init__(self, func: callable, xlim: tuple , fig_num: int = None, figsize: tuple = (8,6)):
        """
        Initialize demo plot, set up interactive widget and run interective demo.
        """
        plt.close(fig_num)
        self.fig = plt.figure(fig_num, figsize=figsize)
        self.res = 201
        self.f = func
        self.x_vals = np.linspace(xlim[0], xlim[1], self.res)

        
        # Initialverdier for numerisk derivasjon med bakoverdifferanse
        goldenRatio = 1.61803398875
        self.diff_method = "forward"
        x_a = (self.x_vals[-1]-self.x_vals[0])*(1-1/goldenRatio)+self.x_vals[0] # Start demo in golden ratio
        self.h = (self.x_vals[-1]-self.x_vals[0])/20
        x_b = x_a + self.h
        
        # Plot kurven f(x) for alle verdier av x
        ax1 = plt.subplot(1,1,1)
        #ax1.plot([self.x_vals[0], self.x_vals[-1]], [0, 0], 'k', linewidth=0.7) # x-axis 
        ax1.plot(self.x_vals, self.f(self.x_vals))
        #self.y_range = ax1.get_ylim()
        self.y_range = ax1.get_ylim()
        ax1.set_xlabel(r"$x$-axis")
        ax1.set_ylabel(r"$y$-axis")
        ax1.set_title("Foroverdifferanse:\n"+r"$\frac{f(x+h)-f(x)}{h} = \frac{f(%.2f+%.2f)-f(%.2f)}{%.2f} = %.2f$"%(x_a, self.h, x_a, self.h, (self.f(x_b)-self.f(x_a))/self.h))
        ax1.grid(False)
        ax1.set_xlim([xlim[0], xlim[-1]])
    
        # Plot punktene som brukes i derivasjon
        self.diffLocation, = ax1.plot([x_a, x_a, self.x_vals[0]],
                                      [ax1.get_ylim()[0], self.f(x_a), self.f(x_a)],
                                      'C3o:',
                                      linewidth=0.5,
                                      markersize=6)
        
        self.points, = ax1.plot([x_b], 
                                [self.f(x_b)],
                                'C2o:',
                                linewidth=0.7, 
                                markersize=6)
        
        ax1.set_xticks([self.x_vals[0], x_a, x_b, self.x_vals[-1]], 
                       labels=[str(self.x_vals[0]), "$x$", "$x + h$", str(self.x_vals[-1])])
        ax1.set_yticks([ax1.get_ylim()[0], self.f(x_a), self.f(x_b), ax1.get_ylim()[-1]], 
                       labels=[str(self.x_vals[0]), "$f(x)$", "$f(x + h)$", str(self.x_vals[-1])])
        
        # Vis sekantlinjen mellom f(x_a) og f(x_b)
        self.secant, = ax1.plot([self.x_vals[0], self.x_vals[-1]], [0,0],'C2', linewidth=0.7, label="Sekant")
        self.set_secant(x_a, x_b)

        # Vis tangenten til f(x_a)
        self.tangent, = ax1.plot([self.x_vals[0], self.x_vals[-1]], [0,0],'C3', linewidth=0.7, label="Tangent")
        self.set_tangent(x_a)
        
        ax1.legend(loc="upper right")
        self.ax1 = ax1

        self.fig.tight_layout()
        
        #Set up slider panel
        x_slider = widget.FloatSlider(
                                    value = x_a,
                                    min=self.x_vals[0],
                                    max=self.x_vals[-1],
                                    step = (self.x_vals[-1]-self.x_vals[0])/100,
                                    description=r'x',
                                    disabled=False,
                                    style = {'description_width': 'initial'},
                                    layout=Layout(width='95%'),
                                    continuous_update=True
                                    )
        h_input = widget.BoundedFloatText(
                                            value=(self.x_vals[-1]-self.x_vals[0])/20,
                                            min=(self.x_vals[-1]-self.x_vals[0])/100,
                                            max=(self.x_vals[-1]-self.x_vals[0])/5,
                                            step=(self.x_vals[-1]-self.x_vals[0])/100,
                                            description=r'h',
                                            disabled=False,
                                            style = {'description_width': 'initial'},
                                            layout=Layout(width='30%'),
                                            continuous_update=True
                                        )
        method_input = widget.Dropdown(
                                    options=['forward', 'backward', 'center'],
                                    value='forward',
                                    description='Differentiation Method:',
                                    style = {'description_width': 'initial'},
                                    layout=Layout(width='30%'),
                                    disabled=False
                                    )


        
        self.layout = VBox([x_slider, 
                           HBox([h_input, method_input])])
        x_slider.observe(self.on_x_change, names="value")
        h_input.observe(self.on_h_change, names="value")
        method_input.observe(self.update_method, names="value")
       # self.userInput = {'x': x_slider}
        
        # Run demo
        #out = interactive_output(self.update, self.userInput)
        out = widget.Output()
        display(self.layout, out)
    
    def on_x_change(self, sliderChange):
        self.update_x(sliderChange["new"])
    
    def update_x(self, x):
        x_trace, y_trace = self.get_coordinate_trace(x, self.f(x))
        self.diffLocation.set_xdata(x_trace)
        self.diffLocation.set_ydata(y_trace)
        
        if self.diff_method == "forward":
            x_trace, y_trace = self.get_coordinate_trace(x+self.h, self.f(x+self.h))
            self.points.set_xdata(x_trace)
            self.points.set_ydata(y_trace)
            self.set_secant(x, x+self.h)
            self.update_ticks([x, x+self.h],["x","x + h"])
            self.ax1.set_title("Foroverdifferanse:\n"+r"$\frac{f(x+h)-f(x)}{h} = \frac{f(%.2f+%.2f)-f(%.2f)}{%.2f} = %.2f$"%(x, self.h, x, self.h, (self.f(x+self.h)-self.f(x))/self.h))
            
        elif self.diff_method == "backward":
            x_trace, y_trace = self.get_coordinate_trace(x-self.h, self.f(x-self.h))
            self.points.set_xdata(x_trace)
            self.points.set_ydata(y_trace)
            self.set_secant(x-self.h, x)
            self.update_ticks([x-self.h, x],["x - h","x"])
            self.ax1.set_title("Bakoverdifferanse:\n"+r"$\frac{f(x)-f(x-h)}{h} = \frac{f(%.2f)-f(%.2f-%.2f)}{%.2f} = %.2f$"%(x, x, self.h, self.h, (self.f(x)-self.f(x-self.h))/self.h))
            
        elif self.diff_method == "center":
            x_trace1, y_trace1 = self.get_coordinate_trace(x-self.h, self.f(x-self.h))
            x_trace2, y_trace2 = self.get_coordinate_trace(x+self.h, self.f(x+self.h))
            x_trace2.reverse()
            y_trace2.reverse()
            self.points.set_xdata(x_trace1+x_trace2)
            self.points.set_ydata(y_trace1+y_trace2)
            self.set_secant(x-self.h, x+self.h)        
            self.update_ticks([x-self.h, x, x+self.h],["x - h","x","x + h"])
            self.ax1.set_title("Foroverdifferanse:\n"+r"$\frac{f(x+h)-f(x-h)}{2\cdot h} = \frac{f(%.2f+%.2f)-f(%.2f-%.2f)}{2\cdot %.2f} = %.2f$"%(x, self.h, x, self.h, self.h, (self.f(x+self.h)-self.f(x-self.h))/self.h/2))

        self.ax1.set_xlim([self.x_vals[0], self.x_vals[-1]])
        self.ax1.set_ylim([self.y_range[0], self.y_range[-1]])
        self.set_tangent(x)
        
    def update_method(self, change):
        self.diff_method = change["new"]
        self.update_x(self.diffLocation.get_xdata()[0])
        
    def on_h_change(self, inputChange):
        self.update_h(inputChange["new"])
    
    def update_h(self, h):
        self.h = h
        x = self.diffLocation.get_xdata()[0]
        print(x)
        self.update_x(x)
        
    def set_secant(self, x1, x2):
        a = (self.f(x2) - self.f(x1))/(x2-x1)
        b = self.f(x1) - a*x1
        y_a = a*self.x_vals[0]+b
        y_b = a*self.x_vals[-1]+b
        self.secant.set_ydata([y_a, y_b])
    
    def set_tangent(self, x):
        h = 1/512
        
        a = (self.f(x+h) - self.f(x-h))/(2*h)
        b = self.f(x) - a*x
        y_a = a*self.x_vals[0]+b
        y_b = a*self.x_vals[-1]+b
        self.tangent.set_ydata([y_a, y_b])

    def get_coordinate_trace(self, x, y):
        x_trace = [x, x, 1.1*self.x_vals[0] - 0.1*self.x_vals[-1]]
        y_trace = [1.1*self.y_range[0] - 0.1*self.y_range[-1], y, y]
        return x_trace, y_trace

    def update_ticks(self, x_points, substrings):
        y_points = [self.f(x) for x in x_points]
        xticks = [self.x_vals[0]]+x_points+[self.x_vals[-1]]
        yticks = [self.y_range[0]]+y_points+[self.y_range[-1]]
        xticklabels = ["%.2f"%self.x_vals[0]]+substrings+["%.2f"%self.x_vals[-1]]
        yticklabels = ["%.2f"%self.y_range[0]]+["f(%s)"%s for s in substrings]+["%.2f"%self.y_range[-1]]
        self.ax1.set_xticks(xticks, xticklabels)
        self.ax1.set_yticks(yticks, yticklabels)
