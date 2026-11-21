// Graph geometry stays in world coordinates; stars and labels stay screen-sized.
let graphSignature = '';
let graphNodeCount = 0;

function starGradient(id, stops) {
  const gradient = el('radialGradient', { id });
  for (const [offset, opacity] of stops) {
    gradient.append(
      el('stop', {
        offset,
        'stop-color': '#9acfff',
        'stop-opacity': opacity,
      }),
    );
  }
  return gradient;
}

function updateGraphTransform() {
  const layer = $('graph').querySelector('.graph-layer');
  if (!layer) {
    return;
  }
  layer.setAttribute('transform', `translate(${pan.x} ${pan.y}) scale(${scale})`);
  for (const node of layer.querySelectorAll('.node')) {
    const { x, y } = node.dataset;
    node.setAttribute('transform', `translate(${x} ${y}) scale(${1 / scale})`);
  }
  const labelsVisible = graphNodeCount <= 12 && scale >= 0.8;
  $('graph').classList.toggle('labels-visible', labelsVisible);
}

function updateGraphSelection() {
  for (const node of $('graph').querySelectorAll('.node')) {
    const isSelected = node.dataset.id === selected;
    node.classList.toggle('selected', isSelected);
    node.setAttribute('aria-pressed', String(isSelected));
  }
  for (const edge of $('graph').querySelectorAll('.edge')) {
    const related =
      edge.dataset.source === selected || edge.dataset.target === selected;
    edge.classList.toggle('related', Boolean(selected) && related);
    edge.classList.toggle('muted', Boolean(selected) && !related);
  }
}

function createStar(document, position) {
  const node = el('g', {
    class: 'node',
    tabindex: 0,
    role: 'button',
    'aria-label': document.name,
    'data-id': document.id,
    'data-x': position.x,
    'data-y': position.y,
  });
  node.append(el('circle', { r: 17, class: 'hit-target' }));
  const visual = el('g', { class: 'star-visual' });
  visual.append(
    el('circle', { r: 20, class: 'halo' }),
    el('ellipse', { rx: 11, ry: 0.75, class: 'ray' }),
    el('ellipse', { rx: 0.75, ry: 11, class: 'ray' }),
    el('circle', { r: 7, class: 'near-glow' }),
    el('circle', { r: 2.8, class: 'core' }),
    el('circle', { r: 12, class: 'selection' }),
  );
  const caption = el('g', { class: 'node-label' });
  const shortName =
    document.name.length > 26 ? document.name.slice(0, 24) + '…' : document.name;
  caption.append(
    el('rect', {
      x: 15,
      y: -24,
      width: shortName.length * 6.2 + 14,
      height: 21,
      class: 'label',
    }),
  );
  const text = el('text', { x: 22, y: -10 });
  text.textContent = shortName;
  caption.append(text);
  const title = el('title');
  title.textContent = document.name + '\n' + document.path;
  node.append(visual, caption, title);

  function activate() {
    trashMode = false;
    tabs();
    select(document.id);
  }
  node.onclick = (event) => {
    event.stopPropagation();
    activate();
  };
  node.onkeydown = (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      activate();
    }
  };
  return node;
}

function renderGraph(documents) {
  const graph = $('graph');
  const width = graph.clientWidth;
  const height = graph.clientHeight;
  const signature = JSON.stringify([width, height, documents, state.edges]);
  if (signature === graphSignature) {
    updateGraphSelection();
    updateGraphTransform();
    return;
  }
  graphSignature = signature;
  graphNodeCount = documents.length;
  const focusedId = graph.contains(document.activeElement)
    ? document.activeElement.dataset.id
    : null;
  const defs = el('defs');
  defs.append(
    starGradient('star-halo', [
      ['0%', 0.85],
      ['18%', 0.5],
      ['45%', 0.16],
      ['75%', 0.04],
      ['100%', 0],
    ]),
    starGradient('star-near', [
      ['0%', 1],
      ['35%', 0.75],
      ['100%', 0],
    ]),
  );
  const layer = el('g', { class: 'graph-layer' });
  const points = new Map(
    documents.map((item, index) => {
      const angle = index * 2.39996;
      const radius =
        Math.sqrt((index + 0.5) / Math.max(1, documents.length)) *
        Math.min(width * 0.35, height * 0.34);
      return [
        item.id,
        {
          x: width / 2 + Math.cos(angle) * radius,
          y: height / 2 + Math.sin(angle) * radius,
        },
      ];
    }),
  );
  for (const edge of state.edges) {
    const source = points.get(edge.source);
    const target = points.get(edge.target);
    if (source && target) {
      layer.append(
        el('line', {
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          class: 'edge',
          'data-source': edge.source,
          'data-target': edge.target,
        }),
      );
    }
  }
  for (const item of documents) {
    layer.append(createStar(item, points.get(item.id)));
  }
  graph.replaceChildren(defs, layer);
  updateGraphSelection();
  updateGraphTransform();
  if (focusedId) {
    const focusedNode = [...layer.querySelectorAll('.node')].find(
      (node) => node.dataset.id === focusedId,
    );
    focusedNode?.focus({ preventScroll: true });
  }
}
