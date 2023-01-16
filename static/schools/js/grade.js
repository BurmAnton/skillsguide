document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-change').forEach(btn =>{
        btn.addEventListener('click', (event) => {
            let student_id = btn.dataset.student;
            document.querySelectorAll(`.input-${student_id}`).forEach(input =>{
                if (input.disabled){
                    input.disabled = false;
                } else {
                    input.disabled = true;
                }
            })
            if (btn.innerHTML === "Изменить") {
                btn.style.display = 'none';
                document.querySelector(`.btn-delete-${student_id}`).style.display = 'block';
                document.querySelector(`.btn-save-${student_id}`).style.display = 'block';
                document.querySelectorAll(`.stream-${student_id}`).forEach(btn =>{
                    btn.style.display = 'block';
                })
              } else {
                document.querySelector(`.btn-change-${student_id}`).style.display = 'block';
                document.querySelector(`.btn-delete-${student_id}`).style.display = 'none';
                document.querySelector(`.btn-save-${student_id}`).style.display = 'none';
                document.querySelectorAll(`.stream-${student_id}`).forEach(btn =>{
                    btn.style.display = 'none';
                })
            }
            document.querySelector(`.btn-save-${student_id}`).parentElement.classList.toggle('modal-footer-default');
        })
    })
    document.querySelectorAll('.btn-submit').forEach(btn =>{
        btn.addEventListener('click', (event) => {
            console.log("btn")
            let student_id = btn.dataset.student;
            document.querySelector(`.change-student-${student_id}`).click();
        })
    })
})