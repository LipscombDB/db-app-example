# db-app-example

A small Flask application that reads and writes actor data in the MySQL `sakila` sample database.

## Prerequisites

- Python 3.10 or newer (check with `python3 --version`, or `py --version` on Windows)
- MySQL running locally on port 3306, with the [sakila sample database](https://dev.mysql.com/doc/sakila/en/) installed

By default the app connects to the `sakila` database as MySQL user `root`. You can change the user and database name in `.env` (see step 5). The host and port, `127.0.0.1:3306`, are not read from `.env`; to change them, edit `db_cred` in `core/__init__.py`.

## Setup

This application must be run from inside a virtual environment, so its libraries don't conflict with anything else on your computer. The app will refuse to start if you skip this.

1. **(Recommended, one time only)** Tell pip to install packages only inside a virtual environment:

   ```
   pip3 config set global.require-virtualenv true
   ```

   This applies to every Python project on your computer, not just this one. If it gets in the way of other work, undo it with:

   ```
   pip3 config unset global.require-virtualenv
   ```

2. From the project folder, create the virtual environment:

   - macOS / Linux:
     ```
     python3 -m venv venv
     ```
   - Windows:
     ```
     py -m venv venv
     ```

3. Activate it. You need to do this every time you open a new terminal.

   - macOS / Linux:
     ```
     source venv/bin/activate
     ```
   - Windows (PowerShell, the default in Windows Terminal and VS Code):
     ```
     venv\Scripts\Activate.ps1
     ```
     If you get an error that running scripts is disabled on this system, run this once and then try again:
     ```
     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
     ```
   - Windows (Command Prompt):
     ```
     venv\Scripts\activate.bat
     ```

   Your prompt should now start with `(venv)`.

4. Install the required libraries:

   ```
   pip install -r requirements.txt
   ```

5. Create a file named `.env` in the project folder containing your MySQL password:

   ```
   PASSWORD=your_mysql_password
   ```

   If you connect as a MySQL user other than `root`, or your database isn't named `sakila`, add these lines too:

   ```
   DB_USER=your_mysql_user
   DB_NAME=your_database_name
   ```

   This file is ignored by git, so your password won't be committed.

## Running the app

With the virtual environment activated:

```
python app.py
```

Then open http://127.0.0.1:8000 in your browser.

To have the app reload automatically when you edit the code, and show detailed error pages, add this line to your `.env` file:

```
FLASK_DEBUG=1
```

Only do this on your own computer: the debug error pages let anyone who can reach the app run code on it.

When you're finished, run `deactivate` to leave the virtual environment.

## Running the tests

The tests use [pytest](https://docs.pytest.org/). With the virtual environment activated, run all of them with:

```
pytest
```

To run one file, or one test in it:

```
pytest tests/test_actors.py
pytest tests/test_actors.py::test_add_actor
```

The tests connect to the same MySQL database as the app, using the settings in your `.env` file, so MySQL must be running. Every actor a test adds has the last name `PYTEST-TEMP` and is deleted when the test finishes, so your sakila data is left as it was.
