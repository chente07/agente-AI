# agente-AI
# agente-AI instrucciones para que jale en su compu

# para los papus que usan linux

git clone URL_DEL_REPOSITORIO
cd proyecto_pulmones

python3 -m venv env
source env/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

# a los de windows 

git clone URL_DEL_REPOSITORIO
cd proyecto_pulmones

python -m venv env
env\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
