/** Local-only volunteer feedback. No analytics, remote submission or real-trial certification. */
export function setupTrial(doc = document, win = window) {
  const root = doc.getElementById('trial-form');
  if (!root) return;
  let startedAt = null;
  let startedClock = null;
  const status = doc.getElementById('status');
  const feedback = doc.getElementById('feedback');
  const text = name => root.querySelector(`[name="${name}"]`).value.trim();
  const required = ['role', 'familiarity', 'example', 'purpose', 'evidence', 'actions', 'usefulness'];
  const start = doc.getElementById('start');
  start.addEventListener('click', () => {
    if (startedAt !== null) return;
    startedAt = new Date().toISOString();
    startedClock = win.performance.now();
    doc.getElementById('answers').disabled = false;
    start.disabled = true;
    doc.getElementById('start-status').textContent = 'Started. Open the example in the other tab, then return here. Nothing is uploaded.';
  });
  const invalidate = () => {
    if (!feedback.value) return;
    feedback.value = '';
    doc.getElementById('result').hidden = true;
    status.textContent = 'Answers changed. Prepare feedback again before sharing.';
  };
  root.addEventListener('input', invalidate);
  root.addEventListener('change', invalidate);
  doc.getElementById('prepare').addEventListener('click', () => {
    if (startedAt === null) return;
    const missing = required.find(name => !text(name));
    if (missing) {
      status.textContent = 'Please answer the highlighted question. An incomplete or negative experience is a valid response.';
      root.querySelector(`[name="${missing}"]`).focus();
      return;
    }
    const seconds = Math.max(0, Math.round((win.performance.now() - startedClock) / 1000));
    const rows = [
      '# ReviewRadar volunteer observations',
      'Protocol: first-use-v1. Self-reported observations; participant identity and completion are not verified by this page.',
      `Started (UTC): ${startedAt}`, `Prepared (UTC): ${new Date().toISOString()}`,
      `Elapsed seconds: ${seconds} (includes pauses, reading and writing; not measured savings)`,
      `Perspective: ${text('role')}`, `Prior PR familiarity: ${text('familiarity')}`, `Example used: ${text('example')}`,
      '\n## What I thought the app did', text('purpose'),
      '\n## Request, response and evidence I inspected', text('evidence'),
      '\n## Save / reviewed / reopen observations', text('actions'),
      '\n## Friction and whether I would use it', text('usefulness'),
      '\n## Help, interruptions or incomplete tasks', text('help') || 'Not provided',
      `\nQuotation permission: ${text('quotePermission') === 'anonymous_only' ? 'Anonymous quotations of these answers allowed. No named quotation permission.' : 'Not granted. Ask separately before quoting.'}`,
      '\nPrepared locally. The page did not submit this feedback. Public GitHub comments expose the commenter’s account.'
    ];
    feedback.value = rows.join('\n\n');
    doc.getElementById('result').hidden = false;
    status.textContent = 'Prepared locally. Review the text before downloading or sharing.';
    feedback.focus();
  });
  doc.getElementById('download').addEventListener('click', () => {
    if (!feedback.value) return;
    const url = win.URL.createObjectURL(new win.Blob([feedback.value], {type:'text/plain;charset=utf-8'}));
    const link = doc.createElement('a');
    link.href = url; link.download = 'reviewradar-volunteer-feedback.txt';
    doc.body.append(link); link.click(); link.remove();
    win.setTimeout(() => win.URL.revokeObjectURL(url), 1000);
    status.textContent = 'Downloaded to your computer. Nothing was submitted.';
  });
  doc.getElementById('copy').addEventListener('click', async () => {
    if (!feedback.value) return;
    try {
      await win.navigator.clipboard.writeText(feedback.value);
      status.textContent = 'Copied. Sharing is your choice; nothing was submitted.';
    } catch {
      status.textContent = 'Clipboard unavailable. Select the prepared text to copy it, or download it.';
      feedback.focus(); feedback.select();
    }
  });
}
if (typeof document !== 'undefined') setupTrial();
