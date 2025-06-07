document.addEventListener('DOMContentLoaded', () => {
  const btnName = document.getElementById('by-name');
  const btnSeries = document.getElementById('by-series');
  const input = document.getElementById('search-input');
  const searchSelect = document.getElementById('search-series-select');
  const results = document.getElementById('results');
  let mode = 'name';
  let debounceTimer = null;

  if (btnName && btnSeries && input && searchSelect && results) {
    btnName.addEventListener('click', () => {
      mode = 'name';
      btnName.classList.add('active');
      btnSeries.classList.remove('active');
      input.style.display = 'block';
      searchSelect.style.display = 'none';
      input.value = '';
      results.innerHTML = '';
    });

    btnSeries.addEventListener('click', () => {
      mode = 'series';
      btnSeries.classList.add('active');
      btnName.classList.remove('active');
      input.style.display = 'none';
      searchSelect.style.display = 'block';
      searchSelect.selectedIndex = 0;
      results.innerHTML = '';

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

    searchSelect.addEventListener('change', () => {
      const query = searchSelect.value;
      if (!query) {
        results.innerHTML = '';
        return;
      }
      performSearch(query);
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
          enableCardHoverZoom();
        })
        .catch(err => {
          console.error('搜尋失敗：', err);
          results.innerHTML = '<p>搜尋失敗，請稍後再試。</p>';
        });
    }
  }

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
