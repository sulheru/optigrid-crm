echo "Iniciando server..."
python manage.py runserver 2>&1 | tee tmp/server_output.txt
echo ""
echo "Cerrando server"
