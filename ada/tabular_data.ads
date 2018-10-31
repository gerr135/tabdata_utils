--
-- Top of Tabular_Data hierarchy.
-- Copyright (C) 2018  George Shapovalov <gshapovalov@gmail.com>
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.
--

with Ada.Strings.Unbounded;use Ada.Strings.Unbounded;
with Ada.Text_IO;
with Ada.Containers.Vectors;

package Tabular_Data is

    Debug : Boolean := False;

    --  supported file/data types
    type Tabular_Formats is (csv,atf,xvg);
    type FileExt is new String(1..3);
    type TabularFormat_ExtArray is array (Tabular_Formats) of FileExt;
    TabularFormat_Extensions : constant TabularFormat_ExtArray := ("csv", "atf", "xvg");

    -- root class, handling actual data. The IO methods are in the derived classes
    type TabularData is tagged private;
    function Npts(T : TabularData) return Natural;
    function Ncols(T : TabularData) return Positive;
    function has_time(T : TabularData) return Boolean;

    type CSV_Data is new TabularData with private;
    function  readCSV (F : Ada.Text_IO.File_Type) return CSV_Data;
--     procedure readCSV (T : out CSV_Data; F : Ada.Text_IO.File_Type);
    procedure writeCSV(T : out CSV_Data; F : Ada.Text_IO.File_Type);

    type ATF_Data is new TabularData with private;
    procedure readATF (T : out ATF_Data; F : Ada.Text_IO.File_Type);
    procedure writeATF(T : out ATF_Data; F : Ada.Text_IO.File_Type);

    type XVG_Data is new TabularData with private;
    procedure readATF (T : out XVG_Data; F : Ada.Text_IO.File_Type);
    procedure writeATF(T : out XVG_Data; F : Ada.Text_IO.File_Type);


private

    package UStrings is new Ada.Containers.Vectors (
        Element_Type => Unbounded_String, Index_Type => Positive);

    type TabularData is tagged record
        comment, header : UStrings.Vector;
        colID : UStrings.Vector;
    end record;

    type CSV_Data is new TabularData with null record;
    type ATF_Data is new TabularData with null record;
    type XVG_Data is new TabularData with null record;

end Tabular_Data;
