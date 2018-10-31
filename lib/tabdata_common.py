#
# Common code for TabData class files - exceptions, constants, etc..
# Copyright (C) 2018  George Shapovalov <gshapovalov@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class TabData_Error(Exception):
    """Base data format exception."""
    pass

class FormatMismatch(TabData_Error):
    "a subclass of IO formatting exceptions"

class CSV_Error(TabData_Error):
    "Error in base csv file format"

class HEKA_CSV_Error(FormatMismatch):
    """Error with the data format in HEKA csv file."""
    pass
class ATF_Error(FormatMismatch):
    """Error with the data format in atf file."""
    pass
class XVG_Error(FormatMismatch):
    """Error with the data format in xvg (xmgrace) file."""
    pass

class DimensionMismatch(TabData_Error):
    "a subclass for exceptions when pairing two tables of incompatibel dimensions"


TabData_Formats = ["csv","atf","xvg","heka_csv"]
TabData_Format_Extensions = ["csv","atf","xvg","dat"]
