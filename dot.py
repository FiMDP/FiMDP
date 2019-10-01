import subprocess
import sys

from math import inf
#TODO build a list and join it in the end into string

tab_MI_style      = ' border="0" cellborder="0" cellspacing="0"'
tab_MI_cell_style = ' bgcolor="white"'
tab_MI_cell_font  = ' color="orange" point-size="10"'

tab_SR_cell_style = ' bgcolor="white"'
tab_SR_cell_font  = ' color="red" point-size="10"'

default_options = "ms"

class consMDP2dot:
    """Convert consMDP to dot"""
    
    def __init__(self, mdp, options=""):
        self.mdp = mdp
        self.str = ""
        self.options = default_options + options

        self.act_color = "blue"

        self.opt_mi = False
        self.opt_sr = False

        MI = mdp.minInitCons

        if "m" in self.options:
            self.opt_mi = MI is not None and MI.values is not None
        if "M" in self.options:
            mdp.get_minInitCons()
            self.opt_mi = True

        if "s" in self.options:
            self.opt_sr = MI is not None and MI.safe_values is not None
        if "S" in self.options:
            mdp.get_safeReloads()
            self.opt_sr = True

    def get_dot(self):
        self.start()
        
        m = self.mdp
        for s in range(m.num_states):
            self.process_state(s)
            for a in m.actions_for_state(s):
                self.process_action(a)
        
        self.finish()
        return self.str
        
    def start(self):
        gr_name = self.mdp.name if self.mdp.name else ""
   
        self.str += f"digraph \"{gr_name}\" {{\n"
        self.str += "  rankdir=LR\n"
        
    def finish(self):
        self.str += "}\n"
        
    def get_state_name(self, s):
        name = s if self.mdp.state_labels[s] is None else self.mdp.state_labels[s]
        return name
    
    def process_state(self, s):
        self.str += f"\n  {s} ["

        # name
        state_str = self.get_state_name(s)

        # minInitCons
        if self.opt_mi or self.opt_sr:
            mi = self.mdp.minInitCons
            state_str = f"<table{tab_MI_style}>" + \
                        f"<tr><td>{state_str}</td>"

        if self.opt_mi:
            val = mi.values[s]
            val = "∞" if val == inf else val
            state_str += f"<td{tab_MI_cell_style}>" + \
                f"<font{tab_MI_cell_font}>{val}</font></td>"

        if self.opt_sr:
            val = mi.safe_values[s]
            val = "∞" if val == inf else val
            state_str += f"<td{tab_SR_cell_style}>" + \
                f"<font{tab_SR_cell_font}>{val}</font></td>"

        if self.opt_mi or self.opt_sr:
            state_str += "</tr></table>"

        self.str += f'label=<{state_str}>'

        # Reload states are double circled
        if self.mdp.is_reload(s):
            self.str += ", peripheries=2"
        self.str += "]\n"
    
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
            self.str += f"      {act_id} -> {dst}[label={p}]"
        

def dot_to_svg(dot_str):
    """
    Send some text to dot for conversion to SVG.
    """
    try:
        dot_pr = subprocess.Popen(['dot', '-Tsvg'],
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
              + stderr.decode('utf-8'), file=sys.stderr)
    ret = dot_pr.wait()
    if ret:
        raise subprocess.CalledProcessError(ret, 'dot')
    return stdout.decode('utf-8')