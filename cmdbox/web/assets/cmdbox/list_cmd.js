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
        $('#cmd_items').append(elem);
    };
    py_list_cmd.forEach(row => {card_func(row, true)});
    py_list_cmd.forEach(row => {card_func(row, false)});
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
            const py_get_cmd_choices = await get_cmd_choices(mode, cmd);
            row_content.html('');
            // オプション一覧をフォームに追加
            const add_form_func = (i, row, next_elem) => {
                const target_name = row.opt;
                let input_elem, elem;
                if(!row.choice) {
                    // 選択肢がない場合
                    if(row.type=='text') {
                        elem = $(cmd_modal.find('.row_content_template_text').html());
                    } else if(row.type=='dict') {
                        elem = $(cmd_modal.find('.row_content_template_dict').html());
                    } else {
                        elem = $(cmd_modal.find('.row_content_template_str').html());
                    }
                    if (next_elem) next_elem.after(elem);
                    else row_content.append(elem);
                    input_elem = elem.find('.row_content_template_input');
                    input_elem.removeClass('row_content_template_input');
                    input_elem.val(row.default);
                }
                else {
                    // 選択肢がある場合
                    if(row.type=='dict') {
                        elem = $(cmd_modal.find('.row_content_template_dict_choice').html());
                    } else {
                        elem = $(cmd_modal.find('.row_content_template_choice').html());
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
                    input_elem.html(mkopt(row.choice));
                    input_elem.val(`${row.default!=null?row.default:''}`);
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
                // マルチの場合は追加ボタンを追加
                if(row.multi){
                    const btn_a = $('<button class="btn btn-secondary add_buton" type="button"></button>');
                    btn_a.append('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus" viewBox="0 0 16 16">'
                                +'<path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>'
                                +'</svg>');
                    input_elem.parent().append(btn_a);
                    let mk_func = (row, next_elem) => {
                        // row, next_elemの値を残すためにクロージャーにする
                        return () => {
                            const r = {...row};
                            //r.hide = next_elem.is(':hidden');
                            add_form_func(0, r, next_elem);
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
                        btn_t.append('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">'
                                +'<path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>'
                                +'<path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>'
                                +'</svg>');
                        input_elem.parent().append(btn_t);
                        btn_t.click(mk_func(input_elem.parent().parent(), row));
                    }
                }
                const title = elem.find('.row_content_template_title');
                title.html('');
                title.attr('title', window.navigator.language=='ja'?row.discription_ja:row.discription_en)
                if (row.required) {
                    title.append('<span class="text-danger" title="required">*</span>');
                }
                if (row.choice_show) {
                    title.append('<span class="text-primary" title="choice_show">*</span>');
                }
                title.append(`<span>${row.opt}</span>`);
                if (row.hide) {
                    elem.addClass('row_content_hide').hide();
                } else {
                    title.addClass('text-decoration-underline');
                }
            }
            // 表示オプションを追加
            py_get_cmd_choices.filter(row => !row.hide).forEach((row, i) => add_form_func(i, row, null));
            // 高度なオプションを表示するリンクを追加
            const show_link = $('<div class="text-center card-hover mb-3"><a href="#">[ advanced options ]</a></div>');
            show_link.click(() => row_content.find('.row_content_hide').toggle());
            row_content.append(show_link);
            // 非表示オプションを追加
            py_get_cmd_choices.filter(row => row.hide).forEach((row, i) => add_form_func(i, row, null));
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
        const [title, opt] = get_param(cmd_modal);
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
        const [title, opt] = get_param(cmd_modal);
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
        const [title, opt] = get_param(cmd_modal);
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

// コマンドフォームからパラメータを取得
const get_param = (modal_elem) => {
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
            if(data_val!='true' && data_val!='false') $(elem).addClass('is-invalid');
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
const get_cmd_choices = async (mode, cmd) => {
    const formData = new FormData();
    formData.append('mode', mode);
    formData.append('cmd', cmd);
    const res = await fetch('gui/get_cmd_choices', {method: 'POST', body: formData});
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