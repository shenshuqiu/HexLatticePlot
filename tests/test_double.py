from HexLattice.coordinates import AxialCoordinate, DoubleWidthCoordinate

def test_double_to_axial():
    """
    Double-Width coordinate
        (-1,-1)   (1,-1)
    (-2,0)   (0,0)   (2,0)
        (-1,1)   (1,1)

    Axial coordinate
        (0,-1)    (1,-1)
    (-1,0)    (0,0)    (1,0)
        (-1,1)    (0,1)
    """
    double_axial_coord_dict = {
        ( 2,  0): (+1,  0),
        ( 1,  1): ( 0, +1),
        (-1,  1): (-1, +1),
        (-2,  0): (-1,  0),
        (-1, -1): ( 0, -1),
        ( 1, -1): (+1, -1)
    }
    
    for double_coord, axial_coord in double_axial_coord_dict.items():
        dwc = DoubleWidthCoordinate(*double_coord)
        ac_w = dwc.convert_to_axial()
        dwc_converted = dwc.converted_from_axial(AxialCoordinate(axial_coord))
        assert (ac_w.x, ac_w.z) == axial_coord
        assert dwc_converted == dwc
        
