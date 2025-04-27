# SwatGuide

## Project Description
SwatGuide is a platform designed to better the Swarthmore student experience by providing a collaborative space for students to create and share guides on various topics related to campus life. Users can edit guides to keep information up-to-date, ensuring that all students have access to the latest insights.

## Team Members
- Bereket Nigussie
- Tsiyon Abera
- Melanie Navarro

# Setup
## a. Clone the repository

```bash
    $ git clone <github filepath>
    $ cd <filepath>
    $ ls
```

- Here is a [Visual Guide](https://medium.com/@ashk3l/a-visual-introduction-to-git-9fdca5d3b43a) to help you better understand git.

## b. Set Up Your Virtual Environment

**1.** In your lab repository on the terminal, create a virtual environment.:

```bash
    $ uv venv
```

**2.** To activate your virtual environment, type:

```bash
    $ source .venv/bin/activate
```

**3.** To deactivate your virtual environment, type:

```bash
    $ deactivate
```

**4.** Check that your virtual environment is using the correct version of Python:

```bash
    (.venv) $ which python
```
- You should see something like <path_to_directory>/.venv/bin/python.

**5.** Now install Flask and Flask-SQLAlchemy and other required Python libraries:

```bash
    $ uv pip install flask flask-cors Flask-SQLAlchemy
``` 

or use the following bash command

```bash
    $ uv pip install -r requirements.txt
```

## c. Run Your Flask APP

- You can start your flask web server using the following command:

```bash
    $ flask run --debug --reload
```

## Features
- Create and edit guides
- Search for guides
- User profile pages

