import subprocess
import sys

from math import inf
#TODO build a list and join it in the end into string

tab_MI_style      = ' border="0" cellborder="0" cellspacing="0"'
tab_MI_cell_style = ' bgcolor="white"'
tab_MI_cell_font  = ' color="orange" point-size="10"'

default_options = "m"

class consMDP2dot:
    """Convert consMDP to dot"""
    
    def __init__(self, mdp, options=""):
        self.mdp = mdp
        self.str = ""
        self.options = default_options + options
        
        self.act_color = "blue"
        
        self.opt_mi = False

        if "M" in self.options:
            mdp.compute_minInitCons()
            self.opt_mi = True
        if "m" in self.options:
            mi = mdp.minInitCons
            self.opt_mi = mi is not None

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
        self.str += f"  {s} ["

        # name
        state_str = self.get_state_name(s)

        # minInitCons
        if self.opt_mi:
            mi = self.mdp.minInitCons
            val = mi.values[s]
            val = "∞" if val == inf else val
            state_str = f"<table{tab_MI_style}>" + \
            f"<tr><td>{state_str}</td>" + \
            f"<td{tab_MI_cell_style}><font{tab_MI_cell_font}>" + \
            f"{val}</font></td></tr>" +\
            "</table>"
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