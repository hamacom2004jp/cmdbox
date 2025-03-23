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
    const storage_name_key = 'cmdbox-signin-name';
    const storage_password_key = 'cmdbox-signin-password';
    const storage_remember_key = 'cmdbox-signin-remember';
    const selecter_name = '.form-signin .form-signin-name';
    const selecter_password = '.form-signin .form-signin-password';
    const selecter_remember = '.form-signin .form-signin-remember';
    const form_signin = $('.form-signin');
    form_signin.attr('action', location.pathname.replace('/signin', '/dosignin'));
    form_signin.off('submit').on('submit', (event) => {
        const remember = $(selecter_remember).prop('checked');
        if (remember) {
            localStorage.setItem(storage_name_key, $(selecter_name).val());
            localStorage.setItem(storage_password_key, $(selecter_password).val());
            localStorage.setItem(storage_remember_key, remember);
        } else {
            localStorage.removeItem(storage_name_key);
            localStorage.removeItem(storage_password_key);
            localStorage.removeItem(storage_remember_key);
        }
    });
    const name = localStorage.getItem(storage_name_key);
    const password = localStorage.getItem(storage_password_key);
    const remember = localStorage.getItem(storage_remember_key);
    if (name) {
        $(selecter_name).val(name);
    }
    if (password) {
        $(selecter_password).val(password);
    }
    if (remember) {
        $(selecter_remember).prop('checked', true);
    }
    const btn_eye = $('.eye_buton');
    btn_eye.off('click').on('click', (event) => {
        const input = $('.form-signin-password');
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
            btn_eye.find('use').attr('href', '#svg_eye_btn');
        } else {
            input.attr('type', 'password');
            btn_eye.find('use').attr('href', '#svg_eyeslash_btn');
        }
    });
    const btn_google = $('.btn-google');
    const btn_github = $('.btn-github');
    const btn_azure = $('.btn-azure');
    btn_google.off('click').on('click', async (event) => {
        const path = window.location.pathname.replace('/signin', '');
        window.location.href = `../oauth2/google${path}?n=${cmdbox.randam_string(8)}`;
    });
    btn_github.off('click').on('click', async (event) => {
        const path = window.location.pathname.replace('/signin', '');
        window.location.href = `../oauth2/github${path}?n=${cmdbox.randam_string(8)}`;
    });
    btn_azure.off('click').on('click', async (event) => {
        const path = window.location.pathname.replace('/signin', '');
        window.location.href = `../oauth2/azure${path}?n=${cmdbox.randam_string(8)}`;
    });
    oauth2_enabled().then((res) => {
        if (res.google) btn_google.show();
        else btn_google.hide();
        if (res.github) btn_github.show();
        else btn_github.hide();
        if (res.azure) btn_azure.show();
        else btn_azure.hide();
    });
});
const get_client_data = async () => {
    const res = await fetch('gui/get_client_data', {method: 'GET'});
    return await res.text();
}
const bbforce_cmd = async () => {
    const res = await fetch('bbforce_cmd', {method: 'GET'});
    return await res.json();
}
const oauth2_enabled = async () => {
    const res = await fetch('../oauth2/enabled', {method: 'GET'});
    return await res.json();
}