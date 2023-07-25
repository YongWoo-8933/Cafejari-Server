from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UserIdBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            # 중복된 username이 있는지 확인
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        # 유저를 구분할 수 있는 추가적인 조건
        if user.id:
            # 유저를 구분할 수 있는 로직을 추가로 처리
            # 예: 유저의 id값을 활용하여 구분
            # 여기서는 단순히 `user`를 반환하지만, 필요에 따라 추가 로직을 구현할 수 있습니다.
            return user

        return None