document.addEventListener('DOMContentLoaded', () => {
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
    }, 800);
  }
});