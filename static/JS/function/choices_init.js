// choices_init.js
// 初始化 Choices.js 外掛，美化並強化「商品標籤」多選下拉選單（上架商品用）

document.addEventListener('DOMContentLoaded', () => {
  const seriesSelect = document.getElementById('series-select'); // 找到系列多選下拉

  // 只在有這個 select 的頁面（如商品上架）才執行
  if (seriesSelect) {
    // 將 Choices.js 套件初始化於此 select
    // 可多選、可移除、支援搜尋、可顯示預設提示、不自動排序
    seriesSelect.choicesInstance = new Choices(seriesSelect, {
      removeItemButton: true,            // 可在選中標籤右側顯示移除按鈕
      searchEnabled: true,               // 支援下拉搜尋
      placeholder: true,                 // 支援 placeholder
      placeholderValue: '選擇商品標籤...', // placeholder 內容
      shouldSort: false                  // 維持選項順序，不自動排序
    });
  }
});
