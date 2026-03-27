# Create migrations for all apps
python manage.py makemigrations accounts chat openai_integration emergency resources university mood assessment

# View the SQL that will be executed
python manage.py sqlmigrate accounts 0001
python manage.py sqlmigrate chat 0001
# etc.

# Apply migrations
python manage.py migrate

python manage.py import_students --file data/sample_students.json --create-years

python manage.py import_resources --file data/resources.json --clear

python manage.py import_assessments --file data/assessments.json
