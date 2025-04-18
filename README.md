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

## refactoring remarks
A mini-plan for the refactoring branch

### Rationale
We need to add calc capabilities. At the very least fitting, normalization, baseline correction. 
Potentially a full algebra. This is best done via numpy facilities. However numpy arrays are
fixed size. Adding new rows/columns is possible via stacking, but this would recreate/copy arrays
and seems rather wasteful. Plus the IO code is well tested by now. So, we need to support alternative
data representations it seems.

### Implementation
Support alternative representations. Keep list-based class for the IO (primarily reading). 
Add numpy.array-based class for computation. Go with class hierarchy. Use abstract class at the top, 
or just raise exceptions on data access methods?

<L> class TabDataBase  - abstract or with stub methods?
<L> class TabDataFlex  - old, list-based data. Supports full IO, but no calc.
<L> class TabDataNP    - new, numpy.array-based data. Supports cala, for IO supports writes, but not reads?
