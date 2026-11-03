import { nextId } from './ids';

export function notify(d, userId, text) {
  d.notifications.push({ id: nextId(d), userId, text, at: new Date().toISOString(), read: false });
}
export function notifyAdmins(d, text) {
  d.users.filter(u => u.role === 'admin').forEach(a => notify(d, a.id, text));
}
export function notificationsFor(d, userId, limit) {
  return d.notifications.filter(n => n.userId === userId).slice(-limit).reverse();
}
