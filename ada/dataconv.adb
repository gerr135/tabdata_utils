--
-- convert between various (text) formats of tabular data
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

with Ada.Command_Line, GNAT.Command_Line;
with Ada.Directories, Ada.Environment_Variables;
with Ada.Text_IO;
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;
-- all methods in .Unbounded are easy to ident and have unique names, no need to hide visibility

with Tabular_Data;

procedure dataconv is

    procedure printUsage is
        use Ada.Text_IO;
    begin
        Put_Line ("convert data in tabular form from one  (text) fomat to another.");
        New_Line;
        Put_Line ("usage:");
        Put_Line ("   " & Ada.Command_Line.Command_Name & " [-h -g -n: -v]  infile outfile");
        New_Line;
        Put_Line ("options:");
        Put_Line ("-h      print this help");
        Put_Line ("-i      input format, one of [csv,atf,xvg] (try to guess if omitted)");
        Put_Line ("-k      output format, one of [cvs,atf,xvg] (if omitted, go by extension)");
--         Put_Line ("-o      output file name (stdout if skipped)");
        Put_Line ("-v      be verbose");
    end printUsage;
    Finish : exception;

    type ParamRec is record
        inFN, outFN  : Unbounded_String := Null_Unbounded_String;
        iFmt, oFmt   : Unbounded_String := Null_Unbounded_String;
        Debug   : Boolean := False;
    end record;

    procedure processCommandLine (params : in out ParamRec) is
        use Ada.Command_Line, GNAT.Command_Line, Ada.Text_IO;
        Options : constant String := "h i: k: v";
    begin
        if Argument_Count < 2 then
            printUsage;
            raise Finish;
        end if;
        begin -- need to process local exceptions
            loop
                case Getopt (Options) is
                    when ASCII.NUL =>
                        exit;
                    --  end of option list
                    when 'v' => params.Debug := True;
                    when 'h' =>
                        printUsage;
                        raise Finish;
                    when 'i' => params.iFmt := To_Unbounded_String(Parameter);
                    when others =>
                        raise Program_Error;
                        --  serves to catch "damn, forgot to include that option here"
                end case;
            end loop;
        exception
            when Invalid_Switch =>
                Put_Line ("Invalid Switch " & Full_Switch);
                raise Finish;
            when Invalid_Parameter =>
                Put_Line ("No parameter for " & Full_Switch);
                raise Finish;
            when Data_Error =>
                Put_Line ("Invalid numeric format for switch" & Full_Switch);
                raise Finish;
        end;
        params.inFN  := To_Unbounded_String (Get_Argument (Do_Expansion => True));
        params.outFN := To_Unbounded_String (Get_Argument (Do_Expansion => True));
    end processCommandLine;

    use Ada.Text_IO;
    use Tabular_Data;

    params : ParamRec;
    Fin, Fout : File_Type;



begin  -- main
    processCommandLine (params);
    Open(Fin, Mode=>In_File, Name=>To_String(params.inFN));
    declare
        DD : TabularData'Class := readCSV(Fin);
    begin
        Close(Fin);
        Open(Fout, Mode=>Out_File, Name=>To_String(params.outFN));
        ATF_Data(DD).writeATF(Fout);
        Close(Fout);
    end;
exception
	when Finish => null;
end dataconv;
