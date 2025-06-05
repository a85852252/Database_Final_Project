// main.js
document.addEventListener('DOMContentLoaded', () => {
  const btnName = document.getElementById('by-name');
  const btnSeries = document.getElementById('by-series');
  const input = document.getElementById('search-input');
  const results = document.getElementById('results');
  let mode = 'name';

  btnName.addEventListener('click', () => {
    mode = 'name';
    btnName.classList.add('active');
    btnSeries.classList.remove('active');
    input.placeholder = '請輸入卡片名稱…';
    results.innerHTML = '';
  });

  btnSeries.addEventListener('click', () => {
    mode = 'series';
    btnSeries.classList.add('active');
    btnName.classList.remove('active');
    input.placeholder = '請輸入系列名稱…';
    results.innerHTML = '';
  });

  let debounceTimer = null;

  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const query = input.value.trim();
      if (!query) {
        results.innerHTML = '';
        return;
      }

      fetch(`/api/search?q=${encodeURIComponent(query)}&mode=${mode}`)
        .then(res => res.json())
        .then(data => {
          const html = data.length ? data.map(card => `
            <div class="card-result">
              <img src="${card.image_url}" alt="${card.name}" loading="lazy">
              <div class="card-info">
                <div class="card-name">${card.name}</div>
                <div class="card-code">${card.code}</div>
                <div class="card-price">價格：${card.price}</div>
                <div class="card-stock">庫存：${card.stock}</div>
              </div>
            </div>
          `).join('') : '<p>查無資料</p>';

          results.innerHTML = html;
        });
    }, 300);
  });
});
