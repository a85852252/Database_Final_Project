const btnName = document.getElementById('by-name');
const btnSeries = document.getElementById('by-series');
const input = document.getElementById('search-input');
const select = document.getElementById('series-select');
const results = document.getElementById('results');
let mode = 'name';

btnName.addEventListener('click', () => {
  mode = 'name';
  btnName.classList.add('active');
  btnSeries.classList.remove('active');
  input.style.display = 'block';
  select.style.display = 'none';
  results.innerHTML = '';
});

btnSeries.addEventListener('click', () => {
  mode = 'series';
  btnSeries.classList.add('active');
  btnName.classList.remove('active');
  input.style.display = 'none';
  select.style.display = 'block';
  results.innerHTML = '';

  if (select.options.length === 1) {
    fetch('/api/series_list')
      .then(res => res.json())
      .then(data => {
        select.innerHTML = '<option value="" disabled selected>請選擇系列名稱 (代號)…</option>';
        data.forEach(series => {
          const option = document.createElement('option');
          option.value = series.code;                              
          option.textContent = `[${series.code}] ${series.name}`;   
          select.appendChild(option);
        });
      });
  }
});

function performSearch(query) {
  fetch(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}`)
    .then(res => res.json())
    .then(data => {
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
    });
}

let debounceTimer = null;
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

select.addEventListener('change', () => {
  const query = select.value;
  if (!query) {
    results.innerHTML = '';
    return;
  }
  performSearch(query);
});

document.addEventListener('DOMContentLoaded', () => {
  const backToTop = document.getElementById('back-to-top');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      backToTop.style.display = 'flex';  
      backToTop.style.opacity = '1';
    } else {
      backToTop.style.opacity = '0';
      setTimeout(() => {
        if (window.scrollY <= 300) {
          backToTop.style.display = 'none';
        }
      }, 200);
    }
  });

  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  console.log('🔧 main.js 已載入並執行');

  // ===== Part 1：Flash 訊息自動淡出 / 移除遮罩層 =====
  const flashOverlay = document.getElementById('flash-overlay');
  const flashItems = document.querySelectorAll('#flash-box .flash');

  if (flashOverlay && flashItems.length > 0) {
    // 等 3 秒後開始淡出
    setTimeout(() => {
      flashItems.forEach(item => {
        item.classList.add('fade-out');
      });
      // 再等 0.5 秒（與 CSS transition 時間對齊）後移除整個遮罩層
      setTimeout(() => {
        if (flashOverlay.parentNode) {
          flashOverlay.parentNode.removeChild(flashOverlay);
        }
      }, 500);
    }, 3000);
  }

const input = document.getElementById('search-input');
  // 依系列搜尋的下拉選單
  const select = document.getElementById('series-select');
  // 最終顯示搜尋結果的容器
  const results = document.getElementById('results');
  // 預設搜尋模式
  let mode = 'name';
  let debounceTimer = null;

  // 如果找不到 #search-input，代表這支程式不該在此頁面執行搜尋邏輯
  if (input && results) {
    // 切換到「依卡片名稱搜尋」按鈕
    const btnName = document.getElementById('by-name');
    // 切換到「依系列搜尋」按鈕
    const btnSeries = document.getElementById('by-series');

    // 綁定「依卡片名稱」Tab 的點擊
    if (btnName && btnSeries) {
      btnName.addEventListener('click', () => {
        mode = 'name';
        btnName.classList.add('active');
        btnSeries.classList.remove('active');
        input.style.display = 'block';
        if (select) select.style.display = 'none';
        results.innerHTML = '';
      });
      // 綁定「依系列搜尋」Tab 的點擊
      btnSeries.addEventListener('click', () => {
        mode = 'series';
        btnSeries.classList.add('active');
        btnName.classList.remove('active');
        input.style.display = 'none';
        if (select) select.style.display = 'block';
        results.innerHTML = '';

        // 載入一次性的系列下拉選項
        if (select && select.options.length === 1) {
          fetch('/api/series_list')
            .then(res => res.json())
            .then(data => {
              data.forEach(series => {
                const option = document.createElement('option');
                // 顯示格式：[代號] 系列名稱
                option.value = series.code;
                option.textContent = `[${series.code}] ${series.name}`;
                select.appendChild(option);
              });
            })
            .catch(err => console.error('載入系列列表錯誤：', err));
        }
      });
    }

    // 當輸入框內容改變時（防抖 300ms）
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

    // 如果下拉選單存在，則綁定「選擇系列後立即查詢」
    if (select) {
      select.addEventListener('change', () => {
        const query = select.value;
        if (!query) {
          results.innerHTML = '';
          return;
        }
        performSearch(query);
      });
    }

    // 共用的查詢函式
    function performSearch(query) {
      fetch(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}`)
        .then(res => res.json())
        .then(data => {
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
        })
        .catch(err => {
          console.error('搜尋失敗：', err);
          results.innerHTML = '<p>搜尋失敗，請稍後再試。</p>';
        });
    }
  }

  // ===== Part 3：其它頁面可放的 JS（例如回到頂部、懶加載等） =====
  // … 如果有其他腳本，也同樣放在這裡，用 if(...) 判斷是否需要執行 …
});