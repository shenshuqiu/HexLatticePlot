from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field, fields
from typing import Literal, Sequence, TypedDict, Optional, Union, Callable

import numpy as np

# The Six valid Directions of Hexagons
ValidDirections = Literal['right', 'bottom-right', 'bottom-left', 'left', 'top-left', 'top-right']
DIRACTIONS = ['right', 'bottom-right', 'bottom-left', 'left', 'top-left', 'top-right']
ValidCoordinateType = Literal['axial', 'ring', 'cube', 'double_width', 'cartesian']

# ---------------------------------------------------------------------------------------------------------------------
#                                                           Axial Coordinate
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class AxialCoordinate:
    """
    A data class representing a axial coordinate
    
    Attributes:
        x (int): Increase from left to right
        z (int): Increase from top left to bottom right
        name(str): The name of coordinate

    Example:
            (0,-1)    (1,-1)  
        (-1,0)    (0,0)    (1,0)
            (-1,1)    (0,1)
    """
    x: int = 0
    z: int = 0
    name: str = field(default='axial', init=False, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return True
    
    def __init__(self, *args) -> None:
        """
        Coordinary initialization. The coordinate class can be initialized with a sequence or with two int. 
        AxialCoordinate((1,1)) is equivalent to AxialCoordinate(1,1).
            
        Raises:
            TypeError: Invalid init args
        """
        
        # Initialized with a sequence
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 2:
            self.x, self.z = args[0]
            
        # Initialized with two integers
        elif len(args) == 2 and all(isinstance(arg, int) for arg in args):
            self.x, self.z = args
            
        # Raise error if arguments are invalid
        else:
            raise TypeError(f'Invalid arguments: Expected either two integers or a tuple of two integers, received {args}.')
    
    def move(self, direction: ValidDirections, distance: int) -> 'AxialCoordinate':
        """
        Moves the coordinate in a specified direction by a certain distance.

        Args:
            direction (ValidDirections): The direction in which to move the coordinat
            distance (int): The number of steps to move in the given direction which can be negtive

        Raises:
            KeyError: If an invalid direction is provided, this error is raised
            TypeError: If an invalid distance is provided, this error is raised

        Returns:
            AxialCoordinate: The modified axial coordinate after moving in the given direction.
        """
        if not isinstance(distance, int):
            raise TypeError(f'The distance \'{distance}\' is invalid. The distance must be int.')
        
        if direction == 'bottom-left':
            self.x -= distance
            self.z += distance
        elif direction == 'bottom-right':
            self.z += distance
        elif direction == 'left':
            self.x -= distance
        elif direction == 'right':
            self.x += distance
        elif direction == 'top-left':
            self.z -= distance
        elif direction == 'top-right':
            self.x += distance
            self.z -= distance
        else:
            raise KeyError(f'The direction \'{direction}\' is invalid. The valid directions are {ValidCoordinateType}')
        return self
    
    def get_new_by_moving(self, direction: ValidDirections, distance: int) -> 'AxialCoordinate':
        """
        Get a new coordinate by moving
        """
        new_coord = deepcopy(self)
        new_coord.move(direction, distance)
        return new_coord
    
    def get_new_by_rotating(self, num_of_rotation: int) -> 'AxialCoordinate':
        """
        Get a new coordinate by rotating clockwise

        Args:
            num_of_rotation (int): Rotate clockwise by num_of_rotation * 60 degrees, e.g. num_of_rotation = -2 means rotate by -120 degrees clockwise

        Returns:
            AxialCoordinate: Rotated Coordinate
        """
        if not isinstance(num_of_rotation, int):
            raise ValueError(f'Invalid number of rotaion {num_of_rotation}')
        
        x, z = self.as_tuple()
        y = - x - z
        l = [x, y, z]
        
        def __once_coord_rotating(l: Sequence[int]) -> Sequence[int]:
            """
            Cube Coordinate changing with rotation clockwise
            
            Examples:
                Clockwise Rotation:
                    [x, y, z] --> [-z, -x, -y]
            """
            return [-l[2], -l[0], -l[1]]
        
        for _ in range(num_of_rotation % 6):
            l = __once_coord_rotating(l)
        
        return AxialCoordinate(l[0], l[2])
        
    def get_neighbour(self, direction: ValidDirections) -> 'AxialCoordinate':
        neighbour_copyed = deepcopy(self)
        neighbour_copyed.move(direction, 1)
        return neighbour_copyed
    
    def get_all_neighbour(self) -> list['AxialCoordinate']:
        neighbour_list = list()
        for direction in DIRACTIONS:
            coord_copy = deepcopy(self)
            neighbour_list.append(coord_copy.move(direction, 1.0))
        return neighbour_list
    
    def as_tuple(self) -> tuple[int]:
        """
        Returns the coordinates as a tuple.
        """
        return (self.x, self.z)
    
    def __add__(self, other: 'AxialCoordinate') -> 'AxialCoordinate':
        return AxialCoordinate(self.x+other.x, self.z+other.z)
    
    def __rmul__(self, factor: int) -> 'AxialCoordinate':
        return AxialCoordinate(factor*self.x, factor*self.z)
    
    def __lt__(self, other: 'AxialCoordinate') -> bool:
        return self.x < other.x if self.x != other.x else self.z < other.z
    
    def __eq__(self, other: 'AxialCoordinate') -> bool:
        return (self.x == other.x) & (self.z == other.z)
    
    def convert_to_axial(self) -> 'AxialCoordinate':
        return self
    
    @staticmethod
    def converted_from_axial(axial_coord: 'AxialCoordinate') -> 'AxialCoordinate':
        return AxialCoordinate(axial_coord.x, axial_coord.z)
    
# ---------------------------------------------------------------------------------------------------------------------
#                                                           Abstract Coordinate
# ---------------------------------------------------------------------------------------------------------------------

class AbstractCoordinate(ABC):
    """
    An abstract base class for a coordinate system that is independent of specific instances. This class requires defining the mapping relationship between this coordinate system and the axial coordinates.
    """
    
    @abstractmethod
    def coord_is_valid(coord: Sequence[int]) -> bool:
        """
        Validate the initialization coordinates.

        Args:
            coord (Sequence[int]): A coordinate tuple, e.g., (1, 2).

        Returns:
            bool: Returns True if the coordinates are valid, otherwise False.
        """
        pass
    
    def __init__(self, *args) -> None:
        """
        Initializes the coordinate. The coordinate class can be initialized either with a sequence or with two integers.
        Example: AxialCoordinate((1,1)) is equivalent to AxialCoordinate(1,1).
        
        Raises:
            TypeError: If initialization arguments are invalid.
        """
        
        # Initialized with a sequence
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 2 and self.coord_is_valid(args[0]):
            self.x, self.z = args[0]
            
        # Initialized with two integers
        elif len(args) == 2 and all(isinstance(arg, int) for arg in args) and self.coord_is_valid(args):
            self.x, self.z = args
            
        # Raise error if arguments are invalid
        else:
            raise TypeError(f'Invalid arguments: Expected either two integers or a tuple of two integers, received {args}.')
    
    @abstractmethod
    def convert_to_axial(self) -> AxialCoordinate:
        """
        Converts this coordinate instance to an axial coordinate.
        """
        pass
    
    @abstractmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'AbstractCoordinate':
        """
        Converts and returns this coordinate instance from an axial coordinate. Usually defined as a static method.
        """
        pass
    
    def __add__(self, other: 'AbstractCoordinate') -> 'AbstractCoordinate':
        """
        Adds two coordinate instances using axial conversion.
        """
        summed_axial = self.convert_to_axial() + other.convert_to_axial()
        return self.converted_from_axial(summed_axial)
    
    def __rmul__(self, factor: int) -> 'AbstractCoordinate':
        """
        Multiplies this coordinate instance by a factor, applying the operation in axial space.
        """
        muled_axial = factor * self.convert_to_axial()
        return self.converted_from_axial(muled_axial)
    
    def __lt__(self, other: 'AbstractCoordinate') -> bool:
        """
        Less than comparison for coordinates based on axial representation.
        """
        return self.convert_to_axial() < other.convert_to_axial()
    
    def __eq__(self, other: 'AbstractCoordinate') -> bool:
        """
        Equality comparison for coordinates based on axial representation.
        """
        return self.convert_to_axial() == other.convert_to_axial()
    
    def as_tuple(self):
        """
        Returns the coordinates as a tuple.
        """
        return tuple(getattr(self, field.name) for field in fields(self) if field.repr)
    
    def move(self, direction: ValidDirections, distance: int) -> 'AbstractCoordinate':
        """
        Moves this coordinate in a specified direction by a specified distance, and updates the instance.
        """
        moved_axial = self.convert_to_axial().move(direction, distance)
        new_recoords = self.converted_from_axial(moved_axial)
        
        # Update self
        for attr_name, attr_value in vars(new_recoords).items():
            setattr(self, attr_name, attr_value)
        return self
    
    def get_new_by_moving(self, direction: ValidDirections, distance: int) -> 'AbstractCoordinate':
        """
        Get a new coordinate by moving
        """
        new_coord = deepcopy(self)
        new_coord.move(direction, distance)
        return new_coord
    
    def get_new_by_moving(self, direction: ValidDirections, distance: int) -> 'AbstractCoordinate':
        """
        Get a new coordinate by moving
        """
        new_coord = deepcopy(self)
        new_coord.move(direction, distance)
        return new_coord
    
    def get_new_by_rotating(self, num_of_rotation: int) -> 'AbstractCoordinate':
        """
        Get a new coordinate by rotating clockwise

        Args:
            num_of_rotation (int): Rotate clockwise by num_of_rotation * 60 degrees, e.g. num_of_rotation = -2 means rotate by -120 degrees clockwise

        Returns:
            AbstractCoordinate: Rotated Coordinate
        """
        if not isinstance(num_of_rotation, int):
            raise ValueError(f'Invalid number of rotaion {num_of_rotation}')
        
        x, z = self.convert_to_axial().as_tuple()
        y = - x - z
        l = [x, y, z]
        
        def __coord_rotating(l: Sequence[int]) -> Sequence[int]:
            """
            Cube Coordinate changing with rotation clockwise
            
            Examples:
                Clockwise Rotation:
                    [x, y, z] --> [-y, -z, -x]
            """
            return [-l[1], -l[2], -l[0]]
        
        for _ in range(num_of_rotation % 6):
            l = __coord_rotating(l)
        
        return self.converted_from_axial(AxialCoordinate(l[0], l[2]))
    
    def get_neighbour(self, direction: ValidDirections) -> 'AbstractCoordinate':
        """
        Retrieves a neighboring coordinate based on the specified direction.
        """
        neighbour_axial = self.convert_to_axial().get_neighbour(direction)
        return self.converted_from_axial(neighbour_axial)
    
    def get_all_neighbour(self) -> list['AbstractCoordinate']:
        """
        Retrieves all neighboring coordinates.
        """
        axial_neighbour_list = self.convert_to_axial().get_all_neighbour()
        return [self.converted_from_axial(axial) for axial in axial_neighbour_list]


# ---------------------------------------------------------------------------------------------------------------------
#                                                           Ring Coordinate
# ---------------------------------------------------------------------------------------------------------------------
@dataclass    
class RingCoordinate(AbstractCoordinate):
    """
    A data class representing a ring coordinate
    
    Attributes:
        r (int): The Manhattan distance from the center point. Default value is 0, which represent the center.
        k (int): Starting from the positive x-axis, clockwise ordinal.
        name(str): The name of coordinate
        
    Example:
            (1,4)   (1,5)
        (1,3)   (0,0)   (1,0)
            (1,2)   (1,1)
    """
    r: int = 0
    k: int = 0
    name: str = field(default='ring', init=False, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return all(x >= 0 for x in coord)
    
    def convert_to_axial(self) -> AxialCoordinate:
        """
        The formula for convertion can be seen in ../document/conversion_formula.md

        Returns:
            AxialCoordinate: converted axial coordinate
        """
        r = self.r
        k = self.k
        
        x = ( + abs(k - 2 * r)  \
              + abs(k - 3 * r)  \
              - abs(k - 5 * r)  \
            ) / 2               \
              - k / 2 + r    
        
        z = ( - abs(k - 1 * r)  \
              - abs(k - 2 * r)  \
              + abs(k - 4 * r)  \
              + abs(k - 5 * r)  \
            ) / 2               \
              + k - 3 * r
              
        return AxialCoordinate(round(x), round(z))
    
    @staticmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'RingCoordinate':
        """
        The formula for convertion can be seen in ../document/conversion_formula.md

        Args:
            axial_coord (AxialCoordinate): target axial coordinate 

        Returns:
            RingCoordinate: converted ring coordinate
        """
        x = axial_coord.x
        z = axial_coord.z
        y = - x - z
        r = (abs(x) + abs(y) + abs(z)) / 2
        
        # rotate axial_coord counterclockwise until x >= 0 and z >= 0
        num_of_rotation = 0
        new_x, new_z = x, z
        new_axial_coord = deepcopy(axial_coord)
        while(new_x < 0 or new_z < 0):
            new_axial_coord = new_axial_coord.get_new_by_rotating(-1)
            new_x, new_z = new_axial_coord.as_tuple()
            num_of_rotation += 1
        k = num_of_rotation * r + new_z
        
        return RingCoordinate(round(r), round(k))
    
    @staticmethod
    def get_all_coord_by_r(r_max: int) -> list['RingCoordinate']:
        """
        Gererate all RingCoordinate whose r <= r_max
        """
        res_list = list()
        for x in range(-int(r_max), int(r_max) + 1):
            for y in range(-int(r_max), int(r_max) + 1):
                for z in range(-int(r_max), int(r_max) + 1):
                    if x + y + z == 0:
                        res_list.append(RingCoordinate.converted_from_axial(AxialCoordinate(x, z)))
        return res_list
        
# ---------------------------------------------------------------------------------------------------------------------
#                                                           Cube Coordinate
# ---------------------------------------------------------------------------------------------------------------------

@dataclass
class CubeCoordinate(AbstractCoordinate):
    """
    A data class representing a double_width coordinate
    
    Attributes:
        x (int): Increase from bottom left to top right
        y (int): Increase from bottom right to top left
        z (int): Increase from top to bottom
        name(str): The name of coordinate
        
    Example:
              (0,1,-1)    (1,0,-1)
        (-1,1,0)    (0,0,0)    (1,-1-0)
              (-1,0,1)    (0,-1,1)           
    """
    x: int = 0
    y: int = 0
    z: int = 0
    name: str = field(default='cube', init=False, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return super().coord_is_valid()
    
    def __init__(self, *args: Union[int, Sequence[int]]) -> None:
        # input Sequence[int]
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 3 and sum(args[0]) == 0:
            self.x, self.y, self.z = args[0]
            
        # input x, z
        elif len(args) == 2 and all(isinstance(arg, int) for arg in args): 
            self.x, self.y = args
            self.z = - self.x - self.y
            
        # input x, y, z
        elif len(args) == 3 and all(isinstance(arg, int) for arg in args) and sum(args) == 0:
            self.x, self.y, self.z = args
            
        # Raise TypeError
        else:
            raise TypeError(f'Invalid arguments {args}: Must be 3 int whose sum is 0.')
    
    def convert_to_axial(self) -> AxialCoordinate:
        return AxialCoordinate(self.x, self.z)
    
    @staticmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'CubeCoordinate':
        x = axial_coord.x
        z = axial_coord.z
        y = - x - z
        return CubeCoordinate(x, y, z)

# ---------------------------------------------------------------------------------------------------------------------
#                                                           Double Width Coordinate
# ---------------------------------------------------------------------------------------------------------------------

@dataclass
class DoubleWidthCoordinate(AbstractCoordinate):
    """
    A data class representing a double width coordinate
    
    Attributes:
        x (int): Increase 2 from left to right
        z (int): Increase from top to bottom
        name(str): The name of coordinate
        
    Example:
            (-1,-1)   (1,-1)
        (-2,0)   (0,0)   (2,0)
            (-1,1)   (1,1)     
    """
    x: int = 0
    z: int = 0
    name: str = field(default='double_width', init=False, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return super().coord_is_valid()
    
    def convert_to_axial(self) -> AxialCoordinate:
        return AxialCoordinate(round((self.x-self.z)/2), self.z)
    
    @staticmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'DoubleWidthCoordinate':
        x = 2 * axial_coord.x + axial_coord.z
        z = axial_coord.z
        return DoubleWidthCoordinate(x, z)
    
# ---------------------------------------------------------------------------------------------------------------------
#                                                           Cartesian Coordinate
# ---------------------------------------------------------------------------------------------------------------------
@dataclass
class CartesianCoordinate(AbstractCoordinate):
    """
    A data class representing a cartesian coordinate
    
    Attributes:
        x (float): Increase from left to right
        y (float): Increase from bottom to top
        name(str): The name of coordinate
        
    Example:
              (-1/2,sqrt(3)/2)       (1/2,sqrt(3)/2)
        (-1,0)                  (0,0)                (1,0)  
              (-1/2,-sqrt(3)/2)      (1/2,-sqrt(3)/2) 
    """
    x: float    = 0.
    y: float    = 0.
    tol: float  = field(default=1e-4, repr=False)
    name: str   = field(default='cartesian', init=False, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return super().coord_is_valid()
    
    def __init__(self, *args: Union[float, Sequence[float]]) -> None:
        # Input Sequence
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 2 and all(isinstance(arg, float) for arg in args[0]):
            self.x, self.y = args[0]
            
        # Input 2 floats           
        elif len(args) == 2 and all(isinstance(arg, float) for arg in args): 
            self.x, self.y = args
            
        # Raise TypeError
        else:
            raise TypeError(f'Invalid arguments {args}: Must be 2 floats or a sequence of 2 floats.')
    
    def convert_to_axial(self) -> AxialCoordinate:
        """
        Convert CartesianCoordinate to the NEAREST AxialCoordinate

        Returns:
            The NEAREST AxialCoordinate
        """
        x = round(self.x + self.z / np.sqrt(3))
        z = round(-2 * self.z / np.sqrt(3))
        return AxialCoordinate(x,z)
        
    @staticmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'CartesianCoordinate':
        x = axial_coord.x + axial_coord.z / 2
        z = -np.sqrt(3) * axial_coord.z / 2
        return CartesianCoordinate(x, z)
    
    def __rmul__(self, factor: float) -> 'CartesianCoordinate':
        return CartesianCoordinate(factor*self.x, factor*self.y)
    

# ---------------------------------------------------------------------------------------------------------------------
#                                                           Coordinate
# ---------------------------------------------------------------------------------------------------------------------
# Different coordinate representations which can be found at the following website: https://www.redblobgames.com/grids/hexagons/#coordinates-offset
class CoordinateFactory:
    
    # create coordinate_dict
    #  { 'ring' : RingCoordinate,
    #    'axial': AxialCoordinate,
    #    ...
    #  }
    coordinate_dict = dict()
    for coord_class in AbstractCoordinate.__subclasses__():
        coordinate_dict[getattr(coord_class, 'name')] = coord_class
    coordinate_dict['axial'] = AxialCoordinate
    
    @staticmethod
    def check_coord_type(coord_class: AbstractCoordinate) -> None:
        if not isinstance(coord_class, AxialCoordinate)  and not any(isinstance(coord_class, c_class) for c_class in AbstractCoordinate.__subclasses__()):
            raise ValueError(f'Invalid coordinary type \'{coord_class}\'.')

    @staticmethod
    def convert_all(coord_class: AbstractCoordinate) -> dict[ValidCoordinateType, AbstractCoordinate]:
        CoordinateFactory.check_coord_type(coord_class)
        res_dict = dict()
        axial_coord = coord_class.convert_to_axial()
        for c_type, c_class in CoordinateFactory.coordinate_dict.items():
            res_dict[c_type] = c_class.converted_from_axial(axial_coord)
        return res_dict
        
            

@dataclass
class Coordinate(AbstractCoordinate):
    """
    A data class storage all coordinate for a point
    """
    ring:           Optional[RingCoordinate]          = field(default=None)
    cube:           Optional[CubeCoordinate]          = field(default=None, repr=False)
    axial:          Optional[AxialCoordinate]         = field(default=None)

    double_width:  Optional[DoubleWidthCoordinate]    = field(default=None, repr=False)
    cartesian:      Optional[CartesianCoordinate]     = field(default=None, repr=False)
    
    def coord_is_valid(coord: Sequence[int]) -> bool:
        return super().coord_is_valid()

    def __init__(self, coord_class: AbstractCoordinate) -> None:
        CoordinateFactory.check_coord_type(coord_class)
        coord_dict = CoordinateFactory.convert_all(coord_class)
        for coord_type, coord_object in coord_dict.items():
            setattr(self, coord_type, coord_object)
            
    def convert_to_axial(self) -> AxialCoordinate:
        return self.axial
    
    @staticmethod
    def converted_from_axial(axial_coord: AxialCoordinate) -> 'Coordinate':
        return Coordinate(AxialCoordinate((axial_coord.x, axial_coord.z)))