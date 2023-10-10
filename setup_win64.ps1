#
#	INSTALLATION SCRIPT FOR WINDOWS
#	To be executed in the git ROOT folder

# create a pip.ini file for user in case it does not exist
# the purpose is to add trusted hosts, otherwise pip will fail
if(-Not (iex "Test-Path -Path C:\Users\$env:UserName\pip\pip.ini")){
	if(-Not (iex "Test-Path -Path C:\Users\$env:UserName\pip"))
	{
		mkdir C:\Users\$env:UserName\pip
	}
	echo "[global]
trusted-host = pypi.org files.pythonhosted.org
http.sslVerify = false" | out-file -encoding ascii C:\Users\$env:UserName\pip\pip.ini
} else {
	echo "[WARNING] pip.ini file already exists, skipping."
}

# create the Python propel environment
python -m venv ..\.python

# set environment variable TMPDIR
if(-Not (iex "Test-Path -Path ..\.python\tmp\"))
{
	mkdir ..\.python\tmp\
}

$filePath= "..\.python\Scripts\Activate.ps1"
$linenumber= Get-Content $filePath | select-string "# SIG # Begin signature block"
$textToAdd= "
# Defining TMPDIR variable
`$env:TMPDIR='../.python/tmp/'
"
$fileContent = Get-Content $filePath
$fileContent[$linenumber.LineNumber-2] += $textToAdd
$fileContent | Set-Content $filePath

# activate Python environment
$env:PYTHONPATH=''
..\.python\Scripts\Activate.ps1

echo "installing pip"
..\.python\scripts\python.exe -m pip install --no-cache-dir --upgrade pip

# install other python libraries
echo "installing pre-commit"
pip install -U -q pre-commit nbstripout
pre-commit install --install-hooks

echo "installing setuptools"
pip install --no-cache-dir -q -U setuptools
echo "installing pip-tools"
pip install --no-cache-dir -q -U pip-tools
echo "installing wheel"
pip install --no-cache-dir -q -U wheel

#install project library requirements
echo "generating requirements"
pip-compile -o requirements_win.txt --quiet --annotate --resolver=backtracking --header requirements.in
echo "installing python package requirements"
pip install --no-cache-dir --retries 50 --no-warn-conflicts --requirement requirements_win.txt

# set environment variable PYTHONPATH (shall not be done prior to install)
$linenumber= Get-Content $filePath | select-string "# SIG # Begin signature block"
$textToAdd= "
# Defining PYTHONPATH variable
`$env:PYTHONPATH='src/'
"
$fileContent = Get-Content $filePath
$fileContent[$linenumber.LineNumber-2] += $textToAdd
$fileContent | Set-Content $filePath

deactivate
..\.python\Scripts\Activate.ps1

# Run tests to verify integrity
cd src/
pytest
cd ..
