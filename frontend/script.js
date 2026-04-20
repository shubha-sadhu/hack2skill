function getAuthHeaders() {
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please login first");
    goPage("login");
    return {};
  }

  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  };
}

// ── CONFIG ──────────────────────────────────────────────────
const BASE = 'http://127.0.0.1:8000';

// ── UTILS ───────────────────────────────────────────────────
const $ = id => document.getElementById(id);

function goPage(name) {
	document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
	$('page-' + name).classList.add('active');
	window.scrollTo(0, 0);
}

function toast(msg) {
	const t = $('toast');
	t.textContent = msg;
	t.classList.add('show');
	setTimeout(() => t.classList.remove('show'), 2400);
}

// ── TYPEWRITER ───────────────────────────────────────────────
const phrases = [
	["Predict delays.", "Outrun disruption."],
	["See risk early.", "Ship smarter."],
	["Know before delay.", "Act before loss."]
];

function typewriterLoop() {
	const l1 = document.getElementById('line1');
	const l2 = document.getElementById('line2');

	let p = 0, i = 0, phase = 1;
	const speed = 50;
	const delay = 1200;

	function tick() {
		const [line1, line2] = phrases[p];

		if (phase === 1) {
			l1.textContent = line1.slice(0, i++);
			if (i <= line1.length) return setTimeout(tick, speed);
			phase = 2; i = 0;
			return setTimeout(tick, 300);
		}

		if (phase === 2) {
			l2.textContent = line2.slice(0, i++);
			if (i <= line2.length) return setTimeout(tick, speed);
			phase = 3;
			return setTimeout(tick, delay);
		}

		if (phase === 3) {
			i = i - 1;
			l2.textContent = line2.substring(0, i) || " ";
			if (i > 0) return setTimeout(tick, 40);

			phase = 4;
			i = line1.length;
			return setTimeout(tick, 150);
		}

		if (phase === 4) {
			i = i - 1;
			l1.textContent = line1.substring(0, i) || " ";
			if (i > 0) return setTimeout(tick, 40);

			p = (p + 1) % phrases.length;
			phase = 1;
			i = 0;
			return setTimeout(tick, 300);
		}
	}

	tick();
}

typewriterLoop();

// show UI once
document.getElementById('hero-p').classList.add('show');
document.getElementById('hero-pills').classList.add('show');
document.getElementById('hero-actions').classList.add('show');

// ── RISK HELPERS ─────────────────────────────────────────────
function riskColor(s) { return s >= .7 ? 'var(--red)' : s >= .4 ? 'var(--amber)' : 'var(--green)'; }
function riskClass(s) { return s >= .7 ? 'r' : s >= .4 ? 'a' : 'g'; }
function riskLevel(s) { return s >= .7 ? 'HIGH' : s >= .4 ? 'MEDIUM' : 'LOW'; }

// ── VALIDATION ───────────────────────────────────────────────
function validate() {
	document.querySelectorAll('#page-single .field').forEach(f => f.classList.remove('error'));
	let ok = true;
	[
		['s-mode',   v => v !== ''],
		['s-status', v => v !== ''],
		['s-days',   v => v !== '' && !isNaN(v) && +v >= 0],
		['s-wday',   v => v !== '' && +v >= 0 && +v <= 6],
		['s-month',  v => v !== '' && +v >= 1 && +v <= 12],
		['s-qty',    v => v !== '' && +v >= 1],
		['s-sales',  v => v !== '' && !isNaN(v) && +v >= 0],
		['s-profit', v => v !== '' && !isNaN(v) && +v >= -1 && +v <= 1],
		['s-lat',    v => v !== '' && !isNaN(v)],
		['s-lon',    v => v !== '' && !isNaN(v)],
		['s-cust',   v => v.trim() !== ''],
		['s-order',  v => v.trim() !== ''],
	].forEach(([id, fn]) => {
		if (!fn($(id).value)) { $(id).closest('.field').classList.add('error'); ok = false; }
	});
	return ok;
}

// ── EXAMPLE DATA ─────────────────────────────────────────────
function fillEx() {
	const v = {
		mode: 'Second Class', status: 'PENDING_PAYMENT', days: '3', wday: '2',
		month: '7', qty: '3', sales: '299.97', profit: '0.44',
		lat: '18.35', lon: '-66.07', cust: 'Puerto Rico', order: 'Germany'
	};
	Object.entries(v).forEach(([k, val]) => $('s-' + k).value = val);
	document.querySelectorAll('#page-single .field').forEach(f => f.classList.remove('error'));
}

function buildPayload() {
	return {
		Shipping_Mode: $('s-mode').value,
		Order_Status: $('s-status').value,
		Days_for_shipment_scheduled: +$('s-days').value,
		order_weekday: +$('s-wday').value,
		order_month: +$('s-month').value,
		Order_Item_Quantity: +$('s-qty').value,
		Sales: +$('s-sales').value,
		Order_Item_Profit_Ratio: +$('s-profit').value,
		Latitude: +$('s-lat').value,
		Longitude: +$('s-lon').value,
		Customer_Country: $('s-cust').value.trim(),
		Order_Country: $('s-order').value.trim()
	};
}

// ── SINGLE PREDICT ───────────────────────────────────────────
async function runPredict() {
	if (!validate()) return;
	$('p-load').classList.add('show');
	$('p-err').classList.remove('show');
	$('p-result').style.display = 'none';

	let data;
	try {
		const r = await fetch(`${BASE}/predict`, {
			method: 'POST',
			headers: getAuthHeaders(),
			body: JSON.stringify(buildPayload())
		});
		if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
		data = await r.json();
	} catch (e) {
		$('p-load').classList.remove('show');
		$('p-err').textContent = 'Error: ' + e.message + ' — is the API running at localhost:8000?';
		$('p-err').classList.add('show');
		return;
	}

	$('p-load').classList.remove('show');
	const sc = data.final_risk_score ?? 0;
	const pr = data.delay_probability ?? 0;
	const dy = data.delay_days ?? 0;
	const wd = data.will_delay;

	$('r-prob').textContent = (pr * 100).toFixed(1) + '%';
	$('r-prob').className = 'mval ' + riskClass(pr);
	$('r-days').textContent = wd ? dy.toFixed(1) + 'd' : '—';
	$('r-days').className = 'mval ' + (wd ? 'a' : 'g');
	$('r-score').textContent = sc.toFixed(2);
	$('r-score').className = 'mval ' + riskClass(sc);
	$('r-fill').style.width = (sc * 100).toFixed(1) + '%';
	$('r-fill').style.background = riskColor(sc);
	$('r-level').textContent = riskLevel(sc);

	const lvl = riskLevel(sc).toLowerCase();
	$('r-badge').className = 'badge ' + lvl;
	$('r-badge').innerHTML = '<span class="badge-dot"></span>' + (wd ? 'delay expected' : 'on time');

	if (data.disruption_summary) {
		$('r-disc-text').textContent = data.disruption_summary;
		$('r-disc').style.display = 'block';
	} else {
		$('r-disc').style.display = 'none';
	}

	$('p-result').style.display = 'block';
	toast('Prediction complete');
}

// ── BATCH ────────────────────────────────────────────────────
let csvRows = [];
let selectedFile = null;

function loadCSV(ev) {
	const file = ev.target.files[0];
	if (!file) return;
	selectedFile = file;

	$('b-fname').textContent = file.name;
	$('b-btn').disabled = false;
	const rd = new FileReader();
	rd.onload = e => {
		const lines = e.target.result.trim().split('\n');
		const hdrs = lines[0].split(',').map(h => h.trim());
		csvRows = lines.slice(1)
			.map(l => {
				const vs = l.split(','), r = {};
				hdrs.forEach((h, i) => r[h] = (vs[i] || '').trim());
				return r;
			})
			.filter(r => Object.values(r).some(v => v !== ''));
		toast(`Loaded ${csvRows.length} rows`);
	};
	rd.readAsText(file);
}

async function runBatch() {
	$('b-load').classList.add('show');
	$('b-err').classList.remove('show');
	$('b-results').style.display = 'none';

	let data;
	try {
		const fd = new FormData();
		fd.append("file", selectedFile);

		const token = localStorage.getItem("token");

		const r = await fetch(`${BASE}/predict-batch-file`, {
			method: 'POST',
			headers: {
				"Authorization": `Bearer ${localStorage.getItem("token")}`
			}, 
			body: fd
		});
		if (!r.ok) throw new Error(`${r.status}`);
		data = await r.json();
	} catch (e) {
		$('b-load').classList.remove('show');
		$('b-err').textContent = 'Error: ' + e.message + ' — check API at localhost:8000';
		$('b-err').classList.add('show');
		return;
	}

	$('b-load').classList.remove('show');
	const rows = Array.isArray(data) ? data : (data.results || []);
	$('b-tbody').innerHTML = '';
	rows.forEach((row, i) => {
		const sc = row.final_risk_score ?? 0;
		const lvl = riskLevel(sc).toLowerCase();
		const tr = document.createElement('tr');
		tr.innerHTML = `
      <td style="font-family:var(--mono);color:var(--muted)">${i + 1}</td>
      <td style="font-family:var(--mono);font-size:10px">${row.Customer_Country || '—'} → ${row.Order_Country || '—'}</td>
      <td>${row.Shipping_Mode || '—'}</td>
      <td style="font-family:var(--mono)">${((row.delay_probability ?? 0) * 100).toFixed(1)}%</td>
      <td style="font-family:var(--mono)">${row.will_delay ? (row.delay_days ?? 0).toFixed(1) + 'd' : '—'}</td>
      <td style="font-family:var(--mono)">${sc.toFixed(2)}</td>
      <td><span class="badge ${lvl}"><span class="badge-dot"></span>${lvl.toUpperCase()}</span></td>
    `;
		$('b-tbody').appendChild(tr);
	});

	$('b-results').style.display = 'block';
	toast(`${rows.length} predictions done`);
}

// ── CHARTS ───────────────────────────────────────────────────
const cOpts = {
	color: '#5f7a9f',
	plugins: { legend: { display: false } },
	scales: {
		x: { grid: { color: 'rgba(79,142,255,.08)' }, ticks: { color: '#5f7a9f', font: { size: 9 } } },
		y: { grid: { color: 'rgba(79,142,255,.08)' }, ticks: { color: '#5f7a9f', font: { size: 9 } } }
	}
};

new Chart($('c-mode'), {
	type: 'bar',
	data: {
		labels: ['First', 'Second', 'Standard', 'Same Day'],
		datasets: [{ data: [0.48, 0.72, 0.65, 0.21], backgroundColor: ['#22c98a', '#f5a623', '#f5365c', '#4f8eff'], borderRadius: 5, borderSkipped: false }]
	},
	options: { ...cOpts, responsive: true, maintainAspectRatio: true }
});

new Chart($('c-risk'), {
	type: 'doughnut',
	data: {
		labels: ['Low', 'Medium', 'High'],
		datasets: [{ data: [82, 101, 65], backgroundColor: ['#22c98a', '#f5a623', '#f5365c'], borderWidth: 0, hoverOffset: 4 }]
	},
	options: {
		responsive: true, maintainAspectRatio: true, cutout: '60%',
		plugins: { legend: { display: true, position: 'right', labels: { color: '#8aa4c8', font: { size: 10 }, boxWidth: 8, padding: 10 } } }
	}
});

new Chart($('c-vol'), {
	type: 'line',
	data: {
		labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr'],
		datasets: [{
			data: [28, 34, 19, 41, 38, 52, 36],
			borderColor: '#4f8eff', backgroundColor: 'rgba(79,142,255,.07)',
			tension: .4, fill: true, pointBackgroundColor: '#4f8eff', pointRadius: 3, pointHoverRadius: 5
		}]
	},
	options: { ...cOpts, responsive: true, maintainAspectRatio: false }
});

// Login routine
async function login() {
  const res = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      email: document.getElementById("email").value,
      password: document.getElementById("password").value
    })
  });

  if (!res.ok) {
    alert("Login failed ❌");
    return;
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);

  alert("Login successful ✅");

  // redirect to dashboard
  goPage('dash');
}

// Logout routine
function logout() {
  localStorage.removeItem("token");
  alert("Logged out");
  location.reload();
}

// Authentication check
window.onload = () => {
  const token = localStorage.getItem("token");

  if (!token) {
    goPage("login");
  } else {
    goPage("dash");
  }
};

//Signup routine
async function signup() {
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;

  if (!email || !password) {
    alert("Fill all fields");
    return;
  }

  const res = await fetch(`${BASE}/signup`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    alert("Signup failed ❌ (user may already exist)");
    return;
  }

  // 🔥 AUTO LOGIN
  const loginRes = await fetch(`${BASE}/login`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ email, password })
  });

  const data = await loginRes.json();
  localStorage.setItem("token", data.access_token);

  alert("Signup + Login successful ✅");

  goPage("dash");
}