# First step with Pytango

Just playing and getting to know the API

```python
In [1]: import tango                                                                                                                                                                          

In [2]: tango.Database                                                                                                                                                                        
Out[2]: tango._tango.Database

In [3]: tango.Database()                                                                                                                                                                      
Out[3]: Database(127.0.0.1, 10000)

In [4]: database = _                                                                                                                                                                          

In [5]: database.get_device_name()                                                                                                                                                            
---------------------------------------------------------------------------
ArgumentError                             Traceback (most recent call last)
<ipython-input-5-73b10e603c6e> in <module>
----> 1 database.get_device_name()

ArgumentError: Python argument types in
    None.get_device_name(Database)
did not match C++ signature:
    get_device_name(Tango::Database {lvalue}, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >)

In [6]: database.get_device_name('*', '*')                                                                                                                                                    
Out[6]: DbDatum(name = '*', value_string = ['dserver/DataBaseds/2', 'dserver/Starter/29f704a99d50', 'dserver/TangoAccessControl/1', 'dserver/TangoTest/test', 'sys/access_control/1', 'sys/database/2', 'sys/tg_test/1', 'tango/admin/29f704a99d50'])

In [7]: tango.DeviceProxy('sys/tg_test/1')                                                                                                                                                    
Out[7]: TangoTest(sys/tg_test/1)

In [8]: tango_test_device = tango.DeviceProxy('sys/tg_test/1')                                                                                                                                

In [9]: tango_test_device.boolean_image                                                                                                                                                       
Out[9]: 
array([[False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       ...,
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False]])

In [10]: tango_test_device.read_attribute('boolean_image')                                                                                                                                    
Out[10]: 
DeviceAttribute(data_format = tango._tango.AttrDataFormat.IMAGE, dim_x = 251, dim_y = 251, has_failed = False, is_empty = False, name = 'boolean_image', nb_read = 63001, nb_written = 1, quality = tango._tango.AttrQuality.ATTR_VALID, r_dimension = AttributeDimension(dim_x = 251, dim_y = 251), time = TimeVal(tv_nsec = 0, tv_sec = 1572014880, tv_usec = 427142), type = tango._tango.CmdArgType.DevBoolean, value = array([[False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       ...,
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False]]), w_dim_x = 1, w_dim_y = 0, w_dimension = AttributeDimension(dim_x = 1, dim_y = 0), w_value = array([], shape=(0, 1), dtype=bool))

In [11]: tango_test_device = tango.DeviceProxy('sys/tg_test/1')  # creates connection, does not send data                                                                                     

In [12]: tango_test_device.read_attribute('boolean_image')  # sends data                                                                                                                      
Out[12]: 
DeviceAttribute(data_format = tango._tango.AttrDataFormat.IMAGE, dim_x = 251, dim_y = 251, has_failed = False, is_empty = False, name = 'boolean_image', nb_read = 63001, nb_written = 1, quality = tango._tango.AttrQuality.ATTR_VALID, r_dimension = AttributeDimension(dim_x = 251, dim_y = 251), time = TimeVal(tv_nsec = 0, tv_sec = 1572014913, tv_usec = 619470), type = tango._tango.CmdArgType.DevBoolean, value = array([[False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       ...,
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False]]), w_dim_x = 1, w_dim_y = 0, w_dimension = AttributeDimension(dim_x = 1, dim_y = 0), w_value = array([], shape=(0, 1), dtype=bool))

In [13]: tango_test_device.boolean_image  # an alias to read_attribute that returns a subset of the info                                                                                      
Out[13]: 
array([[False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       ...,
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False],
       [False, False, False, ..., False, False, False]])

In [14]: tango_test_device.poll_attribute('double_scalar', 1000)  # poll every 1000 ms                                                                                                        

In [15]: def callback(event): 
    ...:     print(event) 
    ...:                                                                                                                                                                                      

In [16]: tango_test_device.subscribe_event('double_scalar', tango.EventType.PERIODIC_EVENT, callback)                                                                                         
EventData[
     attr_name = 'tango://127.0.0.1:10000/sys/tg_test/1/double_scalar'
    attr_value = DeviceAttribute(data_format = tango._tango.AttrDataFormat.SCALAR, dim_x = 1, dim_y = 0, has_failed = False, is_empty = False, name = 'double_scalar', nb_read = 1, nb_written = 1, quality = tango._tango.AttrQuality.ATTR_VALID, r_dimension = AttributeDimension(dim_x = 1, dim_y = 0), time = TimeVal(tv_nsec = 0, tv_sec = 1572015178, tv_usec = 106427), type = tango._tango.CmdArgType.DevDouble, value = 248.39563653759686, w_dim_x = 1, w_dim_y = 0, w_dimension = AttributeDimension(dim_x = 1, dim_y = 0), w_value = 0.0)
        device = TangoTest(sys/tg_test/1)
           err = False
        errors = ()
         event = 'periodic'
reception_date = TimeVal(tv_nsec = 0, tv_sec = 1572015179, tv_usec = 78827)]

Out[16]: 1

EventData[
     attr_name = 'tango://127.0.0.1:10000/sys/tg_test/1/double_scalar'
    attr_value = DeviceAttribute(data_format = tango._tango.AttrDataFormat.SCALAR, dim_x = 1, dim_y = 0, has_failed = False, is_empty = False, name = 'double_scalar', nb_read = 1, nb_written = 1, quality = tango._tango.AttrQuality.ATTR_VALID, r_dimension = AttributeDimension(dim_x = 1, dim_y = 0), time = TimeVal(tv_nsec = 0, tv_sec = 1572015179, tv_usec = 106538), type = tango._tango.CmdArgType.DevDouble, value = 248.39563653759686, w_dim_x = 1, w_dim_y = 0, w_dimension = AttributeDimension(dim_x = 1, dim_y = 0), w_value = 0.0)
        device = TangoTest(sys/tg_test/1)
           err = False
        errors = ()
         event = 'periodic'
reception_date = TimeVal(tv_nsec = 0, tv_sec = 1572015179, tv_usec = 106787)]

In [17]: tango_test_device.unsubscribe_event(1)  
```
