/* 小松鼠的果子课 · 共用交互 */
(function () {
  const PROGRESS_KEY = 'squirrel-fruit-course-v1';
  const PARENT_KEY = 'squirrel-fruit-parent-mode';

  function readProgress() {
    try { return JSON.parse(localStorage.getItem(PROGRESS_KEY)) || {}; }
    catch (e) { return {}; }
  }

  function saveProgress(p) {
    try { localStorage.setItem(PROGRESS_KEY, JSON.stringify(p)); } catch (e) {}
  }

  function updateProgressUI() {
    const p = readProgress();
    document.querySelectorAll('[data-progress]').forEach(function (el) {
      const id = el.getAttribute('data-progress');
      el.classList.toggle('earned', !!p[id]);
    });
  }

  function markDone(id) {
    const p = readProgress();
    p[id] = true;
    saveProgress(p);
    updateProgressUI();
    burst();
  }

  function setParentMode(on) {
    document.body.classList.toggle('parent-mode', !!on);
    try { localStorage.setItem(PARENT_KEY, on ? '1' : '0'); } catch (e) {}
    const btn = document.getElementById('parentToggle');
    if (btn) btn.textContent = on ? '关闭家长模式' : '家长模式';
  }

  function toggleParent() {
    setParentMode(!document.body.classList.contains('parent-mode'));
  }

  function speak(text) {
    if (!('speechSynthesis' in window)) {
      alert('这个浏览器不支持朗读，请家长读给孩子听。');
      return;
    }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'zh-CN';
    u.rate = 0.9;
    u.pitch = 1.05;
    const voices = window.speechSynthesis.getVoices();
    const zh = voices.find(function (v) { return /zh|Chinese|中文/i.test(v.lang + ' ' + v.name); });
    if (zh) u.voice = zh;
    window.speechSynthesis.speak(u);
  }

  function setupReadButtons() {
    document.querySelectorAll('[data-read-target]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const el = document.querySelector(btn.getAttribute('data-read-target'));
        if (el) speak(el.innerText.replace(/\s+/g, ' ').trim());
      });
    });
  }

  function setupReveals() {
    document.querySelectorAll('[data-reveal]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const el = document.querySelector(btn.getAttribute('data-reveal'));
        if (!el) return;
        el.classList.toggle('show');
        const open = el.classList.contains('show');
        btn.textContent = open ? '藏起来' : (btn.getAttribute('data-label') || '看答案');
      });
    });
  }

  function setupDoneButtons() {
    document.querySelectorAll('[data-done]').forEach(function (btn) {
      const id = btn.getAttribute('data-done');
      if (readProgress()[id]) {
        btn.textContent = '⭐ 已贴星星！';
        btn.disabled = true;
      }
      btn.addEventListener('click', function () {
        markDone(id);
        btn.textContent = '⭐ 已贴星星！';
        btn.disabled = true;
      });
    });
  }

  function burst() {
    const layer = document.createElement('div');
    layer.className = 'confetti';
    const emojis = ['⭐', '🍎', '🌰', '🍐', '🍊', '✨'];
    for (let i = 0; i < 18; i++) {
      const s = document.createElement('span');
      s.textContent = emojis[Math.floor(Math.random() * emojis.length)];
      s.style.left = (Math.random() * 100) + '%';
      s.style.top = '-10%';
      s.style.animationDelay = (Math.random() * 0.5) + 's';
      layer.appendChild(s);
    }
    document.body.appendChild(layer);
    setTimeout(function () { layer.remove(); }, 2400);
  }

  function setupParentToggle() {
    const btn = document.getElementById('parentToggle');
    if (btn) btn.addEventListener('click', toggleParent);
  }

  document.addEventListener('DOMContentLoaded', function () {
    try {
      if (localStorage.getItem(PARENT_KEY) === '1') setParentMode(true);
    } catch (e) {}
    updateProgressUI();
    setupReadButtons();
    setupReveals();
    setupDoneButtons();
    setupParentToggle();
  });

  window.SquirrelCourse = {
    speak: speak,
    markDone: markDone,
    updateProgressUI: updateProgressUI
  };
})();
