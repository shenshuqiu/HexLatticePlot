from typing import Optional, Literal, Callable
from dataclasses import dataclass

import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes
from matplotlib.patches import Polygon, Circle
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np

from HexLattice.coordinates import AbstractCoordinate

from .coordinates import Coordinate, ValidDirections, CartesianCoordinate
from .plot_config import PlotConfig

@dataclass
class HexCell(Coordinate):
    
    def __init__(
            self, 
            centre_coord: AbstractCoordinate,
            radius: float           = 1 / np.sqrt(3),
            text:   Optional[str]   = None,
            value:  Optional[float] = None,
            real_cartesian: Optional[float] = None
        ) -> None:
        super().__init__(centre_coord)
        self.centre         = Coordinate(centre_coord)
        self.radius         = radius
        self.text           = text
        self.value          = value
        self.real_cartesian = self.cartesian if real_cartesian is None else real_cartesian
    
    def get_neighbour(self, direction: ValidDirections) -> 'HexCell':
        neighbour_axial_coord = self.centre.axial.get_neighbour(direction)
        return HexCell(Coordinate(neighbour_axial_coord))
    
    @property
    def vertexes_pointy(self) -> list[tuple]:
        res_list = list()
        for angle in range(30, 360, 60):
            angle_rad = angle / 180 * np.pi
            x = self.real_cartesian.x + self.radius * np.cos(angle_rad)
            z = self.real_cartesian.y + self.radius * np.sin(angle_rad)
            res_list.append(CartesianCoordinate(x, z).as_tuple())
        return res_list
    
    def __rmul__(self, factor: float) -> 'HexCell':
        """
        HexCell is multiplied when it it used for HexLattice.
        """
        return HexCell(self.centre, factor*self.radius, self.text, self.value, factor*self.real_cartesian)
    
    # valued in HexLattice Object
    ObjectRelatedCoordinate: tuple = None
    
@dataclass
class HexLattice:
    
    def __init__(self, HexCells: list[HexCell], pitch: float = 1) -> None:
        self.pitch = pitch
        real_hex_cells: list[HexCell] = list()
        record = list()
        for hex_cell in HexCells:
            if hex_cell in record:
                continue
            else:
                record.append(hex_cell)
                
                # Only hex_cell.real_cartesian is changed when pitch multiply hex_cell
                real_hex_cells.append(pitch * hex_cell)
                
        self.HexCells = real_hex_cells
    
    @property
    def value_list(self) -> np.array:
        hex_cell_value_list = [hex_cell.value for hex_cell in self.HexCells]
        if all(hex_cell_value is None for hex_cell_value in hex_cell_value_list):
            return np.array([0 for _ in hex_cell_value_list])
        else:
            return np.array([0 if hex_cell_value is None else hex_cell_value for hex_cell_value in hex_cell_value_list])
    
    @property
    def normed_value_list(self) -> np.array:
        value_list = self.value_list
        value_min  = np.min(value_list)
        value_max  = np.max(value_list)
        return (value_list - value_min) / (value_max - value_min)
    
    def mappable(self, pc: PlotConfig) -> ScalarMappable:
        norm = Normalize(vmin=np.min(self.value_list), vmax=np.max(self.value_list))
        cmap = pc.color_map
        return ScalarMappable(norm, cmap)
        
    
    def assign_object_related_coordinates(self, assigner: Callable[[HexCell], tuple]):
        """
        Assigns a tuple to ObjectRelatedCoordinate of each HexCell using a provided function.

        Args:
            assigner (Callable[[HexCell], tuple]): Function to generate a tuple for each HexCell.
        """
        for cell in self.HexCells:
            cell.ObjectRelatedCoordinate = assigner(cell)
            
    def _plot_cells(self, ax: Axes, pc: PlotConfig, shape_func: Callable, text_mode: Literal['value', 'text']) -> Axes:
        for i, hex_cell in enumerate(self.HexCells):
            if text_mode == 'value':
                color = pc.color_map(self.normed_value_list[i])
                label = round(hex_cell.value, 2)
                text_color = pc.text_color_func(color)
            elif text_mode == 'text':
                color = pc.hex_face_color
                label = hex_cell.text
                text_color = pc.text_color
            else:
                raise TypeError('Wrong Plot Type!')

            patch = shape_func(hex_cell, color, pc.hex_edge_color)
            ax.add_patch(patch)
            ax.text(
                hex_cell.real_cartesian.x,
                hex_cell.real_cartesian.y,
                label,
                ha='center',
                va='center',
                fontsize=pc.text_size,
                color=text_color
            )
        ax.set_title(pc.image_name)
        return ax

    def _setup_ax(self, pc: PlotConfig, ax: Optional[Axes]) -> Axes:
        pc.set_plot_config()
        if ax is None:
            ax = plt.subplot()
        all_x = [[v[0] for v in cell.vertexes_pointy] for cell in self.HexCells]
        all_z = [[v[1] for v in cell.vertexes_pointy] for cell in self.HexCells]
        ax.set_xlim((np.min(all_x) - pc.figure_expand, np.max(all_x) + pc.figure_expand))
        ax.set_ylim((np.min(all_z) - pc.figure_expand, np.max(all_z) + pc.figure_expand))
        ax.set_aspect('equal')
        ax.axis('off')
        return ax

    def plot_hex(self, pc: PlotConfig, ax: Axes = None) -> Axes:
        ax = self._setup_ax(pc, ax)

        def polygon_func(cell: HexCell, facecolor, edgecolor):
            return Polygon(
                cell.vertexes_pointy,
                closed=True,
                facecolor=facecolor,
                edgecolor=edgecolor
            )

        text_mode = 'text' if all(cell.text is not None for cell in self.HexCells) else 'value'
        return self._plot_cells(ax, pc, polygon_func, text_mode)

    def plot_circle(self, pc: PlotConfig, ax: Axes = None, plot_type: Literal['value', 'text'] = 'value') -> Axes:
        ax = self._setup_ax(pc, ax)

        def circle_func(cell: HexCell, facecolor, edgecolor):
            return Circle(
                cell.real_cartesian.as_tuple(),
                radius=cell.radius * np.sqrt(3) / 2,
                facecolor=facecolor,
                edgecolor=edgecolor
            )

        return self._plot_cells(ax, pc, circle_func, plot_type)

        
