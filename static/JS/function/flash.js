// flash.js
// 處理所有 base.html flash 訊息（成功、警告、錯誤...）的「自動淡出」效果

document.addEventListener('DOMContentLoaded', () => {
  const flashOverlay = document.getElementById('flash-overlay');        // 整個彈窗區塊
  const flashItems = document.querySelectorAll('#flash-box .flash');    // 所有訊息（可能有多條）

  // 如果有 flash 訊息才啟用自動消失
  if (flashOverlay && flashItems.length > 0) {
    // 顯示 800ms 後，啟動淡出動畫
    setTimeout(() => {
      flashItems.forEach(item => item.classList.add('fade-out')); // 交給 CSS 動畫處理透明
      // 0.5 秒動畫結束後，整個 overlay 區塊移除出 DOM
      setTimeout(() => {
        if (flashOverlay.parentNode) {
          flashOverlay.parentNode.removeChild(flashOverlay);
        }
      }, 500); // fade-out 動畫時間要跟 CSS 一致
    }, 800); // 保持彈窗 0.8 秒再開始淡出
  }
});
