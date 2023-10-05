from django.core.exceptions import ObjectDoesNotExist
from firebase_admin import messaging
from notification.serializers import PushNotificationSerializer


class FirebaseMessage:

    @staticmethod
    def push_message(title, body, push_type, user_object):
        try:
            token = user_object.profile.fcm_token
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
                )
                messaging.send(message)
        except ObjectDoesNotExist:
            pass

    @staticmethod
    def push_messages(title, body, push_type, user_object_list):
        message_list = []
        user_id_list = []
        for user_object in user_object_list:
            user_id_list.append(user_object.id)
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
            messaging.send_each(message_list)