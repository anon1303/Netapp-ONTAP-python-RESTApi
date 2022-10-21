echo "--> Upgrading Python pip (for both versions)"
pip install --upgrade pip
pip3 install --upgrade pip

echo "--> Installing Python client libraries and dependencies"
pip install requests
pip install docopt
pip install prettytable


