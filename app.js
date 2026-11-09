// Shared bits for every page: storage, the challenge calendar maths, the workout log.
// Everything saves on this phone only (localStorage). Keys start with c21:
const C21 = (() => {
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d } catch (e) { return d } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)) } catch (e) { } },
    del(k) { try { localStorage.removeItem(k) } catch (e) { } }
  };
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const EMBED_OK = !/claude|anthropic/i.test(location.hostname) && location.protocol !== 'file:';
  let DATA = null;
  async function load() {
    if (DATA) return DATA;
    const r = await fetch('data/challenge.json');
    if (!r.ok) throw new Error('did not load');
    DATA = await r.json();
    return DATA;
  }
  const iso = d => d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  const today = () => { const d = new Date(); d.setHours(0, 0, 0, 0); return d };
  // The challenge starts the day the app is first opened, unless she picks another day on the calendar.
  function startDate() {
    let s = store.get('c21:start', null);
    if (!s) { s = iso(today()); store.set('c21:start', s) }
    const [y, m, d] = s.split('-').map(Number);
    return new Date(y, m - 1, d);
  }
  function setStart(d) { store.set('c21:start', iso(d)) }
  // "I'm on day N today": moves the start so that today is day N.
  function setToday(n) { const d = today(); d.setDate(d.getDate() - (n - 1)); setStart(d) }
  function dayNumber() { return Math.round((today() - startDate()) / 864e5) + 1 }   // may be < 1 or > 21
  function dateOf(n) { const d = startDate(); d.setDate(d.getDate() + n - 1); return d }
  const doneDays = () => store.get('c21:days', {});
  function markDay(n, on = true) { const d = doneDays(); if (on) d[n] = Date.now(); else delete d[n]; store.set('c21:days', d) }
  // Called when a workout is finished: tick the first not-done day that carries this workout.
  function logWorkout(w) {
    const log = store.get('c21:log', []); log.push({ t: Date.now(), id: w.id, name: w.name }); store.set('c21:log', log.slice(-300));
    if (!DATA) return;
    const d = doneDays();
    const day = DATA.days.find(x => x.workout === w.id && !d[x.day]) || DATA.days.find(x => x.workout === w.id);
    if (day) markDay(day.day);
  }
  function workoutOf(id) { return (DATA.workouts || []).find(w => w.id === id) || null }
  function weekOf(id) { return (DATA.weeks || []).find(w => w.id === id) || null }
  function weekWorkouts(id) { return DATA.workouts.filter(w => w.week === id) }
  function beep() {
    try {
      const c = new (window.AudioContext || window.webkitAudioContext)(); const g = c.createGain(); g.connect(c.destination); g.gain.value = .25;
      const o = c.createOscillator(); o.connect(g); o.frequency.value = 880; o.start(); o.stop(c.currentTime + .18);
      const o2 = c.createOscillator(); o2.connect(g); o2.frequency.value = 1175; o2.start(c.currentTime + .22); o2.stop(c.currentTime + .45)
    } catch (e) { }
    try { navigator.vibrate && navigator.vibrate([150, 80, 150]) } catch (e) { }
  }
  function yt(id, title, autoplay) {
    return `<div class="embed"><iframe src="https://www.youtube-nocookie.com/embed/${esc(id)}?rel=0&modestbranding=1&playsinline=1${autoplay ? '&autoplay=1' : ''}" title="${esc(title)}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe></div>`;
  }
  if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => { });
  return { store, esc, EMBED_OK, load, data: () => DATA, startDate, setStart, setToday, dayNumber, dateOf, doneDays, markDay, logWorkout, workoutOf, weekOf, weekWorkouts, beep, yt, iso, today };
})();
