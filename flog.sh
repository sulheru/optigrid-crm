echo "Iniciando server..."
python manage.py runserver 0.0.0.0:8000 &> tmp/runserver.log 2>&1
echo ""
echo "Cerrando server"
