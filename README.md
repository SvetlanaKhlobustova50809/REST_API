
# Для запуска требуется:
- Создать пользователя в PostgreSQL, у меня это postgres
- Изменить переменную USERNAME и указать localhost в файле pyDB.py

# При запуске Docker контейнера:
- прописать следующие команды, указав нужный порт
```
docker build -t flask-rest-api .
docker run -d -p 5000:5000 flask-rest-api
```
- просмотреть логи можно так
```
docker logs <CONTAINER ID OR CONTAINER NAME>
```
# Если по какой-то причине не запускается Docker контейнер:
- выполнить установку следующих библиотек: flask, Pyjwt, werkzeug, validate_email_address, sqlalchemy
- запустить файл pyDB.py

Тестирование POST запросов выполняла в Postman

  
