document.addEventListener('DOMContentLoaded', () => {
  const seriesSelect = document.getElementById('series-select');
  if (seriesSelect) {
    seriesSelect.choicesInstance = new Choices(seriesSelect, {
      removeItemButton: true,
      searchEnabled: true,
      placeholder: true,
      placeholderValue: '選擇商品標籤...',
      shouldSort: false
    });
  }
});
