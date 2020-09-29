"""
Core module defining the functions for converting a consumption Markov Decision 
Process from consMDP model to dot representation and present it. 
"""

import subprocess
import sys
dotpr = 'dot'
debug = False

from math import inf

from .objectives import *

#TODO build a list and join it in the end into string

default_MI_style         = ' border="0" cellborder="0" cellspacing="0"' +\
                       ' cellpadding="1" align="center" valign="middle"' +\
                       ' style="rounded" bgcolor="#ffffff50"'
if debug:
    default_MI_style         = ' border="1" cellborder="1" cellspacing="0" cellpadding="0"'

tab_state_cell_style = ' rowspan="{}"'

cell_style    = ' align="center" valign="middle"'
tab_MI_cell_font     = ' color="orange" point-size="10"'

tab_SR_cell_font     = ' color="red" point-size="10"'

# Positive reachability
tab_PR_cell_font     = ' color="deepskyblue" point-size="10"'

# Almost sure reachability
tab_AR_cell_font     = ' color="dodgerblue4" point-size="10"'

# Reachability-safe
tab_RS_cell_font     = ' color="blue4" point-size="10"'

# Büchi
tab_BU_cell_font     = ' color="forestgreen" point-size="10"'

# Büchi-safe
tab_BS_cell_font     = ' color="darkgreen" point-size="10"'

targets_style        = ', style="filled", fillcolor="#0000ff20"'
targets_Buchi_style  = ', style="filled", fillcolor="#00ff0020"'

default_options = "msrRb"

class consMDP2dot:
    """Convert consMDP to dot"""

    def __init__(self, mdp, solver=None, options=""):
        self.mdp = mdp
        self.str = ""

        if options != "" and options[0] == ".":
            self.options = default_options + options[1:]
        else:
            self.options = default_options


        self.act_color = "black"
        self.prob_color = "gray52"
        self.label_row_span = 2


        self.opt_mi = {"name": "MinInitCons", "enabled": False, "color": "orange"}
        self.opt_sr = {"name": "Safe levels", "enabled": False, "color": "color"}
        self.opt_pr = {"name": "Positive reachability", "enabled": False, "color": "deepskyblue"}
        self.opt_ar = {"name": "Almost-sure reachability", "enabled": False, "color": "dodgerblue4"}
        self.opt_bu = {"name": "Büchi", "enabled": False, "color": "forestgreen"}
        # ?? reachability safe  - buchi safe

        self.options_list = []


        self.el = solver
        self.targets = None if solver is None else solver.targets

        if "m" in self.options:
            self.opt_mi["enabled"] = self.el is not None and MIN_INIT_CONS in self.el.min_levels
            self.options_list.append(self.opt_mi)

        if "s" in self.options:
            self.opt_sr["enabled"] = self.el is not None and SAFE in self.el.min_levels
            self.options_list.append(self.opt_sr)

        if "P" in self.options:
            self.opt_pr["enabled"] = self.el is not None and POS_REACH in self.el.min_levels
            self.options_list.append(self.opt_pr)

        if "R" in self.options:
            self.opt_ar["enabled"] = self.el is not None and AS_REACH in self.el.min_levels
            self.options_list.append(self.opt_ar)
        elif "r" in self.options:
            self.opt_ar["enabled"] = self.el is not None and AS_REACH in self.el.min_levels
            self.options_list.append(self.opt_ar)

        if "b" in self.options:
            self.opt_bu["enabled"] = self.el is not None and BUCHI in self.el.min_levels
            self.options_list.append(self.opt_bu)
            if self.opt_bu:
                self.label_row_span = 3

    def get_dot(self):
        self.start()

        m = self.mdp
        for s in range(m.num_states):
            self.process_state(s)
            for a in m.actions_for_state(s):
                self.process_action(a)
        self.add_key()
        self.finish()
        return self.str

    def start(self):
        gr_name = self.mdp.name if self.mdp.name else ""

        self.str += f"digraph \"{gr_name}\" {{\n"
        self.str += "  rankdir=LR\n"

    def finish(self):
        self.str += "}\n"

    def get_state_name(self, s):
        name = s if self.mdp.names[s] is None else self.mdp.names[s]
        return name
    
    def process_state(self, s):
        self.str += f"\n  {s} [shape=rectangle, style=rounded, "

        # name
        state_str = self.get_state_name(s)

        # minInitCons
        if self.opt_mi["enabled"] or \
                self.opt_sr["enabled"] or \
                self.opt_pr["enabled"] or \
                self.opt_ar["enabled"] or \
                self.opt_bu["enabled"]:
            state_str = f"<table{default_MI_style}>" + \
                        f"<tr><td{tab_state_cell_style.format(self.label_row_span)}>{state_str}</td>"

        if self.opt_mi["enabled"]:
            val = self.el.get_min_levels(MIN_INIT_CONS)[s]
            val = "∞" if val == inf else val
            state_str += f"<td{cell_style}>" + \
                f"<font{tab_MI_cell_font}>{val}</font></td>"

        if self.opt_sr["enabled"]:
            val = self.el.get_min_levels(SAFE)[s]
            val = "∞" if val == inf else val
            state_str += f"<td{cell_style}>" + \
                f"<font{tab_SR_cell_font}>{val}</font></td>"

        if self.opt_mi["enabled"] or \
                self.opt_sr["enabled"] or \
                self.opt_pr["enabled"] or \
                self.opt_bu["enabled"]:
            state_str += f"</tr><tr>"

            empty_row = True
            # positive reachability
            if self.opt_pr["enabled"]:
                empty_row = False
                val = self.el.get_min_levels(POS_REACH)[s]
                val = "∞" if val == inf else val
                state_str += f"<td{cell_style}>" + \
                    f"<font{tab_PR_cell_font}>{val}</font></td>"

            # almost-sure reachability
            if self.opt_ar["enabled"]:
                empty_row = False
                val = self.el.get_min_levels(AS_REACH)[s]
                val = "∞" if val == inf else val
                state_str += f"<td{cell_style}>" + \
                    f"<font{tab_AR_cell_font}>{val}</font></td>"
                val = self.el.helper_levels[AS_REACH][s]
                val = "∞" if val == inf else val
                state_str += f"<td{cell_style}>" + \
                    f"<font{tab_RS_cell_font}>{val}</font></td>"

            if empty_row:
                state_str += "<td></td>"

            # buchi
            if self.opt_bu["enabled"]:
                state_str += f"</tr><tr>"
                empty_row = False
                val = self.el.get_min_levels(BUCHI)[s]
                val = "∞" if val == inf else val
                state_str += f"<td{cell_style}>" + \
                    f"<font{tab_BU_cell_font}>{val}</font></td>"
                val = self.el.helper_levels[BUCHI][s]
                val = "∞" if val == inf else val
                state_str += f"<td{cell_style}>" + \
                    f"<font{tab_BS_cell_font}>{val}</font></td>"

            if empty_row:
                state_str += "<td></td>"

            state_str += "</tr></table>"

        self.str += f'label=<{state_str}>'

        # Reload states are double circled and target states filled
        if self.mdp.is_reload(s):
            self.str += ", peripheries=2"
        if self.targets is not None and s in self.targets and \
                (self.opt_pr["enabled"] or \
                 self.opt_ar["enabled"] or \
                 self.opt_bu):
            self.str += targets_style
        self.str += "]\n"


    def add_key(self):
        self.str += "subgraph {\n\ntbl [\n\nshape=plaintext\n\nlabel=<\n\n<table border='0' cellborder='1' color='blue' cellspacing='0'>\n"
        self.str += "<tr><td>Key</td></tr>\n"
        self.str += "<tr><td cellpadding='0'>\n<table color='black' cellspacing='2'>\n"
        self.str += "<tr><td>one  </td><td>two  </td><td>three</td></tr>\n"
        self.str += "<tr><td>four </td><td>five </td><td>six  </td></tr>\n"
        self.str += "<tr><td>seven</td><td>eight</td><td>nine </td></tr>\n"
        for opt in self.options_list:
            name = opt["name"]
            color = opt["color"]
            self.str += "<tr>"
            self.str += f"<td>{name.format(color)}</td>"
            self.str += "</tr>\n"

        self.str += "\n</table>\n</td>\n</tr>\n </table>\n>];\n}"

    def process_action(self, a):
        act_id = f"\"{a.src}_{a.label}\""
        
        # Src -> action-node
        self.str += f"    {a.src} -> {act_id}"
        self.str += f"[arrowhead=onormal,label=\"{a.label}: {a.cons}\""
        self.str += f", color={self.act_color}, fontcolor={self.act_color}]\n"
        
        # action-node
        self.str += f"    {act_id}[label=<>,shape=point]\n"
        
        # action-node -> dest
        for dst, p in a.distr.items():
            self.str += f"      {act_id} -> {dst}[label={p}, color={self.prob_color}, fontcolor={self.prob_color}]"
        

def dot_to_svg(dot_str):
    """
    Send some text to dot for conversion to SVG.
    """
    try:
        dot_pr = subprocess.Popen([dotpr, '-Tsvg'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("The command 'dot' seems to be missing on your system.\n"
              "Please install the GraphViz package "
              "and make sure 'dot' is in your PATH.", file=sys.stderr)
        raise

    stdout, stderr = dot_pr.communicate(dot_str.encode('utf-8'))
    if stderr:
        print("Calling 'dot' for the conversion to SVG produced the message:\n"
              + stderr.decode('utf-8') + dot_str, file=sys.stderr)
    ret = dot_pr.wait()
    if ret:
        raise subprocess.CalledProcessError(ret, 'dot')
    return stdout.decode('utf-8')
