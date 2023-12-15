from PyQt5 import QtWidgets
import numpy as np
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter, ParameterTree

class MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()

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
            {'name': 'Tangent Point', 'type': 'str', 'value': '(0, 0)', 'readonly': True},
            {'name': 'Intersection Point', 'type': 'str', 'value': '(0, 0)', 'readonly': True},
        ]
        self.params = Parameter.create(name='params', type='group', children=params)
        self.parameter_tree = ParameterTree()
        self.parameter_tree.setParameters(self.params, showTop=False)

        # Add parameter tree to layout
        self.parameter_tree.setMinimumWidth(200)
        self.layout.addWidget(self.parameter_tree)

        # Create plot
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground('w')
        self.plot_graph.setAspectLocked(True)
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.getViewBox().setRange(xRange=(-10, 10), yRange=(-10, 10))
        self.plot_graph.getAxis('bottom').setTickSpacing(1, 1)
        self.plot_graph.getAxis('left').setTickSpacing(1, 1)
        self.plot_graph.getViewBox().setMouseEnabled(x=False, y=False)
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

        # Create a plot item for the tangent point
        self.tangent_point = pg.PlotDataItem(pen=None, symbolBrush='g', symbolSize=10)
        self.plot_graph.addItem(self.tangent_point)

        # Create a plot item for the tangent line
        self.tangent_line = pg.PlotDataItem(pen=pg.mkPen('g', width=2))
        self.plot_graph.addItem(self.tangent_line)

        # Create a plot item for the intersection point
        self.intersection_point = pg.PlotDataItem(pen=None, symbolBrush='g', symbolSize=15)

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
            self.params.param('Inner Radius').setLimits((1, value))


    def update_starting_point(self, param, value):
        outer_radius = self.params.param('Outer Radius').value()
        inner_radius = self.params.param('Inner Radius').value()

        # Update the position of the starting point plot item
        self.params.param('Starting Point').setValue(f'(0, {outer_radius})')
        self.starting_point.setData([0], [outer_radius])

        # Calculate the angle of the tangent point
        tangent_angle = np.radians(180) - np.arccos(inner_radius / outer_radius)
        print(f"Tangent Angle: {np.degrees(tangent_angle)} degrees")

        # Calculate the starting angle
        starting_angle = (np.radians(180 - 90 - np.degrees(tangent_angle))) * -1
        print(f"Starting Angle: {np.degrees(starting_angle)} degrees")

        # Calculate the length of the adjacent side
        adjacent_side = 2 * inner_radius
        print(f"Adjacent Side: {adjacent_side}")

        # Calculate the coordinates of the intersection point on the outer circle
        intersection_point_x = adjacent_side * np.cos(starting_angle)
        intersection_point_y = -outer_radius * np.sin(tangent_angle)
        intersection_point = (intersection_point_x, intersection_point_y)
        print(f"Intersection Point: {intersection_point}")

        # Draw the line from the starting point to the intersection point
        self.tangent_line.setData([0, intersection_point[0]], [outer_radius, intersection_point[1]])

        # Draw the intersection point on the plot
        self.intersection_point.setData([intersection_point[0]], [intersection_point[1]])

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()