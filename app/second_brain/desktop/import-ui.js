'use strict';
async function nativeAdd(destination = '') {
  $('add').disabled = true;
  try {
    const rows = await window.pywebview.api.choose_files(destination);
    await refresh();
    if (rows.length) {
      const savedFiles = rows.filter((result) => result.ok);
      const failedFiles = rows.filter((result) => !result.ok);
      const errorDetails = failedFiles
        .map((result) => (result.path || '') + ' — ' + result.error)
        .join('\n');
      const summary = `Đã lưu ${savedFiles.length}/${rows.length} file.`;

      notice(summary + '\n' + errorDetails);
    }
  } catch (e) {
    notice(String(e));
  } finally {
    $('add').disabled = false;
  }
}
$('add').onclick = () => nativeAdd('');
$('new-folder').onclick = () => {
  options('folder-parent', (state.folders || []).filter(Boolean), 'storage/');
  $('folder-name').value = '';
  $('folder-error').textContent = '';
  $('folder-dialog').showModal();
};
$('cancel-folder').onclick = () => $('folder-dialog').close();
$('create-folder').onclick = async () => {
  const name = $('folder-name').value.trim();
  if (!name || /[\\/]/.test(name) || name === '.' || name === '..') {
    $('folder-error').textContent = 'Nhập tên thư mục hợp lệ.';
    return;
  }
  const parent = $('folder-parent').value;
  const relativePath = parent ? parent + '/' + name : name;

  try {
    const response = await window.pywebview.api.create_folder(relativePath);
    if (!response.ok) {
      throw Error(response.error);
    }

    await refresh();
    $('folder-dialog').close();
    notice('Đã tạo thư mục ' + response.folder);
  } catch (e) {
    $('folder-error').textContent = String(e);
  }
};
function contextActions(items, x, y) {
  const menu = $('trash-menu');
  menu.replaceChildren();
  for (const [label, fn] of items) {
    menu.append(
      button(label, () => {
        menu.hidden = true;
        fn();
      }),
    );
  }
  menu.hidden = false;
  menu.style.left = Math.max(0, Math.min(x, innerWidth - menu.offsetWidth - 8)) + 'px';
  menu.style.top = Math.max(0, Math.min(y, innerHeight - menu.offsetHeight - 8)) + 'px';
  menu.querySelector('button').focus();
}
async function deleteFolder(path) {
  try {
    const r = await window.pywebview.api.delete_folder(path);
    if (!r.ok) {
      throw Error(r.error);
    }
    await refresh();
  } catch (e) {
    notice(String(e));
  }
}
async function restoreFolder(identifier) {
  try {
    const response = await window.pywebview.api.restore_folder(identifier);
    if (!response.ok) {
      throw Error(response.error);
    }

    await refresh();
  } catch (error) {
    notice(String(error));
  }
}

const expandedFolders = new Set();
function renderTree(docs) {
  const host = $('documents');
  host.replaceChildren();
  const root = { folders: new Map(), files: [] };
  const normalize = (p) => p.replaceAll('\\', '/');
  const base = normalize(state.storage_root || '');
  function relative(path) {
    const p = normalize(path);
    return base && p.startsWith(base + '/') ? p.slice(base.length + 1) : p;
  }
  function ensure(path) {
    let node = root;
    for (const part of normalize(path).split('/').filter(Boolean)) {
      if (!node.folders.has(part)) {
        node.folders.set(part, { folders: new Map(), files: [] });
      }
      node = node.folders.get(part);
    }
    return node;
  }
  if (!trashMode) {
    for (const path of state.folders || []) {
      ensure(path);
    }
  } else {
    for (const entry of state.folder_trash || []) {
      if (entry.state === 'ready') {
        ensure(relative(entry.original));
      }
    }
  }
  for (const doc of docs) {
    ensure(relative(folder(doc))).files.push(doc);
  }
  function draw(node, parent, prefix = '') {
    for (const [name, child] of [...node.folders].sort(([a], [b]) =>
      a.localeCompare(b),
    )) {
      const path = prefix ? prefix + '/' + name : name;
      const key = (trashMode ? 'trash:' : 'active:') + path;
      const group = document.createElement('details');
      group.open = expandedFolders.has(key);
      group.ontoggle = () => {
        if (group.open) {
          expandedFolders.add(key);
        } else {
          expandedFolders.delete(key);
        }
      };
      const summary = document.createElement('summary');
      summary.textContent = '📁 ' + name;
      if (!trashMode) {
        summary.oncontextmenu = (e) => {
          e.preventDefault();
          contextActions(
            [
              ['add..', () => nativeAdd(path)],
              ['delete', () => deleteFolder(path)],
            ],
            e.clientX,
            e.clientY,
          );
        };
      }
      if (trashMode) {
        const record = (state.folder_trash || []).find(
          (r) => relative(r.original) === path,
        );
        if (record) {
          summary.oncontextmenu = (e) => {
            e.preventDefault();
            contextActions(
              [['Khôi phục thư mục', () => restoreFolder(record.id)]],
              e.clientX,
              e.clientY,
            );
          };
        }
      }
      const children = document.createElement('div');
      draw(child, children, path);
      group.append(summary, children);
      parent.append(group);
    }
    for (const doc of node.files) {
      const entry = button(
        '▤ ' + doc.name,
        () => {
          if (trashMode) {
            selected = doc.id;
            openPreview(doc.id);
          } else {
            select(doc.id);
          }
        },
        selected === doc.id ? 'chosen' : '',
      );
      entry.oncontextmenu = (e) => {
        e.preventDefault();
        selected = doc.id;
        if (trashMode) {
          showTrashMenu(doc.id, e.clientX, e.clientY);
        } else {
          contextActions(
            [
              ['view', () => openPreview(doc.id)],
              ['delete', () => action('trash')],
            ],
            e.clientX,
            e.clientY,
          );
        }
      };
      parent.append(entry);
    }
  }
  draw(root, host);
}
