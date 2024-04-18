import numpy as np

from HexLattice.coordinates import AxialCoordinate, CartesianCoordinate

def test_cartesian_to_axial():
    """
    Cartesian coordinate
            (-1/2,sqrt(3)/2)       (1/2,sqrt(3)/2)
    (-1,0)                  (0,0)                (1,0)  
            (-1/2,-sqrt(3)/2)      (1/2,-sqrt(3)/2)   
        
    Axial coordinate
        (0,-1)    (1,-1)  
    (-1,0)    (0,0)    (1,0)
        (-1,1)    (0,1)
    
    """
    cartesian_axial_coord_dict = {
        (1, 0)                  : (+1,  0),
        ( 1/2, -np.sqrt(3)/2)   : ( 0, +1),
        (-1/2, -np.sqrt(3)/2)   : (-1, +1),
        (-1, 0)                 : (-1,  0),
        (-1/2,  np.sqrt(3)/2)   : ( 0, -1),
        ( 1/2,  np.sqrt(3)/2)   : (+1, -1)
    }
    
    for cartesian_coord, axial_coord in cartesian_axial_coord_dict.items():
        cc = CartesianCoordinate(cartesian_coord)
        ac = cc.convert_to_axial()
        cc_converted = cc.converted_from_axial(AxialCoordinate(axial_coord))
        assert all(np.isclose((ac.x, ac.z), axial_coord, atol=1e-5))
        assert all(np.isclose((cc_converted.x, cc_converted.z), (cc.x, cc.z), atol=1e-5))