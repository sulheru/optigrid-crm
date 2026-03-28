python manage.py test apps.external_actions -v 2 &> tmp/apps_external_actions.txt
python manage.py check &>> tmp/apps_external_actions.txt
cat tmp/apps_external_actions.txt
