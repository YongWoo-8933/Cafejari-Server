from rest_framework import status
from rest_framework.response import Response

from cafejari.settings import UPDATE_COOLTIME


class ServiceError:

    @staticmethod
    def _error_dict(error_code, error_message, detail=None):
        dict_data = {"error_code": error_code, "error_message": error_message}
        if detail is not None:
            dict_data["detail"] = detail
        return dict_data

    # 600번대 - chore
    @classmethod
    def no_request_value_response(cls, *args):
        values = ""
        for index, value in enumerate(args):
            if index == len(args) - 1:
                values += value
            else:
                values += f"{value}, "
        return Response(cls._error_dict(
            error_code=600, error_message=f"{values}을(를) 찾을 수 없습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def is_not_debug_mode_response(cls, *args):
        return Response(cls._error_dict(
            error_code=601, error_message="서버가 디버그 모드가 아닙니다"), status=status.HTTP_409_CONFLICT)

    # 700번대 - user
    @classmethod
    def no_user_response(cls):
        return Response(cls._error_dict(
            error_code=700, error_message="해당 유저가 존재하지 않습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def unauthorized_user_response(cls):
        return Response(cls._error_dict(
            error_code=701, error_message="해당 활동을 수행할 권한이 없습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def invalid_nickname_response(cls):
        return Response(cls._error_dict(
            error_code=702, error_message="닉네임에는 공백 및 특수문자를 허용하지 않습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def invalid_nickname_length_response(cls):
        return Response(cls._error_dict(
            error_code=703, error_message="닉네임은 2~10자로 정해주세요"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def duplicated_nickname_response(cls):
        return Response(cls._error_dict(
            error_code=704, error_message="이미 존재하는 닉네임입니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def profile_exist_response(cls):
        return Response(cls._error_dict(
            error_code=705, error_message="가입이 완료된 유저입니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_social_account_response(cls):
        return Response(cls._error_dict(
            error_code=706, error_message="소셜 계정으로 가입되지 않은 사용자입니다"), status=status.HTTP_409_CONFLICT)


    # 800번대 - cafe
    @classmethod
    def no_cafe_floor_response(cls):
        return Response(cls._error_dict(
            error_code=800, error_message="해당 카페 층이 존재하지 않습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_cafe_seat_response(cls):
        return Response(cls._error_dict(
            error_code=801, error_message="해당 층에는 좌석이 없어 활동 불가합니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def update_cooltime_response(cls):
        return Response(cls._error_dict(
            error_code=802, error_message=f"마지막 업데이트로부터 {UPDATE_COOLTIME}분 후 업데이트 가능합니다"), status=status.HTTP_409_CONFLICT)


    # 900번대 request
    @classmethod
    def duplicated_cafe_response(cls):
        return Response(cls._error_dict(
            error_code=900, error_message="이미 존재하는 카페이거나, 등록 요청이 거절된 카페입니다"), status=status.HTTP_409_CONFLICT)


    # 1000번대 shop
    @classmethod
    def no_item_response(cls):
        return Response(cls._error_dict(
            error_code=1000, error_message="해당 아이템이 존재하지 않습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def not_enough_point_response(cls):
        return Response(cls._error_dict(
            error_code=1001, error_message="포인트가 부족합니다. 포인트를 더 모으거나 다른 상품을 구매해주세요"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def gifticon_send_failure_response(cls):
        return Response(cls._error_dict(
            error_code=1002, error_message="서버 내 에러로 기프티콘 발송 요청에 실패했습니다. 잠시 후 다시 시도해주세요"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def gifticon_delete_failure_response(cls):
        return Response(cls._error_dict(
            error_code=1003, error_message="사용되지않은 기프티콘은 삭제할 수 없습니다. 먼저 사용완료 처리해주세요"), status=status.HTTP_409_CONFLICT)


    # 1100번대 cafe_log
    @classmethod
    def already_like_response(cls):
        return Response(cls._error_dict(
            error_code=1100, error_message="이미 좋아요를 누른 로그 입니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_cafe_log_response(cls):
        return Response(cls._error_dict(
            error_code=1102, error_message="존재하지 않는 카페 로그입니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_cafe_log_like_response(cls):
        return Response(cls._error_dict(
            error_code=1103, error_message="해당 로그를 좋아요한 이력이 없습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_cafe_response(cls):
        return Response(cls._error_dict(
            error_code=1104, error_message="존재하지 않는 카페입니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def no_snapshot_response(cls):
        return Response(cls._error_dict(
            error_code=1105, error_message="이미지가 존재하지 않습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def like_to_my_log_forbidden_response(cls):
        return Response(cls._error_dict(
            error_code=1106, error_message="내가 쓴 글에는 좋아요를 누를 수 없습니다"), status=status.HTTP_409_CONFLICT)

    @classmethod
    def already_report_response(cls):
        return Response(cls._error_dict(
            error_code=1107, error_message="해당 글을 이미 신고하셨습니다. 확인 후 조치하겠습니다"), status=status.HTTP_409_CONFLICT)


