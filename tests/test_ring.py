from HexLattice.coordinates import AxialCoordinate, RingCoordinate

def test_ring_to_axial():
    """
    Ring coordinate
        (1,4)   (1,5)
    (1,3)   (0,0)   (1,0)  
        (1,2)   (1,1)
        
    Axial coordinate
        (0,-1)    (1,-1)  
    (-1,0)    (0,0)    (1,0)
        (-1,1)    (0,1)
    
    """
    ring_axial_coord_dict = {
        (1, 0): (+1,  0),
        (1, 1): ( 0, +1),
        (1, 2): (-1, +1),
        (1, 3): (-1,  0),
        (1, 4): ( 0, -1),
        (1, 5): (+1, -1)
    }
    
    for ring_coord, axial_coord in ring_axial_coord_dict.items():
        rc = RingCoordinate(ring_coord)
        ac = rc.convert_to_axial()
        rc_converted = rc.converted_from_axial(AxialCoordinate(axial_coord))
        assert (ac.x, ac.z) == axial_coord
        assert(rc_converted) == rc