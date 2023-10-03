# Пример миграции базы данных в "flask":

# создать базу данных
flask db init

# -m "комментарий"
flask db migrate -m "new fields in user model"

flask db upgrade

# Перевод строк сайта
pybabel extract -F babel.cfg -k _l -o messages.pot .

# -F считать файл конфигурации
# -k добавить _l в считывание как и _
# -o имя выходного файла

# Создаем новый каталог для языка перевода
pybabel init -i messages.pot -d app/translations -l ru

# -i берет messages.pot в качестве входных данных
# -d папка переводов
# -l язык перевода

# "создаем файл .mo"
# "flask-babel использует его для загрузки переводов в приложени"
pybabel compile -d app/translations

# Обновить перевод
pybabel update -i messages.pot -d app/translations

# Добавить установленные библиотеки в requirements.txt
pip freeze > requirements.txt
