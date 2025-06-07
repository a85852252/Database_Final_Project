document.addEventListener('DOMContentLoaded', () => {
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
});
