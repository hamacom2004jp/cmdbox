const cmdbox = {}
/**
 * ダークモード切替
 * @param {bool} dark_mode 
 */
cmdbox.change_dark_mode = (dark_mode) => {
    const html = $('html');
    if(dark_mode) html.attr('data-bs-theme','dark');
    else if(html.attr('data-bs-theme')=='dark') html.removeAttr('data-bs-theme');
    else html.attr('data-bs-theme','dark');
    $('body').css('background-color', '');
};
cmdbox.change_color_mode = (color_mode) => {
    const html = $('html');
    color_mode = !color_mode ? localStorage.getItem('color_mode') : color_mode;
    if(color_mode == 'light') html.attr('data-bs-theme','light');
    else if(color_mode == 'midnight') html.attr('data-bs-theme','midnight');
    else if(color_mode == 'deepsea') html.attr('data-bs-theme','deepsea');
    else if(color_mode == 'verdant') html.attr('data-bs-theme','verdant');
    else if(color_mode == 'bumblebee') html.attr('data-bs-theme','bumblebee');
    else if(color_mode == 'crimson') html.attr('data-bs-theme','crimson');
    else html.attr('data-bs-theme','dark');
    localStorage.setItem('color_mode', color_mode);
    if (color_mode) {
        const elem = $('.change_color_mode');
        elem.val(color_mode);
        elem.css('background-color', 'var(--bs-body-bg)');
        elem.css('color', 'var(--bs-body-color)');
    }
    $('body').css('background-color', '');
};
/**
 * ローディング表示
 */
cmdbox.show_loading = async (target) => {
    if (!target) {
        const elem = $('#loading');
        elem.removeClass('d-none');
        return;
    }
    $('<div class="spinner-grow spinner-grow-sm" role="status"><span class="visually-hidden">Loading...</span></div>').appendTo(target);
    await cmdbox.sleep(100);
    $('<div class="spinner-grow spinner-grow-sm" role="status"><span class="visually-hidden">Loading...</span></div>').appendTo(target);
    await cmdbox.sleep(100);
    $('<div class="spinner-grow spinner-grow-sm" role="status"><span class="visually-hidden">Loading...</span></div>').appendTo(target);
};
cmdbox.sleep = (time) => new Promise((r) => setTimeout(r, time));
/**
 * ローディング非表示
 */
cmdbox.hide_loading = () => {
    const elem = $('#loading');
    elem.addClass('d-none');
    const progress = $('#progress');
    progress.addClass('d-none');
};
/**
 * テキストデータかどうか判定
 * @param {number[]} array - バイト配列
 * @returns {bool} - テキストデータかどうか
 */
cmdbox.is_text = (array) => {
    const textChars = [7, 8, 9, 10, 12, 13, 27, ...cmdbox.range(0x20, 0xff, 1)];
    return array.every(e => textChars.includes(e));
};
/**
 * Dateオブジェクトを日付文字列に変換
 * @param {Date} date - Dateオブジェクト
 * @returns {string} - 日付文字列
 */
cmdbox.toDateStr = (date) => {
    return date.toLocaleDateString('ja-JP', {
        year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', second:'2-digit'
    });
};
/**
 * 指定された範囲の数値の配列を生成する
 * @param {number} start - 開始値
 * @param {number} stop - 終了値
 * @param {number} step - ステップ数
 * @returns {number[]} - 生成された数値の配列
 */
cmdbox.range = (start, stop, step) => {
    return Array.from({ length: (stop - start) / step + 1 }, (_, i) => start + i * step);
};
/**
 * アラートメッセージ表示
 * @param {object} res - レスポンス
 */
cmdbox.message = (res) => {
    msg = JSON.stringify(res)
    alert(msg.replace(/\\n/g, '\n'));
    cmdbox.hide_loading();
};
/**
 * コンテキストパスを取得
 * @returns {string} - コンテキストパス
 */
cmdbox.ctx_path = () => {
    const cur_path = window.location.pathname;
    if (cur_path.indexOf('dosignin') >= 0) {
        return cur_path.slice(0, cur_path.indexOf('dosignin'));
    }
    else if (cur_path.indexOf('signin') >= 0) {
        return cur_path.slice(0, cur_path.indexOf('signin'));
    }
    return '';
}
/**
 * コピーライト表示
 */
cmdbox.copyright = async () => {
    const res = await fetch('copyright', {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    $('.copyright').text(await res.text());
};
/**
 * appid表示
 * @param {string} sel - セレクタ
 */
cmdbox.appid = async (sel) => {
    const res = await fetch(`${cmdbox.ctx_path()}gui/appid`, {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const appid = await res.text()
    $(sel).text(appid);
    const head = $('head');
    head.append(`<title>${appid}</title>`);
    head.append(`<link rel="icon" type="image/x-icon" href="assets/${appid}/favicon.ico">`);
};
/**
 * 指定のセレクタの前要素にロゴ画像を設定
 * 
 * @param {string} sel - セレクタ
 **/
cmdbox.set_logoicon = async (sel) => {
    const res = await fetch('gui/version_info', {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const verinfos = await res.json();
    for (const v of verinfos) {
        if (!v['thisapp']) continue;
        $(sel).before(`<img class="icon-logo me-3" src="${v['icon']}" width="40" height="40"/>`);
        cmdbox.logoicon_src = v['icon'];
        break;
    }
};
/**
 * サインアウト
 * @param {string} sitepath - サイトパス
 **/
cmdbox.singout = (sitepath) => {
    if (confirm('Sign out ok ?')) {
        const rand = cmdbox.random_string(8);
        location.href = `dosignout/${sitepath}?r=${rand}`;
    }
};
cmdbox.editapikey = async () => {
    const user = await cmdbox.user_info();
    if (!user) {
        cmdbox.message('user not found');
        return;
    }
    const editapikey_modal = $('#editapikey_modal').length?$('#editapikey_modal'):$(`<div id="editapikey_modal" class="modal" tabindex="-1" style="display: none;" aria-hidden="true"/>`);
    editapikey_modal.html('');
    const daialog = $(`<div class="modal-dialog modal-lg ui-draggable ui-draggable-handle"/>`).appendTo(editapikey_modal);
    const form = $(`<form id="editapikey_form" class="modal-content novalidate"/>`).appendTo(daialog);
    const header = $(`<div class="modal-header"/>`).appendTo(form);
    header.append('<h5 class="modal-title">Edit ApiKey</h5>');
    header.append('<button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close" style="margin-left: 0px;">'
                 +'<svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>'
                 +'</button>');
    const body = $(`<div class="modal-body"/>`).appendTo(form);
    const row_content = $(`<div class="row row_content"/>`).appendTo(body);
    const table = $(`<table class="table table-bordered table-hover"/>`).appendTo(row_content);
    const thead = $(`<thead><tr/></thead>`).appendTo(table);
    thead.find('tr').append(`<th class="th" scope="col" width="40">-</th>`);
    thead.find('tr').append(`<th class="th" scope="col">apikey name</th>`);
    thead.find('tr').append(`<th class="th" scope="col" width="112">key</th>`);
    thead.find('tr').append(`<th class="th" scope="col">expiration</th>`);
    thead.find('tr').append(`<th class="th" scope="col">note</th>`);
    const tbody = $(`<tbody/>`).appendTo(table);
    if (user['apikeys']) {
        Object.keys(user['apikeys']).forEach((name, i) => {
            const tr = $(`<tr/>`).appendTo(tbody);
            $(`<td>${i+1}</td>`).appendTo(tr);
            $(`<td>${name}</td>`).appendTo(tr);
            const td_key = $(`<td><span>********</span></td>`).appendTo(tr);
            // コピー用のボタン
            const td_btn_copy = $(`<button type="button" class="btn btn_copy p-0 ms-1">`
                +`<svg class="bi bi-copy" width="16" height="16" fill="currentColor"><use href="#btn_copy"></use></svg>`
                +`</button>`).appendTo(td_key);
            td_btn_copy.off('click').on('click', (event) => {
                const key = user['apikeys'][name][0];
                if (!key) {
                    cmdbox.message({'error': 'No key available for this apikey.'});
                    return;
                }
                navigator.clipboard.writeText(key).then(() => {
                    cmdbox.message({'success': 'Key copied to clipboard.'});
                }).catch((err) => {
                    cmdbox.message({'error': `Failed to copy key: ${err}`});
                });
            });
            // ダウンロードボタン
            const td_btn_download = $(`<a type="button" class="btn btn_download p-0 m-0">`
                +`<svg class="bi bi-download" width="16" height="16" fill="currentColor"><use href="#btn_download"></use></svg>`
                +`</a>`).appendTo(td_key);
            const blob = new Blob([user['apikeys'][name][0]], {"type":"text/plain"});
            const download_url = (window.URL || window.webkitURL).createObjectURL(blob);
            td_btn_download.attr('href', download_url).attr('download', `${name}.txt`);
            // 有効期限とメモ
            const exp = user['apikeys'][name][1];
            if (exp) $(`<td>${exp}</td>`).appendTo(tr);
            else $(`<td>-</td>`).appendTo(tr);
            const note = user['apikeys'][name][2];
            $(`<td>${note}</td>`).appendTo(tr);
        });
    }
    /*const apikey_names = user['apikeys'] ? Object.keys(user['apikeys']) : [];
    apikey_names.forEach((name, i) => {
        const tr = $(`<tr/>`).appendTo(tbody);
        const td_no = $(`<td>${i+1}</td>`).appendTo(tr);
        const td_name = $(`<td>${name}</td>`).appendTo(tr);
        const exp = user['apikeys'][name];
    });*/
    const footer = $(`<div class="modal-footer"/>`).appendTo(form);
    const addapikey_btn = $(`<button type="button" class="btn btn-info">Add apikey</button>`).appendTo(footer);
    addapikey_btn.off('click').on('click', async (event) => {
        const apikey_name = window.prompt('Please enter the apikey name.');
        if (!apikey_name) return;
        const res = await fetch('gui/apikey/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'name': user['name'], 'apikey_name': apikey_name})
        });
        if (res.status != 200) {
            cmdbox.message({'error':`${res.status}: ${res.statusText}`});
            return;
        }
        cmdbox.message(await res.json());
        editapikey_modal.modal('hide');
        cmdbox.editapikey();
    });
    const delapikey_btn = $(`<button type="button" class="btn btn-warning">Del apikey</button>`).appendTo(footer);
    delapikey_btn.off('click').on('click', async (event) => {
        const apikey_name = window.prompt('Please enter the apikey name.');
        if (!apikey_name) return;
        const res = await fetch('gui/apikey/del', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({'name': user['name'], 'apikey_name': apikey_name})
        });
        if (res.status != 200) {
            cmdbox.message({'error':`${res.status}: ${res.statusText}`});
            return;
        }
        cmdbox.message(await res.json());
        editapikey_modal.modal('hide');
        cmdbox.editapikey();
    });
    const close_btn = $('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>').appendTo(footer);
    editapikey_modal.appendTo('body');
    daialog.draggable({cursor:'move',cancel:'.modal-body'});
    editapikey_modal.modal('show');
};
/**
 * 現在のユーザーのパスワード変更
 */
cmdbox.passchange = async () => {
    const user = await cmdbox.user_info();
    if (!user) {
        cmdbox.message('user not found');
        return;
    }
    if (user['hash']=='oauth2') {
        cmdbox.message('This account is an OAuth2 account and cannot be changed.');
        return;
    }
    if (user['hash']=='saml') {
        cmdbox.message('This account is an SAML account and cannot be changed.');
        return;
    }
    const chpass_modal = $('#chpass_modal').length?$('#chpass_modal'):$(`<div id="chpass_modal" class="modal" tabindex="-1" style="display: none;" aria-hidden="true"/>`);
    chpass_modal.html('');
    const daialog = $(`<div class="modal-dialog ui-draggable ui-draggable-handle"/>`).appendTo(chpass_modal);
    const form = $(`<form id="chpass_form" class="modal-content novalidate"/>`).appendTo(daialog);
    const header = $(`<div class="modal-header"/>`).appendTo(form);
    header.append('<h5 class="modal-title">Change Password</h5>');
    header.append('<button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close" style="margin-left: 0px;">'
                 +'<svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>'
                 +'</button>');
    const body = $(`<div class="modal-body"/>`).appendTo(form);
    const row_content = $(`<div class="row row_content"/>`).appendTo(body);
    const crrent_pass = $(`<div class="col-12 mb-3"><div class="input-group">`+
        `<label class="input-group-text">Current Password</label>`+
        `<input type="password" class="form-control" name="password"/>`+
        `<button class="btn btn-secondary eye_buton" type="button"><svg width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><use href="#svg_eyeslash_btn"></use></svg></button>`+
        `</div>`).appendTo(row_content);
    crrent_pass.find('.eye_buton').off('click').on('click', () => {
        const input = crrent_pass.find('input');
        const btn = crrent_pass.find('.eye_buton');
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
            btn.find('use').attr('href', '#svg_eye_btn');
        } else {
            input.attr('type', 'password');
            btn.find('use').attr('href', '#svg_eyeslash_btn');
        }
    });
    const new_pass = $(`<div class="col-12 mb-3"><div class="input-group">`+
        `<label class="input-group-text">New Password</label>`+
        `<input type="password" class="form-control" name="new_password"/>`+
        `<button class="btn btn-secondary gen_buton" type="button"><svg width="16" height="16" fill="currentColor" class="bi bi-magic" viewBox="0 0 16 16"><use href="#svg_magic_btn"></use></svg></button>`+
        `<button class="btn btn-secondary eye_buton" type="button"><svg width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><use href="#svg_eyeslash_btn"></use></svg></button>`+
        `</div>`).appendTo(row_content);
    new_pass.find('.eye_buton').off('click').on('click', () => {
        const input = new_pass.find('input');
        const btn = new_pass.find('.eye_buton');
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
            btn.find('use').attr('href', '#svg_eye_btn');
        } else {
            input.attr('type', 'password');
            btn.find('use').attr('href', '#svg_eyeslash_btn');
        }
    });
    const confirm_pass = $(`<div class="col-12 mb-3"><div class="input-group">`+
        `<label class="input-group-text">Confirm Password</label>`+
        `<input type="password" class="form-control" name="confirm_password"/>`+
        `<button class="btn btn-secondary eye_buton" type="button"><svg width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><use href="#svg_eyeslash_btn"></use></svg></button>`+
        `</div>`).appendTo(row_content);
    confirm_pass.find('.eye_buton').off('click').on('click', () => {
        const input = confirm_pass.find('input');
        const btn = confirm_pass.find('.eye_buton');
        if (input.attr('type') == 'password') {
            input.attr('type', 'text');
            btn.find('use').attr('href', '#svg_eye_btn');
        } else {
            input.attr('type', 'password');
            btn.find('use').attr('href', '#svg_eyeslash_btn');
        }
    });
    new_pass.find('.gen_buton').off('click').on('click', () => {
        const newinput = new_pass.find('input');
        const confinput = confirm_pass.find('input');
        cmdbox.genpass().then((pass) => {
        if (!pass || pass.length == 0) return;
            newinput.val(pass[0]['password']);
            confinput.val(pass[0]['password']);
        });
    });
    const footer = $(`<div class="modal-footer"/>`).appendTo(form);
    footer.append('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>');
    const change = $(`<button type="button" class="btn btn-success">Change</button>`).appendTo(footer);
    change.off('click').on('click', async (event) => {
        cmdbox.show_loading();
        const res = await fetch('password/change', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                'user_name': user['name'],
                'password': crrent_pass.find('input').val(),
                'new_password': new_pass.find('input').val(),
                'confirm_password': confirm_pass.find('input').val()
            })
        });
        cmdbox.hide_loading();
        cmdbox.message(await res.json());
    });
    chpass_modal.appendTo('body');
    daialog.draggable({cursor:'move',cancel:'.modal-body'});
    chpass_modal.modal('show');
};
$(()=>{
    // サインアウトメニューを表示
    fetch('usesignout', {method: 'GET'}).then(async res => {
        try {
            if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
            const json = await res.json();
            const usesignout = json['success']['usesignout'];
            if (!usesignout) return;
            const user = await cmdbox.user_info();
            if (!user) return;
            const user_info_menu = $('.user_info');
            user_info_menu.removeClass('d-none').addClass('d-flex');

            if (!user_info_menu.find('.dropdown-menu .changepass-menu-item').length) {
                const changepass_item = $(`<li><a class="dropdown-item changepass-menu-item" href="#" onclick="cmdbox.passchange();">Change Password</a></li>`);
                user_info_menu.find('.dropdown-menu').append(changepass_item);
            }
            if (!user_info_menu.find('.dropdown-menu .editapikey-menu-item').length) {
                const editapikey_item = $(`<li><a class="dropdown-item editapikey-menu-item" href="#" onclick="cmdbox.editapikey();">Edit ApiKey</a></li>`);
                user_info_menu.find('.dropdown-menu').append(editapikey_item);
            }
            if (!user_info_menu.find('.dropdown-menu .signout-menu-item').length) {
                const parts = location.pathname.split('/');
                const sitepath = parts[parts.length-1];
                const signout_item = $(`<li><a class="dropdown-item signout-menu-item" href="#" onclick="cmdbox.singout('${sitepath}');">Sign out</a></li>`);
                user_info_menu.find('.dropdown-menu').append(`<li><hr class="dropdown-divider"></li>`).append(signout_item);
            }
            user_info_menu.find('.user_info_note').html(`Groups: ${user['groups'].join(', ')}`);
            user_info_menu.find('.username').text(user['name']);
        } catch (e) {}
    });
    cmdbox.appid('.navbar-brand');
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    // サインイン関連エラーがある場合表示
    if (window.location.search) {
        const params = new URLSearchParams(window.location.search);
        if (params.has('error') || params.has('warn')) {
            const elem = $(`<div class="alert alert-warning alert-dismissible d-block position-absolute start-50 translate-middle-x" role="alert">`).css('z-index', '10000');
            const msgelem = $('<div>Sign in faild: The ID or PW is incorrect or the user is not authorized.</div>').appendTo(elem);
            if (params.get('error') == 'noauth') msgelem.text('Sign in faild: No credentials are available. Please sign in.');
            if (params.get('error') == 'expirationofpassword') msgelem.text('Sign in faild: The password has expired.');
            if (params.get('error') == 'appdeny') msgelem.text('OAuth2 succeeded but app not allowed.');
            if (params.get('error') == 'apikeyfail') msgelem.text('Authentication failed due to incorrect apikey.');
            if (params.get('error') == 'unauthorizedsite') msgelem.text('Access to an unauthorized site.');
            if (params.get('error') == 'lockout') msgelem.text('The account is locked.');
            if (params.get('warn') == 'passchange') msgelem.text('Your password has not been changed or is about to expire. Please change your password.');
            $('<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>').appendTo(elem);
            $('body').prepend(elem);
        }
    }
});
/**
 * バージョンモーダルを初期化
 */
cmdbox.init_version_modal = () => {
    $('#versions_modal').on('shown.bs.modal', async () => {
        // cmdboxのバージョン情報取得
        const versions_func = async (tabid, title, icon, url) => {
            const tab = $(`<li class="nav-item" role="presentation">`)
            const btn = $(`<button class="nav-link" id="${tabid}-tab" data-bs-toggle="tab" data-bs-target="#${tabid}" type="button" role="tab" aria-controls="${tabid}" aria-selected="true"/>`);
            if (icon) btn.append(`<span><img class="me-2" src="${icon}" width="32" height="32"/>${title}</span>`);
            else {
                btn.addClass('mt-2');
                btn.html(title);
            }
            tab.append(btn);
            $('.version-tabs').prepend(tab);
            if (!url) return;
            const tabcont = $(`<div class="tab-pane fade show" id="${tabid}" role="tabpanel" aria-labelledby="${tabid}-tab"/>`);
            $('.version-content').prepend(tabcont);
            const res = await fetch(url, {method: 'GET'});
            if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
            const vi = await res.json();
            vi.forEach((v, i) => {
                v = v.replace(/<([^>]+)>/g, '<a href="$1" target="_blank">$1</a>');
                const div = $('<div></div>');
                tabcont.append(div);
                if(i==0) {
                    div.addClass('d-flex');
                    div.addClass('m-3');
                    div.append(`<h4><pre class="m-0">${v}</pre></h4>`);
                } else if(i==1) {
                    div.addClass('m-3');
                    div.append(`<h4>${v}</h4>`);
                } else {
                    div.addClass('ms-5 me-5');
                    div.append(`<h6>${v}</h6>`);
                }
            });
            $('.version-tabs').find('.nav-link').removeClass('active');
            $('.version-content').children().removeClass('active');
            $('.version-tabs').find('.nav-link').first().addClass('active');
            $('.version-content').children().first().addClass('active');
        }
        $('.version-tabs').html('');
        $('.version-content').html('<div class="tab-pane fade" id="versions_used" role="tabpanel" aria-labelledby="versions_used-tab">versions_used</div>');
        await versions_func('versions_used', 'Used software', null, null);
        const res = await fetch('gui/version_info', {method: 'GET'});
        if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
        const verinfos = await res.json();
        for (const v of verinfos) {
            await versions_func(v['tabid'], v['title'], v['icon'], v['url']);
        }
        // usedのバージョン情報取得
        const versions_used_func = async () => {
            const res = await fetch('versions_used', {method: 'GET'});
            if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
            const vu =  await res.json();
            $('#versions_used').html('');
            const div = $('<div class="overflow-auto" style="height:calc(100vh - 260px);"></div>');
            const table = $('<table class="table table-bordered table-hover table-sm"></table>');
            const table_head = $('<thead class="table-dark bg-dark"></thead>');
            const table_body = $('<tbody></tbody>');
            table.append(table_head);
            table.append(table_body);
            div.append(table);
            $('#versions_used').append(div);
            vu.forEach((row, i) => {
                const tr = $('<tr></tr>');
                row.forEach((cel, j) => {
                    const td = $('<td></td>').text(cel);
                    tr.append(td);
                });
                if(i==0) table_head.append(tr);
                else table_body.append(tr);
            });
        };
        versions_used_func();
    });
};
/**
 * モーダルボタン初期化
 */
cmdbox.init_modal_button = () => {
    // modal setting
    $('.modal-dialog').draggable({cursor:'move',cancel:'.modal-body'});
    $('#filer_modal .modal-dialog').draggable({cursor:'move',cancel:'.modal-body, .filer_address'});
    $('.btn_window_stack').off('click').on('click', () => {
        $('.btn_window_stack').css('margin-left', '0px').hide();
        $('.btn_window').css('margin-left', 'auto').show();
        $('.btn_window_stack').parents('.modal-dialog').removeClass('modal-fullscreen');
    });
    $('.btn_window').off('click').on('click', () => {
        $('.btn_window_stack').css('margin-left', 'auto').show();
        $('.btn_window').css('margin-left', '0px').hide();
        $('.btn_window_stack').parents('.modal-dialog').css('top', '').css('left', '').addClass('modal-fullscreen');
    });
    $('.btn_window_stack').css('margin-left', '0px').hide();
    $('.btn_window').css('margin-left', 'auto').show();
    $('.bbforce').off('click').on('click', async () => {
        await bbforce_cmd();
        cmdbox.hide_loading();
    });
    // F5 and Ctrl+R 無効化
    $(document).on('keydown', (e) => {
        if ((e.which || e.keyCode) == 116) {
            return false;
        } else if ((e.which || e.keyCode) == 82 && e.ctrlKey) {
            return false;
        }
    });
};
/**
 * ファイルサイズ表記を取得する
 * @param {number} size - ファイルサイズ
 * @returns {string} - ファイルサイズ表記
 */
cmdbox.calc_size = (size) => {
    const kb = 1024
    const mb = Math.pow(kb, 2)
    const gb = Math.pow(kb, 3)
    const tb = Math.pow(kb, 4)
    let target = null
    let unit = 'B'
    if (size >= tb) {
        target = tb
        unit = 'TB'
    } else if (size >= gb) {
        target = gb
        unit = 'GB'
    } else if (size >= mb) {
        target = mb
        unit = 'MB'
    } else if (size >= kb) {
        target = kb
        unit = 'KB'
    }
    const res = target !== null ? Math.floor((size / target) * 100) / 100 : size
    return `${res} ${unit}`
};
/**
 * カラーコードを取得する
 * @param {bool} color - カラーを指定。省略するとランダムなカラーコードを生成
 * @returns {string, array} - カラーコード
 **/
cmdbox.random_color = (color=undefined) => {
    if (!color) {
        color = [(~~(256 * Math.random())), (~~(256 * Math.random())), (~~(256 * Math.random()))];
    } else if (typeof color === 'string') {
        color = color.split(',').map(e => parseInt(e, 16));
    }
    code = color.map(e => ("00"+e.toString(16)).slice(-2)).join('');
    return code;
};
/**
 * カラーコードを取得する
 * @param {number} id - ラベルID
 * @returns {string} - カラーコード
 **/
cmdbox.make_color4id = (id=0) => {
    color = [(~~(256*(id/(256**3)))), (~~(256*(id/(256**2)))), (~~(256*(id/(256**1))))];
    code = color.map(e => ("00"+e.toString(16)).slice(-2)).join('');
    return code;
};
/**
 * ランダムな文字列を生成する
 * @param {number} length - 文字列の長さ
 * @returns {string} - ランダムな文字列
 **/
cmdbox.random_string = (length) => {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    return Array.from({length: length}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
};
/**
 * ファイル名から拡張子を取り除いた文字列を取得する
 * @param {string} filename - ファイル名
 * @returns {string} - 拡張子を取り除いた文字列
 **/
cmdbox.chopext = (filename) => {
    return filename.replace(/\.[^/.]+$/, "");
};
/**
 * Imageオブジェクトを使用して画像を読み込むPromiseを生成する
 * @param {string} url - 画像のURL
 * @returns {Promise} - 画像の読み込みPromise
 **/
cmdbox.load_img_sync = (url) => {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(`Failed to load image's URL: ${url}`));
        img.src = url;
    });
};
/**
 * サーバーAPI実行
 * @param {object} opt - オプション
 * @returns {Promise} - レスポンス
 */
cmdbox.sv_exec_cmd = async (opt) => {
    return fetch('exec_cmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(opt)
    }).then(response => response.json()).catch((e) => {
        console.log(e);
    });
};
/**
 * 接続情報取得
 * @param {bool} do_sv_exec_cmd - cmdbox.sv_exec_cmdを使用してserverモードのlistコマンドを実行する場合はtrue
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @returns {object | Promise} - 接続情報又はPromise
 */
cmdbox.get_server_opt = (do_sv_exec_cmd, parent_elem) => {
    if (do_sv_exec_cmd) {
        const prom = fetch('get_server_opt', {method: 'GET'}).then(res => res.json()).then(opt => {
            cmdbox.initargs = opt;
            parent_elem.find('.filer_host').val(opt['host']);
            parent_elem.find('.filer_port').val(opt['port']);
            parent_elem.find('.filer_password').val(opt['password']);
            parent_elem.find('.filer_svname').val(opt['svname']);
            parent_elem.find('.filer_client_data').val("client");
            parent_elem.find('.filer_client_data').val(opt['data']);
        });
        return prom;
    }
    try {
        const filer_host = parent_elem.find('.filer_host').val();
        const filer_port = parent_elem.find('.filer_port').val();
        const filer_password = parent_elem.find('.filer_password').val();
        const filer_svname = parent_elem.find('.filer_svname').val();
        const filer_scope = parent_elem.find('.filer_scope').val();
        const filer_client_data = parent_elem.find('.filer_client_data').val();
        return {"host":filer_host, "port":filer_port, "password":filer_password, "svname":filer_svname, "scope": filer_scope, "client_data": filer_client_data};
    } catch (e) {
        console.log(e);
        return {};
    }
};
/**
 * サーバーリスト取得
 * @param {$} parent_elem - 接続先情報のhidden要素を含む祖先要素
 * @param {function} call_back_func - サーバーリストを選択した時のコールバック関数
 * @param {bool} server_only - サーバーのみ表示
 * @param {bool} current_only - カレントのみ表示
 */
cmdbox.load_server_list = (parent_elem, call_back_func, server_only, current_only) => {
    cmdbox.show_loading();
    parent_elem.find('.filer_svnames').remove();
    const mk_func = (elem) => {return ()=>{
        parent_elem.find('.filer_server_bot').text(elem.attr('data-svname'));
        parent_elem.find('.filer_host').val(elem.attr('data-host'));
        parent_elem.find('.filer_port').val(elem.attr('data-port'));
        parent_elem.find('.filer_password').val(elem.attr('data-password'));
        parent_elem.find('.filer_svname').val(elem.attr('data-svname'));
        parent_elem.find('.filer_scope').val(elem.attr('data-scope'));
        parent_elem.find('.filer_client_data').val(elem.attr('data-client_data'));
        if (call_back_func) call_back_func(cmdbox.get_server_opt(false, parent_elem));
        //fsapi.tree(fsapi.right, "/", fsapi.right.find('.tree-menu'), false);
    }};
    if (!cmdbox.initargs['client_only'] && !current_only) {
        const opt = cmdbox.get_server_opt(false, parent_elem);
        opt['mode'] = 'server';
        opt['cmd'] = 'list';
        opt["capture_stdout"] = true;
        delete opt['svname'];
        cmdbox.sv_exec_cmd(opt).then(res => {
            if(res && res['success']) res = [res];
            if(!res[0] || !res[0]['success']) {
                cmdbox.message(res);
                return;
            }
            if(res.length<=0 || !res[0]['success']) {
                cmdbox.hide_loading();
                return;
            }
            const svnames = {};
            res[0]['success'].forEach(elem => {
                const svname = elem['svname'].split('-')[0];
                if (svnames[svname]) return;
                svnames[svname] = true;
                const a_elem = $(`<a class="dropdown-item" href="#" data-client_data="">${svname} ( ${opt['host']}:${opt['port']} )</a>`);
                a_elem.attr('data-host', opt['host']);
                a_elem.attr('data-port', opt['port']);
                a_elem.attr('data-password', opt['password']);
                a_elem.attr('data-svname', svname);
                a_elem.attr('data-scope', "server");
                a_elem.off("click").on("click", mk_func(a_elem));
                const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
                parent_elem.find('.filer_server').append(li_elem);
            });
            parent_elem.find('.filer_server').find('.dropdown-item:first').click();
        }).catch((e) => {
            console.log(e);
        }).finally(() => {
            cmdbox.hide_loading();
        });
    }
    const cl = (label, local_dir) => {
        const a_elem = $(`<a class="dropdown-item" href="#">${label}</a>`);
        a_elem.attr('data-host', cmdbox.initargs['host']);
        a_elem.attr('data-port', cmdbox.initargs['port']);
        a_elem.attr('data-password', cmdbox.initargs['password']);
        a_elem.attr('data-svname', label);
        a_elem.attr('data-scope', label);
        a_elem.attr('data-client_data', local_dir);
        a_elem.off("click").on("click", (event) => {
            parent_elem.find('.filer_address').val(current_only ? '.' : '/');
            mk_func($(event.target))();
        });
        const li_elem = $('<li class="filer_svnames"></li>').append(a_elem);
        parent_elem.find('.filer_server').append(li_elem);
    }
    if (current_only) cl('current', '.');
    else if (!server_only) {
        cl('client', cmdbox.initargs['data']);
        cl('current', '.');
    }
    parent_elem.find('.filer_server').find('.dropdown-item:first').click();
};
/**
 * deployリスト取得
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {function} error_func - エラー時のコールバック関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.deploy_list = (target, error_func=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'deploy_list';
    opt['capture_stdout'] = true;
    cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(res => {
        if(!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        if (!res[0]['success']['data']) {
            cmdbox.hide_loading();
            return
        }
        return res[0]['success'];
    });
};
/**
 * 現在のユーザー情報取得
 * @returns {Promise} - レスポンス
 */
cmdbox.user_info = async () => {
    const res = await fetch('gui/user_info', {method: 'GET'});
    if (!res.ok) return null;
    const user = await res.json()
    return user;
};
/**
 * 新しいパスワード取得
 * @param {number} pass_length - パスワードの長さ
 * @param {number} pass_count - パスワードの数
 * @param {string} use_alphabet - アルファベットを使用するかどうか
 * @param {string} use_number - 数字を使用するかどうか
 * @param {string} use_symbol - 記号を使用するかどうか
 * @param {string} similar - 似た文字を除外するかどうか
 * @param {function} error_func - エラー時のコールバック関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.genpass = (pass_length=16, pass_count=1, use_alphabet="both", use_number="use", use_symbol="use", similar="exclude", error_func=undefined) => {
    const opt = {};
    opt['mode'] = 'web';
    opt['cmd'] = 'genpass';
    opt['pass_length'] = pass_length;
    opt['pass_count'] = pass_count;
    opt['use_alphabet'] = use_alphabet;
    opt['use_number'] = use_number;
    opt['use_symbol'] = use_symbol;
    opt['similar'] = similar;
    opt['capture_stdout'] = true;
    cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(res => {
        if(!res[0] || !res[0]['success']) {
            cmdbox.hide_loading();
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.message(res);
            return res[0];
        }
        const ret = res[0]['success'];
        cmdbox.hide_loading();
        return ret['passwords'];
    });
};
/**
 * ファイルリスト取得
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {bool} recursive - 再帰的に取得するかどうか
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_list = (target, svpath, recursive=false, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_list';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    opt['recursive'] = recursive ? true : false;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * ファイルダウンロード
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_download = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_download';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    opt['capture_maxsize'] = 1024**3*10;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success'] || !res[0]['success']['data']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    }).catch((e) => {
        console.log(e);
    });
};
/**
 * ファイルアップロード
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {FormData} formData - ファイルデータ
 * @param {bool} orverwrite - 上書きするかどうか
 * @param {function} progress_func - 進捗状況を表示する関数。呼出時の引数はe(イベントオブジェクト)のみ
 * @param {function} success_func - 成功時のコールバック関数。呼出時の引数はtarget, svpath, data
 * @param {function} error_func - エラー時のコールバック関数。呼出時の引数はtarget, svpath, data
 * @param {bool} async_fg - 非同期で実行するかどうか
 */
cmdbox.file_upload = (target, svpath, formData, orverwrite=false, progress_func=undefined, success_func=undefined, error_func=undefined, async_fg=true) => {
    const param = {method: 'POST', body: formData};
    const opt = cmdbox.get_server_opt(false, target);
    let param_str = `host=${encodeURI(opt['host'])}`;
    param_str += `&port=${encodeURI(opt['port'])}`;
    param_str += `&password=${encodeURI(opt['password'])}`;
    param_str += `&svname=${encodeURI(opt['svname'])}`;
    param_str += `&orverwrite=${!!orverwrite}`;
    param_str += `&svpath=${encodeURI(svpath)}`;
    param_str += `&scope=${encodeURI(opt['scope'])}`;
    param_str += `&client_data=${encodeURI(opt['client_data'])}`;
    $.ajax({ // fetchだとxhr.upload.onprogressが使えないため、$.ajaxを使用
        url: `filer/upload?${param_str}`,
        type: 'POST',
        processData: false,
        contentType: false,
        async: async_fg,
        data: formData,
        xhr: function() {
            const xhr = $.ajaxSettings.xhr();
            xhr.upload.onprogress = function(e) {
                if (e.lengthComputable && progress_func) {
                    progress_func(e);
                }
            };
            return xhr;
        },
        success: function(data) {
            if (success_func) {
                success_func(target, svpath, data);
            }
        },
        error: function(data) {
            console.log(data);
            cmdbox.message(data);
            if (error_func) {
                error_func(target, svpath, data);
            }
        }
    });
}
/**
 * ファイルコピ－
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} from_path - コピー元パス
 * @param {string} to_path - コピー先パス
 * @param {bool} orverwrite - 上書きするかどうか
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 */
cmdbox.file_copy = (target, from_path, to_path, orverwrite=false, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_copy';
    opt['capture_stdout'] = true;
    opt['from_path'] = from_path;
    opt['to_path'] = to_path;
    opt['orverwrite'] = orverwrite;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * ファイル移動
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} from_path - 移動元パス
 * @param {string} to_path - 移動先パス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 */
cmdbox.file_move = (target, from_path, to_path, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_move';
    opt['capture_stdout'] = true;
    opt['from_path'] = from_path;
    opt['to_path'] = to_path;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * ファイル削除
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_remove = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_remove';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * ディレクトリ削除
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_rmdir = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_rmdir';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * ディレクトリ作成
 * @param {$} target - 接続先情報のhidden要素を含む祖先要素
 * @param {string} svpath - サーバーパス
 * @param {function} error_func - エラー時のコールバック関数
 * @param {function} exec_cmd - サーバーAPI実行関数
 * @returns {Promise} - レスポンス
 **/
cmdbox.file_mkdir = (target, svpath, error_func=undefined, exec_cmd=undefined) => {
    const opt = cmdbox.get_server_opt(false, target);
    opt['mode'] = 'client';
    opt['cmd'] = 'file_mkdir';
    opt['capture_stdout'] = true;
    opt['svpath'] = svpath;
    cmdbox.show_loading();
    const exec = exec_cmd ? exec_cmd : cmdbox.sv_exec_cmd;
    return exec(opt).then(res => {
        if (res && res['success']) res = [res];
        if (!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            cmdbox.hide_loading();
            cmdbox.message(res);
            return;
        }
        return res[0]['success'];
    });
};
/**
 * プログレスバー表示
 * @param {number} _min - 最小値
 * @param {number} _max - 最大値
 * @param {number} _now - 現在値
 * @param {string} _text - テキスト
 * @param {bool} _show - 表示するかどうか
 * @param {bool} _cycle - サイクル表示するかどうか
 */
cmdbox.progress = (_min, _max, _now, _text, _show, _cycle) => {
    const prog_elem = $('.progress');
    const bar_elem = prog_elem.find('.progress-bar');
    const bar_text = bar_elem.find('.progress-bar-text');
    if(_show) prog_elem.removeClass('d-none');
    else prog_elem.addClass('d-none');
    prog_elem.attr('aria-valuemin', _min);
    prog_elem.attr('aria-valuemax', _max);
    prog_elem.attr('aria-valuenow', _now);
    if (!_cycle) {
        const par = Math.floor((_now / (_max-_min)) * 10000) / 100
        bar_elem.css('left', 'auto').css('width', `${par}%`);
        bar_text.text(`${par.toFixed(2)}% ( ${_now} / ${_max} ) ${_text}`);
        if (cmdbox.progress_handle) clearTimeout(cmdbox.progress_handle);
    } else {
        let maxwidth = prog_elem.css('width');
        maxwidth = parseInt(maxwidth.replace('px', ''));
        let left = bar_elem.css('left');
        if (!left || left=='auto') left = 0;
        else left = parseInt(left.replace('px', ''));
        if (left > maxwidth) left = -200;
        left += 2;
        bar_elem.css('width', '200px').css('position', 'relative').css('left', `${left}px`);
        bar_text.text(_text?_text:'Server processing...');
        cmdbox.progress_handle = setTimeout(() => {
            if (!$('#loading').is('.d-none')) cmdbox.progress(_min, _max, _now, _text, _show, _cycle);
        }, 20);
    }
};
/**
 * ユーザーデータを保存
 * @param {string} cat - カテゴリ
 * @param {string} key - キー
 * @param {string} val - 値
 * @returns {Promise}
 */
cmdbox.save_user_data = async (cat, key, val) => {
    const formData = new FormData();
    formData.append('categoly', cat);
    formData.append('key', key);
    formData.append('val', val);
    const res = await fetch('gui/user_data/save', {method:'POST', body:formData});
    if (!res.ok) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const msg = await res.json()
    return msg;
};
/**
 * ユーザーデータを取得
 * @param {string} cat - カテゴリ
 * @param {string} key - キー
 * @returns {Promise}
 */
cmdbox.load_user_data = async (cat, key) => {
    const formData = new FormData();
    formData.append('categoly', cat);
    if (key) formData.append('key', key);
    const res = await fetch('gui/user_data/load', {method:'POST', body:formData});
    if (!res.ok) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const data = await res.json();
    return data;
};
/**
 * ユーザーデータを削除
 * @param {string} cat - カテゴリ
 * @param {string} key - キー
 * @returns {Promise}
 */
cmdbox.delete_user_data = async (cat, key) => {
    const formData = new FormData();
    formData.append('categoly', cat);
    formData.append('key', key);
    const res = await fetch('gui/user_data/delete', {method:'POST', body:formData});
    if (!res.ok) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const data = await res.json();
    return data;
};
/**
 * コマンドピンを保存
 * @param {string} title - タイトル
 * @param {bool} pin - ピン
 */
cmdbox.save_cmd_pin = async (title, pin) => {
    return await cmdbox.save_user_data('cmdpins', title, pin?'on':'off');
};
/**
 * コマンドピンをロード
 * @param {string} title - タイトル
 * @returns {Promise}
 */
cmdbox.load_cmd_pin = async (title) => {
    return await cmdbox.load_user_data('cmdpins', title);
};
/**
 * パイプピンを保存
 * @param {string} title - タイトル
 * @param {bool} pin - ピン
 */
cmdbox.save_pipe_pin = async (title, pin) => {
    return await cmdbox.save_user_data('pipepins', title, pin?'on':'off');
};
/**
 * パイプピンをロード
 * @param {string} title - タイトル
 * @returns {Promise}
 */
cmdbox.load_pipe_pin = async (title) => {
    return await cmdbox.load_user_data('pipepins', title);
}
/**
 * コマンドモーダルのフォームを追加
 * @param {number} i - インデックス
 * @param {$} cmd_modal - コマンドモーダル
 * @param {$} row_content - 行コンテンツ
 * @param {object} row - 行データ(コマンドオプション)
 * @param {$} next_elem - 次の要素
 * @param {number} lcolsize - 横長のカラムサイズ
 * @param {number} scolsize - 通常のカラムサイズ
 * @returns {void}
 */
cmdbox.add_form_func = (i, cmd_modal, row_content, row, next_elem, lcolsize=12, scolsize=6) => {
    const target_name = row.opt;
    // clmsg_idのオプションは隠しオプション扱い。restapiで指定はできる。
    if (target_name=='clmsg_id') return;
    let input_elem, elem;
    if(!row.choice) {
        // 選択肢がない場合
        if(row.type=='text') {
            elem = $(`<div class="col-${lcolsize} mb-3">` // row_content_template_text
                    +'<div class="input-group">'
                    +'<label class="input-group-text row_content_template_title">title</label>'
                    +'<textarea class="form-control row_content_template_input" rows="1" style="field-sizing:content;"></textarea>'
                    +'</div></div>');
        } else if(row.type=='dict') {
            elem = $(`<div class="col-${lcolsize} mb-3">` // row_content_template_dict
                    +'<div class="input-group">'
                    +'<label class="input-group-text row_content_template_title">title</label>'
                    +'<input type="text" class="form-control row_content_key row_content_template_input">'
                    +'<label class="input-group-text">=</label>'
                    +'<input type="text" class="form-control row_content_val row_content_template_input">'
                    +'</div></div>');
        } else if (row.type=='passwd') {
            elem = $(`<div class="col-${scolsize} mb-3">` // row_content_template_str
                    +'<div class="input-group">'
                    +'<label class="input-group-text row_content_template_title">title</label>'
                    +'<input type="password" class="form-control row_content_template_input">'
                    +'<button class="btn btn-outline-secondary" type="button">'
                    +'<svg class="bi bi-eyeslash" width="16" height="16" fill="currentColor"><use href="#svg_eyeslash_btn"></use></svg>'
                    +'<svg class="bi bi-eye d-none" width="16" height="16" fill="currentColor"><use href="#svg_eye_btn"></use></svg>'
                    +'</button>'
                    +'</div></div>');
            elem.find('button').on('click', function() {
                const elem = $(this);
                elem.find('svg').toggleClass('d-none');
                const i = elem.prev('input');
                i.attr('type', i.attr('type')==='password'?'text':'password');
            });
        } else {
            elem = $(`<div class="col-${scolsize} mb-3">` // row_content_template_str
                    +'<div class="input-group">'
                    +'<label class="input-group-text row_content_template_title">title</label>'
                    +'<input type="text" class="form-control row_content_template_input">'
                    +'</div></div>');
        }
        if (next_elem) next_elem.after(elem);
        else row_content.append(elem);
        input_elem = elem.find('.row_content_template_input');
        if(row.type=='date') input_elem.attr('type', 'date');
        else if(row.type=='datetime') input_elem.attr('type', 'datetime-local');
        input_elem.removeClass('row_content_template_input');
        input_elem.val(row.default);
    }
    else {
        // 選択肢がある場合
        let select_html = `<select class="form-select row_content_template_select"${row.type=='mlist'?' multiple':''}></select>`;
        if (row.choice_edit){
            select_html = `<input type="text" class="form-control row_content_key row_content_template_input">`;
            select_html+= `<datalist class="row_content_template_select"></datalist>`;
        }
        if(row.type=='dict') {
            if (Array.isArray(row.choice)) {
                elem = $(`<div class="col-${lcolsize} mb-3">` // row_content_template_dict_choice
                        +'<div class="input-group">'
                        +'<label class="input-group-text row_content_template_title">title</label>'
                        +'<input type="text" class="form-control row_content_key row_content_template_input">'
                        +'<label class="input-group-text">=</label>'
                        + select_html
                        +'</div></div>');
            }
            else {
                elem = $(`<div class="col-${lcolsize} mb-3">` // row_content_template_dict_choice
                        +'<div class="input-group">'
                        +'<label class="input-group-text row_content_template_title">title</label>'
                        +'<select class="form-select row_content_key row_content_template_select"></select>'
                        +'<label class="input-group-text">=</label>'
                        + select_html
                        +'</div></div>');
            }
        } else {
            elem = $(`<div class="col-${scolsize} mb-3">` // row_content_template_choice
                    +'<div class="input-group">'
                    +'<label class="input-group-text row_content_template_title">title</label>'
                    + select_html
                    +'</div></div>');
        }
        if (next_elem) next_elem.after(elem);
        else row_content.append(elem);
        input_elem = elem.find('.row_content_template_select,.row_content_template_input');
        input_elem.removeClass('row_content_template_select').removeClass('row_content_template_input');
        if (row.choice_show) {
            input_elem.addClass('choice_show');
            input_elem.change(() => {
                let names = []
                for (const ns of Object.values(row.choice_show)) {
                    if (Array.isArray(ns)) {
                        ns.forEach(n => names.push(n));
                    } else {
                        names.push(ns);
                    }
                }
                names = [...new Set(names)];
                names.forEach(name => row_content.find(`[name="${name}"]`).parent().parent().hide());
                const v = input_elem.val();
                if (!row.choice_show[v]) return;
                row.choice_show[v].forEach(n => row_content.find(`[name="${n}"]`).parent().parent().show());
            });
        }
        // 配列をoptionタグに変換
        const mkopt = (arr) => {
            if (!arr) return '';
            const opt = arr.map(row => {
                if (row && typeof row === 'object') {
                    key = Object.keys(row)[0];
                    d = window.navigator.language=='ja'?row[key].description_ja:row[key].description_en;
                    return `<option value="${key}" description="${d}">${key}</option>`;
                }
                return `<option value="${row}" description="">${row}</option>`;
            }).join('');
            return opt;
        }
        if (Array.isArray(row.choice)) {
            // 配列の場合
            input_elem.html(mkopt(row.choice));
            input_elem.val(`${row.default!=null?row.default:''}`);
        } else {
            // 辞書の場合
            const cho = [row.choice['key'], row.choice['val']];
            let def = row.default!=null?[row.default, row.default]:null;
            if (row.default && typeof row.default === 'object') {
                def[0] = Object.keys(row.default)[0];
                def[1] = row.default[def[0]];
            }
            input_elem.each((i, e) => {
                $(e).html(mkopt(cho[i]));
                $(e).val(`${def!=null?def[i]:''}`);
            });
        }
    }
    let index = 0;
    if (cmd_modal.find(`[name="${target_name}"]`).length > 0) {
        index = 0;
        cmd_modal.find(`[name="${target_name}"][param_data_index]`).each((i, val) => {
            v = Number($(val).attr('param_data_index'));
            if (index <= v) index = v + 1;
        });
    }
    input_elem.attr('name', target_name);
    if(row.type=='dict') {
        input_elem.each((i, e) => {
            $(e).attr('id', target_name + (index + i));
            $(e).attr('param_data_index', (index + i));
        });
    } else {
        input_elem.attr('id', target_name + index);
        input_elem.attr('param_data_index', index);
    }
    input_elem.attr('required', row.required);
    input_elem.attr('param_data_type', row.type);
    input_elem.attr('param_data_multi', row.multi);
    input_elem.attr('param_data_web', row.web);
    if (row.web=='mask' || row.web=='readonly') {
        input_elem.attr('disabled', 'disabled');
    }
    // 選択肢編集可能な場合はinputのIDを参考にdatalistのIDを設定
    if (row.choice_edit) {
        input_elem.each((i, e) => {
            const elem = $(e), elem_id = elem.attr('id');
            elem.next().attr('id', elem_id + '_options');
            elem.attr('list', elem_id + '_options');
        });
    }
    // ファイルタイプの場合はファイラーモーダルを開くボタンを追加
    if(row.type=='file'){
        const btn = $('<button class="btn btn-secondary" type="button">file</button>');
        input_elem.parent().append(btn);
        const mk_func = (tid, tn) => {
            // tid, tnの値を残すためにクロージャーにする
            return () => {
                const current_path = $(`[id="${tid}"]`).val();
                fmodal.filer_modal_func(tid, tn, current_path, false, true);
            }
        }
        btn.click(mk_func(input_elem.attr('id'), input_elem.attr('name')));
    }
    // ディレクトリタイプの場合はファイラーモーダルを開くボタンを追加
    if(row.type=='dir'){
        const btn = $('<button class="btn btn-secondary" type="button">dir</button>');
        input_elem.parent().append(btn);
        const mk_func = (tid, tn) => {
            // tid, tnの値を残すためにクロージャーにする
            return () => {
                const current_path = $(`[id="${tid}"]`).val();
                fmodal.filer_modal_func(tid, tn, current_path, true, true);
            }
        }
        btn.click(mk_func(input_elem.attr('id'), input_elem.attr('name')));
    }
    // コマンド実行ボタンを追加
    if(row.callcmd){
        const btn_a = $('<button class="btn btn-secondary callcmd_buton" type="button"></button>');
        btn_a.append('<svg class="bi bi-command" width="16" height="16" fill="currentColor"><use href="#btn_command"></use></svg>');
        input_elem.parent().append(btn_a);
        btn_a.click(eval(row.callcmd));
    }
    // マルチの場合は追加ボタンを追加
    if(row.multi){
        const btn_a = $('<button class="btn btn-secondary add_buton" type="button"></button>');
        btn_a.append('<svg class="bi bi-plus" width="16" height="16" fill="currentColor"><use href="#btn_plus"></use></svg>');
        input_elem.parent().append(btn_a);
        let mk_func = (row, next_elem) => {
            // row, next_elemの値を残すためにクロージャーにする
            return () => {
                const r = {...row};
                //r.hide = next_elem.is(':hidden');
                cmdbox.add_form_func(0, cmd_modal, row_content, r, next_elem, lcolsize, scolsize);
            }
        }
        btn_a.click(mk_func(row, input_elem.parent().parent()));
        // 2個目以降は削除ボタンを追加
        const len = cmd_modal.find(`[name="${target_name}"]`).length;
        if (row.type!='dict' && len > 1 || row.type=='dict' && len > 2) {
            mk_func = (del_elem, row) => {
                // del_elemの値を残すためにクロージャーにする
                return () => del_elem.remove();
            }
            const btn_t = $('<button class="btn btn-secondary" type="button"></button>');
            btn_trash
            btn_t.append('<svg class="bi bi-trash" width="16" height="16" fill="currentColor"><use href="#btn_trash"></use></svg>');
            input_elem.parent().append(btn_t);
            btn_t.click(mk_func(input_elem.parent().parent(), row));
        }
    }
    const title = elem.find('.row_content_template_title');
    title.html('');
    title.attr('title', window.navigator.language=='ja'?row.description_ja:row.description_en)
    if (row.required) {
        title.append('<span class="text-danger" title="required">*</span>');
    }
    if (row.choice_show) {
        title.append('<span class="text-primary" title="choice_show">*</span>');
    }
    title.append(`<span>${row.opt}</span>`);
    if (row.hide) {
        if (row_content.find('.row_content_hide').is(':hidden')) elem.hide();
        elem.addClass('row_content_hide');
    } else {
        title.addClass('text-decoration-underline');
    }
    if (row.opt=='help') {
        elem.find(':input').prop('disabled', true);
        elem.find('.row_content_template_title').remove();
    }
}
/**
 * コマンドボタンを実行します
 * @param {object} mode - モード
 * @param {string} cmd - コマンド
 * @param {object} params - パラメータ
 * @param {function} callback - コールバック関数
 * @param {string} title - コマンドタイトル
 * @param {string} opt_name - オプション名
 */
cmdbox.callcmd = async (mode, cmd, params, callback, title, opt_name) => {
    const opt = {
        mode: mode,
        cmd: cmd,
        ...params,
    };
    let res = await fetch('exec_cmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(opt)
    });
    if (res.status != 200) {
        cmdbox.message({'error':`${res.status}: ${res.statusText}`});
        console.log({'error':`${res.status}: ${res.statusText}`});
        return;
    }
    try {
        res = await res.json();
    } catch (e) {
        cmdbox.message({'error':`JSON parse error: ${e}`});
        console.log({'error':`JSON parse error: ${e}`});
        return;
    }
    if (res && res['success']) res = [res];
    if (!res[0] || !res[0]['success']) {
        cmdbox.message(res);
        console.log({'error':res});
        return;
    }
    if (callback) callback(res[0]['success']);
    if (!title || !opt_name) return;
    return cmdbox.load_cmd(title).then(cmd_opt => {
        if (!cmd_opt || cmd_opt['error']) {
            cmdbox.message(cmd_opt);
            console.log({'error':cmd_opt});
            return;
        }
        if (!cmd_opt[opt_name]) return;
        $(`[name="${opt_name}"]`).val(cmd_opt[opt_name]);
    });
};
cmdbox.load_cmd = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('gui/load_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
/**
 * コマンド選択肢取得
 * @param {string} mode - モード
 * @param {string} cmd - コマンド
 * @returns {Promise} - コマンドオプション
 */
cmdbox.get_cmd_choices = async (mode, cmd) => {
    const formData = new FormData();
    formData.append('mode', mode);
    formData.append('cmd', cmd);
    const res = await fetch('gui/get_cmd_choices', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
// コマンドフォームからパラメータを取得
cmdbox.get_param = (modal_elem) => {
    modal_elem.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
    const opt = {};
    const title = modal_elem.find('[name="title"]').val();
    opt["modal_mode"] = modal_elem.find('[name="modal_mode"]').val();
    opt["mode"] = modal_elem.find('[name="mode"]').val();
    opt["cmd"] = modal_elem.find('[name="cmd"]').val();
    if(!opt["mode"]) delete opt["mode"];
    if(!opt["cmd"]) delete opt["cmd"];
    opt["title"] = title;
    const isFloat = (i) => {
        try {
            n = Number(i);
            return n % 1 !== 0;
        } catch(e) {
            return false;
        }
    }
    const isInt = (i) => {
        try {
            n = Number(i);
            return n % 1 === 0;
        } catch(e) {
            return false;
        }
    }
    // フォームの入力値をチェック（不正な値があればフォームに'is-invalid'クラスを付加する）
    const dict_buf = {};
    modal_elem.find('.row_content, .row_content_common').find('input, select, textarea').each((i, elem) => {
        const data_name = $(elem).attr('name');
        let data_val = $(elem).val();
        const data_type = $(elem).attr('param_data_type');
        const data_web = $(elem).attr('param_data_web');
        const data_index = parseInt($(elem).attr('param_data_index'));
        const data_multi = $(elem).attr('param_data_multi');
        if ($(elem).attr('required') && (!data_val || data_val=='')) {
            $(elem).addClass('is-invalid');
        } else if (data_type=='int' && !data_web) {
            if(data_val && data_val!='') {
                if(!isInt(data_val)) $(elem).addClass('is-invalid');
                else {
                    $(elem).removeClass('is-invalid');
                    $(elem).addClass('is-valid');
                    data_val = parseInt(data_val);
                }
            } else {
                $(elem).removeClass('is-invalid');
                $(elem).addClass('is-valid');
            }
        } else if (data_type=='float') {
            if(data_val && data_val!='') {
                if(!isFloat(data_val) && !isInt(data_val)) $(elem).addClass('is-invalid');
                else {
                    $(elem).removeClass('is-invalid');
                    $(elem).addClass('is-valid');
                    data_val = parseFloat(data_val);
                }
            } else {
                $(elem).removeClass('is-invalid');
                $(elem).addClass('is-valid');
            }
        } else if (data_type=='bool') {
            if(data_val!='true' && data_val!='false' && !$(elem).prop('disabled')) $(elem).addClass('is-invalid');
            else {
                data_val = data_val=='true';
                $(elem).removeClass('is-invalid');
                $(elem).addClass('is-valid');
            }
        } else if (data_type=='dict') {
            data_val = data_val ? data_val : '';
            if(data_val.indexOf(' ')>=0) $(elem).addClass('is-invalid');
            else {
                $(elem).removeClass('is-invalid');
                $(elem).addClass('is-valid');
            }
        } else if (data_type=='text') {
            $(elem).removeClass('is-invalid');
            $(elem).addClass('is-valid');
        } else {
            $(elem).removeClass('is-invalid');
            $(elem).addClass('is-valid');
        }
        if(data_multi=='true' || data_type=='dict') {
            if (data_type=='dict') {
                if(!opt[data_name]) {
                    opt[data_name] = {};
                    dict_buf[data_name] = {};
                }
                if(data_index%2==0) dict_buf[data_name]['key'] = data_val;
                else if (dict_buf[data_name]['key']) {
                    opt[data_name][dict_buf[data_name]['key']] = data_val;
                    delete dict_buf[data_name]['key'];
                }
            } else {
                if(!opt[data_name]) opt[data_name] = [];
                if(data_val && data_val!='') opt[data_name].push(data_val);
                else if(data_val==false) opt[data_name].push(data_val);
            }
        } else {
            if(data_val && data_val!='') opt[data_name] = data_val;
            else if(data_val==false) opt[data_name] = data_val;
        }
    });
    return [title, opt];
}
