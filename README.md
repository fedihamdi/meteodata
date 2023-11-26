![Docker workflow](https://github.com/fedihamdi/meteodata/actions/workflows/docker-image.yml/badge.svg)
![Quality workflow](https://github.com/fedihamdi/meteodata/actions/workflows/pylint.yml/badge.svg)
[![Django CI](https://github.com/fedihamdi/meteodata/actions/workflows/django.yml/badge.svg)](https://github.com/fedihamdi/meteodata/actions/workflows/django.yml)
![Pylint Score](https://github.com/fedihamdi/meteodata/blob/feature/reaper_app/pylint-badge.svg)

# meteodata

Project structure is as follow:

> Further documentation will be available in the upcoming days

## TL;DR
to run the current version on your machine, do the following :
1. Pull the image from the docker hub.
```
docker pull fedihamdi/breatheeasyapp:latest
```
2. Start the app.
```
docker run -it -p 8000:8000 fedihamdi/breatheeasyapp:latest
```
## 🚀 Building and Running locally (no docker needed)
1. Clone the current repo.
```
git clone https://github.com/fedihamdi/meteodata.git
```
2. Go to repo "meteodata/src/reaper"
```
cd ~/meteodata/src/reaper
```
3. Create and install the requirements (I am using conda)
  > * Create conda env
```
conda create -n meteodata_39 python==3.9.18
```
> * activate conda env
```
conda activate meteodata_39
```
> * Install requirements
```
pip install -r requirements.txt
```
>> 👉 Once that is done, you are ready to go :

```
py manage.py makemigrations
python manage.py migrate
```
> 👉 Create the Superuser
```
python manage.py createsuperuser
```
> 👉 Start the app
```
py manage.py runserver 0.0.0.0:8000
```
🥇 At this point, the app runs at ➡️ http://localhost:8000/

## Codebase structure
```
~:.
│   .gitattributes
│   .gitignore
│   data_file_2022-07-10.csv
│   download.nc
│   download_pollen_forcasts.nc
│   interactive_map_corrected.html
│   interactive_map_corrected_bright.html
│   LICENSE
│   main.py
│   random_data.nc
│   random_data2.nc
│   README.md
│   requirements.txt
│   testapi.py
│
├───.idea
│   │   .gitignore
│   │   meteodata.iml
│   │   misc.xml
│   │   modules.xml
│   │   vcs.xml
│   │   workspace.xml
│   │
│   └───inspectionProfiles
│           profiles_settings.xml
│
├───.ipynb_checkpoints
├───models
│       random_forest_dumb_model.pkl
│
├───notebooks
│   │   Modelisation.ipynb
│   │   R&D + EDA.ipynb
│   │
│   └───.ipynb_checkpoints
│           Modelisation-checkpoint.ipynb
│           R&D + EDA-checkpoint.ipynb
│
├───src
│   │   cams_data_retrieval.py
│   │   era5_data_retriever.py
│   │   model_job.py
│   │   processing_job.py
│   │   __init__.py
│   │
│   ├───app
│   │   │   app.py
│   │   │   __init__.py
│   │   │
│   │   └───Breatheeasy
│   │       │   db.sqlite3
│   │       │   manage.py
│   │       │   __init__.py
│   │       │
│   │       ├───Breatheeasy
│   │       │   │   asgi.py
│   │       │   │   settings.py
│   │       │   │   urls.py
│   │       │   │   views.py
│   │       │   │   wsgi.py
│   │       │   │   __init__.py
│   │       │   │
│   │       │   └───__pycache__
│   │       │           settings.cpython-310.pyc
│           era5_data_retriever.cpython-310.pyc
│
└───tests
    ├───integration
    └───unit

```
