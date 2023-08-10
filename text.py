greet = """
Здравствуйте!

Это чат поддержки Яндекс.Лавки.

Мы на связи с 09:00 до 21:00 по московскому времени в будние дни, а еще нам можно написать в форму обратной связи, если вам так удобнее ☺

Я — добрый робот поддержки. Постараюсь вам помочь, а если не получится — позову своих коллег-операторов.

Какой у вас вопрос?

— Если у вас вопрос про время доставки (например, курьер с вашим заказом 
опаздывает) — выберите кнопку "Время доставки"
— Если ваш заказ не привезли совсем (Курьер опаздывает больше чем на 40 
минут) — выберите кнопку "Не привезли заказ"
— Если ваш товар повреждён — выберите кнопку "Товар повреждён"
— Если вам привезли испорченный продукт — выберите кнопку "Испорченный продукт"
— Если у вас вопрос по любому другому нашему сервису, выберите кнопку "Другой вопрос" 
"""
menu = "📍 Выберите категорию вашего вопроса"

instruction = "Ты - агент службы поддержки сервиса Яндекс.Лавка. " \
              "Пока у тебя нет никакого функционала, поэтому на все " \
              "вопросы вежливо отвечай, что пока ты ещё ничего не умеешь " \
              "и успокаивай клиентов, поднимай им настроение."

gen_text = "📝 Отправьте текст запроса к нейросети для генерации текста"
gen_image = "🖼 Отправьте текст запроса к нейросети для генерации изображения"
gen_exit = "Чтобы выйти из диалога с нейросетью нажмите на кнопку ниже"
gen_error = f'🚫 Ошибка генерации. Возможные причины:\n1. Перегружены сервера OpenAI\n2. Ваш запрос нарушил правила OpenAI\n3. Ошибка в работе бота\nЕсли вы считаете, что проблема вызвана неисправностью бота, сообщите админу'
text_watermark = '\n_______________________________________\nСоздано при ' \
                 'помощи YandexGPT'
img_watermark = "Создано при помощи @dalle_chatgpt_bot"
gen_wait = "⏳Пожалуйста, подождите немного, пока нейросеть обрабатывает ваш запрос..."

err = "🚫 К сожалению произошла ошибка, попробуйте позже"