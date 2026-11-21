'use strict';
const $ = (id) => document.getElementById(id);
const ns = 'http://www.w3.org/2000/svg';
let state = { documents: [], trash: [], tags: [], edges: [], operations: [] };
let selected = null;
let trashMode = false;
let scale = 1;
let pan = { x: 0, y: 0 };
const folder = (d) => d.path.replace(/[/\\][^/\\]+$/, '');
function el(tag, attributes = {}) {
  const element = document.createElementNS(ns, tag);

  for (const [name, value] of Object.entries(attributes)) {
    element.setAttribute(name, value);
  }

  return element;
}

function button(text, onClick, className = '') {
  const element = document.createElement('button');
  element.textContent = text;
  element.onclick = onClick;
  element.className = className;

  return element;
}
function notice(text) {
  if (trashMode) {
    if (text && text !== 'Đã hoàn tất.') {
      window.alert(text);
    }
    return;
  }
  $('notice').textContent = text;
}
const current = () => (trashMode ? state.trash : state.documents) || [];
function select(id) {
  selected = id;
  renderDetails();
  render();
}
async function action(name) {
  try {
    const r = await window.pywebview.api.action(selected, name);
    if (!r.ok) {
      throw Error(r.error);
    }
    if (!r.cancelled) {
      notice('Đã hoàn tất.');
    }
    await refresh();
  } catch (e) {
    notice(String(e));
  }
}
function renderDetails() {
  const d = current().find((d) => d.id === selected);
  $('details').hidden = trashMode || !d;
  if (trashMode || !d) {
    return;
  }
  $('name').textContent = '▤ ' + d.name;
  $('path').textContent = d.path;
  const statusLabels = {
    available: '● File sẵn sàng',
    missing: '⚠ Không tìm thấy file',
  };
  const fileStatus = statusLabels[d.status] || '⚠ Không đọc được file';
  $('status').textContent = fileStatus + ' · Chưa lập chỉ mục RAG';
  $('tags').value = d.tags.join(', ');
  $('selected-tags').replaceChildren();
  for (const tag of d.tags) {
    $('selected-tags').append(
      button(tag + (trashMode ? '' : ' ×'), () => {
        if (!trashMode) {
          saveTags(d.tags.filter((t) => t !== tag));
        }
      }),
    );
  }
  $('edit-tags').hidden = trashMode;
  $('actions').replaceChildren();
  const actions = trashMode
    ? [
        ['Khôi phục', 'restore'],
        ['Chọn đích khác', 'restore_as'],
        ['Xóa vĩnh viễn', 'purge'],
      ]
    : [
        ['▤ Xem nội dung', 'preview'],
        ['↗ Mở bản sao', 'open'],
        ['⟳ Làm mới', 'refresh'],
        ['♜ Thùng rác', 'trash'],
      ];
  for (const [label, name] of actions) {
    let className = '';
    if (['trash', 'purge'].includes(name)) {
      className = 'danger';
    } else if (name === 'open') {
      className = 'primary';
    }

    const onClick = () => {
      if (name === 'preview') {
        return openPreview(selected);
      }
      if (name === 'refresh') {
        return refresh().catch((error) => notice(String(error)));
      }
      return action(name);
    };

    $('actions').append(button(label, onClick, className));
  }
}
function render() {
  const q = $('search').value.toLocaleLowerCase();
  const tag = $('tag-filter').value;
  const dir = $('folder-filter').value;
  const docs = state.documents.filter((document) => {
    const searchableText = [document.name, document.path, ...document.tags]
      .join(' ')
      .toLocaleLowerCase();
    const matchesQuery = searchableText.includes(q);
    const matchesTag = !tag || document.tags.includes(tag);
    const matchesFolder = !dir || folder(document) === dir;

    return matchesQuery && matchesTag && matchesFolder;
  });
  $('count').textContent = `▤ ${docs.length}/${state.documents.length} tài liệu`;
  $('filter-state').textContent =
    q || tag || dir ? '▽ Đang lọc tài liệu' : '▽ Không có bộ lọc';
  $('empty').hidden = docs.length > 0;
  $('empty').textContent = state.documents.length
    ? 'Không có tài liệu khớp bộ lọc.'
    : 'Thêm file đầu tiên để thắp sáng vũ trụ tri thức.';
  renderGraph(docs);
  if (typeof renderTree === 'function') {
    renderTree(trashMode ? current() : docs);
  }
  $('all-tags').replaceChildren();
  for (const t of state.tags) {
    $('all-tags').append(
      button(t.label, () => {
        $('tag-filter').value = t.label;
        render();
      }),
    );
  }
}
function options(id, values, label) {
  const select = $(id);
  const old = select.value;
  select.replaceChildren(new Option(label, ''));
  for (const v of values) {
    select.add(new Option(v, v));
  }
  select.value = values.includes(old) ? old : '';
}
async function refresh() {
  const r = await window.pywebview.api.get_state();
  if (!r.ok) {
    throw Error(r.error);
  }
  state = { trash: [], operations: [], ...r.data };
  options('destination', (state.folders || []).filter(Boolean), 'storage/');
  options(
    'tag-filter',
    state.tags.map((t) => t.label),
    '◇ Tag',
  );
  options('folder-filter', [...new Set(state.documents.map(folder))], '▱ Thư mục');
  if (state.operations.length) {
    notice(
      '⚠ Có thao tác file gián đoạn. Các tài liệu liên quan được khóa để tránh mất dữ liệu. Kiểm tra journal trước khi tiếp tục.',
    );
  }
  renderDetails();
  render();
}
async function saveTags(tags) {
  try {
    const r = await window.pywebview.api.set_tags(selected, tags);
    if (!r.ok) {
      throw Error(r.error);
    }
    await refresh();
    notice('Đã lưu tag.');
  } catch (e) {
    notice(String(e));
  }
}
function tabs() {
  $('tab-docs').classList.toggle('active', !trashMode);
  $('tab-trash').classList.toggle('active', trashMode);
  $('import-tools').hidden = trashMode;
  $('notice').hidden = trashMode;
  $('list-title').hidden = trashMode;
  $('list-title').textContent = 'Thư mục & tài liệu';
  $('trash-menu').hidden = true;
}
$('tab-docs').onclick = () => {
  trashMode = false;
  selected = null;
  tabs();
  renderDetails();
  render();
};
$('tab-trash').onclick = () => {
  trashMode = true;
  selected = null;
  tabs();
  renderDetails();
  render();
};
$('edit-tags').onclick = () => {
  $('tag-editor').hidden = !$('tag-editor').hidden;
};
$('save').onclick = () => saveTags($('tags').value.split(','));
$('search').oninput = render;
$('tag-filter').onchange = render;
$('folder-filter').onchange = render;
$('fit').onclick = () => {
  scale = 1;
  pan = { x: 0, y: 0 };
  updateGraphTransform();
};
$('reset').onclick = () => {
  $('search').value = '';
  $('tag-filter').value = '';
  $('folder-filter').value = '';
  $('fit').click();
};
function zoom(f) {
  scale = Math.max(0.3, Math.min(4, scale * f));
  updateGraphTransform();
}
$('zoom-in').onclick = () => zoom(1.2);
$('zoom-out').onclick = () => zoom(1 / 1.2);
$('graph').onwheel = (e) => {
  e.preventDefault();
  zoom(e.deltaY < 0 ? 1.1 : 1 / 1.1);
};
let drag = null;
$('graph').onpointerdown = (e) => {
  if (e.target.closest('.node')) {
    return;
  }
  drag = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  $('graph').setPointerCapture(e.pointerId);
};
$('graph').onpointermove = (e) => {
  if (drag) {
    pan = { x: e.clientX - drag.x, y: e.clientY - drag.y };
    updateGraphTransform();
  }
};
$('graph').onpointerup = () => {
  drag = null;
};
$('graph').onpointercancel = () => {
  drag = null;
};
$('settings').onclick = () =>
  notice(
    'Python + HTML/JS · config.yaml tại root dự án. MCP, RAG và UI quản trị quyền chưa triển khai.',
  );
$('add').onclick = async () => {
  $('add').disabled = true;
  try {
    const results = await window.pywebview.api.choose_files($('destination').value);
    notice(
      results
        .map((r) =>
          r.ok
            ? (r.duplicate ? 'Đã quản lý: ' : 'Đã thêm: ') + r.path
            : 'Lỗi: ' + r.error,
        )
        .join('\n'),
    );
    await refresh();
  } catch (e) {
    notice(String(e));
  } finally {
    $('add').disabled = false;
  }
};
window.addEventListener('pywebviewready', async () => {
  try {
    await refresh();
    $('add').disabled = false;
  } catch (e) {
    notice(String(e));
  }
});
new ResizeObserver(render).observe($('universe'));

const previews = new Map();
function showPreview(id) {
  const value = previews.get(id);
  $('preview-tabs').replaceChildren();
  for (const [key, item] of previews) {
    $('preview-tabs').append(
      button(item.name, () => showPreview(key)),
      button('×', () => {
        previews.delete(key);
        if (previews.size) {
          showPreview(previews.keys().next().value);
        } else {
          $('preview-dialog').close();
        }
      }),
    );
  }
  $('preview-body').replaceChildren();
  if (value.kind === 'image') {
    const image = document.createElement('img');
    image.src = value.content;
    image.alt = value.name;
    $('preview-body').append(image);
  } else {
    const note = document.createElement('p');
    note.textContent =
      (value.note || 'Văn bản chỉ đọc') +
      (value.limited ? ' — Nội dung bị giới hạn' : '');
    const pre = document.createElement('pre');
    pre.textContent = value.content;
    $('preview-body').append(note, pre);
  }
  if (!$('preview-dialog').open) {
    $('preview-dialog').showModal();
  }
}
async function openPreview(id) {
  try {
    const r = await window.pywebview.api.preview(id);
    if (!r.ok) {
      throw Error(r.error);
    }
    previews.set(id, r.data);
    showPreview(id);
  } catch (e) {
    notice(String(e));
  }
}
$('close-preview').onclick = () => $('preview-dialog').close();
function showTrashMenu(id, x, y) {
  selected = id;
  const menu = $('trash-menu');
  menu.replaceChildren();
  for (const [label, name] of [
    ['Xem nội dung', 'preview'],
    ['Khôi phục', 'restore'],
    ['Khôi phục ở vị trí khác', 'restore_as'],
    ['Xóa vĩnh viễn', 'purge'],
  ]) {
    menu.append(
      button(
        label,
        () => {
          menu.hidden = true;
          if (name === 'preview') {
            openPreview(id);
          } else {
            action(name);
          }
        },
        name === 'purge' ? 'danger' : '',
      ),
    );
  }
  menu.hidden = false;
  menu.style.left = Math.max(0, Math.min(x, innerWidth - menu.offsetWidth - 8)) + 'px';
  menu.style.top = Math.max(0, Math.min(y, innerHeight - menu.offsetHeight - 8)) + 'px';
  menu.querySelector('button').focus();
}
document.addEventListener('click', (e) => {
  if (!e.target.closest('#trash-menu')) {
    $('trash-menu').hidden = true;
  }
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    $('trash-menu').hidden = true;
  }
});
