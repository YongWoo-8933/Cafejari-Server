import logging

from django.core.exceptions import ObjectDoesNotExist
from firebase_admin import messaging
from firebase_admin.messaging import UnregisteredError

from notification.serializers import PushNotificationSerializer


class FirebaseMessage:

    @staticmethod
    def push_message(title, body, push_type, user_object, save_model):
        try:
            token = user_object.profile.fcm_token
            if save_model:
                serializer = PushNotificationSerializer(data={
                    "title": title,
                    "body": body,
                    "type": push_type,
                    "user": user_object.id
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
            if token:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    token=user_object.profile.fcm_token,
                    data={
                        "bottom_tab_index": "2"
                    }
                )
                try:
                    messaging.send(message)
                except UnregisteredError:
                    pass
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def push_messages(title, body, push_type, user_object_list, save_model):
        message_list = []
        user_id_list = []
        for user_object in user_object_list:
            user_id_list.append(user_object.id)
            if save_model:
                serializer = PushNotificationSerializer(data={
                    "title": title,
                    "body": body,
                    "type": push_type,
                    "user": user_object.id
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
            try:
                token = user_object.profile.fcm_token
                if token:
                    message_list.append(
                        messaging.Message(
                            notification=messaging.Notification(
                                title=title,
                                body=body,
                            ),
                            token=token,
                        )
                    )
            except ObjectDoesNotExist:
                continue
        if message_list:
            try:
                messaging.send_each(message_list)
            except UnregisteredError:
                pass
