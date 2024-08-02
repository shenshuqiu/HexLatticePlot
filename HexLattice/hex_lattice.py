from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes._axes import Axes
from matplotlib.patches import Polygon, Circle
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import numpy as np

from HexLattice.coordinates import AbstractCoordinate

from .coordinates import *
from .plot_config import *

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
            
    def plot_hex(self, pc: PlotConfig, ax: Axes=None) -> tuple[Axes, Optional[ScalarMappable]]:
        # set plot config
        pc.set_plot_config()
        
        # plot all Hex on ax
        if ax is None:
            ax = plt.subplot()
        
        # set ax lim through HexCells
        all_x = [[vertex[0] for vertex in hex_cell.vertexes_pointy] for hex_cell in self.HexCells]
        all_z = [[vertex[1] for vertex in hex_cell.vertexes_pointy] for hex_cell in self.HexCells]
        x_min = np.min(all_x)
        x_max = np.max(all_x)
        z_min = np.min(all_z)
        z_max = np.max(all_z)
        ax.set_ylim((z_min-pc.figure_expand*abs(z_min), z_max+pc.figure_expand*abs(z_max)))
        ax.set_xlim((x_min-pc.figure_expand*abs(x_min), x_max+pc.figure_expand*abs(x_max)))
        ax.set_aspect('equal')
        ax.axis('off')
        
        
        # Create Polygon by HexCells
        for i, hex_cell in enumerate(self.HexCells):
            if hex_cell.text is not None:
                # Create Polygon
                hex_patch = Polygon(
                    hex_cell.vertexes_pointy,
                    closed      = True,
                    facecolor   = pc.hex_face_color,
                    edgecolor   = pc.hex_edge_color,
                )
                ax.add_patch(hex_patch)
                
                # add text
                centre_x = hex_cell.real_cartesian.x
                centre_y = hex_cell.real_cartesian.y
                ax.text(
                    centre_x,
                    centre_y,
                    hex_cell.text,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize = pc.text_size,
                    color = pc.text_color
                )
                
            else:
                # calculate hex color by value
                hex_face_color = pc.color_map(self.normed_value_list[i])
                
                # Create Polygon
                hex_patch = Polygon(
                    hex_cell.vertexes_pointy,
                    closed      = True,
                    facecolor   = hex_face_color,
                    edgecolor   = pc.hex_edge_color,
                )
                ax.add_patch(hex_patch)
                
                # add text
                centre_x = hex_cell.real_cartesian.x
                centre_y = hex_cell.real_cartesian.y
                ax.text(
                    centre_x,
                    centre_y,
                    round(hex_cell.value, 2),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize = pc.text_size,
                    color = pc.text_color_func(hex_face_color)
                )
                
        
        ax.set_title(pc.image_name)
        
        return ax                
    
    def plot_circle(self, pc: PlotConfig, ax: Axes=None) -> Axes:
        # set plot config
        pc.set_plot_config()
        
        # plot all Hex on ax
        if ax is None:
            ax = plt.subplot()
        
        # set ax lim through HexCells
        all_x = [[vertex[0] for vertex in hex_cell.vertexes_pointy] for hex_cell in self.HexCells]
        all_z = [[vertex[1] for vertex in hex_cell.vertexes_pointy] for hex_cell in self.HexCells]
        x_min = np.min(all_x)
        x_max = np.max(all_x)
        z_min = np.min(all_z)
        z_max = np.max(all_z)
        ax.set_ylim((z_min-pc.figure_expand*abs(z_min), z_max+pc.figure_expand*abs(z_max)))
        ax.set_xlim((x_min-pc.figure_expand*abs(x_min), x_max+pc.figure_expand*abs(x_max)))
        ax.set_aspect('equal')
        ax.axis('off')
        
        plot_by_value = all(hex_cell.text is None for hex_cell in self.HexCells)
        # Create Polygon by HexCells
        for i, hex_cell in enumerate(self.HexCells):
            if plot_by_value:
                # Create Polygon
                hex_patch = Circle(
                    hex_cell.real_cartesian.as_tuple(),
                    radius      = 0.8 * hex_cell.radius,
                    facecolor   = hex_face_color,
                    edgecolor   = pc.hex_edge_color,
                )
                ax.add_patch(hex_patch)
                
                # add text
                centre_x = hex_cell.real_cartesian.x
                centre_y = hex_cell.real_cartesian.y
                ax.text(
                    centre_x,
                    centre_y,
                    round(hex_cell.value, 2),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize = pc.text_size,
                    color = pc.text_color_func(hex_face_color)
                )
            else:
                                # Create Polygon
                hex_patch = Circle(
                    hex_cell.real_cartesian.as_tuple(),
                    radius      = 0.8 * hex_cell.radius,
                    facecolor   = pc.hex_face_color,
                    edgecolor   = pc.hex_edge_color,
                )
                ax.add_patch(hex_patch)
                
                # add text
                centre_x = hex_cell.real_cartesian.x
                centre_y = hex_cell.real_cartesian.y
                ax.text(
                    centre_x,
                    centre_y,
                    hex_cell.text,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize = pc.text_size,
                    color = pc.text_color
                )
                # calculate hex color by value
                hex_face_color = pc.color_map(self.normed_value_list[i])
                

                
        ax.set_title(pc.image_name)
        
        return ax
        
