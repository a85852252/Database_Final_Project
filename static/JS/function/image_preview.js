// 商品圖片即時預覽（上架商品用）
// 功能：選擇多張圖片時即時預覽，每張圖右上可點✖移除，不用重新上傳所有檔案

document.addEventListener('DOMContentLoaded', () => {
  const imageInput = document.getElementById('image-input');      // <input type="file" ...> 元素
  const imagePreview = document.getElementById('image-preview');  // 預覽區容器
  let selectedFiles = [];                                         // 暫存目前選取的檔案陣列

  // 若頁面有上傳圖片元件，才啟用本功能
  if (imageInput && imagePreview) {

    // input 選擇圖片時觸發
    imageInput.addEventListener('change', function () {
      selectedFiles = Array.from(this.files);  // 轉為可編輯陣列
      updateImagePreview();
    });

    // 更新預覽區：每張圖包一個 wrapper+✖按鈕
    function updateImagePreview() {
      imagePreview.innerHTML = '';
      selectedFiles.forEach((file, idx) => {
        // 只預覽圖片格式
        if (!file.type.startsWith('image/')) return;
        const reader = new FileReader();
        reader.onload = function (e) {
          // 建立外層 div 方便定位刪除按鈕
          const wrapper = document.createElement('div');
          wrapper.style.position = 'relative';
          wrapper.style.display = 'inline-block';

          // 圖片本體
          const img = document.createElement('img');
          img.src = e.target.result;
          img.style.maxWidth = '120px';
          img.style.maxHeight = '120px';
          img.style.borderRadius = '8px';
          img.style.boxShadow = '0 2px 8px rgba(0,0,0,0.14)';
          img.style.objectFit = 'cover';
          img.style.display = 'block';

          // 右上角刪除按鈕
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
          // 點擊移除按鈕，刪除對應圖片，並同步 input
          btn.addEventListener('click', function () {
            selectedFiles.splice(idx, 1); // 移除這一張
            updateImagePreview();         // 重新 render 預覽
            syncFilesToInput();           // 同步 input 的檔案串
          });

          wrapper.appendChild(img);
          wrapper.appendChild(btn);
          imagePreview.appendChild(wrapper);
        };
        reader.readAsDataURL(file); // 將圖片轉 base64 預覽
      });
      // 若全部都刪掉，清空 input
      if (selectedFiles.length === 0) imageInput.value = '';
    }

    // 讓 input.files 跟 selectedFiles 同步（支援移除功能）
    function syncFilesToInput() {
      const dt = new DataTransfer();
      selectedFiles.forEach(file => dt.items.add(file));
      imageInput.files = dt.files;
    }
  }
});
