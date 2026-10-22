const urls = document.querySelector('#urls');
const previewButton = document.querySelector('#preview');
const startButton = document.querySelector('#start');
const previewCard = document.querySelector('#preview-card');
const message = document.querySelector('#message');
const quality = document.querySelector('#quality');
let mode = 'video';

function showMessage(text, error = false) {
  message.textContent = text;
  message.classList.remove('hidden', 'error');
  if (error) message.classList.add('error');
}
function currentUrl() { return urls.value.split(/\r?\n/).map(x => x.trim()).find(Boolean) || ''; }

document.querySelector('#new-download').addEventListener('click', event => {
  event.preventDefault();
  urls.value = '';
  previewCard.classList.add('hidden');
  quality.innerHTML = '<option value="">Automática · mejor disponible</option>';
  document.querySelector('#quality-row').classList.add('hidden');
  document.querySelectorAll('.format-card').forEach(button => button.classList.toggle('selected', button.dataset.mode === 'video'));
  mode = 'video';
  document.querySelector('#destination').textContent = 'downloads/video';
  message.classList.add('hidden');
  message.classList.remove('error');
  closeCompletion();
  urls.focus();
});

function closeCompletion() {
  document.querySelector('#completion-modal').classList.add('hidden');
}
function showCompletion(jobId, job) {
  const modal = document.querySelector('#completion-modal');
  const summary = document.querySelector('#completion-summary');
  const files = document.querySelector('#completion-files');
  files.replaceChildren();
  const completed = job.files?.length || 0;
  summary.textContent = job.errors?.length
    ? `${completed} de ${job.total} archivos descargados. ${job.errors.length} con error.`
    : `${completed} ${completed === 1 ? 'archivo listo' : 'archivos listos'} para abrir.`;
  (job.files || []).forEach((file, index) => {
    const row = document.createElement('div');
    row.className = 'completion-file';
    const name = document.createElement('span');
    name.textContent = file.name;
    const link = document.createElement('a');
    link.href = `/api/jobs/${encodeURIComponent(jobId)}/files/${index}`;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = 'Ver archivo';
    row.append(name, link);
    files.append(row);
  });
  (job.errors || []).forEach(error => {
    const row = document.createElement('div');
    row.className = 'completion-file error';
    const label = document.createElement('span');
    label.textContent = error;
    row.append(label);
    files.append(row);
  });
  modal.classList.remove('hidden');
  modal.querySelector('.modal-x').focus();
}
document.querySelectorAll('[data-dismiss="true"]').forEach(button => button.addEventListener('click', closeCompletion));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closeCompletion();
});

document.querySelectorAll('.format-card').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.format-card').forEach(item => item.classList.remove('selected'));
  button.classList.add('selected');
  mode = button.dataset.mode;
  document.querySelector('#quality-row').classList.toggle('hidden', mode !== 'video');
  document.querySelector('#destination').textContent = `downloads/${mode}`;
}));

previewButton.addEventListener('click', async () => {
  const url = currentUrl();
  if (!url) return showMessage('Pega un enlace de YouTube para consultar el video.', true);
  previewButton.disabled = true;
  previewButton.textContent = 'Consultando…';
  message.classList.add('hidden');
  try {
    const response = await fetch('/api/preview', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({url})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    previewCard.innerHTML = `<img src="${data.thumbnail}" alt=""><div><b></b><small></small></div>`;
    previewCard.querySelector('b').textContent = data.title;
    previewCard.querySelector('small').textContent = `${data.author} · ${Math.floor(data.duration / 60)} min`;
    previewCard.classList.remove('hidden');
    quality.innerHTML = '<option value="">Automática · mejor disponible</option>';
    data.formats.forEach(format => {
      const option = document.createElement('option');
      option.value = format.itag;
      option.textContent = `${format.resolution} · MP4`;
      quality.append(option);
    });
  } catch (error) { showMessage(error.message || 'No se pudo consultar el video.', true); }
  finally { previewButton.disabled = false; previewButton.innerHTML = 'Consultar video <span>→</span>'; }
});

async function watchJob(id) {
  const response = await fetch(`/api/jobs/${id}`);
  const job = await response.json();
  showMessage(`${job.message} ? ${job.completed}/${job.total}${job.errors?.length ? ` ? Errores: ${job.errors.length}` : ''}`);
  if (job.status !== 'done') return setTimeout(() => watchJob(id).catch(() => showMessage('Se perdi? la conexi?n con la descarga.', true)), 1100);
  startButton.disabled = false;
  startButton.innerHTML = 'Descargar ahora <span>?</span>';
  showCompletion(id, job);
}

startButton.addEventListener('click', async () => {
  if (!urls.value.trim()) return showMessage('Pega al menos un enlace para empezar.', true);
  startButton.disabled = true;
  startButton.textContent = 'Iniciando…';
  try {
    const response = await fetch('/api/download', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({urls:urls.value, mode, itag:quality.value})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    showMessage('Descarga iniciada. Puedes dejar esta pestaña abierta para ver el progreso.');
    watchJob(data.job_id);
  } catch (error) {
    showMessage(error.message || 'No se pudo iniciar la descarga.', true);
    startButton.disabled = false;
    startButton.innerHTML = 'Descargar ahora <span>↓</span>';
  }
});
