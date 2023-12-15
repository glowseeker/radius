from PyQt5 import QtWidgets
import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        # Set the window size and disable manual resizing
        self.setFixedSize(800, 600)

        # Create layout and add to central widget
        self.layout = QtWidgets.QHBoxLayout()
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(self.layout)

        # Create parameters and tree
        params = [
            {'name': 'Inner Radius', 'type': 'float', 'value': 1, 'limits': (1, 10), 'step': 0.1},
            {'name': 'Outer Radius', 'type': 'float', 'value': 10, 'limits': (1, 10), 'step': 0.1},
            {'name': 'Starting Point', 'type': 'str', 'value': '(0, 0)', 'readonly': True},
        ]
        self.params = Parameter.create(name='params', type='group', children=params)
        self.parameter_tree = ParameterTree()
        self.parameter_tree.setParameters(self.params, showTop=False)

        # Set initial limits
        self.params.param('Inner Radius').setLimits((0, self.params.param('Outer Radius').value()))
        self.params.param('Outer Radius').setLimits((self.params.param('Inner Radius').value(), 10))

        # Add parameter tree to layout
        self.parameter_tree.setMinimumWidth(200)
        self.layout.addWidget(self.parameter_tree)

        # Create plot
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground('w')
        self.plot_graph.setAspectLocked(True)
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.getViewBox().setRange(xRange=(-10, 10), yRange=(-10, 10))
        self.plot_graph.getViewBox().setMouseEnabled(x=False, y=False)
        self.plot_graph.getAxis('bottom').setTickSpacing(1, 1)
        self.plot_graph.getAxis('left').setTickSpacing(1, 1)
        pen = pg.mkPen(width=2)
        self.plot_graph.plot([-11, 11], [0, 0], pen=pen)  # X-axis
        self.plot_graph.plot([0, 0], [-11, 11], pen=pen)  # Y-axis

        # Connect parameter changes to circle update
        self.params.param('Inner Radius').sigValueChanged.connect(self.update_circles)
        self.params.param('Outer Radius').sigValueChanged.connect(self.update_circles)
        self.params.param('Inner Radius').sigValueChanged.connect(self.update_limits)
        self.params.param('Outer Radius').sigValueChanged.connect(self.update_limits)
        self.params.param('Outer Radius').sigValueChanged.connect(self.update_starting_point)
        self.params.param('Inner Radius').sigValueChanged.connect(self.update_starting_point)

        
        # Create a plot item for the starting point
        self.starting_point = pg.PlotDataItem(pen=None, symbolBrush='g', symbolSize=10)
        self.plot_graph.addItem(self.starting_point)

        # Create a plot item for the tangent line
        self.tangent_line = pg.PlotDataItem(pen=pg.mkPen('g', width=2))
        self.plot_graph.addItem(self.tangent_line)

        # Draw circles
        self.inner_circle = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.outer_circle = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
        self.plot_graph.addItem(self.inner_circle)
        self.plot_graph.addItem(self.outer_circle)
        self.init_circles()
        
        # Add plot to layout
        self.layout.addWidget(self.plot_graph)
    
    def init_circles(self):
        inner_radius = self.params.param('Inner Radius').value()
        outer_radius = self.params.param('Outer Radius').value()

        # Calculate points for inner circle
        theta = np.linspace(0, 2*np.pi, 100)
        x = inner_radius * np.cos(theta)
        y = inner_radius * np.sin(theta)
        self.inner_circle.setData(x, y)

        # Calculate points for outer circle
        x = outer_radius * np.cos(theta)
        y = outer_radius * np.sin(theta)
        self.outer_circle.setData(x, y)

        # Initialize starting point
        self.update_starting_point(self.params.param('Outer Radius'), outer_radius)

    def update_circles(self, param, value):
        # Calculate points for inner circle
        theta = np.linspace(0, 2*np.pi, 100)
        x = value * np.cos(theta)
        y = value * np.sin(theta)
        if param.name() == 'Inner Radius':
            self.inner_circle.setData(x, y)
        else:
            self.outer_circle.setData(x, y)
    
    def update_limits(self, param, value):
        if param.name() == 'Inner Radius':
            self.params.param('Outer Radius').setLimits((value, 10))
        else:  # param.name() == 'Outer Radius'
            self.params.param('Inner Radius').setLimits((0, value))

    def update_starting_point(self, param, value):
        # Update starting point
        outer_radius = self.params.param('Outer Radius').value()
        self.params.param('Starting Point').setValue(f'(0, {outer_radius})')

        # Update the position of the starting point plot item
        self.starting_point.setData([0], [outer_radius])

        # Calculate the point on the inner circle that is closest to the tangent
        inner_radius = self.params.param('Inner Radius').value()

        # Calculate the angle of the tangent point
        angle = np.arcsin(inner_radius / outer_radius)

        # Calculate the coordinates of the tangent point on the inner circle
        tangent_point_x = inner_radius * np.cos(angle)
        tangent_point_y = inner_radius * np.sin(angle)

        tangent_point = (tangent_point_x, tangent_point_y)

        # Draw the tangent line
        self.tangent_line.setData([0, tangent_point[0]], [outer_radius, tangent_point[1]])

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()