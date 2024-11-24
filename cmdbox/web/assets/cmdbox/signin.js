$(() => {
    // ダークモード対応
    cmdbox.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);

    $('.theme-item').off('click').on('click', (event) => {
        $('.theme-item').removeClass('active');
        const elem = $(event.target);
        elem.addClass('active');
        theme = elem.attr('data-bs-theme-value');
        if (theme === 'auto') {
            cmdbox.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
            return;
        }
        $('html').attr('data-bs-theme', theme);
    });
    const storage_userid_key = 'cmdbox-signin-userid';
    const storage_password_key = 'cmdbox-signin-password';
    const storage_remember_key = 'cmdbox-signin-remember';
    const selecter_userid = '.form-signin .form-signin-userid';
    const selecter_password = '.form-signin .form-signin-password';
    const selecter_remember = '.form-signin .form-signin-remember';
    const form_signin = $('.form-signin');
    form_signin.attr('action', location.pathname.replace('/signin', '/dosignin'));
    form_signin.off('submit').on('submit', (event) => {
        const remember = $(selecter_remember).prop('checked');
        if (remember) {
            localStorage.setItem(storage_userid_key, $(selecter_userid).val());
            localStorage.setItem(storage_password_key, $(selecter_password).val());
            localStorage.setItem(storage_remember_key, remember);
        } else {
            localStorage.removeItem(storage_userid_key);
            localStorage.removeItem(storage_password_key);
            localStorage.removeItem(storage_remember_key);
        }
    });
    const userid = localStorage.getItem(storage_userid_key);
    const password = localStorage.getItem(storage_password_key);
    const remember = localStorage.getItem(storage_remember_key);
    if (userid) {
        $(selecter_userid).val(userid);
    }
    if (password) {
        $(selecter_password).val(password);
    }
    if (remember) {
        $(selecter_remember).prop('checked', true);
    }
    if (window.location.search) {
        const params = new URLSearchParams(window.location.search);
        if (params.has('error')) {
            const elem = $(`<div class="alert alert-warning alert-dismissible d-block" role="alert">`);
            elem.append('<div>Sign in faild</div>');
            elem.append('<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>');
            $('body').prepend(elem);
        }
    }
});
const get_client_data = async () => {
    const res = await fetch('gui/get_client_data', {method: 'GET'});
    return await res.text();
}
const bbforce_cmd = async () => {
    const res = await fetch('bbforce_cmd', {method: 'GET'});
    return await res.json();
}
