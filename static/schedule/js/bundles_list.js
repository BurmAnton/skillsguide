document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.cycle-next').forEach(btn =>{
        btn.addEventListener('click', (event) => {
            let bundle_id = btn.dataset.bundleid;
            document.querySelector(`#Step1${bundle_id}`).style.display = 'none';
            document.querySelector(`#Step2${bundle_id}`).style.display = 'block';
            btn.style.display = 'none';
            document.querySelector(`#AddCycleSubmit${bundle_id}`).style.display = 'block';
        })
    })
    document.querySelectorAll('.is_any_day').forEach(checkbox =>{
        checkbox.addEventListener('change', (event) => {
            let bundle_id = checkbox.dataset.bundleid;
            if (event.currentTarget.checked) {
                document.querySelector(`#DaysOfWeek${bundle_id}`).style.display = 'none';
                document.querySelector(`#DaysPerWeek${bundle_id}`).style.display = 'block';
            } else {
                document.querySelector(`#DaysOfWeek${bundle_id}`).style.display = 'block';
                document.querySelector(`#DaysPerWeek${bundle_id}`).style.display = 'none';
            }
        })
    })
})