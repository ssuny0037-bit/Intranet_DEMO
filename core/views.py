from django.shortcuts import render, get_object_or_404, redirect
from .models import CalendarEvent
from .forms import CalendarEventForm   # 이거 forms에서 만들 거라 미리 적어둠


def calendar_view(request):
    events = CalendarEvent.objects.all()
    return render(request, 'core/calendar.html', {'events': events})


def calendar_event_detail(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    return render(request, 'core/calendar_detail.html', {'event': event})


def calendar_event_create(request):
    # 달력에서 클릭한 날짜가 ?start= 로 넘어오면 초기값으로 사용
    initial = {}
    start_param = request.GET.get('start')
    if start_param:
        # "2025-12-09" 같은 형식
        from datetime import datetime
        try:
            date = datetime.fromisoformat(start_param).date()
            initial['start_at'] = datetime.combine(date, datetime.min.time())
        except ValueError:
            pass

    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if request.user.is_authenticated:
                event.created_by = request.user
            event.save()
            return redirect('calendar')
    else:
        form = CalendarEventForm(initial=initial)

    return render(request, 'core/calendar_form.html', {'form': form})
