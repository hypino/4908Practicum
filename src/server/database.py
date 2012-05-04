import tables
import numpy
import datetime

class Record(tables.IsDescription):
    # columns
    timeStamp = Int64Col()
    col1 = Float64Col()
    col2 = Float64Col()
    col3 = Float64Col()
    col4 = Float64Col()
    col5 = Float64Col()
    col6 = Float64Col()
    col7 = Float64Col()
    col8 = Float64Col()
    
