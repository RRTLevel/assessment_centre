## Introduction 

This minimal application is a Django boilerplate for web applications.
It contains everything you need to get started so that you can start building your functionality straight away.

---

<br>

## Getting Started


This project uses Python 3.13 and Django 5.2.

To setup the application, you will need to create a virtual environment and install the requirements:

``` 
python -m venv venv
```

Activate the virtual enviroment:

```
.\venv\Scripts\activate
```

Install the dependencies:

```
pip install -r .\requirements.txt
```

Copy the example environment variables:

```
cp example.env .env
```

Create your local database:

```
python app\manage.py migrate
```

Load the example fixtures:

```
python app\manage.py loaddata app\app_src\fixtures\01_users.json
python app\manage.py loaddata app\app_src\fixtures\02_notes.json
```

Create a local superuser account and answer the prompts

```
python app\manage.py createsuperuser
```

Run the application:

```
python app\manage.py runserver 8000
```


You should now be able to visit your running application at http://localhost:8000

<br>
