"""
Core module defining the functions for converting a consumption Markov Decision 
Process from consMDP model to dot representation and present it. 
"""

import subprocess
import sys
import math

dotpr = 'dot'

from .objectives import *
from .objectives import _HELPER_AS_REACH, _HELPER_BUCHI

tab_state_cell_style = ' rowspan="{}"'
cell_style    = ' align="center" valign="middle"'
targets_style        = ', style="filled", fillcolor="#0000ff20"'
default_table_style         = ' border="0" cellborder="0" cellspacing="0"' +\
                       ' cellpadding="1" align="center" valign="middle"' +\
                       ' style="rounded" bgcolor="#ffffff50"'

default_options = "sprb<50"

# For each letter set a list of objectives that should be displayed
opt_to_objs = {
    "m": [MIN_INIT_CONS],
    "s": [SAFE],
    "p": [POS_REACH],
    "r": [AS_REACH],
    "R": [AS_REACH, _HELPER_AS_REACH],
    "b": [BUCHI],
    "B": [BUCHI, _HELPER_BUCHI],
}

table_shape = [
    [SAFE, POS_REACH, AS_REACH, BUCHI],
    [MIN_INIT_CONS, "dummy", _HELPER_AS_REACH, _HELPER_BUCHI]
]

class consMDP2dot:
    """Convert consMDP to dot"""

    def __init__(self, mdp, solver=None, options=""):
        self.mdp = mdp

        self.opt_string = default_options
        if options:
            if options[0] == ".":
                self.opt_string += options[1:]
            else:
                self.opt_string = options

        max_states = math.inf
        max_i = self.opt_string.find("<")
        if max_i > -1:
            pos = max_i + 1
            max_v = ""
            while pos < len(self.opt_string) and self.opt_string[pos].isdigit():
                max_v += self.opt_string[pos]
                pos += 1
            max_states = int(max_v)

        self._opts = {
            "print_legend" : "l" in self.opt_string,
            "print_MELs" : False,
            "max_states" : max_states
        }

        self.act_color = "black"
        self.prob_color = "gray52"

        self.solver = solver
        self.targets = [] if solver is None else solver.targets

        # Trim the mdp if needed
        self.incomplete = set()
        if self.mdp.num_states > max_states:
            from .utils import copy_consmdp
            self.mdp, state_map = copy_consmdp(self.mdp,
                                               max_states=max_states,
                                               solver=solver)
            self.incomplete = self.mdp.incomplete
            # Update targets accordingly
            self.targets = [state_map[s] for s in state_map if s in self.targets]

        if solver is None:
            self.mel_values = None
        else:
            self.mel_values = solver.min_levels.copy()
            helpers = solver.helper_levels.copy()

            # Rename states for trimmed automata
            if self.incomplete:
                for objective in self.mel_values:
                    vals = self.mel_values[objective]
                    new_vals = []
                    for s, p in state_map.items():
                        new_vals.append(vals[s])
                    self.mel_values[objective] = new_vals
                for objective in helpers:
                    vals = helpers[objective]
                    new_vals = []
                    for s, p in state_map.items():
                        new_vals.append(vals[s])
                    helpers[objective] = new_vals

            if AS_REACH in helpers:
                self.mel_values[_HELPER_AS_REACH] = helpers[AS_REACH]
            if BUCHI in helpers:
                self.mel_values[_HELPER_BUCHI] = helpers[BUCHI]

        # Prepare for printing MELs
        self._mel_opts = {
            "print": False,
            "rows": [False, False],
            "cols":  [False, False, False, False],
            "shape": table_shape,
        }

        self.mel_settings = dict()
        self.mel_settings[SAFE] = {
            "name": "Safe levels",
            "enabled": False,
            "color": "red",
        }

        self.mel_settings[POS_REACH] = {
            "name": "Positive reachability",
            "enabled": False,
            "color": "deepskyblue",
        }

        self.mel_settings[AS_REACH] = {
            "name": "Almost-sure reachability",
            "enabled": False,
            "color": "dodgerblue4",
        }

        self.mel_settings[BUCHI] = {
            "name": "Büchi",
            "enabled": False,
            "color": "forestgreen",
        }

        self.mel_settings[MIN_INIT_CONS] = {
            "name": "MinInitCons",
            "enabled": False,
            "color": "orange",
        }

        self.mel_settings[_HELPER_AS_REACH] = {
            "name": "Reachability-safe",
            "enabled": False,
            "color": "blue4",
        }

        self.mel_settings[_HELPER_BUCHI] = {
            "name": "Büchi-safe",
            "enabled": False,
            "color": "darkgreen",
        }

        self.mel_settings["dummy"] = {
            "enabled": False,
        }

        # Resolve which values should be printed
        requested = set()
        for opt in opt_to_objs:
            if opt in self.opt_string:
                requested.update(opt_to_objs[opt])

        if not self.mel_values is None:
            for row, cols in enumerate(self._mel_opts["shape"]):
                for col, objective in enumerate(cols):
                    enabled = objective in requested and \
                              objective in self.mel_values

                    if enabled:
                        self.mel_settings[objective]["enabled"] = True
                        self._opts["print_MELs"] = True
                        self._mel_opts["rows"][row] = True
                        self._mel_opts["cols"][col] = True

        self.res = ""

    def get_dot(self):
        self.start()

        m = self.mdp
        for s in range(m.num_states):
            self.process_state(s)
            for a in m.actions_for_state(s):
                self.process_action(a)
            if s in self.incomplete:
                self.add_incomplete(s)
        if self._opts["print_legend"]:
            self.add_key()
        self.finish()
        return self.res

    def start(self):
        gr_name = self.mdp.name if self.mdp.name else ""

        self.res += f"digraph \"{gr_name}\" {{\n"
        self.res += "  rankdir=LR\n"

    def finish(self):
        self.res += "}\n"

    def get_state_name(self, s):
        name = str(s) if self.mdp.names[s] is None else self.mdp.names[s]
        return name
    
    def process_state(self, s):
        self.res += f"\n  {s} ["

        # name
        name = self.get_state_name(s)

        # Create the state label (a table if MELs requested)
        if self._opts["print_MELs"]:
            state_str = f"<table{default_table_style}>"

            # Start with a state name
            rows = sum(self._mel_opts["rows"])
            state_str += f"<tr><td rowspan='{rows}'>{name}</td>"

            print_tr = False
            for row, cols in enumerate(self._mel_opts["shape"]):
                if print_tr:
                    state_str += f"<tr>"

                for col, objective in enumerate(cols):
                    settings = self.mel_settings[objective]
                    if not self._mel_opts["cols"][col]:
                        continue
                    if not settings["enabled"]:
                        state_str += "<td></td>"
                        continue

                    color = settings["color"]
                    val = self.mel_values[objective][s]
                    if val == math.inf:
                        val = "∞"
                    state_str += f"<td{cell_style}>" \
                                 f"<font color='{color}' point-size='10'>" \
                                 f"{val}</font></td>"
                state_str += "</tr>"
                print_tr = True

            state_str += "</table>"
        else:
            state_str = name

        self.res += f'label=<{state_str}>'

        # Reload states are double circled and target states filled
        if self.mdp.is_reload(s):
            self.res += ", peripheries=2"
        if self.targets is not None and s in self.targets:
            self.res += targets_style
        self.res += "]\n"

    def add_incomplete(self, s):
        """
        Adds a dashed line from s to a dummy ... node for the given state s.
        """
        self.res += f'\n  u{s} [label="...", shape=none, width=0, height=0, ' \
                    f'tooltip="hidden successors"]\n  {s} -> u{s} ' \
                    f'[style=dashed, tooltip="hidden successors"]'

    def add_key(self):
        if not self._opts["print_MELs"]:
            return
        cols = sum(self._mel_opts["cols"])
        self.res += "subgraph {\n\ntbl [color = white,\n\nlabel=<\n\n<table border='0' cellborder='1' color='black' cellspacing='0'>\n"
        self.res += f"<tr><td colspan='{cols}'>Legend</td></tr>\n"

        for row, cols in enumerate(self._mel_opts["shape"]):
            if not self._mel_opts["rows"][row]:
                continue
            self.res += "<tr>"
            for col, objective in enumerate(cols):
                settings = self.mel_settings[objective]
                if not self._mel_opts["cols"][col]:
                    continue
                if not settings["enabled"]:
                    self.res += "<td></td>"
                    continue
                color = settings["color"]
                val = settings["name"]
                self.res += f"<td{cell_style}>" \
                             f"<font color='{color}' point-size='10'>" \
                             f"{val}</font></td>"
            self.res += "</tr>"

        self.res += "</table>\n>];\n}"

    def process_action(self, a):
        act_id = f"\"{a.src}_{a.label}\""
        
        # Src -> action-node
        self.res += f"    {a.src} -> {act_id}"
        self.res += f"[arrowhead=onormal,label=\"{a.label}: {a.cons}\""
        self.res += f", color={self.act_color}, fontcolor={self.act_color}]\n"
        
        # action-node
        self.res += f"    {act_id}[label=<>,shape=point]\n"
        
        # action-node -> dest
        for dst, p in a.distr.items():
            self.res += f"      {act_id} -> {dst}[label={p}, color={self.prob_color}, fontcolor={self.prob_color}]"
        

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
