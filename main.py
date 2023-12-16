import math
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
            {'name': 'Steps', 'type': 'int', 'value': 1, 'limits': (1, 1000), 'step': 1},
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
        self.params.param('Inner Radius').sigValueChanged.connect(self.radius_change)
        self.params.param('Outer Radius').sigValueChanged.connect(self.radius_change)
        self.params.param('Outer Radius').sigValueChanged.connect(self.steps_loop)
        self.params.param('Inner Radius').sigValueChanged.connect(self.steps_loop)
        self.params.param('Steps').sigValueChanged.connect(self.steps_loop)
        
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
        self.steps_loop(self.params.param('Outer Radius'), outer_radius)

    def update_circles(self, param, value):
        # Calculate points for inner circle
        theta = np.linspace(0, 2*np.pi, 100)
        x = value * np.cos(theta)
        y = value * np.sin(theta)
        if param.name() == 'Inner Radius':
            self.inner_circle.setData(x, y)
        else:
            self.outer_circle.setData(x, y)
    
    def radius_change(self, param, value):
        if param.name() == 'Inner Radius':
            self.params.param('Outer Radius').setLimits((value, 10))
        else:  # param.name() == 'Outer Radius'
            self.params.param('Inner Radius').setLimits((1, value))

        for line in self.tangent_lines:
            self.plot_graph.removeItem(line)
            self.tangent_lines.clear()

    def steps_loop(self, param, value):
        outer_radius = self.params.param('Outer Radius').value()
        outer_diameter = 2 * outer_radius
        inner_radius = self.params.param('Inner Radius').value()
        inner_diameter = 2 * inner_radius
        steps = self.params.param('Steps').value()
        
        # Create a list to store the lines
        self.tangent_lines = []
        
        # Calculate the length of the line
        length = np.sqrt(outer_diameter**2 - (inner_diameter**2))
        
        # Calculate the starting angle (in radians)
        angle = np.degrees(np.arcsin(inner_diameter / outer_diameter))

        # Set the current point to the starting point (0, outer_radius)
        current_point_x = 0
        current_point_y = outer_radius

        for _ in range(steps):
            # Calculate the direction of the line from the current point to the origin
            direction_x = -current_point_x
            direction_y = -current_point_y

            # Scale the direction vector to the desired length
            scale = length / np.sqrt(direction_x**2 + direction_y**2)
            direction_x *= scale
            direction_y *= scale

            # Rotate the direction vector by the desired angle
            angle_rad = np.radians(angle)
            rotated_x = direction_x * np.cos(angle_rad) - direction_y * np.sin(angle_rad)
            rotated_y = direction_x * np.sin(angle_rad) + direction_y * np.cos(angle_rad)

            # Calculate the coordinates of the tangent point
            tangent_point_x = current_point_x + rotated_x
            tangent_point_y = current_point_y + rotated_y

            # Create a new line and add it to the list
            tangent_line = pg.PlotDataItem([current_point_x, tangent_point_x], [current_point_y, tangent_point_y], pen=pg.mkPen('g', width=2))
            self.tangent_lines.append(tangent_line)

            # Add the line to the plot
            self.plot_graph.addItem(tangent_line)

            # Update the current point to the tangent point for the next iteration
            current_point_x = tangent_point_x
            current_point_y = tangent_point_y


app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()