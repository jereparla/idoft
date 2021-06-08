# Usage: bash format_checker/run.sh

python3.9 -m venv env
source env/bin/activate
pip3 install -r format_checker/requirements.txt
python3.9 format_checker/main.py 
deactivate