const users = {};
// ユーザー一覧
users.users_list = async () => {
    const groups_res = await fetch('groups/list', {method: 'GET'});
    if (groups_res.status != 200) {
        cmdbox.message({'error':`${groups_res.status}: ${groups_res.statusText}`});
        return;
    }
    const groups_data = await groups_res.json();

    const users_res = await fetch('users/list', {method: 'GET'});
    if (users_res.status != 200) {
        cmdbox.message({'error':`${users_res.status}: ${users_res.statusText}`});
        return;
    }
    const users_data = await users_res.json();
    const users_elem = $('#users_list');
    // ユーザー一覧をクリア
    users_elem.empty();
    // モーダル生成関数
    const users_modal_func = (cols, user) => {
        const modal = $('#users_modal');
        modal.find('.modal-title').text(user && user['name'] ? `Edit User : ${user['name']}` : 'New User');
        const row_content = modal.find('.row_content');
        row_content.empty();
        for (const col of cols) {
            if (col == 'uid' || col == 'name') {
                const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
                row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                const input = row_content.find('.row_content_template_input').removeClass('row_content_template_input');
                input.attr('name', col).val(user ? user[col] : '');
                user && input.attr('disabled', 'disabled').removeAttr('name');
                user && $('<input>').attr('type', 'hidden').attr('name', col).val(user[col]).insertBefore(input);
                continue;
            }
            if (col == 'password') {
                const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
                row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                const input = row_content.find('.row_content_template_input').removeClass('row_content_template_input');
                input.attr('name', col).attr('type', 'password');
                const btn_m = $('<button class="btn btn-secondary gen_buton" type="button"></button>');
                btn_m.append('<svg width="16" height="16" fill="currentColor" class="bi bi-magic" viewBox="0 0 16 16"><use href="#svg_magic_btn"></use></svg>');
                btn_m.appendTo(row.find('.input-group')).click(() => {
                    cmdbox.genpass().then((pass) => {
                        if (pass.length == 0) return;
                        input.val(pass[0]['password']);
                    });
                });
                const btn_e = $('<button class="btn btn-secondary eye_buton" type="button"></button>');
                btn_e.append('<svg width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><use href="#svg_eyeslash_btn"></use></svg>');
                btn_e.appendTo(row.find('.input-group')).click(() => {
                    if (input.attr('type') == 'password') {
                        input.attr('type', 'text');
                        btn_e.find('use').attr('href', '#svg_eye_btn');
                    } else {
                        input.attr('type', 'password');
                        btn_e.find('use').attr('href', '#svg_eyeslash_btn');
                    }
                });
                continue;
            }
            if (col == 'hash') {
                const row = $(modal.find('.row_content_template_choice').html()).appendTo(row_content);
                row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                const select = row_content.find('.row_content_template_select').removeClass('row_content_template_select');
                for (const h of ['', 'oauth2', 'plain', 'md5', 'sha1', 'sha256']) {
                    $('<option>').text(h).val(h).appendTo(select);
                }
                select.attr('name', col).val(user && user[col] ? user[col] : '');
                continue;
            }
            if (col == 'groups') {
                const groups = user && user[col] && user[col].length>0 ? user[col] : [''];
                const groups_add_func = (group, prev) => {
                    const row = $(modal.find('.row_content_template_choice').html()).appendTo(row_content);
                    if (prev) row.insertAfter(prev);
                    const btn_p = $('<button class="btn btn-secondary puls_buton" type="button"></button>');
                    btn_p.append('<svg width="16" height="16" fill="currentColor" class="bi bi-plus" viewBox="0 0 16 16"><use href="#svg_puls_btn"></use></svg>');
                    btn_p.appendTo(row.find('.input-group')).click(() => {groups_add_func('', row);});
                    if (row_content.find('[name="groups"]').length > 0) {
                        const btn_t = $('<button class="btn btn-secondary trash_buton" type="button"></button>');
                        btn_t.append('<svg width="16" height="16" fill="currentColor" class="bi bi-dash" viewBox="0 0 16 16"><use href="#svg_trash_btn"></use></svg>');
                        btn_t.appendTo(row.find('.input-group')).click(() => {row.remove();});
                    }
                    row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                    const select = row_content.find('.row_content_template_select').removeClass('row_content_template_select');
                    $('<option>').text('').val('').appendTo(select);
                    for (const g of groups_data) {
                        $('<option>').text(`${g['gid']} : ${g['name']}`+(g['parent']?` (${g['parent']})`:'')).val(g['name']).appendTo(select);
                    }
                    select.attr('name', 'groups').val(group);
                };
                for (const group of groups) groups_add_func(group);
                continue;
            }
            if (col == 'apikeys') {
                const apikeys = user && user[col] && Object.keys(user[col]).length>0 ? user[col] : {'':''};
                const apikeys_add_func = (apikey,) => {
                    const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
                    row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                    const input = row_content.find('.row_content_template_input').removeClass('row_content_template_input');
                    input.attr('disabled', 'disabled').val(apikey);
                };
                for (const apikey in apikeys) apikeys_add_func(apikey);
                continue;
            }
            const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
            row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
            const input = row_content.find('.row_content_template_input').removeClass('row_content_template_input').attr('name', col).val(user ? user[col] : '');
            col!='email' && input.attr('disabled', 'disabled');
        }
        // apikey追加実行
        modal.find('#cmd_add_apikey').off('click').on('click', async () => {
            const apikey_name = window.prompt('Please enter the apikey name.');
            if (!apikey_name) return;
            const res = await fetch('users/apikey/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'name': row_content.find('[name="name"]').val(), 'apikey_name': apikey_name})
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            cmdbox.message(await res.json());
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        // apikey削除実行
        modal.find('#cmd_del_apikey').off('click').on('click', async () => {
            const apikey_name = window.prompt('Please enter the apikey name.');
            if (!apikey_name) return;
            const res = await fetch('users/apikey/del', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'name': row_content.find('[name="name"]').val(), 'apikey_name': apikey_name})
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            cmdbox.message(await res.json());
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        // 削除実行
        modal.find('#cmd_del').off('click').on('click', async () => {
            if (!window.confirm('Do you want to delete?')) return;
            const res = await fetch('users/del', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'uid': user['uid']})
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        // 保存実行
        modal.find('#cmd_save').off('click').on('click', async () => {
            if (!window.confirm('Do you want to save?')) return;
            const data = {};
            row_content.find('[name]').each((i, p) => {
                const name = $(p).attr('name');
                const val = $(p).val();
                if (name == 'groups') {
                    data[name] = data[name] || [];
                    if (val) data[name].push(val);
                    return;
                }
                if (name == 'apikeys') return;
                data[name] = val;
            });
            const res = await fetch(user ? 'users/edit' : 'users/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            const ret = await res.json();
            cmdbox.message(ret);
            if (!ret['success']) return
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        !user ? modal.find('#cmd_add_apikey').hide() : modal.find('#cmd_add_apikey').show();
        !user ? modal.find('#cmd_del_apikey').hide() : modal.find('#cmd_del_apikey').show();
        !user ? modal.find('#cmd_del').hide() : modal.find('#cmd_del').show();
        modal.modal('show');
    };
    // ユーザー一覧を表示
    const user_table = $('<table/>').addClass('table table-bordered table-hover').appendTo(users_elem);
    // ヘッダ行を作成
    const user_thead = $('<thead/>').appendTo(user_table);
    const cols = new Set();
    if (users_data.length == 0) {
        $('<tr/>').append($('<th class="th"/>').text('No users')).appendTo(user_thead);
        return
    } else {
        const user_thead_tr = $('<tr>').appendTo(user_thead);
        for (const row of users_data) {
            for (const key in row) cols.add(key);
        }
        $('<th class="th"/>').text('-').attr('scope', 'col').attr('width', '40').appendTo(user_thead_tr);
        for (const col of cols) {
            $('<th class="th"/>').text(col).attr('scope', 'col').appendTo(user_thead_tr);
        }
    }
    // 明細行を作成
    const user_tbody = $('<tbody>').appendTo(user_table);
    for (const user_data of users_data) {
        const user_tbody_tr = $('<tr>').appendTo(user_tbody);
        // 編集ボタン
        const user_tbody_tr_actiontd = $('<td>').appendTo(user_tbody_tr);
        const edit_btn = $('<button>').attr('type', 'button').addClass('btn p-0').appendTo(user_tbody_tr_actiontd).on('click', () => {
            return users_modal_func(cols, user_data);
        });
        edit_btn.append('<svg width="24" height="24" fill="currentColor" class="bi bi-plus-lg"><use href="#svg_edit_btn"></use></svg>');
        // 明細項目
        for (const col of cols) {
            const data = user_data[col];
            if (data && Array.isArray(data)) {
                const div = $('<div>').addClass('p-0 m-0');
                data.forEach((item, index) => {
                    $('<div>').addClass('p-0 m-0').text(item).appendTo(div);
                });
                $('<td>').append(div).appendTo(user_tbody_tr);
            } else if (data && typeof data === 'object') {
                const table = $('<table>').addClass('table-sm m-0');
                for (const key in data) {
                    const tr = $('<tr>').appendTo(table);
                    $('<td>').text(key).appendTo(tr);
                    $('<td>').text(data[key]).appendTo(tr);
                }
                $('<td>').append(table).appendTo(user_tbody_tr);
            } else {
                $('<td>').text(data).appendTo(user_tbody_tr);
            }
        }
    }
    // ユーザー追加ボタン
    const add_btn = $('<button>').attr('type', 'button').addClass('btn p-0').css('width', '40px').on('click', () => {
        return users_modal_func(cols, null);
    });
    add_btn.append('<svg width="32" height="32" fill="currentColor" class="bi bi-plus-lg"><use href="#svg_add_btn"></use></svg>');
    users_elem.prepend(add_btn);
};
// グループ一覧
users.groups_list = async () => {
    const groups_res = await fetch('groups/list', {method: 'GET'});
    if (groups_res.status != 200) {
        cmdbox.message({'error':`${groups_res.status}: ${groups_res.statusText}`});
        return;
    }
    const groups_data = await groups_res.json();
    const groups_elem = $('#groups_list');
    // グループ一覧をクリア
    groups_elem.empty();

    // モーダル生成関数
    const groups_modal_func = (cols, group) => {
        const modal = $('#users_modal');
        modal.find('.modal-title').text(group && group['name'] ? `Edit Group : ${group['name']}` : 'New Group');
        const row_content = modal.find('.row_content');
        row_content.empty();
        for (const col of cols) {
            if (col == 'gid' || col == 'name') {
                const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
                row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                const input = row_content.find('.row_content_template_input').removeClass('row_content_template_input');
                input.attr('name', col).val(group ? group[col] : '');
                group && input.attr('disabled', 'disabled').removeAttr('name');
                group && $('<input>').attr('type', 'hidden').attr('name', col).val(group[col]).insertBefore(input);
                continue;
            }
            if (col == 'parent') {
                const row = $(modal.find('.row_content_template_choice').html()).appendTo(row_content);
                row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
                const select = row_content.find('.row_content_template_select').removeClass('row_content_template_select');
                $('<option>').text('').val('').appendTo(select);
                for (const g of groups_data) {
                    $('<option>').text(`${g['gid']} : ${g['name']}`+(g['parent']?` (${g['parent']})`:'')).val(g['name']).appendTo(select);
                }
                select.attr('name', 'parent').val(group ? group[col] : '');
                continue;
            }
            const row = $(modal.find('.row_content_template_str').html()).appendTo(row_content);
            row_content.find('.row_content_template_title').removeClass('row_content_template_title').text(col);
            row_content.find('.row_content_template_input').removeClass('row_content_template_input').attr('name', col).val(group ? group[col] : '');
        }
        // 削除実行
        modal.find('#cmd_del').off('click').on('click', async () => {
            if (!window.confirm('Do you want to delete?')) return;
            const res = await fetch('groups/del', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'gid': group['gid']})
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            cmdbox.message(await res.json());
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        // 保存実行
        modal.find('#cmd_save').off('click').on('click', async () => {
            if (!window.confirm('Do you want to save?')) return;
            const data = {};
            row_content.find('[name]').each((i, p) => {
                const name = $(p).attr('name');
                const val = $(p).val();
                data[name] = val;
            });
            const res = await fetch(group ? 'groups/edit' : 'groups/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            if (res.status != 200) {
                cmdbox.message({'error':`${res.status}: ${res.statusText}`});
                return;
            }
            cmdbox.message(await res.json());
            users.users_list();
            users.groups_list();
            modal.modal('hide');
        });
        modal.find('#cmd_add_apikey').hide();
        modal.find('#cmd_del_apikey').hide();
        !group ? modal.find('#cmd_del').hide() : modal.find('#cmd_del').show();
        modal.modal('show');
    };
    // グループ一覧を表示
    const group_table = $('<table/>').addClass('table table-bordered table-hover').appendTo(groups_elem);
    // ヘッダ行を作成
    const group_thead = $('<thead/>').appendTo(group_table);
    const cols = new Set();
    if (groups_data.length == 0) {
        $('<tr>').append($('<th class="th"/>').text('No groups')).appendTo(group_thead);
        return
    } else {
        const group_thead_tr = $('<tr>').appendTo(group_thead);
        for (const row of groups_data) {
            for (const key in row) cols.add(key);
        }
        $('<th class="th"/>').text('-').attr('scope', 'col').attr('width', '40').appendTo(group_thead_tr);
        for (const col of cols) {
            $('<th class="th"/>').text(col).attr('scope', 'col').appendTo(group_thead_tr);
        }
    }
    // 明細行を作成
    const group_tbody = $('<tbody>').appendTo(group_table);
    for (const group_data of groups_data) {
        const group_tbody_tr = $('<tr>').appendTo(group_tbody);
        // 編集ボタン
        const group_tbody_tr_actiontd = $('<td>').appendTo(group_tbody_tr);
        const edit_btn = $('<button>').attr('type', 'button').addClass('btn p-0').appendTo(group_tbody_tr_actiontd).on('click', () => {
            return groups_modal_func(cols, group_data);
        });
        edit_btn.append('<svg width="24" height="24" fill="currentColor" class="bi bi-plus-lg"><use href="#svg_edit_btn"></use></svg>');
        // 明細項目
        for (const col of cols) {
            const data = group_data[col];
            if (data && Array.isArray(data)) {
                const div = $('<div>').addClass('p-0 m-0');
                data.forEach((item, index) => {
                    $('<div>').addClass('p-0 m-0').text(item).appendTo(div);
                });
                $('<td>').append(div).appendTo(group_tbody_tr);
            } else if (data && typeof data === 'object') {
                const table = $('<table>').addClass('table-sm m-0');
                for (const key in data) {
                    const tr = $('<tr>').appendTo(table);
                    $('<td>').text(key).appendTo(tr);
                    $('<td>').text(data[key]).appendTo(tr);
                }
                $('<td>').append(table).appendTo(group_tbody_tr);
            } else {
                $('<td>').text(data).appendTo(group_tbody_tr);
            }
        }
    }
    // グループ追加ボタン
    const add_btn = $('<button>').attr('type', 'button').addClass('btn p-0').css('width', '40px').on('click', () => {
        return groups_modal_func(cols, null);
    });
    add_btn.append('<svg width="32" height="32" fill="currentColor" class="bi bi-plus-lg"><use href="#svg_add_btn"></use></svg>');
    groups_elem.prepend(add_btn);
};
// コマンドルール一覧
users.cmdrules_list = async () => {
    const cmdrules_res = await fetch('cmdrules/list', {method: 'GET'});
    if (cmdrules_res.status != 200) {
        cmdbox.message({'error':`${cmdrules_res.status}: ${cmdrules_res.statusText}`});
        return;
    }
    const cmdrules_root_data = await cmdrules_res.json();
    const cmdrules_data = cmdrules_root_data['rules'];
    const cmdrules_elem = $('#cmdrules_list');
    // コマンドルール一覧をクリア
    cmdrules_elem.empty();
    // グループ一覧を表示
    $('<div>').text(`policy : ${cmdrules_root_data['policy']}`).appendTo(cmdrules_elem);
    const cmdrule_table = $('<table>').addClass('table table-bordered table-hover').appendTo(cmdrules_elem);
    // ヘッダ行を作成
    const cmdrule_thead = $('<thead>').appendTo(cmdrule_table);
    const cols = new Set();
    if (cmdrules_data.length == 0) {
        $('<tr>').append($('<th class="th"/>').text('No cmdrules')).appendTo(cmdrule_thead);
        return
    } else {
        const cmdrule_thead_tr = $('<tr>').appendTo(cmdrule_thead);
        for (const row of cmdrules_data) {
            for (const key in row) cols.add(key);
        }
        $('<th class="th"/>').text('#').attr('scope', 'col').attr('width', '40').appendTo(cmdrule_thead_tr);
        for (const col of cols) {
            $('<th class="th"/>').text(col).attr('scope', 'col').appendTo(cmdrule_thead_tr);
        }
    }
    // 明細行を作成
    const cmdrule_tbody = $('<tbody>').appendTo(cmdrule_table);
    let i_row=0;
    for (const cmdrule_data of cmdrules_data) {
        i_row++;
        const cmdrule_tbody_tr = $('<tr>').appendTo(cmdrule_tbody);
        // 明細項目
        $('<td>').text(i_row).appendTo(cmdrule_tbody_tr);
        for (const col of cols) {
            const data = cmdrule_data[col];
            if (data && Array.isArray(data)) {
                const div = $('<div>').addClass('p-0 m-0');
                data.forEach((item, index) => {
                    $('<div>').addClass('p-0 m-0').text(item).appendTo(div);
                });
                $('<td>').append(div).appendTo(cmdrule_tbody_tr);
            } else if (data && typeof data === 'object') {
                const table = $('<table>').addClass('table-sm m-0');
                for (const key in data) {
                    const tr = $('<tr>').appendTo(table);
                    $('<td>').text(key).appendTo(tr);
                    $('<td>').text(data[key]).appendTo(tr);
                }
                $('<td>').append(table).appendTo(cmdrule_tbody_tr);
            } else {
                $('<td>').text(data).appendTo(cmdrule_tbody_tr);
            }
        }
    }
};
// パスルール一覧
users.pathrules_list = async () => {
    const pathrules_res = await fetch('pathrules/list', {method: 'GET'});
    if (pathrules_res.status != 200) {
        cmdbox.message({'error':`${pathrules_res.status}: ${pathrules_res.statusText}`});
        return;
    }
    const pathrules_root_data = await pathrules_res.json();
    const pathrules_data = pathrules_root_data['rules'];
    const pathrules_elem = $('#pathrules_list');
    // コマンドルール一覧をクリア
    pathrules_elem.empty();
    // グループ一覧を表示
    $('<div>').text(`policy : ${pathrules_root_data['policy']}`).appendTo(pathrules_elem);
    const pathrule_table = $('<table>').addClass('table table-bordered table-hover').appendTo(pathrules_elem);
    // ヘッダ行を作成
    const pathrule_thead = $('<thead>').appendTo(pathrule_table);
    const cols = new Set();
    if (pathrules_data.length == 0) {
        $('<tr>').append($('<th class="th"/>').text('No cmdrules')).appendTo(pathrule_thead);
        return
    } else {
        const pathrule_thead_tr = $('<tr>').appendTo(pathrule_thead);
        for (const row of pathrules_data) {
            for (const key in row) cols.add(key);
        }
        $('<th class="th"/>').text('#').attr('scope', 'col').attr('width', '40').appendTo(pathrule_thead_tr);
        for (const col of cols) {
            $('<th class="th"/>').text(col).attr('scope', 'col').appendTo(pathrule_thead_tr);
        }
    }
    // 明細行を作成
    const pathrule_tbody = $('<tbody>').appendTo(pathrule_table);
    let i_row=0;
    for (const pathrule_data of pathrules_data) {
        i_row++;
        const pathrule_tbody_tr = $('<tr>').appendTo(pathrule_tbody);
        $('<td>').text(i_row).appendTo(pathrule_tbody_tr);
        // 明細項目
        for (const col of cols) {
            const data = pathrule_data[col];
            if (data && Array.isArray(data)) {
                const div = $('<div>').addClass('p-0 m-0');
                data.forEach((item, index) => {
                    $('<div>').addClass('p-0 m-0').text(item).appendTo(div);
                });
                $('<td>').append(div).appendTo(pathrule_tbody_tr);
            } else if (data && typeof data === 'object') {
                const table = $('<table>').addClass('table-sm m-0');
                for (const key in data) {
                    const tr = $('<tr>').appendTo(table);
                    $('<td>').text(key).appendTo(tr);
                    $('<td>').text(data[key]).appendTo(tr);
                }
                $('<td>').append(table).appendTo(pathrule_tbody_tr);
            } else {
                $('<td>').text(data).appendTo(pathrule_tbody_tr);
            }
        }
    }
};
// パスワード設定一覧
users.passsetting_list = async () => {
    const passsetting_res = await fetch('passsetting/list', {method: 'GET'});
    if (passsetting_res.status != 200) {
        cmdbox.message({'error':`${passsetting_res.status}: ${passsetting_res.statusText}`});
        return;
    }
    const passsetting_root_data = await passsetting_res.json();
    const passsetting_elem = $('#passsetting_list');
    passsetting_elem.html('');
    const mk_card = (setting_elem, title, data) => {
        const card_elem = $('<div class="card m-3"/>').appendTo(setting_elem);
        const cardbody_elem = $('<div class="card-body"/>').appendTo(card_elem);
        cardbody_elem.append(`<h5 class="card-title">${title}</h5>`);
        const table_elem = $('<table class="table table-bordered table-hover"/>').appendTo(cardbody_elem);
        const thead_elem = $('<thead><tr><th class="th">#</th><th class="th">setting</th><th class="th">value</th></tr></thead>').appendTo(table_elem);
        const tbody_elem = $('<tbody/>').appendTo(table_elem);
        let i_row=0;
        for (const key in data) {
            i_row++;
            const tr = $('<tr>').appendTo(tbody_elem);
            $('<td>').text(i_row).appendTo(tr);
            $('<td>').text(key).appendTo(tr);
            $('<td>').text(data[key]).appendTo(tr);
        }
    };
    mk_card(passsetting_elem, 'Password Policy', passsetting_root_data['policy']);
    mk_card(passsetting_elem, 'Password Expiration', passsetting_root_data['expiration']);
    mk_card(passsetting_elem, 'Account Lockout', passsetting_root_data['lockout']);
};
$(() => {
    // カラーモード対応
    cmdbox.change_color_mode();
    // アイコンを表示
    cmdbox.set_logoicon('.navbar-brand');
    // copyright表示
    cmdbox.copyright();
    // バージョン情報モーダル初期化
    cmdbox.init_version_modal();
    // モーダルボタン初期化
    cmdbox.init_modal_button();
    // コマンド実行用のオプション取得
    cmdbox.get_server_opt(true, $('.filer_form')).then((opt) => {
        users.users_list();
        users.groups_list();
        users.cmdrules_list();
        users.pathrules_list();
        users.passsetting_list();
    });
});
