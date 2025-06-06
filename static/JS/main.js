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
      backToTop.style.display = 'flex';  // Flexbox 模式下用 'flex'
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
