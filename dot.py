import subprocess
#TODO build a list and join it in the end into string

class consMDP2dot:
    """Convert consMDP to dot"""
    
    def __init__(self, mdp, options = None):
        self.mdp = mdp
        self.str = ""
        self.options = options
        
        self.act_color = "blue"
        
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
        # Print name
        self.str += f'label="{self.get_state_name(s)}"'

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