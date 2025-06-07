document.addEventListener('DOMContentLoaded', () => {
  // --- Flash 訊息自動淡出 ---
  const flashOverlay = document.getElementById('flash-overlay');
  const flashItems = document.querySelectorAll('#flash-box .flash');
  if (flashOverlay && flashItems.length > 0) {
    setTimeout(() => {
      flashItems.forEach(item => item.classList.add('fade-out'));
      setTimeout(() => {
        if (flashOverlay.parentNode) {
          flashOverlay.parentNode.removeChild(flashOverlay);
        }
      }, 500);
    }, 1500);
  }

  // --- 搜尋功能區（只處理搜尋頁/首頁的 select，不會動到上架頁 select） ---
  const btnName = document.getElementById('by-name');
  const btnSeries = document.getElementById('by-series');
  const input = document.getElementById('search-input');
  const searchSelect = document.getElementById('search-series-select'); // <<<<<< 只抓搜尋用的 select
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

  // --- 回到頂部 ---
  const backToTop = document.getElementById('back-to-top');
  if (backToTop) {
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
  }

  // --- 卡片 Hover 放大 ---
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

  // --- 商品多圖預覽＋可單張刪除 ---
  const imageInput = document.getElementById('image-input');
  const imagePreview = document.getElementById('image-preview');
  let selectedFiles = [];

  if (imageInput && imagePreview) {
    imageInput.addEventListener('change', function () {
      selectedFiles = Array.from(this.files);
      updateImagePreview();
    });

    function updateImagePreview() {
      imagePreview.innerHTML = '';
      selectedFiles.forEach((file, idx) => {
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = function (e) {
          const wrapper = document.createElement('div');
          wrapper.style.position = 'relative';
          wrapper.style.display = 'inline-block';

          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.maxWidth = '120px';
          img.style.maxHeight = '120px';
          img.style.borderRadius = '8px';
          img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.14)';
          img.style.objectFit = 'cover';
          img.style.display = 'block';

          const btn = document.createElement('button');
          btn.innerHTML = '✖';
          btn.type = 'button';
          btn.style.position = 'absolute';
          btn.style.top = '2px';
          btn.style.right = '2px';
          btn.style.background = 'rgba(0,0,0,0.5)';
          btn.style.color = 'white';
          btn.style.border = 'none';
          btn.style.borderRadius = '50%';
          btn.style.width = '22px';
          btn.style.height = '22px';
          btn.style.cursor = 'pointer';
          btn.style.fontSize = '14px';
          btn.title = '移除這張圖片';
          btn.addEventListener('click', function () {
            selectedFiles.splice(idx, 1);
            updateImagePreview();
            syncFilesToInput();
          });

          wrapper.appendChild(img);
          wrapper.appendChild(btn);
          imagePreview.appendChild(wrapper);
        };
        reader.readAsDataURL(file);
      });
      if (selectedFiles.length === 0) imageInput.value = '';
    }

    function syncFilesToInput() {
      const dt = new DataTransfer();
      selectedFiles.forEach(file => dt.items.add(file));
      imageInput.files = dt.files;
    }
  }

  // --- 上架商品頁的商品標籤多選（只有上架頁才有）---
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
