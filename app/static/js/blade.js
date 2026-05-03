// ASE Hub - Blade Panel

function openBlade(title, contentHtml) {
  const overlay = document.getElementById('blade-overlay');
  const blade = document.getElementById('blade');
  document.getElementById('blade-title').textContent = title;
  document.getElementById('blade-body').innerHTML = contentHtml;
  overlay.classList.add('blade-overlay--active');
  blade.classList.add('blade--open');
  document.body.style.overflow = 'hidden';
}

function closeBlade() {
  const overlay = document.getElementById('blade-overlay');
  const blade = document.getElementById('blade');
  overlay.classList.remove('blade-overlay--active');
  blade.classList.remove('blade--open');
  document.body.style.overflow = '';
}

// ESC key to close
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeBlade();
});
