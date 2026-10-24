// @vitest-environment jsdom
// Synthetic interface checks only; never a participant result.
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {setupTrial} from '../public/assets/trial.js';
const html=readFileSync(resolve(process.cwd(),'public/trial.html'),'utf8');
const value=name=>document.querySelector(`[name="${name}"]`);
function answer() {
  for(const name of ['role','familiarity','example']) value(name).selectedIndex=1;
  for(const name of ['purpose','evidence','actions','usefulness']) value(name).value=`SYNTHETIC TEST ONLY: ${name}`;
}
beforeEach(()=>{
  document.documentElement.innerHTML=html.replace(/<!doctype html>/i,'');
  vi.spyOn(window,'fetch').mockRejectedValue(new Error('Network forbidden in trial tests'));
  setupTrial(document,window);
});
afterEach(()=>vi.restoreAllMocks());
describe('local-only volunteer guide',()=>{
  it('does not enable collection before explicit start or make network calls',()=>{
    expect(document.getElementById('answers').disabled).toBe(true);
    expect(fetch).not.toHaveBeenCalled();
    document.getElementById('start').click();
    expect(document.getElementById('answers').disabled).toBe(false);
    expect(document.getElementById('start').disabled).toBe(true);
    expect(fetch).not.toHaveBeenCalled();
  });
  it('accepts negative observations without granting quotation permission',()=>{
    document.getElementById('start').click();answer();
    value('usefulness').value='No. I would use GitHub directly.';
    document.getElementById('prepare').click();
    expect(document.getElementById('feedback').value).toContain('No. I would use GitHub directly.');
    expect(document.getElementById('feedback').value).toContain('Not granted. Ask separately');
    expect(document.getElementById('feedback').value).toContain('not measured savings');
    expect(fetch).not.toHaveBeenCalled();
  });
  it('focuses missing input and never turns source-like input into executable HTML',()=>{
    document.getElementById('start').click();document.getElementById('prepare').click();
    expect(document.activeElement).toBe(value('role'));expect(document.getElementById('result').hidden).toBe(true);
    answer();value('evidence').value='<img src="https://example.invalid/leak" onerror="alert(1)">';
    document.getElementById('prepare').click();
    expect(document.getElementById('feedback').value).toContain('<img');
    expect(document.querySelector('#result img')).toBeNull();expect(fetch).not.toHaveBeenCalled();
  });
  it('invalidates prepared feedback after an answer or consent changes',()=>{
    document.getElementById('start').click();answer();document.getElementById('prepare').click();
    value('quotePermission').value='anonymous_only';value('quotePermission').dispatchEvent(new Event('change',{bubbles:true}));
    expect(document.getElementById('feedback').value).toBe('');expect(document.getElementById('result').hidden).toBe(true);
    document.getElementById('prepare').click();expect(document.getElementById('feedback').value).toContain('Anonymous quotations');
  });
});
