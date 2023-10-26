![Docker workflow](https://github.com/fedihamdi/meteodata/actions/workflows/docker-image.yml/badge.svg)
![Quality workflow](https://github.com/fedihamdi/meteodata/actions/workflows/pylint.yml/badge.svg)
[![Django CI](https://github.com/fedihamdi/meteodata/actions/workflows/django.yml/badge.svg)](https://github.com/fedihamdi/meteodata/actions/workflows/django.yml)
# meteodata
 
Project structure is as follow:

> Further documentation will be available in the upcoming days

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
