// backtotop.js
// 控制「回到頂部」按鈕的顯示與點擊效果

document.addEventListener('DOMContentLoaded', () => {
  const backToTop = document.getElementById('back-to-top'); // 取得「回到頂部」元素

  // 頁面有這個按鈕時才綁定事件
  if (backToTop) {

    // 監聽視窗捲動事件，決定顯示或隱藏按鈕
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) { // 捲動超過 300px 就顯示
        backToTop.style.display = 'flex';
        backToTop.style.opacity = '1';
      } else { // 捲回頂端時淡出、隱藏
        backToTop.style.opacity = '0';
        // 淡出動畫結束後再隱藏，避免閃爍
        setTimeout(() => {
          if (window.scrollY <= 300) {
            backToTop.style.display = 'none';
          }
        }, 200); // 和 CSS transition 配合
      }
    });

    // 點擊按鈕時平滑滾動回頁面頂部
    backToTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
});
