# BurseBot
В разработке.

Клиенская часть реализуется на React. Располагается в деректории [front](https://github.com/ageent/bursebot/tree/main/front).

Коннектор отвечает за взаимодействие с API Tinkoff и связывание фроронтенда и модуля аналитики. 
Реализуется на FastAPI Python. Располагается в деректории [backend](https://github.com/ageent/bursebot/tree/main/backend).

Модуль аналитики отвечат за принятие решений о купле-продаже. Реализуется на Python. 
Располагается в деректории [backend/analytics](https://github.com/ageent/bursebot/tree/main/backend/analytics). 
Описание алгоритма изображено на [этой блок-схеме](https://github.com/ageent/bursebot/blob/main/notebooks/charts/trade.png).
