# PiNK
### Это корпус по "Преступлению и наказанию"
<p>Полный текст «Преступления и наказания» в одном месте - 13 тысяч предложений, 170 тысяч слов</p>
<p>Выполнили: Яна Ананченкова и Даша Баранова</p>
<br></br>
По [этой ссылке](https://anwasty4.pythonanywhere.com/) можно открыть сайт корпуса
<br></br>
[Вот](https://drive.google.com/file/d/1NKfNeIbm_PeLBg2XXgW5uuRItlT2fin4/view?usp=sharing) используемая база данных
- В папке `templates` хранятся html-шаблоны страниц
- Файл `app.py` - основной файл web-приложения
- В файл `models.py` инициализируется база данных
- Файл `funcs.py` содержит функции, используемые для обработки запросов пользователя

#### Про режимы
В корпусе можно искать одно слово, 2-граммы и 3-граммы в режимах «Поиск леммы», «Поиск словоформы», «Поиск части речи»
<p>Чтобы найти слова определённой части речи, тебе необходимо добавить к своему запросу специальную функцию:</p>p

<p>- <i>Знакомый.NOUN</i> - выдаст все предложения, где слово «знакомый» будет существительным.</p>
<p>- <i>Знакомый.ADJ</i> - выдаст все предложения, где слово «знакомый» будет прилагательным.</p>

<p>Список используемых тегов можно найти на страницах с поиском.</p>


