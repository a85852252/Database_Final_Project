document.addEventListener('DOMContentLoaded', () => {
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
});
