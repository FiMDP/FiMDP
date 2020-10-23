__version__ = "2.0"

from . import core
from . import energy_solvers
from . import explicit
from . import objectives

from .core import ConsMDP


def setup(**kwargs):
    """
    Configure FiMDP for nice display.

    This is manly useful in Jupyter/IPython.

    Note that this function needs to be called before any automaton is
    displayed.  Afterwards it will have no effect (you should restart
    Python, or the Jupyter/IPython Kernel).

    Parameters
    ----------
    fillcolor : str
        the color to use for states (default: '#eeeeff')
    fillcolor_target : str
        the color to use for target states (default: '#ddffdd')
    font : str
        the font to use in the GraphViz output (default: 'Lato')
    show_default : str
        default options for show()
    show_names : bool
        show names of states (default `True`), if `False` show only state ID
    state_labels : bool
        show labels (sets of AP) of LabeledConsMDPs (default `True`)
    max_states : int
        maximum number of states in GraphViz output (default: 50)
    """
    from . import dot as _dot
    _dot._show_default += kwargs.get("show_default", "sprb")
    _dot._dot_options["font"] = kwargs.get("font", "Lato")
    _dot._dot_options["fillcolor"] = kwargs.get("fillcolor", "#eeeeffcc")
    _dot._dot_options["fillcolor_target"] = kwargs.get("fillcolor_target", "#ccffcc")
    _dot._dot_options["names"] = kwargs.get("show_names", True)
    _dot._dot_options["state_labels"] = kwargs.get("state_labels", True)
