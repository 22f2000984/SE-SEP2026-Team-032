export function when(iso) {
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}
export function topicsText(list) {
  return list && list.length ? list.join(', ') : '-';
}
export function userName(d, userId) {
  const u = d.users.find(x => x.id === userId);
  return u ? u.name : 'Unknown';
}
export function latestMatchOf(d, studentId) {
  return d.matches.filter(m => m.studentId === studentId).slice(-1)[0] || null;
}
