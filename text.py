greet = """
Здравствуйте!

Это чат поддержки Яндекс.Лавки.

Мы на связи с 09:00 до 21:00 по московскому времени в будние дни, а еще нам 
можно написать в форму обратной связи, если вам так удобнее ☺

Я — добрый робот поддержки. Постараюсь вам помочь, а если не получится — 
позову своих коллег-операторов.

Какой у вас вопрос?

— Если у вас вопрос про время доставки (например, курьер с вашим заказом 
опаздывает) — выберите кнопку "Время доставки"
— Если ваш заказ не привезли совсем (Курьер опаздывает больше чем на 40 
минут) — выберите кнопку "Не привезли заказ"
— Если ваш товар повреждён — выберите кнопку "Товар повреждён"
— Если вам привезли испорченный продукт — выберите кнопку "Испорченный продукт"
— Если у вас вопрос по любому другому нашему сервису, выберите кнопку 
"Другой вопрос" 
"""
menu = "📍 Выберите категорию вашего вопроса"

instruction = "Ты - агент службы поддержки сервиса Яндекс Лавка. " \
              "Пока у тебя нет никакого функционала, поэтому на все " \
              "вопросы вежливо отвечай, что пока ты ещё ничего не умеешь " \
              "и успокаивай клиентов, поднимай им настроение."
classification_prompt = """В нашей системе существует 4 категории проблем к 
которым относятся сообщения пользователя с соответствующими им цифрами:
1 - Заказ опаздывает 
2 - Товар в заказе повреждён
3 - У продукта в заказе истёк срок годности
4 - Полученные товары не соответствуют товарам заказа
Ты получишь сообщение пользователя и будешь должен отнести его к одному из 
классов, и вывести только соответствующую ему цифру. Если сообщение не 
относится ни к одной из категорий или вопрос тебе непонятен, выведи 0. """
gen_text = "В чём заключается ваш вопрос?"
gen_exit = "Чтобы выйти из диалога с нейросетью нажмите на кнопку ниже"
gen_error = f'🚫 Ошибка генерации'
text_watermark = ''
img_watermark = "Создано при помощи @YandexGPT"
gen_wait = "⏳Пожалуйста, подождите немного, пока нейросеть обрабатывает ваш " \
           "запрос..."

err = "🚫 К сожалению произошла ошибка, попробуйте позже"
