# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
url = "http://haleinee.herokuapp.com/"


def main():
    vk_session = vk_api.VkApi(
        token="45f6ed504964fd4eb6093238f44db01ec4791749cfddd05d875e8f001b07fd68a2baaa44d9cd6f71df14f")

    longpoll = VkBotLongPoll(vk_session, "204162851")

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            if u"Команды" in event.obj.message['text']:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=u"Сайт - актуальный адрес нашего сайта",
                                 random_id=random.randint(0, 2 ** 64))
            elif u"Сайт" in event.obj.message['text']:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=url,
                                 random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=u"Спасибо, что написали нам. Мы обязательно ответим",
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
