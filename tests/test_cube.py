from HexLattice.coordinates import AxialCoordinate, CubeCoordinate

def test_cube_to_axial():
    """
    Cube coordinate
            (0,1,-1)    (1,0,-1)
    (-1,1,0)    (0,0,0)    (1,-1-0)
            (-1,0,1)    (0,-1,1)     
        
    Axial coordinate
        (0,-1)    (1,-1)  
    (-1,0)    (0,0)    (1,0)
        (-1,1)    (0,1)
    
    """
    cube_axial_coord_dict = {
        (+1, -1,  0): (+1,  0),
        ( 0, -1, +1): ( 0, +1),
        (-1,  0, +1): (-1, +1),
        ( 0, +1, -1): (-1,  0),
        ( 0, +1, -1): ( 0, -1),
        (+1,  0, -1): (+1, -1)
    }
    
    for cube_coord, axial_coord in cube_axial_coord_dict.items():
        rc = CubeCoordinate(cube_coord)
        ac = rc.convert_to_axial()
        rc_converted = rc.converted_from_axial(AxialCoordinate(axial_coord))
        assert (ac.x, ac.z) == axial_coord
        assert(rc_converted) == rc