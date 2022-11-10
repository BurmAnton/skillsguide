document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.is_online').forEach(check =>{
        check_is_online(check);
        check.addEventListener('change', function() {
            check_is_online(check);
        })
    })
})

function check_is_online(check){
    const testid = check.dataset.testid;
    if (check.checked) {
        document.querySelector(`.test${testid}_workshop`).style.display = 'none';
        document.querySelector(`.test${testid}_conference`).style.display = 'block';
    } else {
        document.querySelector(`.test${testid}_workshop`).style.display = 'block';
        document.querySelector(`.test${testid}_conference`).style.display = 'none';
    }
}