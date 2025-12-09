document.addEventListener('DOMContentLoaded', function () {
  const typeSelect = document.getElementById('id_event_type');
  const titleInput = document.getElementById('id_title');

  if (!typeSelect || !titleInput) {
    return;
  }

  function updateTitle() {
    const value = typeSelect.value;
    // 종류가 LEAVE(연차/휴가)이고, 제목이 비어 있으면 자동 입력
    if (value === 'LEAVE' && !titleInput.value) {
      titleInput.value = '연차 신청';
    }
  }

  typeSelect.addEventListener('change', updateTitle);
});
