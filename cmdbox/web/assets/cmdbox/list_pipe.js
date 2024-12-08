// 保存済みパイプラインファイル一覧の取得
list_pipe_func = async () => {
    $('#pipe_items').html('');
    const kwd = $('#pipe_kwd').val();
    const py_list_pipe = await list_pipe(kwd?`*${kwd}*`:'*');
    $('#pipe_items').append($($('#pipe_add').html()));
    py_list_pipe.forEach(row => {
        const elem = $($('#pipe_template').html());
        elem.find('.pipe_title').text(row['title']);
        elem.find('.pipe_desc').text(row['description']);
        $('#pipe_items').append(elem);
    });
}
list_pipe_func_then = () => {
    // パイプラインカードクリック時の処理（モーダルダイアログを開く）
    const pipe_card_func = async (e) => {
        cmdbox.show_loading();
        const pipe_modal = $('#pipe_modal');
        pipe_modal.find('.is-invalid, .is-valid').removeClass('is-invalid').removeClass('is-valid');
        let row_content = pipe_modal.find('.row_content');
        row_content.html('');
        let modal_title = $(e.currentTarget).find('.pipe_title').text();
        cmd_select_template_func = (add_buton, py_list_cmd) => {
            const cmd_select_template = $(pipe_modal.find('.cmd_select_template').html());
            row_content = pipe_modal.find('.row_content_common .row_content');
            if(row_content.find('.cmd_select_item').length > 0) {
                add_buton.parents('.cmd_select_item').after(cmd_select_template);
            } else {
                row_content.append(cmd_select_template);
                cmd_select_template.find('[name="pipe_cmd"]').attr('required', true);
                cmd_select_template.find('.del_buton').hide();
            }
            const pipe_cmd_select = cmd_select_template.find('[name="pipe_cmd"]');
            pipe_cmd_select.append('<option></option>');
            py_list_cmd.forEach(cmd => {
                const option = $('<option></option>');
                pipe_cmd_select.append(option);
                option.attr('value', cmd['title']);
                option.text(`${cmd['title']}(mode=${cmd['mode']}, cmd=${cmd['cmd']})`);
            });
            cmd_select_template.find('.add_buton').click((e) => {
                cmd_select_template_func($(e.currentTarget), py_list_cmd);
            });
            cmd_select_template.find('.del_buton').click((e) => {
                $(e.currentTarget).parents('.cmd_select_item').remove();
            });
            return cmd_select_template;
        }
        if(modal_title != '') {
            // パイプラインファイルの読み込み
            const py_list_cmd = await list_cmd(null);
            const cmd_select = cmd_select_template_func(pipe_modal.find('.row_content_common .row_content .add_buton'), py_list_cmd)
            const py_load_pipe = await load_pipe(modal_title);
            Object.entries(py_load_pipe).forEach(([key, val]) => {
                if (typeof val === 'boolean') {
                    val = val.toString();
                }
                // フォームに値をセット
                if(Array.isArray(val)){
                    val.forEach((v, i) => {
                        const e = pipe_modal.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                        $(e).click();
                    });
                    pipe_modal.find(`[name="${key}"]`).each((i, e) => {
                        if (val[i] && val[i]!="" || i==0) $(e).val(val[i]);
                        else $(e).parent().find('.del_buton').click();
                    });
                } else {
                    pipe_modal.find(`[name="${key}"]`).val(val);
                }
            });
            $('#cmd_del').show();
            pipe_modal.find('[name="title"]').attr('readonly', true);
        } else {
            // 新規パイプラインファイルの作成
            modal_title = 'New Pipeline';
            $('#cmd_del').hide();
            pipe_modal.find('[name="title"]').val('');
            pipe_modal.find('[name="title"]').attr('readonly', false);
            pipe_modal.find('[name="description"]').val('');
            const py_list_cmd = await list_cmd(null);
            cmd_select_template_func(pipe_modal.find('.row_content_common .row_content .add_buton'), py_list_cmd)
        }
        pipe_modal.find('.modal-title').text(`Pipeline : ${modal_title}`);
        pipe_modal.modal('show');
        pipe_modal.find('.btn_window_stack').click();
        cmdbox.hide_loading();
    }
    $('.pipe_card').off('click').on('click', pipe_card_func);
    // パイプラインファイルの保存
    $('#pipe_save').off('click').on('click', async () => {
        const pipe_modal = $('#pipe_modal');
        const [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content, .row_content_common').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        const result = await save_pipe(title, opt);
        await list_pipe_func();
        $('.pipe_card').off('click').on('click', pipe_card_func);
        if (result['success']) alert(result['success']);
        else if (result['warn']) alert(result['warn']);
        cmdbox.hide_loading();
    });
    // パイプラインファイルの削除
    $('#pipe_del').off('click').on('click', async () => {
        const pipe_modal = $('#pipe_modal');
        const title = pipe_modal.find('[name="title"]').val();
        cmdbox.show_loading();
        if (window.confirm(`delete "${title}"?`)) {
            await del_pipe(title);
            pipe_modal.modal('hide');
            await list_pipe_func();
            $('.pipe_card').off('click').on('click', pipe_card_func);
        }
        cmdbox.hide_loading();
    });
    // パイプラインファイルの実行
    $('#pipe_exec').off('click').on('click', async () => {
        const pipe_modal = $('#pipe_modal');
        const [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        // コマンドの実行
        exec_pipe(title, opt).then((result) => {
            pipe_modal.modal('hide');
            //cmdbox.hide_loading();
        });
    });
    // RAW表示の実行
    $('#pipe_raw').off('click').on('click', async () => {
        const pipe_modal = $('#pipe_modal');
        const [title, opt] = get_param(pipe_modal);
        if (pipe_modal.find('.row_content').find('.is-invalid').length > 0) {
            return;
        }
        cmdbox.show_loading();
        // コマンドの実行
        raw_pipe(title, opt).then((result) => {
            view_raw_func(title, result);
            cmdbox.hide_loading();
        });
    });
};

const list_pipe = async (kwd) => {
    const formData = new FormData();
    formData.append('kwd', kwd?`*${kwd}*`:'*');
    const res = await fetch('gui/list_pipe', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const load_pipe = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('gui/load_pipe', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const save_pipe = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('gui/save_pipe', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const del_pipe = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('gui/del_pipe', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const exec_pipe = async (title, opt) => {
    const res = await fetch(`exec_pipe/${title}`,
        {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(opt)});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
const raw_pipe = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('gui/raw_pipe', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}