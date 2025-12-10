from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField('업체명', max_length=200)
    memo = models.TextField('메모', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "업체"
        verbose_name_plural = "업체 목록"


class CompanyTag(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='업체'
    )
    name = models.CharField('태그', max_length=50)

    class Meta:
        verbose_name = '업체 태그'
        verbose_name_plural = '업체 태그 목록'
        ordering = ['name']

    def __str__(self):
        return f'#{self.name}'

class CompanyMemo(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='memos',
        verbose_name='업체'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='작성자'
    )
    content = models.TextField('상담내용')
    created_at = models.DateTimeField('작성일시', auto_now_add=True)

    class Meta:
        verbose_name = '상담'
        verbose_name_plural = '상담내역'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company.name} - {self.created_at:%Y-%m-%d}'


class CompanySite(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='site')
    domain = models.CharField('도메인', max_length=200, blank=True)
    admin_url = models.CharField('관리자 URL', max_length=200, blank=True)
    admin_id = models.CharField('관리자 ID', max_length=100, blank=True)
    admin_pw = models.CharField('관리자 PW', max_length=100, blank=True)
    hosting_company = models.CharField('호스팅 업체', max_length=100, blank=True)
    hosting_expire_at = models.DateField('호스팅 만료일', null=True, blank=True)
    domain_registrar = models.CharField('도메인 등록처', max_length=100, blank=True)
    domain_expire_at = models.DateField('도메인 만료일', null=True, blank=True)
    memo = models.TextField('사이트 메모', blank=True)
    class Meta:
        verbose_name = "업체 사이트"
        verbose_name_plural = "업체 사이트 목록"

    def __str__(self):
        return f'{self.company.name} 사이트 정보'
    
class Team(models.Model):
    name = models.CharField('팀명', max_length=100)
    description = models.CharField('설명', max_length=200, blank=True)

    class Meta:
        verbose_name = '팀'
        verbose_name_plural = '팀 목록'

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='팀/부서',
        related_name='employees',
    )
    position = models.CharField('직급', max_length=50, blank=True)
    phone = models.CharField('전화번호', max_length=30, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = '직원'
        verbose_name_plural = '직원 목록'

class CompanyRequest(models.Model):
    STATUS_CHOICES = [
        ('OPEN', '진행 전'),
        ('DOING', '진행 중'),
        ('DONE', '완료'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='requests')
    title = models.CharField('요청 업무', max_length=200)
    description = models.TextField('요청 상세', blank=True)
    assignee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='담당자')
    status = models.CharField('상태', max_length=10, choices=STATUS_CHOICES, default='OPEN')
    requested_at = models.DateTimeField('요청일시', auto_now_add=True)
    completed_at = models.DateTimeField('완료일시', null=True, blank=True)
    class Meta:
        verbose_name = "요청사항"
        verbose_name_plural = "요청사항 목록"

    def __str__(self):
        return f'[{self.company.name}] {self.title}'

from django.db import models
from django.contrib.auth.models import User
# 위쪽에 이미 있을 거라 생각하지만, 혹시 없으면 꼭 추가


class CalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('GENERAL', '일반'),
        ('COMPANY', '업체 관련'),
        ('MEETING', '회의'),
        ('LEAVE', '연차/휴가'),
    ]

    title = models.CharField('일정 제목', max_length=200, blank=True)
    description = models.TextField('상세 내용', blank=True)

    start_at = models.DateTimeField('시작 일시')
    end_at = models.DateTimeField('종료 일시', null=True, blank=True)

    event_type = models.CharField(
        '종류',
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='GENERAL'
    )
    
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='관련 업체',
        related_name='events'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='관련 직원',
        related_name='events'
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='등록한 사용자',
        related_name='created_events'
    )
    created_at = models.DateTimeField('등록일시', auto_now_add=True)

    class Meta:
        verbose_name = '일정'
        verbose_name_plural = '일정 목록'
        ordering = ['-start_at']

    def __str__(self):
        return self.title or '제목 없음'

    from django.urls import reverse
    def get_absolute_url(self):
        return reverse('calendar_event_detail', args=[self.pk])


