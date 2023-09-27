# Пример миграции базы данных в "flask":

..... .......... -- "------комментарий-------"
flask db migrate -m "new fields in user model"
..... .......... -- "------------------------"
..... ..........
flask db upgrade
..... ..........

....... ....... "--------перевод строк сайта--------"
pybabel extract -F babel.cfg -k _l -o messages.pot .
....... ....... "-----------------------------------"
_ -F считать файл конфигурации
_ -k добавить _l в считывание как и _
_ -o имя выходного файла

....... .... "создаем новый каталог для языка перевода"
pybabel init -i messages.pot -d app/translations -l ru
....... .... "----------------------------------------"
_ -i берет messages.pot в качестве входных данных
_ -d папка переводов
_ -l язык перевода

....... ....... .................................................
_ "создаем файл .mo"
_ "flask-babel использует его для загрузки переводов в приложени"
....... ....... "-----------------"
pybabel compile -d app/translations
....... ....... "-----------------"
....... ....... .................................................

....... ...... "---------обновить перевод---------"
pybabel update -i messages.pot -d app/translations
....... ...... "----------------------------------"

pip freeze > requirements.txt