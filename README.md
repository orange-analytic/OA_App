# Getting Started (installation)
1.	Get Python installed
2.  Go to the root directory and open a PowerShell window
3.  Run setup_win64.ps1 to setup the environment. If need be, one must also add the native python.exe path to the Windows 'path' environment variable
4.  After completing the installation, one can activate the project python environment in any PowerShell window by executing the script at [from project root]..\.python\Scripts\Activate.ps1
5.  Copy the datasets required at data/01_raw/
6.  Run the main pipeline to populate intermediate & output datasets (which can then be accessed through the kedro catalog in notebooks)
* 	To run a pipeline, enter the following in command line (PowerShell window): kedro run -p main -e base
*	To run a notebook using the same base environment as the pipeline, run in command line (PowerShell window): kedro jupyter notebook --ip=localhost --env base
*	To run unit tests, enter the following in command line (PowerShell window): pytest src/tests/
*  	In a jupyter notebook file, go to "File > Jupytext > Pair notebook with light Script" to convert your notebook to a .py light script such that source code versioning can work properly. .ipynb are not to be kept in the repo
