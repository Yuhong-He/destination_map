# Destination Map

## How to run it
1. Open terminal on the project root path, install any dependencies:
    ```shell
    pip install -r requirements.txt
    ```
2. Create a file `config.py` under the project root path, use your MySQL configuration:
    ```python
    HOSTNAME = "localhost" # Your database hostname
    PORT = 3306 # Your database port
    USERNAME = "root" # Your database account username
    PASSWORD = "" # Your database account password
    DATABASE = "airport_coords"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}" \
                              f"?charset=utf8"
    ```
3. Create a database `airport_coords`.
4. Then execute following commands:
    ```shell
    flask db init
    flask db migrate
    flask db upgrade
    ```
5. Run the project by
    ```shell
    flask run
    ```