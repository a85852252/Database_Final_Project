// 搜尋功能（首頁/卡牌搜尋頁）主 JS
document.addEventListener('DOMContentLoaded', () => {
  // 取得主要元件
  const btnName = document.getElementById('by-name');              // 「依卡片名稱」搜尋按鈕
  const btnSeries = document.getElementById('by-series');          // 「依系列」搜尋按鈕
  const input = document.getElementById('search-input');           // 文字搜尋框
  const searchSelect = document.getElementById('search-series-select'); // 系列下拉選單
  const results = document.getElementById('results');              // 搜尋結果區
  let mode = 'name';                                               // 當前搜尋模式（name/series）
  let debounceTimer = null;                                        // 防止輸入搜尋過於頻繁

  // 確認頁面元素都存在才繼續
  if (btnName && btnSeries && input && searchSelect && results) {

    // 切換到「依卡片名稱」搜尋模式
    btnName.addEventListener('click', () => {
      mode = 'name';
      btnName.classList.add('active');
      btnSeries.classList.remove('active');
      input.style.display = 'block';
      searchSelect.style.display = 'none';
      input.value = '';
      results.innerHTML = '';
    });

    // 切換到「依系列」搜尋模式
    btnSeries.addEventListener('click', () => {
      mode = 'series';
      btnSeries.classList.add('active');
      btnName.classList.remove('active');
      input.style.display = 'none';
      searchSelect.style.display = 'block';
      searchSelect.selectedIndex = 0;
      results.innerHTML = '';

      // 若第一次載入且還沒抓過系列清單，就 AJAX 取得所有系列資料
      if (searchSelect.options.length === 1) {
        fetch('/api/series_list')
          .then(res => res.json())
          .then(data => {
            searchSelect.innerHTML = '<option value="" disabled selected>請選擇系列名稱 (代號)…</option>';
            data.forEach(series => {
              const option = document.createElement('option');
              option.value = series.code;
              option.textContent = `[${series.code}] ${series.name}`;
              searchSelect.appendChild(option);
            });
          });
      }
    });

    // 文字輸入時（名稱搜尋），防抖處理，延遲 300ms 後發送請求
    input.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = input.value.trim();
        if (!query) {
          results.innerHTML = '';
          return;
        }
        performSearch(query);
      }, 300);
    });

    // 系列下拉選單變動時，立即查詢
    searchSelect.addEventListener('change', () => {
      const query = searchSelect.value;
      if (!query) {
        results.innerHTML = '';
        return;
      }
      performSearch(query);
    });

    /**
     * 實際 AJAX 發送搜尋請求
     * @param {string} query - 搜尋關鍵字或系列代碼
     */
    function performSearch(query) {
      fetch(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}`)
        .then(res => res.json())
        .then(data => {
          // 若有資料，產生卡片 HTML；否則顯示「查無資料」
          const html = data.length
            ? data.map(card => `
                <div class="card-result">
                  <img src="${card.image_url}" alt="${card.name}" loading="lazy">
                  <div class="card-info">
                    <div class="card-name">${card.name}</div>
                    <div class="card-code">${card.code}</div>
                    <div class="card-price">價格：${card.price}</div>
                    <div class="card-stock">庫存：${card.stock}</div>
                  </div>
                </div>
              `).join('')
            : '<p>查無資料</p>';
          results.innerHTML = html;
          enableCardHoverZoom();
        })
        .catch(err => {
          console.error('搜尋失敗：', err);
          results.innerHTML = '<p>搜尋失敗，請稍後再試。</p>';
        });
    }
  }

  /**
   * 卡片 hover 時放大效果（觸發 .zoomed class，加強用戶體驗）
   * 用 setTimeout 防止滑過時閃爍
   */
  function enableCardHoverZoom() {
    document.querySelectorAll('.card-result').forEach(card => {
      let zoomTimer = null;
      card.addEventListener('mouseenter', () => {
        zoomTimer = setTimeout(() => {
          card.classList.add('zoomed');
        }, 250);
      });
      card.addEventListener('mouseleave', () => {
        clearTimeout(zoomTimer);
        card.classList.remove('zoomed');
      });
    });
  }
});
