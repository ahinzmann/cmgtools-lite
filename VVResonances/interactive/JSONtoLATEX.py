import glob
import os
import json


class JSONtoLaTeXtableParser:

    def __init__(self, path, output_file):
        """
        Constructor. Set path where the JSON files are stored,
        e. g. "/some/path/to/results/*/*.json"
        Also filename for output file is needed
        """
        self.files = glob.glob(path)
        self.lines = []
        self.out = output_file


    def __build_latex_tab_string(self, data, args):
        """ extract values from data using keywords from args """
        s = ""
        for i, key in enumerate(args):
            if i < len(args) - 1:
                s += str(data[key]) + " & "
            else:
                s += str(data[key]) + "\\" + "\\"
        return s


    def parse_first_level_to_latex_tab(self, *args):
        """ extract data from flat dictionary """
        self.header= args
        for file_n in self.files:
            with open(file_n, 'r') as fd:
                data = json.load(fd)
                s = self.__build_latex_tab_string(data, args)
                self.lines.append(s)


    def parse_second_level_to_latex_tab(self, first_level_key, *args):
        """ extract data from a dictionary within a dictionary """
        self.header= args
        for file_n in self.files:
            with open(file_n, 'r') as fd:
                data = json.load(fd)[first_level_key]
                s = self.__build_latex_tab_string(data, args)
                self.lines.append(s)


    def parse_x_level_to_latex_tab(self, level, *args):
        """
        extract data from a dictionary within a dictionary
        within a dictionary ... e. g.:
        result[level1][level2][level3] ...
        """
        self.header= args
        for file_n in self.files:
            with open(file_n, 'r') as fd:
                data = json.load(fd)
                for l in level:
                    data = data[l]
                s = self.__build_latex_tab_string(data, args)
                self.lines.append(s)


    def create_latex_table(self):
        """
        create simple LaTeX table based on extracted data.
        """
        self.table = "\\begin{tabular}{|"
        self.table += len(self.header) * "l|" + "} \\hline \n"
        for i, h in enumerate(self.header):
            if i < len(self.header) - 1:
                self.table += h.replace("_", " ") + " & "
            else:
                self.table += h.replace("_", " ") + " \\" + "\\ \\hline \n"
        for line in self.lines:
            self.table += line + "\n"
        self.table += "\\hline \n"
        self.table += "\\end{tabular}"


    def write_rows_to_file(self):
        """ write only rows with extracted data to file"""
        with open(self.out, 'w') as fd:
            for line in self.lines:
                fd.write(line + "\n")


    def write_table_to_file(self):
        """ write complete table to file """
        with open(self.out, 'w') as fd:
            fd.write(self.table)
