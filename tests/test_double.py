from HexLattice.coordinates import AxialCoordinate, DoubleHeightCoordinate, DoubleWidthCoordinate

def test_double_to_axial():
    """
    Double-Width coordinate
        (-1,-1)   (1,-1)
    (-2,0)   (0,0)   (2,0)
        (-1,1)   (1,1) 
        
    Double-Height coordinate
        (0,-2)   (1,-1)
    (-1,-1)   (0,0)   (1,1)
        (-1,1)   (0,2)     
        
    Axial coordinate
        (0,-1)    (1,-1)  
    (-1,0)    (0,0)    (1,0)
        (-1,1)    (0,1)
    
    """
    double_axial_coord_dict = {
        (( 2,  0), ( 1,  1)): (+1,  0),
        (( 1,  1), ( 0,  2)): ( 0, +1),
        ((-1,  1), (-1,  1)): (-1, +1),
        ((-2,  0), (-1, -1)): (-1,  0),
        ((-1, -1), ( 0, -2)): ( 0, -1),
        (( 1, -1), ( 1, -1)): (+1, -1)
    }
    
    for double_coord, axial_coord in double_axial_coord_dict.items():
        dwc = DoubleWidthCoordinate(double_coord[0])
        dhc = DoubleHeightCoordinate(double_coord[1])
        ac_w = dwc.convert_to_axial()
        ac_h = dhc.convert_to_axial()
        dwc_converted = dwc.converted_from_axial(AxialCoordinate(axial_coord))
        dhc_converted = dhc.converted_from_axial(AxialCoordinate(axial_coord))
        assert (ac_w.x, ac_w.z) == axial_coord
        assert (ac_h.x, ac_h.z) == axial_coord
        assert(dwc_converted) == dwc
        assert(dhc_converted) == dhc
        