# tabdata_utils
A collection of utils to convert and process data in various (text) tabular formats
(mainly simulations and electrophysiology)

This is a collection of recent code to process data files in text formats, generic
tabular and specific to electrophysiology and MD simulations (.atf, .xvg produced by
gromacs and similar).

The actual useful utils are under util/ subdir, they use the actual datatype/converter
class defined under lib/. So, you need both dirs if you copy this code somewhere.
The tests/ subdir contains test units that are used during development, using sample data
under dat/.
The ada/ dir contains initial (very bare, far from complete) code to do a similar thing in
Ada (the lack of proper data organization and type checking in python makes for quite a
ride when you come back to your code say 10 years later. But this is more of an excersize,
so this part will likely see only sporadic development).
