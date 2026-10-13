/* Standalone data layer.
   Inside Claude the page talks to the artifact database through window.claude.
   Anywhere else (Vercel, a local server) this shim stands in for it: it reads one
   JSON snapshot, data/db.json, and serves it read-only. Shape of the file:
   { "exportedAt": "YYYY-MM-DD", "collections": { "<collection>": { "<docId>": { ...document } } } } */
(function(){
  if(window.claude && window.claude.use) return;
  var store = null, exportedAt = null;
  var load = fetch('data/db.json', {cache: 'no-store'})
    .then(function(r){ if(!r.ok) throw new Error('no data file'); return r.json(); })
    .then(function(j){ store = j.collections || j; exportedAt = j.exportedAt || null; return true; })
    .catch(function(){ store = null; return false; });
  function snap(c){ var col = (store && store[c]) || {}; return {docs: Object.keys(col).sort().map(function(id){ return {id: id, exists: true, data: function(){ return col[id]; }}; })}; }
  function deny(){ var e = new Error('This copy is read-only'); e.code = 'invalid_argument'; return Promise.reject(e); }
  function docRef(c, id){ return {id: id, path: c + '/' + id, set: deny, update: deny, delete: deny}; }
  var db = {
    doc: function(p){ var i = p.indexOf('/'); return docRef(p.slice(0, i), p.slice(i + 1)); },
    collection: function(c){ return {
      doc: function(id){ return docRef(c, id || 'new'); },
      onSnapshot: function(cb){ load.then(function(){ cb(snap(c)); }); return function(){}; }
    }; }
  };
  window.claude = {use: function(name){ return load.then(function(ok){ return !ok ? null : name === 'db' ? db : name === 'user' ? {can: function(){ return Promise.resolve(false); }} : null; }); }};
  function banner(ok){
    var n = document.createElement('div');
    n.setAttribute('role', 'status');
    n.style.cssText = 'padding:8px 16px;font-size:13px;line-height:1.4;background:var(--warn-wash);color:var(--warn-text);border-bottom:1px solid var(--line)';
    n.textContent = ok
      ? 'Read-only copy' + (exportedAt ? ', data exported ' + exportedAt : '') + '. Tasks, targets and counts are edited on the Claude page.'
      : 'No data file found. This build reads public/data/db.json. See the README.';
    document.body.insertBefore(n, document.body.firstChild);
  }
  load.then(function(ok){ if(document.body) banner(ok); else document.addEventListener('DOMContentLoaded', function(){ banner(ok); }); });
})();
