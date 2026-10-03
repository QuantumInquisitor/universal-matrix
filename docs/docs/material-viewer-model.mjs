const fail = message => { throw new Error(message); };
const finite = x => typeof x === 'number' && Number.isFinite(x);
const vector = (x, n) => Array.isArray(x) && x.length === n && x.every(finite);
export const pointPoweredIdentity = Object.freeze({
  inertia_model: 'material-body-point-inertia-v1',
  state_layout: 'material-powered-node9-edge2-input1-v1',
  energy_ownership: 'material-powered-node-edge-group-ledgers-v1',
});
const validateIdentity = data => {
  // Absence alone retains historical v1 point-model compatibility.
  if (!Object.hasOwn(data, 'model_identity')) return;
  const value = data.model_identity;
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).length !== Object.keys(pointPoweredIdentity).length ||
      Object.entries(pointPoweredIdentity).some(([key, expected]) => value[key] !== expected)) {
    fail('Unsupported inertia, state layout or energy ownership.');
  }
};
export function validate(data) {
  if (data?.schema !== 'matrix-science-viewer-timeseries-v1') fail('Unsupported frame schema.');
  validateIdentity(data);
  if (!Array.isArray(data.frames) || !data.frames.length || data.frames.length !== data.frame_count) fail('Invalid frame count.');
  if (!Number.isInteger(data.module_count) || data.module_count < 1) fail('Invalid module count.');
  const u = data.units;
  if (u?.source_length !== 'metre' || u.time !== 'second' || u.energy !== 'joule' || u.angle !== 'radian' || !finite(u.display_m_per_unit) || u.display_m_per_unit <= 0) fail('Unsupported units.');
  let previous = -Infinity;
  let identities;
  const hasMechanical = data.frames[0]?.modules?.[0]?.mechanical_j !== undefined;
  for (const frame of data.frames) {
    if (!finite(frame.time_s) || frame.time_s <= previous) fail('Times must increase.');
    previous = frame.time_s;
    if (!Array.isArray(frame.modules) || frame.modules.length !== data.module_count) fail('Module count changed.');
    const ids = [];
    for (const m of frame.modules) {
      if (hasMechanical ? !finite(m.mechanical_j) : m.mechanical_j !== undefined) fail('Inconsistent mechanical energy ledger.');
      if (typeof m.id !== 'string' || !vector(m.q, 2) || !vector(m.rates, 2)) fail('Invalid module state.');
      for (const v of [m.reserve_j, m.delivered_work_j, m.input_j, m.losses_j?.damping, m.losses_j?.conversion, m.losses_j?.leakage]) if (!finite(v)) fail('Invalid energy ledger.');
      if (!Array.isArray(m.bodies) || m.bodies.length !== 22) fail('Expected 22 source bodies per module.');
      const bodies = new Set();
      for (const b of m.bodies) {
        if (typeof b.id !== 'string' || bodies.has(b.id)) fail('Invalid body identity.');
        bodies.add(b.id);
        if (!Array.isArray(b.vertices_m) || !b.vertices_m.length || !b.vertices_m.every(v => vector(v,3))) fail('Invalid metre geometry.');
        if (!Array.isArray(b.vertices_display) || b.vertices_display.length !== b.vertices_m.length) fail('Missing display geometry.');
        b.vertices_m.forEach((v,i) => {
          if (!vector(b.vertices_display[i],3) || v.some((x,j) => Math.abs(x / u.display_m_per_unit - b.vertices_display[i][j]) > 1e-10)) fail('Display scale disagrees with metre geometry.');
        });
      }
      ids.push([m.id, ...bodies].join('|'));
    }
    if (new Set(frame.modules.map(m => m.id)).size !== data.module_count) fail('Duplicate modules.');
    if (identities && JSON.stringify(ids) !== identities) fail('Body identities changed between frames.');
    identities = JSON.stringify(ids);
    for (const field of ['edge_potential_j', 'edge_work_j']) {
      if (!Array.isArray(frame[field]) || !frame[field].flat().every(finite)) fail('Invalid edge ledger.');
    }
  }
  return data;
}
export function frameAt(frames, time) {
  let index = 0;
  while (index + 1 < frames.length && frames[index + 1].time_s <= time) index++;
  return index;
}
export function project([x,y,z], yaw, pitch) {
  const a = x*Math.cos(yaw) + z*Math.sin(yaw);
  const b = -x*Math.sin(yaw) + z*Math.cos(yaw);
  return [a, y*Math.cos(pitch)-b*Math.sin(pitch), y*Math.sin(pitch)+b*Math.cos(pitch)];
}

export function mechanicalLabel(module) {
  return module.mechanical_j === undefined ? "Unavailable in this export" : module.mechanical_j.toExponential(6) + " J";
}
