import { ref } from 'vue';

const message = ref('');
const visible = ref(false);
let timer = null;

export function useToast() {
  function toast(text) {
    message.value = text;
    visible.value = true;
    clearTimeout(timer);
    timer = setTimeout(() => { visible.value = false; }, 2400);
  }
  return { message, visible, toast };
}
