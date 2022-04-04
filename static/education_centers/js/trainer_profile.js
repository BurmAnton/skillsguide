document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-add-link').forEach(btn =>{
        let slot_id = btn.dataset.slot
        document.querySelector('.slot-input').setAttribute('value',slot_id);
    });

    document.querySelectorAll('.btn-change-link').forEach(btn =>{
        let slot_id = btn.dataset.slot
        document.querySelector('.slot-input').setAttribute('value',slot_id);
        let instruction = btn.dataset.instruction
        document.querySelector('.instruction-input').innerHTML = instruction;
        let zoom = btn.dataset.zoom
        document.querySelector('.zoom-input').setAttribute('value',zoom);
    })
})