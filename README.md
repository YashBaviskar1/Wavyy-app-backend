### Running the backend locally

Prerequites :

- python and pip installed in system (along with python -m venv)

# installation process

```bash
git clone https://github.com/YashBaviskar1/Wavyy-app-backend.git
```

```
cd  Wavvy-app-backend
```

create a virtual enviroment (optional but reccomanded)

```bash
python3 -m venv env
```

activate the virtual enviroment

```bash
env/Scripts/activate  #(windows)
source env/bin/activate #(linux)
```

after virtual env is activate, download all the dependices

```bash
pip install -r requirements.txt
```

then run these following commands to start the server locally

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver

```
