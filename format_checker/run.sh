# Usage: bash format_checker/run.sh

path=$(pwd)/env/bin/python3.9
$path -m pip install --upgrade pip
python3 -m venv env
source env/bin/activate
pip install -r format_checker/requirements.txt
python3 format_checker/main.py 
deactivate