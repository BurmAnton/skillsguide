document.addEventListener('DOMContentLoaded', function() {
    const cssPhone = 'input[name="phone"';
    (new phoneMask()).init(cssPhone);
    //Скрываем форму регистрации и выбора типа регистрации
    document.querySelector('.reg-form').style.display = "none";
    document.querySelector('.reg-choice-form').style.display = "none";

    //Добавляем прослушивание кнопки регистрации
    document.querySelector('.reg-button').addEventListener('click', () => {choice()});
    
    document.querySelector("#form-disability").style.display = "none";
    document.querySelector('#disability-check').addEventListener('change', (event) => {
        if (event.currentTarget.checked) {
            document.querySelector('#form-disability').style.display = "block";
        } else {
            document.querySelector('#form-disability').style.display = "none";
        }
    })

    document.querySelectorAll('.parent-step-mandatory').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.parent-step-mandatory')});
    });
    document.querySelectorAll('.child-step-mandatory').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.child-step-mandatory')});
    });
    document.querySelectorAll('.child-step-mandatory-select').forEach(input =>{
        input.addEventListener('change', () => {cheak_step('.child-step-mandatory')});
    });
    document.querySelectorAll('.auth-step').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.auth-step-mandatory')});
    });
    document.querySelectorAll('.auth-step-mandatory-phone').forEach(input =>{
        input.addEventListener('input', () => {cheak_step('.auth-step-mandatory')});
    });

    document.querySelector('.btn-forward').addEventListener('click', () => {
        click_forward();
    });

    document.querySelector('.btn-backward').addEventListener("click", () => window.history.back());
    document.querySelector('.btn-submit').addEventListener('click', () =>{
        send_reg_info();
    });


    document.querySelectorAll('.auth-step').forEach(field => {
        field.style.display = 'none';
    })
    document.querySelector('.btn-submit').style.display = 'none';

    //Проверка email
    document.querySelector('.reg-email').addEventListener("change", () => {
        let email = document.querySelector('.reg-email');
        var re = /(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
        if (re.test(email.value)){
            email.classList.remove('is-invalid');
            email.classList.add('is-valid');
        }else{
            email.classList.remove('is-valid');
            email.classList.add('is-invalid');
        }
    })

    //Востановление пароля
    document.querySelector('.pass-recovery').addEventListener('click', () => {
        passRecovery();
    });
    document.querySelector('.btn-recovery-code').addEventListener('click', () => {
        passRecovery();
    });

    replaceState();
});

function replaceState(){
    //Определяем начальное состояние
    reg_choice_form = document.querySelector('.reg-choice-form');
    let state = {
        title: document.querySelector('title').innerHTML,
        form_title: 'auth',
        form_subtitle: 'none',
        sign_form: document.querySelector('.sign-form-container').style.display,
        recovery_form: document.querySelector('.pass-rec-form').style.display,
        recovery_btn: "Отправить",
        reg_choice_form: reg_choice_form.style.display,
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: document.querySelector('.reg-form').style.display,
        first_step: document.querySelector('.parent-step-mandatory').style.display,
        second_step: document.querySelector('.child-step-mandatory').style.display,
        last_step: document.querySelector('.auth-step').style.display
    }
    //Заменяем начальное состояние
    window.history.replaceState(state, null, "");
    renderState(state);
}

function renderState(state){
    //Меняем название страницы
    document.querySelector('title').innerHTML = state.title;
    //Меняем заголовок формы
    let form_title = 'Регистрация';
    if (state.form_title === 'auth') {
        form_title = 'Авторизация';
    }  else if (state.form_title === 'choice') {
        form_title = 'Выберите способ регистрации';
    } else if (state.form_title === 'recovery') {
        form_title = 'Востановление пароля';
    }else if (state.form_title === 'recovery_code') {
        form_title = 'Введите код подтверждения';
    }else if (state.form_title === 'recovery_pass') {
        form_title = 'Создайте новый пароль';
    }
    
    document.querySelector('.form-title').firstElementChild.innerHTML = form_title;
    //Меняем подзаголовок формы
    if (state.form_subtitle != 'none'){
        if(document.querySelector('.pass-rec-form').style.display === 'block'){
            document.querySelector('.rec-instruction').firstElementChild.innerHTML = change_step_title(state.form_subtitle);
        }
        else{
            document.querySelector('.step-title').firstElementChild.innerHTML = change_step_title(state.form_subtitle);
        }
    }
    //Меняем форму
    document.querySelector('.sign-form-container').style.display = state.sign_form;

    document.querySelector('.pass-rec-form').style.display = state.recovery_form;
    document.querySelector('.btn-recovery-code').innerHTML =state.recovery_btn;
    if (state.recovery_btn === 'Ввести') {
        document.querySelector('.email-step').style.display = 'none';
        document.querySelector('.code-step').style.display = 'flex';
    } else if (state.recovery_btn === 'Сменить пароль') {
        document.querySelector('.code-step').style.display = 'none';
        document.querySelectorAll('.password-step').forEach(input =>{
            input.style.display = 'flex';
        });
    };

    document.querySelector('.reg-choice-form').style.display = state.reg_choice_form;
    document.querySelector('.reg-form').style.display = state.reg_form;

    if (state.reg_form != 'none') {
        if (state.first_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-forward').style.display = 'block';
            document.querySelector('.btn-submit').style.display = 'none';
            document.querySelector('.child-step-hidden').style.display = 'none';
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-backward').style.display = 'none';
            cheak_step('.parent-step-mandatory');
        } else if (state.second_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.btn-forward').style.display = 'block';
            document.querySelector('.btn-submit').style.display = 'none';
            if (state.reg_choice === 'parent') {
                document.querySelector('.btn-backward').style.display = 'block';
            }
            cheak_step('.child-step-mandatory');
        } else if (state.last_step != 'none') {
            document.querySelectorAll('.parent-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelectorAll('.child-step').forEach(input =>{
                input.style.display = 'none';
            });
            document.querySelector('.child-step-hidden').style.display = 'none';
            document.querySelectorAll('.auth-step').forEach(input =>{
                input.style.display = 'flex';
            });
            document.querySelector('.btn-forward').style.display = 'none';
            document.querySelector('.btn-submit').style.display = 'block';
            document.querySelector('.btn-backward').style.display = 'block';
        };
    };
}

function choice(){
    //Описывает состояние после нажатия кнопки "Регистрации" (шаг "Выбор способа регистрации")
    let state = {
        title: 'Регистрация | ЦОПП СО',
        form_title: "choice",
        form_subtitle: 'none',
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: "flex",
        reg_choice: document.querySelector('.reg-choice-form').dataset.choice,
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Добавляем и рендерим новое состояние в историю
    window.history.pushState(state, null, "/user/registration/choice");
    renderState(state);

    //Обработка кнопок "Назад/Вперёд"
    window.onpopstate = function (event) {
        if (event.state) { state = event.state; }
        renderState(state);
    };

    //Добавляем прослушивание кнопок выбора типа регистрации
    reg_choice_form = document.querySelector('.reg-choice-form');
    document.querySelectorAll('.option-btn').forEach(btn =>{
        btn.addEventListener('click', () => {
            if (btn.classList.contains('parent-option-btn')){
                reg_choice_form.dataset.choice = 'parent';
            }
            else {
                reg_choice_form.dataset.choice = 'child';
                document.querySelector('.btn-backward').style.display = 'none';
            }
            registration();
        });
    });
}

function registration(){
    let reg_choice_form = document.querySelector('.reg-choice-form');
    let subtitle = 'parent-step';
    let first_step = 'flex';
    let second_step = 'none';
    if (reg_choice_form.dataset.choice === 'child') {
        subtitle = 'child-step';
        second_step = 'flex';
        first_step = 'none';
    }
    
    let state = {
        title: 'Регистрация | ЦОПП СО',
        form_title: 'registration',
        form_subtitle: subtitle,
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: 'block',
        first_step: first_step,
        second_step: second_step,
        last_step: 'none'
    }

    window.history.pushState(state, null, `/user/registration/${reg_choice_form.dataset.choice}/1`);
    renderState(state);

    //Обработка кнопки "Назад"
    window.onpopstate = function (event) {
        if (event.state) { state = event.state; }
        renderState(state);
    };
}
function getCountOfDigits(str) {
    return str.replace(/[^0-9]/g, '').length;
  }

function cheak_step(step_name){
    let is_filled = true;
    document.querySelectorAll(step_name).forEach(input => {
        if (input.firstElementChild.value === "") {
            console.log(input)
            is_filled = false;
        };
    });
    document.querySelectorAll(`${step_name}-select`).forEach(input => {
        if (input.value === "") {
            is_filled = false;
        };
    });
    document.querySelectorAll(`${step_name}-cheakbox`).forEach(input => {
        if (input.checked == false) {
            is_filled = false;
        };
    });
    if (step_name === '.auth-step-mandatory'){
        if (getCountOfDigits(document.querySelector('.auth-step-mandatory-phone').firstElementChild.value) != 11){
            is_filled = false;
        }
        
    }

    if (is_filled) {activate_forward_btn(step_name)}
    else {disable_forward_btn(step_name)};

    disability_cheak = document.querySelector('.disability-check');
    if (!disability_cheak.checked){
        document.querySelector(".child-step-hidden").style.display = "none";
    }
    console.log(`is_filled: ${is_filled}`);
};

function activate_forward_btn(step_name){
    if (step_name === '.auth-step-mandatory'){
        button = document.querySelector('.reg-button-end');
        
        button.classList.remove('disabled');
    } else {
        button = document.querySelector('.btn-forward');
        button.classList.remove('disabled');
        button.classList.remove('btn-secondary');
        button.classList.add('btn-primal');
    }
};

function disable_forward_btn(step_name){
    if (step_name === '.auth-step-mandatory'){
        button = document.querySelector('.reg-button-end');
        button.classList.add('disabled');
    } else {
        button = document.querySelector('.btn-forward');
        button.classList.add('disabled');
        button.classList.add('btn-secondary');
        button.classList.remove('btn-primal');
    }
};

function change_step_title(step){
    option = document.querySelector('.reg-choice-form').dataset.choice;
    disability_label = document.querySelector(".disability-label");

    if (step === "parent-step"){
        return "Шаг 1/3: Данные родителя";
    } else if (step === "child-step") {
        if (option === 'parent'){
            disability_label.innerHTML = "У ребенка ОВЗ";
            return "Шаг 2/3: Данные ученика";
        } 
        disability_label.innerHTML = "Я отношусь к лицам с ОВЗ";
        return "Шаг 1/2: Личные данные";
    } else if (step === "auth-step") {
        if (option === 'parent'){
            return "Шаг 3/3: Данные для авторизации";
        }
        return "Шаг 2/2: Данные для авторизации";
    } else if (step === "email_recovery") {
        return "Введите Ваш email и мы пришлём вам код для востановления пароля.";
    } else if (step === "code_recovery") {
        return "На указанный email отправленно письмо с кодом подтверждения."
    } else if (step === "pass_recovery") {
        return "Создайте новый пароль для вашей учётной записи."
    }
}
     
function click_forward(){
    reg_choice_form = document.querySelector('.reg-choice-form');
    child_step = document.querySelector('.child-step');
    parent_step = document.querySelector('.parent-step');

    let first_step = 'none';
    let second_step  = 'none';
    let last_step  = 'none';
    let subtitle  = 'child-step';
    let path = '2';

    if (child_step.style.display != 'none'){
        second_step = 'none';
        last_step = 'flex';
        if (reg_choice_form.dataset.choice === 'parent') {
            path = '3';
        }
        subtitle = 'auth-step';
    } else if (parent_step.style.display != 'none'){
        first_step = 'none';
        second_step = 'flex';
    };
    
    let state = {
        title: document.querySelector('title').innerHTML,
        form_title: 'registration',
        form_subtitle: subtitle,
        sign_form: 'none',
        recovery_form: 'none',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: reg_choice_form.dataset.choice,
        reg_form: 'block',
        first_step: first_step,
        second_step: second_step,
        last_step: last_step
    }
    //Заменяем начальное состояние
    window.history.pushState(state, null, `/user/registration/${reg_choice_form.dataset.choice}/${path}`);
    renderState(state);
};

function getSelectValues(select) {
    var result = [];
    var options = select && select.options;
    var opt;

    for (var i=0, iLen=options.length; i<iLen; i++) {
        opt = options[i];

        if (opt.selected) {
        result.push(opt.value || opt.text);
        }
    }
    return result;
}

function send_reg_info(){
    let email = document.querySelector('.reg-email')
    if (email.classList.contains('is-valid')){
        disabilities = getSelectValues(document.querySelector("#disability_type"))
        fetch('/user/registration/', {
            method: 'POST',
            body: JSON.stringify({
                email: document.querySelector("#Email").value,
                password: document.querySelector("#InputPasswordReg").value,
                confirmation: document.querySelector("#СonfirmPassword").value,
                
                parent_first_name: document.querySelector("#parentName").value,
                parent_last_name: document.querySelector("#parentLastName").value,
                parent_middle_name: document.querySelector("#parentMiddleName").value,

                first_name: document.querySelector("#Name").value,
                last_name: document.querySelector("#LastName").value,
                middle_name: document.querySelector("#MiddleName").value,
                birthday: document.querySelector("#Birthday").value,
                phone: document.querySelector("#phone").value,
                disability_check: document.querySelector("#disability-check").value,
                disabilities: disabilities,
                
                school_id: document.querySelector("#School").value,
                grade_number: document.querySelector("#school_class").value,
                grade_letter: document.querySelector("#school_class_latter").value,
            })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result.message);
                if (result.message === "Account created successfully."){
                    document.querySelector(".email-login").value = document.querySelector("#Email").value;
                    document.querySelector("#LoginPassword").value = document.querySelector("#InputPasswordReg").value;
                    document.querySelector(".sign-button").click();
                } else if (result.message == 'Password mismatch.') {
                    let message = "Введённые пароли не совпадают."
                    alert_fade(message);
                } else if (result.message == 'Email already taken.') {
                    let message = "Email занят."
                    alert_fade(message);
                }else{
                    let message = "При регистрации произошёл сбой. Попробуйте обновить страницу и пройти регистрацию ещё раз."
                    alert_fade(message);
                }
            })
    }else{
        console.log("Email incorect");
    }
};

function passRecovery() {
    let alert = document.querySelector('.alert-danger');
    let form = document.querySelector('.pass-rec-form');
    let email_input = document.querySelector('.email-step');
    let code_input = document.querySelector('.code-step');
    //Определяем текущий шаг востановления пароля
    if (form.style.display === "none"){
        console.log('step_1')
        //Шаг 1. Запрашиваем email
        emailInput();
    } else if (email_input.style.display != "none") {
        console.log('step_2')
        //Шаг 2. Запрашиваем код из письма
        fetch('/user/password/recovery/1/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
            })
        })
        .then(response => response.json())
        .then(result => {
            if (result.message === 'Email exist') {
                alert.style.display = 'none';
                codeInput();
            }
            else {
                message = "Введённый email не зарегистрирован"
                alert_fade(message)
            }
        })
    } else if (code_input.style.display != "none") {
        fetch('/user/password/recovery/2/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
                code: document.querySelector(".code-recovery").value
            }),
        })
        .then(response => response.json())
        .then(result => {
            console.log(result.message)
            if (result.message == 'Code matches') {
                alert.style.display = 'none';
                passChange();
            }
            else {
                message = "Неверный код подтверждения"
                alert_fade(message)
            }
        })
    } else {
        fetch('/user/password/recovery/3/', {
            method: 'POST',
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Accept": "application/json",
                'Content-Type': 'application/json'
              },
            body: JSON.stringify({
                email: document.querySelector(".email-recovery").value,
                password: document.querySelector(".password-recovery").value,
                confirmation: document.querySelector(".confirmation-recovery").value
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result.message == 'Password changed') {
                alert.style.display = 'none';
                document.querySelector(".email-login").value = document.querySelector(".email-recovery").value;
                document.querySelector("#LoginPassword").value = document.querySelector(".password-recovery").value;
                document.querySelector(".sign-button").click();
            } else {
                message = "При попытке смены пароля, произошёл сбой. Попробуйте повторить операцию позже."
                alert_fade(message)
            }
        })
    }
}

function emailInput() {
    title = 'Востановление пароля';
    form_title = 'recovery';
    form_subtitle = 'email_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Отправить",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/user/registration/recovery/1`);
    renderState(state);
}   

function codeInput() {
    title = 'Востановление пароля';
    form_title = 'recovery_code';
    form_subtitle = 'code_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Ввести",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/user/registration/recovery/2`);
    renderState(state);
}

function passChange() {
    title = 'Востановление пароля';
    form_title = 'recovery_pass';
    form_subtitle = 'pass_recovery';

    let state = {
        title: title,
        form_title: form_title,
        form_subtitle: form_subtitle,
        sign_form: 'none',
        recovery_form: 'block',
        recovery_btn: "Сменить пароль",
        reg_choice_form: 'none',
        reg_choice: 'none',
        reg_form: 'none',
        first_step: 'none',
        second_step: 'none',
        last_step: 'none'
    }
    //Сохраняем новое состояние и рендерим его
    window.history.pushState(state, null, `/user/registration/recovery/3`);
    renderState(state);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }const cssPhone = 'input[name="phone"';
            (new phoneMask()).init(cssPhone);
        }
    }
}

function alert_fade(message) {
    let alert = document.querySelector('.alert-danger')
    alert.innerHTML = message
    alert.style.display = 'block'
}
