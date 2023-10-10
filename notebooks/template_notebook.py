# +
import warnings

from IPython.core.display import HTML, display

display(HTML("<style>.container { width:100% !important; }</style>"))
warnings.simplefilter(action="ignore", category=FutureWarning)

# %reload_kedro
# -

raw_test = catalog.load("raw_test")
display(raw_test)
