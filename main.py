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
            {'name': 'Manual', 'type': 'group', 'children': [
                {'name': 'Inner Radius', 'type': 'float', 'value': 1, 'limits': (1, 10), 'decimals': '6'},
                {'name': 'Outer Radius', 'type': 'float', 'value': 10, 'limits': (1, 10)},
                {'name': 'Ratio', 'type': 'str', 'value': '1:10', 'readonly': True},
                {'name': 'Starting Point', 'type': 'str', 'value': '(0, 10)', 'readonly': True},
                {'name': 'Ending Point', 'type': 'str', 'value': '(0, 10)', 'readonly': True},
                {'name': 'Steps', 'type': 'int', 'value': 1, 'limits': (1, 1000), 'step': 1},
                {'name': 'Complete', 'type': 'str', 'value': 'False', 'readonly': True},
            ]},
            {'name': 'Solver', 'type': 'group', 'children': [
                {'name': 'Desired edges', 'type': 'int', 'value': 1, 'limits': (1, 100), 'step': 1},
                {'name': 'Necessary ratio', 'type': 'float', 'value': 1, 'step': 0.0001, 'readonly': True},
                {'name': 'Star', 'type': 'bool', 'value': 'False'},
            ]},
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

        # Connect parameters to functions
        self.params.param('Manual', 'Inner Radius').sigValueChanged.connect(self.update_circles)
        self.params.param('Manual', 'Outer Radius').sigValueChanged.connect(self.update_circles)
        self.params.param('Manual', 'Inner Radius').sigValueChanged.connect(self.radius_change)
        self.params.param('Manual', 'Outer Radius').sigValueChanged.connect(self.radius_change)
        self.params.param('Manual', 'Outer Radius').sigValueChanged.connect(self.steps_loop)
        self.params.param('Manual', 'Inner Radius').sigValueChanged.connect(self.steps_loop)
        self.params.param('Manual', 'Steps').sigValueChanged.connect(self.steps_loop)
        self.params.param('Manual', 'Ratio').sigValueChanged.connect(self.radius_change)
        self.params.param('Solver', 'Desired edges').sigValueChanged.connect(self.solver_ratio)
        self.params.param('Solver', 'Star').sigValueChanged.connect(self.solver_ratio)
        self.params.param('Solver', 'Necessary ratio').sigValueChanged.connect(self.solver_ratio)

        # Initialize the list to store the lines
        self.tangent_lines = []

        # Draw circles
        self.inner_circle = pg.PlotDataItem(pen=pg.mkPen('b', width=2))
        self.outer_circle = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
        self.plot_graph.addItem(self.inner_circle)
        self.plot_graph.addItem(self.outer_circle)
        self.init_circles()
        
        # Add plot to layout
        self.layout.addWidget(self.plot_graph)
    
    def init_circles(self):
        inner_radius = self.params.param('Manual', 'Inner Radius').value()
        outer_radius = self.params.param('Manual', 'Outer Radius').value()

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
        self.steps_loop(self.params.param('Manual', 'Outer Radius'), outer_radius)

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
        outer_radius = self.params.param('Manual', 'Outer Radius').value()
        inner_radius = self.params.param('Manual', 'Inner Radius').value()
        if param.name() == 'Inner Radius':
            self.params.param('Manual', 'Outer Radius').setLimits((value, 10))
        else:  # param.name() == 'Outer Radius'
            self.params.param('Manual', 'Inner Radius').setLimits((1, value))

        # Clear all the lines and redraw
        for line in self.tangent_lines:
            self.plot_graph.removeItem(line)
        self.tangent_lines.clear()
        self.steps_loop(param, value)
        
        # Update the value of the starting point
        self.params.param('Manual', 'Starting Point').setValue(f'(0.00, {outer_radius:.5f})')

        # Calculate the ratio of the radii
        ratio = round(outer_radius / inner_radius, 4)
        self.params.param('Manual', 'Ratio').setValue(f"1:{ratio}")

    def steps_loop(self, param, value):
        outer_radius = self.params.param('Manual', 'Outer Radius').value()
        outer_diameter = 2 * outer_radius
        inner_radius = self.params.param('Manual', 'Inner Radius').value()
        inner_diameter = 2 * inner_radius
        steps = self.params.param('Manual', 'Steps').value()

        # Calculate the length of the line
        length = np.sqrt(outer_diameter ** 2 - inner_diameter ** 2)

        # Calculate the starting angle (in radians)
        angle = np.degrees(np.arcsin(inner_diameter / outer_diameter))

        # Get the current number of steps
        current_steps = len(self.tangent_lines)

        # Set the current point to the starting point (0, outer_radius)
        current_point_x = 0
        current_point_y = outer_radius

        # If the number of steps has been reduced, remove the excess lines
        if current_steps > steps:
            for _ in range(current_steps - steps):
                # Remove the last line from the plot
                self.plot_graph.removeItem(self.tangent_lines.pop())

        # Add or update lines based on the number of steps required
        for i in range(steps):
            if i < current_steps:  # If the line already exists, update its position
                tangent_line = self.tangent_lines[i]
            else:  # If the line does not exist, create a new one
                tangent_line = pg.PlotDataItem(pen=pg.mkPen('g', width=2))
                self.tangent_lines.append(tangent_line)
                self.plot_graph.addItem(tangent_line)

            # Calculate the direction of the line from the current point to the origin
            direction_x = -current_point_x
            direction_y = -current_point_y

            # Scale the direction vector to the desired length
            scale = length / np.sqrt(direction_x ** 2 + direction_y ** 2)
            direction_x *= scale
            direction_y *= scale

            # Rotate the direction vector by the desired angle
            angle_rad = np.radians(angle)
            rotated_x = direction_x * np.cos(angle_rad) - direction_y * np.sin(angle_rad)
            rotated_y = direction_x * np.sin(angle_rad) + direction_y * np.cos(angle_rad)

            # Calculate the coordinates of the tangent point
            tangent_point_x = current_point_x + rotated_x
            tangent_point_y = current_point_y + rotated_y

            # Set the ending point of the line
            self.params.param('Manual', 'Ending Point').setValue(f'({tangent_point_x:.5f}, {tangent_point_y:.5f})')

            # Check if the line's end coordinates match the starting point
            if np.allclose((tangent_point_x, tangent_point_y), (0, outer_radius)):
                self.params.param('Manual', 'Complete').setValue('True')
            else:
                self.params.param('Manual', 'Complete').setValue('False')

            # Update the line coordinates
            tangent_line.setData([current_point_x, tangent_point_x], [current_point_y, tangent_point_y])

            # Update the current point to the tangent point for the next iteration
            current_point_x = tangent_point_x
            current_point_y = tangent_point_y

    def solver_ratio(self, param, value):
        desired_edges = self.params.param('Solver', 'Desired edges').value()
        necessary_ratio = self.params.param('Solver', 'Necessary ratio').value()
        star = self.params.param('Solver', 'Star').value()

        # Get the current values
        desired_edges = self.params.child('Solver', 'Desired edges').value()
        star = self.params.child('Solver', 'Star').value()

        # Calculate the new ratio based on whether 'Star' is checked or not
        if star:
            new_ratio = desired_edges * 2  # Replace with the actual formula
        else:
            new_ratio = desired_edges * 0.5  # Replace with the actual formula

        # Update the 'Necessary ratio' value
        self.params.child('Solver', 'Necessary ratio').setValue(new_ratio)

app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()