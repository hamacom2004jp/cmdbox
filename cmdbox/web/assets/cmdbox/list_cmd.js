// 保存済みコマンドファイル一覧の取得
const list_cmd_func = async () => {
    $('#cmd_items').html('');
    const kwd = $('#cmd_kwd').val();
    const py_list_cmd = await list_cmd(kwd?`*${kwd}*`:'*');
    $('#cmd_items').append($($('#cmd_add').html()));
    const data = await cmdbox.load_cmd_pin(null);
    const pins = data && data['success'] ? data['success'] : {};
    const card_func = (row, ispin) => {
        if (ispin && pins[row.title]!='on') return;
        else if (!ispin && pins[row.title]=='on') return;
        const elem = $($('#cmd_template').html());
        if (pins[row.title]=='on') {
            elem.find('.cmd_title').after('<svg class="bi bi-pin-fill d-inline-block ms-auto" width="24" height="24" fill="currentColor"><use href="#btn_pin_fill"></use></svg>');
        }
        elem.find('.cmd_title').text(row.title);
        elem.find('.cmd_mode').text(row.mode);
        elem.find('.cmd_cmd').text(row.cmd);
        const tags_elem = elem.find('.cmd_tags');
        if (row.tag && Array.isArray(row.tag)) {
            row.tag.forEach(tag => {
                if (tag=='') return;
                tags_elem.append(`<span class="badge text-bg-secondary me-1"><svg class="bi bi-svg_tag" width="16" height="16" fill="currentColor"><use href="#svg_tag"></use></svg>${tag}</span>`);
            });
        }
        if (row.tag && Array.isArray(row.tag)) {
            const tags = new Set([...row.tag]);
            elem.find('.cmd_card').attr('data-tags', Array.from(tags).join(','));
        }
        $('#cmd_items').append(elem);
    };
    py_list_cmd.forEach(row => {card_func(row, true)});
    py_list_cmd.forEach(row => {card_func(row, false)});
    const cmd_item_tags = $('#cmd_item_tags').html('');
    const tag_bot_click = (e) => {
        const ct = $(e.currentTarget);
        const cmd_items = $('#cmd_items').find('.cmd_card:not(.cmd_add)');
        const andor_sw = ct.hasClass('andor_switch');
        const and_val = $('#andor_switch').prop('checked');
        // 選択中のボタンの場合は解除中にする
        if (!andor_sw && ct.hasClass('btn-secondary')) {
            ct.removeClass('btn-secondary');
            ct.addClass('btn-outline-secondary');
        }
        // 解除中のボタンの場合は選択中にする
        else if (!andor_sw && ct.hasClass('btn-outline-secondary')) {
            ct.removeClass('btn-outline-secondary');
            ct.addClass('btn-secondary');
        }
        // 選択中のタグを取得
        const tags = new Set();
        cmd_item_tags.find('.btn-tag').each((i, elem) => {
            if ($(elem).hasClass('btn-secondary')) tags.add($(elem).attr('data-tag'));
        });
        // タグ無しボタンが選択された場合
        if (ct.hasClass('btn_notag') && ct.hasClass('btn-secondary')) {
            cmd_item_tags.find('.btn-tag').removeClass('btn-secondary').addClass('btn-outline-secondary');
            cmd_items.parent().hide();
            cmd_items.each((i, elem) => {
                const el = $(elem);
                const itags = el.attr('data-tags');
                if (itags) return;
                el.parent().show();
            });
            return;
        }
        // notagボタンの選択を解除
        if (!andor_sw) $('#btn_notag').removeClass('btn-secondary').addClass('btn-outline-secondary');
        // タグがない場合は全て表示
        if (tags.size == 0) {
            cmd_items.parent().show();
            return;
        }
        // タグがある場合はタグに一致するものだけ表示
        cmd_items.parent().hide();
        cmd_items.each((i, elem) => {
            const el = $(elem);
            // andorチェックされている場合はすべてのタグを含むものを表示
            if (and_val) {
                const itags = el.attr('data-tags');
                if (!itags) return;
                const etags = itags.split(',');
                if (etags.filter(tag => tags.has(tag)).length == tags.size) el.parent().show();
                return;
            }
            // andorチェックされていない場合はいずれかのタグを含むものを表示
            tags.forEach(tag => {
                const itags = el.attr('data-tags');
                if (!itags) return;
                else if (itags.split(',').includes(tag)) el.parent().show();
            });
        });
    };
    // タグボタンを追加
    py_list_cmd.forEach(row => {
        // タグボタンを追加
        if (!row.tag || !Array.isArray(row.tag)) return;
        row.tag.forEach(tag => {
            if (tag=='') return;
            if (cmd_item_tags.find(`[data-tag="${tag}"]`).length > 0) return;
            const elem = $(`<button type="button" class="btn btn-outline-secondary btn-sm btn-tag me-2">` +
                            `<svg class="bi svg-tag" width="16" height="16" fill="currentColor"><use href="#svg_tag"></use></svg>${tag}</button>`);
            elem.attr('data-tag', tag);
            elem.click(tag_bot_click);
            cmd_item_tags.append(elem);
        });
    });
    // タグ未選択ボタンを追加
    const noselect_bot = $(`<button type="button" class="btn btn-outline-secondary btn-sm btn_notag me-2" id="btn_notag">no tag</button>`);
    noselect_bot.click(tag_bot_click);
    cmd_item_tags.append(noselect_bot);
    // and/orスイッチを追加
    const andor_bot = $(`<div class="form-check form-switch text-secondary d-inline-block"/>`);
    andor_bot.append('<input class="form-check-input andor_switch" type="checkbox" id="andor_switch">');
    andor_bot.append('<label class="form-check-label" for="andor_switch">or / and</label>');
    andor_bot.find('#andor_switch').click(tag_bot_click);
    cmd_item_tags.append(andor_bot);
}
// コマンドファイルの取得が出来た時の処理
const list_cmd_func_then = () => {
    // 配列をoptionタグに変換
    const mkopt = (arr) => {
        if (!arr) return '';
        const opt = arr.map(row => {
            if (typeof row === 'object') {
                key = Object.keys(row)[0];
                d = window.navigator.language=='ja'?row[key].discription_ja:row[key].discription_en;
                return `<option value="${key}" discription="${d}">${key}</option>`;
            }
            return `<option value="${row}" discription="">${row}</option>`;
        }).join('');
        return opt;
    }
    // コマンドカードクリック時の処理（モーダルダイアログを開く）
    const cmd_card_func = async (e) => {
        cmdbox.show_loading();
        const py_get_modes = await get_modes();
        const cmd_modal = $('#cmd_modal');
        cmd_modal.find('[name="mode"]').html(mkopt(py_get_modes));
        // モード変更時の処理（モードに対するコマンド一覧を取得）
        const mode_change = async () => {
            const mode = cmd_modal.find('[name="mode"]').val();
            const py_get_cmds = await get_cmds(mode);
            cmd_modal.find('[name="cmd"]').html(mkopt(py_get_cmds));
            const selected_mode = cmd_modal.find('[name="mode"] option:selected');
            cmd_modal.find('.mode_label').attr('title', selected_mode.attr('discription'));
            const row_content = cmd_modal.find('.row_content');
            row_content.html('');
        }
        cmd_modal.find('[name="mode"]').off('change');
        cmd_modal.find('[name="mode"]').change(mode_change);
        cmd_modal.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
        cmd_modal.find('.cmd_label').removeAttr('title');
        const row_content = cmd_modal.find('.row_content');
        row_content.html('');
        // コマンド変更時の処理（コマンドに対するオプション一覧を取得）
        const cmd_change = async () => {
            const mode = cmd_modal.find('[name="mode"]').val();
            const cmd = cmd_modal.find('[name="cmd"]').val();
            const selected_cmd = cmd_modal.find('[name="cmd"] option:selected');
            cmd_modal.find('.cmd_label').attr('title', selected_cmd.attr('discription'));
            const py_get_cmd_choices = await cmdbox.get_cmd_choices(mode, cmd);
            row_content.html('');
            // 表示オプションを追加
            py_get_cmd_choices.filter(row => !row.hide).forEach((row, i) => cmdbox.add_form_func(i, cmd_modal, row_content, row, null));
            // 高度なオプションを表示するリンクを追加
            const show_link = $('<div class="text-center card-hover mb-3"><a href="#">[ advanced options ]</a></div>');
            show_link.click(() => row_content.find('.row_content_hide').toggle());
            row_content.append(show_link);
            // 非表示オプションを追加
            py_get_cmd_choices.filter(row => row.hide).forEach((row, i) => cmdbox.add_form_func(i, cmd_modal, row_content, row, null));
            cmd_modal.find('.choice_show').change();
        }
        //row_content.find('is-invalid, is-valid').removeClass('is-invalid').removeClass('is-valid');
        cmd_modal.find('[name="modal_mode"]').val('');
        cmd_modal.find('[name="cmd"]').off('change');
        cmd_modal.find('[name="cmd"]').change(cmd_change);
        let modal_title = $(e.currentTarget).find('.cmd_title').text();
        if(modal_title != '') {
            cmd_modal.find('[name="modal_mode"]').val('edit');
            // コマンドファイルの読み込み
            const py_load_cmd = await load_cmd(modal_title);
            cmd_modal.find('[name="mode"]').val(py_load_cmd.mode);
            await mode_change();
            cmd_modal.find('[name="cmd"]').val(py_load_cmd.cmd);
            await cmd_change();
            Object.entries(py_load_cmd).forEach(([key, val]) => {
                if (typeof val === 'boolean') {
                    val = val.toString();
                }
                // フォームに値をセット
                if(Array.isArray(val)){
                    val.forEach((v, i) => {
                        e = cmd_modal.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                        $(e).click();
                    });
                    cmd_modal.find(`[name="${key}"]`).each((i, e) => {
                        if (val[i] && val[i]!="" || i==0) $(e).val(val[i]);
                        else $(e).parent().parent().remove();
                    });
                } else if((typeof val)=="object") {
                    let index = 0;
                    const valsize = Object.keys(val).length * 2;
                    Object.entries(val).forEach(([k, v]) => {
                        cmd_modal.find(`#${key}${index}`).val(k);
                        cmd_modal.find(`#${key}${index+1}`).val(v);
                        const btn = cmd_modal.find(`#${key}${index}`).parent().find('.add_buton')[0];
                        index+=2;
                        if (index < valsize) $(btn).click();
                    });
                } else {
                    cmd_modal.find(`[name="${key}"]`).val(val);
                }
            });
            // 選択肢による表示非表示の設定
            cmd_modal.find(`.choice_show`).each((i, elem) => {
                const input_elem = $(elem);
                input_elem.change();
            });
            cmd_modal.find('#cmd_del').show();
            cmd_modal.find('#cmd_copy').show();
            cmd_modal.find('[name="title_disabled"]').val(cmd_modal.find('[name="title"]').hide().val()).show();
            cmd_modal.find('[name="mode_disabled"]').val(cmd_modal.find('[name="mode"]').hide().val()).show();
            cmd_modal.find('[name="cmd_disabled"]').val(cmd_modal.find('[name="cmd"]').hide().val()).show();
            if (cmd_modal.find('[name="name_disabled"]').length == 0) {
                cmd_modal.find('[name="name"]').after('<input name="name_disabled" type="text" class="form-control" disabled="disabled" style="display:none;">');
            }
            cmd_modal.find('[name="name_disabled"]').val(cmd_modal.find('[name="name"]').hide().val()).show();
        } else {
            cmd_modal.find('[name="modal_mode"]').val('add');
            // 新規コマンドファイルの作成
            modal_title = 'New Command';
            await mode_change();
            cmd_modal.find('#cmd_del').hide();
            cmd_modal.find('#cmd_copy').hide();
            cmd_modal.find('[name="title"]').val('');
            cmd_modal.find('[name="title"]').css('border-top-right-radius','6px').css('border-bottom-right-radius','6px').show();
            cmd_modal.find('[name="title_disabled"]').val('').hide();
            cmd_modal.find('[name="mode"]').css('border-top-right-radius','6px').css('border-bottom-right-radius','6px').show();
            cmd_modal.find('[name="mode_disabled"]').val('').hide();
            cmd_modal.find('[name="cmd"]').css('border-top-right-radius','6px').css('border-bottom-right-radius','6px').show();
            cmd_modal.find('[name="cmd_disabled"]').val('').hide();
            cmd_modal.find('[name="name"]').css('border-top-right-radius','6px').css('border-bottom-right-radius','6px').show();
            cmd_modal.find('[name="name_disabled"]').val('').hide();
        }
        cmd_modal.find('.btn_pin_angle').off('click').on('click', () => {
            const title = cmd_modal.find('[name="title"]').val();
            cmd_modal.find('.btn_pin_angle').hide();
            cmd_modal.find('.btn_pin_fill').show();
            cmdbox.save_cmd_pin(title, true).then(() => list_cmd_func().then(list_cmd_func_then));
        });
        cmd_modal.find('.btn_pin_fill').off('click').on('click', () => {
            const title = cmd_modal.find('[name="title"]').val();
            cmd_modal.find('.btn_pin_fill').hide();
            cmd_modal.find('.btn_pin_angle').show();
            cmdbox.save_cmd_pin(title, false).then(() => list_cmd_func().then(list_cmd_func_then));
        });
        const title = cmd_modal.find('[name="title"]').val();
        if (title) {
            cmdbox.load_cmd_pin(title).then((result) => {
                if (!result['success']) {
                    cmd_modal.find('.btn_pin_fill').hide();
                    cmd_modal.find('.btn_pin_angle').hide();
                } else if (result['success']=='on') {
                    cmd_modal.find('.btn_pin_fill').show();
                    cmd_modal.find('.btn_pin_angle').hide();
                } else {
                    cmd_modal.find('.btn_pin_fill').hide();
                    cmd_modal.find('.btn_pin_angle').show();
                }
            });
        } else {
            cmd_modal.find('.btn_pin_fill').hide();
            cmd_modal.find('.btn_pin_angle').hide();
        }
        cmd_modal.find('.modal-title').text(`Command : ${modal_title}`);
        cmd_modal.find('.row_content_hide').hide();
        cmd_modal.find('.btn_window_stack').click();
        cmd_modal.find('.choice_show').change();
        cmd_modal.modal('show');
        cmdbox.hide_loading();
    }
    $('.cmd_card').off('click').on('click', cmd_card_func);
    $('#cmd_copy').off('click').on('click', async () => {
        const cmd_modal = $('#cmd_modal');
        modal_title = 'New Command';
        cmd_modal.find('.modal-title').text(`Command : ${modal_title}`);
        cmd_modal.find('[name="modal_mode"]').val('add');
        cmd_modal.find('#cmd_copy').hide();
        cmd_modal.find('[name="title"]').val(cmd_modal.find('[name="title"]').val() + '_copy');
        cmd_modal.find('[name="title"]').show();
        cmd_modal.find('[name="title_disabled"]').val('').hide();
        cmd_modal.find('[name="mode"]').show();
        cmd_modal.find('[name="mode_disabled"]').val('').hide();
        cmd_modal.find('[name="cmd"]').show();
        cmd_modal.find('[name="cmd_disabled"]').val('').hide();
        cmd_modal.find('[name="name"]').show();
        cmd_modal.find('[name="name_disabled"]').val('').hide();
    });
    // コマンドファイルの保存
    $('#cmd_save').off('click').on('click', async () => {
        const cmd_modal = $('#cmd_modal');
        const [title, opt] = cmdbox.get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        const result = await save_cmd(title, opt);
        await list_cmd_func();
        $('.cmd_card').off('click').on('click', cmd_card_func);
        if (result.success) {
            cmd_modal.find('[name="modal_mode"]').val('edit');
            alert(result.success);
        }
        else if (result.warn) alert(result.warn);
        cmdbox.hide_loading();
    });
    // コマンドファイルの削除
    $('#cmd_del').off('click').on('click', async () => {
        const cmd_modal = $('#cmd_modal');
        const title = cmd_modal.find('[name="title"]').val();
        cmdbox.show_loading();
        if (window.confirm(`delete "${title}"?`)) {
            await del_cmd(title);
            cmd_modal.modal('hide');
            await list_cmd_func();
            $('.cmd_card').off('click').on('click', cmd_card_func);
        }
        cmdbox.hide_loading();
    });
    // コマンドファイルの実行
    $('#cmd_exec').off('click').on('click', async () => {
        const cmd_modal = $('#cmd_modal');
        const [title, opt] = cmdbox.get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        // コマンドの実行
        exec_cmd(title, opt).then((result) => {
            cmd_modal.modal('hide');
            view_result_func(title, result);
            cmdbox.hide_loading();
        });
    });
    // RAW表示の実行
    $('#cmd_raw').off('click').on('click', async () => {
        const cmd_modal = $('#cmd_modal');
        const [title, opt] = cmdbox.get_param(cmd_modal);
        if (cmd_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        // コマンドの実行
        raw_cmd(title, opt).then((result) => {
            view_raw_func(title, result);
            cmdbox.hide_loading();
        });
    });
};

const list_cmd = async (kwd) => {
    const formData = new FormData();
    formData.append('kwd', kwd?`*${kwd}*`:'*');
    const res = await fetch('gui/list_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const get_modes = async (kwd) => {
    const res = await fetch('gui/get_modes', {method: 'GET'});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const get_cmds = async (mode) => {
    const formData = new FormData();
    formData.append('mode', mode);
    const res = await fetch('gui/get_cmds', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const load_cmd = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('gui/load_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const save_cmd = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('gui/save_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const del_cmd = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('gui/del_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const exec_cmd = async (title, opt) => {
    const res = await fetch(`exec_cmd/${title}`,
        {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(opt)});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    const text = await res.text();
    try {
        return JSON.parse(text);
    } catch (e) {
        return text;
    }
}
const raw_cmd = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('gui/raw_cmd', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}