
const el = document.querySelector('.hero-reference__bottom');
if (el) {
    const s = window.getComputedStyle(el);
    console.log('DISPLAY:', s.display, 'VISIBILITY:', s.visibility, 'OPACITY:', s.opacity, 'HEIGHT:', el.offsetHeight, 'TOP:', el.getBoundingClientRect().top);
} else {
    console.log('NOT FOUND');
}
