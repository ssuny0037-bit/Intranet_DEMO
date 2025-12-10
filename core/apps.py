from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"

    # 이 이름이 앱 폴더 이름이랑 같아야 함!
    name = "core"

    # Admin 왼쪽 메뉴에 보일 이름
    verbose_name = "업체 / 일정 / 직원 관리"
