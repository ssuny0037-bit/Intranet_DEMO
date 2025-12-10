from datetime import datetime, time, timedelta
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.safestring import mark_safe
from django import forms              
from django.db import models          
from .models import (
    Company,
    CompanySite,
    CompanyTag,
    CompanyMemo,
    Employee,
    CompanyRequest,
    CalendarEvent,
)
from datetime import date

admin.site.site_header = "리플레이컴퍼니 INTRANET"      # 왼쪽 상단 큰 제목
admin.site.site_title = "리플레이컴퍼니 INTRANET"       # 브라우저 탭 타이틀
admin.site.index_title = "사이트 관리"                   # 그 아래 "사이트 관리" 글자

def get_expiration_alerts():
    """호스팅/도메인 만료가 30일 이내인 사이트 목록을 돌려준다."""
    today = date.today()
    soon = today + timedelta(days=30)

    alerts = []

    hosting = CompanySite.objects.filter(
        hosting_expire_at__isnull=False,
        hosting_expire_at__lte=soon,
    )
    for site in hosting:
        expire = site.hosting_expire_at
        delta = (expire - today).days

        # D-Day 포맷
        if delta > 0:
            dday = f"D-{delta}"
        elif delta == 0:
            dday = "D-DAY"
        else:
            dday = f"D+{abs(delta)} (만료됨)"

        alerts.append({
            "company": site.company.name,
            "type": "호스팅",
            "date": expire,
            "dday": dday,
            "company_id": site.company.id,
        })

    domain = CompanySite.objects.filter(
        domain_expire_at__isnull=False,
        domain_expire_at__lte=soon,
    )
    for site in domain:
        expire = site.domain_expire_at
        delta = (expire - today).days

        if delta > 0:
            dday = f"D-{delta}"
        elif delta == 0:
            dday = "D-DAY"
        else:
            dday = f"D+{abs(delta)} (만료됨)"

        alerts.append({
            "company": site.company.name,
            "type": "도메인",
            "date": expire,
            "dday": dday,
            "company_id": site.company.id,
        })

    return alerts


# ✅ 주간 반복 일정 생성 액션
def make_weekly_events(modeladmin, request, queryset):
    """
    선택한 일정을 기준으로 앞으로 10주 동안
    매주 같은 요일/시간에 반복 일정을 생성한다.
    """
    for event in queryset:
        for i in range(1, 11):  # 1주 ~ 10주 후까지
            start = event.start_at + timedelta(days=7 * i)
            end = event.end_at + timedelta(days=7 * i) if event.end_at else None

            CalendarEvent.objects.create(
                event_type=event.event_type,
                title=event.title,
                description=event.description,
                start_at=start,
                end_at=end,
                company=event.company,
                employee=event.employee,
                created_by=event.created_by,
            )


make_weekly_events.short_description = "선택한 일정 기준으로 앞으로 10주 반복 일정 생성"

class CompanySiteInline(admin.StackedInline):
    """업체 상세에서 사이트 정보를 바로 편집"""
    model = CompanySite
    extra = 0
    can_delete = False


class CompanyEventInline(admin.TabularInline):
    """업체와 연결된 일정 목록 (읽기 전용)"""
    model = CalendarEvent
    fk_name = 'company'
    extra = 0
    fields = ('title', 'event_type', 'start_at', 'end_at', 'employee')
    readonly_fields = ('title', 'event_type', 'start_at', 'end_at', 'employee')
    can_delete = False
    show_change_link = True  # 일정 클릭 시 일정 수정 화면으로 이동


class CompanyMemoInline(admin.TabularInline):
    """업체 메모 (작성일/작성자 자동)"""
    model = CompanyMemo
    extra = 1
    fields = ('created_at', 'author', 'content')
    readonly_fields = ('created_at', 'author')

    formfield_overrides = {
        models.TextField: {
            'widget': forms.Textarea(attrs={
                'rows': 3,          # 줄 수 (2~3줄 정도 높이)
                'style': 'width: 95%;',
            })
        }
    }


class CompanyTagInline(admin.TabularInline):
    """업체 계약 태그"""
    model = CompanyTag
    extra = 1
    fields = ('name',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'site_domain', 'tag_list')
    search_fields = ('name', 'memo')

    # ✅ 이 템플릿을 업체 수정 화면에 쓰겠다는 선언
    change_form_template = "admin/core/company/change_form.html"

    inlines = [CompanyTagInline, CompanySiteInline, CompanyEventInline, CompanyMemoInline]

    fields = ('name', 'memo')

    def site_domain(self, obj):
        if hasattr(obj, 'site') and obj.site and obj.site.domain:
            return obj.site.domain
        return '-'
    site_domain.short_description = '도메인'

    def tag_list(self, obj):
        tags = obj.tags.all().values_list('name', flat=True)
        if not tags:
            return ''
        return ', '.join(f'#{t}' for t in tags)
    tag_list.short_description = '계약 태그'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, CompanyMemo) and not obj.author:
                obj.author = request.user
            obj.save()
        formset.save_m2m()

    # ✅ 여기서 업체 수정 화면에 넘겨줄 extra_context 를 채운다
    def change_view(self, request, object_id, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['expiration_alerts'] = get_expiration_alerts()
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
     # ✅ 업체 목록 화면에도 expiration_alerts 넣기
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['expiration_alerts'] = get_expiration_alerts()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CompanySite)
class CompanySiteAdmin(admin.ModelAdmin):
    list_display = ('company', 'domain', 'hosting_company', 'hosting_expire_at', 'domain_expire_at')
    search_fields = ('company__name', 'domain')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'team', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(CompanyRequest)
class CompanyRequestAdmin(admin.ModelAdmin):
    list_display = ('company', 'title', 'assignee', 'status', 'requested_at', 'completed_at')
    list_filter = ('status', 'company')
    search_fields = ('title', 'description', 'company__name')


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_at', 'end_at', 'company', 'employee')
    list_filter = ('event_type', 'company', 'employee')
    search_fields = ('title', 'description', 'company__name', 'employee__user__username')
    date_hierarchy = 'start_at'

    # 폼 필드 순서
    fields = (
        'event_type',
        'title',
        'description',
        'start_at',
        'end_at',
        'company',
        'employee',
        'created_by',
    )

    # ✅ 액션 등록 (위에서 정의한 make_weekly_events 사용)
    actions = [make_weekly_events]

    # ✅ change_list 상단에 "캘린더 보기" 추가하기 위한 템플릿
    change_list_template = "admin/core/calendarevent/change_list.html"

    class Media:
        # 종류 선택 시 연차 → 제목 자동 입력 JS
        js = ('admin/js/calendar_event.js',)

    # ✅ add 폼에 들어올 때 ?start=YYYY-MM-DD 있으면 start_at 기본값으로 세팅
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        start_param = request.GET.get('start')
        if start_param:
            try:
                date = datetime.fromisoformat(start_param).date()
                initial['start_at'] = datetime.combine(date, time(9, 0))
            except ValueError:
                pass
        return initial

    # ✅ 저장 시 연차/휴가면 제목 강제로 '연차 신청'으로, created_by 자동 세팅
    def save_model(self, request, obj, form, change):
        if obj.event_type == 'LEAVE':
            obj.title = '연차 신청'
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # ✅ admin 내부에 /calendar/ 경로 추가 (관리자용 캘린더 화면)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "calendar/",
                self.admin_site.admin_view(self.calendar_view),
                name="core_calendarevent_calendar",
            ),
            path(
                "calendar/add/",
                self.admin_site.admin_view(self.calendar_add_view),
                name="core_calendarevent_calendar_add",
            ),
        ]
        return custom_urls + urls


    # ✅ admin용 캘린더 뷰
    def calendar_view(self, request):
        events = CalendarEvent.objects.all()
        context = dict(
            self.admin_site.each_context(request),
            events=events,
            opts=self.model._meta,
            title="일정 캘린더",
        )
        return TemplateResponse(request, "admin/core/calendarevent/calendar.html", context)

    # ✅ 모달에서 넘어온 폼을 처리해서 일정 생성하는 뷰
    def calendar_add_view(self, request):
        if request.method != "POST":
            return redirect("admin:core_calendarevent_calendar")

        date_str = request.POST.get("date")           # YYYY-MM-DD
        start_time = request.POST.get("start_time")   # HH:MM
        end_time = request.POST.get("end_time")       # HH:MM (옵션)
        event_type = request.POST.get("event_type") or "GENERAL"
        title = request.POST.get("title") or ""

        if not date_str or not start_time:
            # 최소한 날짜/시작시간은 있어야 함
            return redirect("admin:core_calendarevent_calendar")

        from datetime import datetime

        try:
            start_dt = datetime.fromisoformat(f"{date_str}T{start_time}:00")
        except ValueError:
            return redirect("admin:core_calendarevent_calendar")

        end_dt = None
        if end_time:
            try:
                end_dt = datetime.fromisoformat(f"{date_str}T{end_time}:00")
            except ValueError:
                end_dt = None

        # 연차/휴가면 제목 자동
        if event_type == "LEAVE" and not title:
            title = "연차 신청"

        event = CalendarEvent(
            event_type=event_type,
            title=title,
            start_at=start_dt,
            end_at=end_dt,
            created_by=request.user if request.user.is_authenticated else None,
        )
        event.save()

        return redirect("admin:core_calendarevent_calendar")
    