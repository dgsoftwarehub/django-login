Sim Switch
------------

This is a project made for a Fiverr client using DRF and PSQL


## How to use

After cloning the project and setting up virtual environment go to the olxclone folder and then use given commands

1.  Install dependencies required to run locally
    ```console
        pip install -r requirements.txt
    ```
   
2.  Create an empty database locally using MySQL.
3.  Rename sampleenv file to .env and add values as required
4.  First we need to make migrations.
    ```console
        python manage.py makemigrations
    ```
    ```console
        python manage.py migrate
    ```

7.  Load up data for categories, subcategories, states and cities
    ```console
        python manage.py loaddata category.json subcategory.json state.json city.json
    ```
    
6.  Create a super user (optional)
    ```console
        python manage.py createsuperuser
    ```

7.  Run the project locally using
    ```console 
        python manage.py runserver
    ```

