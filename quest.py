class QuestStage:
    def __init__(self, step: int, text: str, score: int, answer=None):
        self.step = step
        self.title = str(step) + '. ' + ' '.join(text.split()[:5])
        self.text = text
        self.score = score
        self.answer = answer


quest_list = []

questions = [
    (
        0,
        '''Привет, студент. Волонтерский Центр РЭУ им. Г.В. Плеханова запускает ДоброКвест! Пройдя его, ты сможешь не только узнать всю необходимую информацию о добровольчестве, но и приятно провести время.
Во время квеста за выполнение заданий ты будешь получать баллы, которые ты сможешь обменять на сувенирную продукцию нашего Волонтерского Центра.
Перед тем как начать, я хочу пригласить тебя в беседу, посвященную ДоброКвесту! Вот ссылка: … Некоторые задания ты просто не сможешь выполнить, если не состоишь в беседе, к тому же, если у тебя появятся вопросы, ты всегда можешь задать их там.
''',
        1
    ),

#     (
#         '''Твое первое задание - подписаться на нашу группу Вконтакте https://vk.com/volunteer_reu. Здесь ты всегда можешь найти актуальные новости о волонтерстве и анонсы мероприятий.
# Возвращайся, когда выполнишь задание!
# ''',
#         1
#     ),

    (
        1,
        '''Первые шаги сделаны, идем дальше!
Ты подписался на нашу группу, но оценил ли ты ее контент? Поставь 10 лайков под постами, которые тебе понравились больше всего!
''',
        2
    ),

    (
        2,
        '''Добровольчеством можно заниматься не только в рамках Университета, но и на федеральном уровне. Главная площадка для этого - Добро.ру. Именно на этом сайте ты можешь подать заявку на интересующие мероприятия в качестве волонтера, завести свою электронную книжку волонтера и пройти образовательные курсы. 
Твое задание - зарегистрироваться на платформе и прислать мне скрин личного кабинета, где будет видно твое ФИО с датой регистрации, тогда ты получишь заслуженный балл.
''',
        1
    ),

    (
        3,
        '''Хочешь, чтобы твои друзья тоже узнали про Волонтерский центр? Жми кнопку “рекомендовать” на странице группы Вконтакте.
Жду от тебя скрин, и мы пойдем дальше.
''',
        2
    ),

    (
        4,
        '''Еще больше информации ты сможешь найти в Telegram и Instagram Волонтерского центра. Обязательно подпишись, чтобы быть в курсе всех новостей! Мы не дублируем информацию: на разных площадках - разный контент. 
Telegram: https://t.me/myvmesteREU
Instagram: https://www.instagram.com/vc_reu
Жду скрины с подпиской!
''',
        2
    ),

    (
        5,
        '''Мы не только помогаем проводить мероприятия, но и реализуем собственные проекты. Проекты позволяют ребятам создавать собственные мероприятия, развиваться и развивать других. Напиши их руководителям, чтобы узнать подробности:
https://vk.com/polin_fedtv
https://vk.com/vlad.bodroff
https://vk.com/im?sel=176175731
https://vk.com/kostenko.oksana 
Чтобы подтвердить выполнение, тебе нужно получить от каждого руководителя кусочек фразы, собрать ее и отправить мне. Удачи!
''',
        9,
        'НАШ ДЕВИЗ, который мы придумаем в пятницу'
    ),

    (
        6,
        '''Самое время погрузиться в добровольчество! Твое следующее задание - пройти курс “Основы волонтерства для начинающих” на Добро.ру: https://edu.dobro.ru/courses/28/
Ты узнаешь, что такое волонтерство, с какими проблемами сталкиваются начинающие волонтеры, разберешься, какое из направлений волонтерства тебе ближе.
 
Если ты уже не новичок, то пройди курс “Событийное волонтерство для тим-лидеров”: https://edu.dobro.ru/courses/71/. Ты узнаешь про позицию тим-лидера, познакомишься с его обязанностями и компетенциями, а также узнаешь про основы построения взаимоотношений с волонтерами.
 
Скидывай сертификат о прохождении в формате pdf.
''',
        5
    ),

    (
        7,
        '''Добрых людей в нашей стране действительно много, они занимаются важными делами, которые мы часто не замечаем. Фильм “#ЯВОЛОНТЕР. Истории неравнодушных” расскажет тебе истории наших героев. Они как майор Гром, только настоящие! Посмотри фильм и расскажи, какая история тебя впечатлила больше всего. Напиши отзыв не менее 7 предложений о понравившейся истории.
Ссылка на фильм: https://www.youtube.com/watch?v=d25CO-eEfbg''',
        5
    ),

    (
        8,
        '''В мире волонтерства существует море возможностей! Главное - не бояться задавать вопросы и находить информацию. Познакомься с программой мобильности АВЦ, что это такое и какие у нее требования. Уверен, тебе будет полезно. 
Ответь на следующие вопросы:
- На что направлена программа мобильности?
- Какие есть требования для участия в программе?
- Какие сервисы предоставляются волонтерам?''',
        3
    ),

    (
        9,
        '''В мире волонтерства существует море возможностей! Главное - не бояться задавать вопросы и находить информацию. Познакомься с ГБУ “Мосволонтер”, узнай, что это за центр и чем он занимается. Уверен, тебе будет полезно. 
Ответь на следующие вопросы:
- Перечисли основные направления добровольчества, которыми занимается Мосволонтер
- Напиши 3 проекта, которые реализует Мосволонтер прямо сейчас
- Где находится Мосволонтер?''',
        3
    ),

    (
        10,
        '''В мире волонтерства существует море возможностей! Главное - не бояться задавать вопросы и находить информацию. Узнай про направления волонтерской деятельности и в чем они заключаются - уверен, тебе будет полезно. 
Выбери 3 направления, которые тебя привлекли. Напиши, в чем их основная цель и в каких мероприятиях ты можешь поучаствовать в рамках каждого направления.''',
        3
    ),

    (
        11,
        '''Чем бы ты ни занимался, а soft-skills везде нужны ;) Добровольчество - отличный способ для прокачки себя, в этом ты убедишься в дальнейшем, а пока переходи по любой понравившейся ссылке и выполняй задание!
На сайте ты найдешь много полезного материала по теме, твой минимум - найти на странице тест и пройти его: 
Критическое мышление - https://smartcalend.ru/softskills_criticalthinking 
Эмоциональный интеллект - https://smartcalend.ru/leadership_eq 
Принятие решений - https://smartcalend.ru/softskills_choice
Жду скрин с результатом теста.
''',
        3
    ),

    (
        12,
        '''В Волонтерском Центре активно развивается экологическое направление. В рамках проекта “Создай-Эко” Волонтерский центр собирает вторсырье и отправляет его на переработку. У тебя есть возможность сдать пластик, крышечки, макулатуру, батарейки. 
Сдай вторсырье в ВЦ и запечатли это на фото.
Если выложишь в инстаграм и отметишь vc_reu, то получишь двойные баллы - напиши свой ник в формате “@ник”.
''',
        48
    ),

    (
        13,
        '''Социальное добровольчество - самое развитое направление в стране. Попробуй стать его частью и сделать доброе дело для животных.
Выбирай удобную тебе дату и записывайся на выезд в приют. Вместе мы погуляем с собаками, передадим еду и лекарства для них (сбор ведется в ВЦ) и, конечно, познакомимся!
Для того, чтобы получить баллы за задание, сделай фотографию в приюте и скинь мне.
''',
        10
    ),

    (
        14,
        '''Пришло время попробовать себя в событийном волонтерстве! Выбери любое мероприятие на Добро.ру или на нашей странице Вконтакте, в котором ты можешь поучаствовать до окончания квеста и подавай заявку. Пришли мне название и дату мероприятия, а также фотографию с события. ''',
        10
    ),

    (
        15,
        '''Самое главное в жизни - это люди, которые тебя окружают. “Хочешь идти быстро - иди один. Хочешь идти далеко - идите вместе”, - поэтому предлагаю тебе познакомиться с другими участниками квеста, чтобы “идти вместе”.
Лови напарника на это задание: *ссылка на другого рандомного участника*
Вам нужно сделать совместную фотографию в Волонтерском центре к. 312(3). Под фото напиши 3 факта о своем напарнике и тогда я поставлю тебе баллы.
''',
        3
    )
]

secret_task = (
    '''Это конец! Квест завершается и у тебя есть последняя возможность получить от него пользу. Приглашаю тебя на секретное мероприятие только для участников квеста. Команда Волонтерского центра будет ждать тебя ТОГДА-ТО ТАМ-ТО .''',
    10
)

for question in questions:
    quest_list.append(QuestStage(*question))
