agentView.get_extract_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('extract', 'save');
    const vform_names = ['extract_name', 'extract_type', 'extract_cmd', 'scope', 'loadpath', 'loadregs'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_extract_form = async () => {
    const form = $('#form_extract_edit');
    form.empty();
    const defs = await agentView.get_extract_form_def();
    const model = $('#extract_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_extract = async () => {
    // Extract追加ボタンのクリックイベント
    $('#btn_add_extract').off('click').on('click', async () => {
        await agentView.build_extract_form();
        $('#form_extract_edit [name="extract_name"]').prop('readonly', false);
        $('#form_extract_edit [name="extract_type"]').trigger('change');
        $('#btn_del_extract').hide();
        $('#extract_edit_modal').modal('show');

        // extract_cmdをロード
        await cmdbox.callcmd('cmd','list', {match_opt:['scope','loadpath']},
            (res)=>{
                $("[name='extract_cmd']").empty().append('<option></option>');
                res.forEach(elm=>{$('[name="extract_cmd"]').append('<option value="'+elm["title"]+'">'+elm["title"]+'</option>');});
        },$('[name="title"]').val(),'extract_cmd');
    });

    // Extract保存ボタンのクリックイベント
    $('#btn_save_extract').off('click').on('click', () => {
        agentView.save_extract();
    });

    const container = $('#extract_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('extract', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Extract list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Extract configurations are loaded.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('extract', 'load', {extract_name: item.name});
            if (!res || !res.success) {
                $(`
                    <li class="sf-list-danger-item">
                        <div>
                            <span class="d-block glow-text-magenta system-font" style="font-size: 0.9em;">${item.title}</span>
                            <span class="text-danger">${JSON.stringify(res)}</span>
                        </div>
                    </li>
                `).appendTo(container_ul);
                return;
            }
            const config = res.success || {};

            const itemEl = $(`
                <li class="sf-list-item" style="cursor: pointer;">
                    <div>
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.extract_name}</span>
                        <span>${config.extract_type} / ${config.extract_cmd}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_extract_form();
                const form = $('#form_extract_edit');
                form.find('[name="extract_name"]').val(config.extract_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'extract_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (input.attr('type') === 'checkbox') {
                            input.prop('checked', config[key]);
                        } else {
                            input.val(config[key]);
                        }
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_extract').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.extract_name}'?`)) return;
                    await agentView.exec_cmd('extract', 'del', {extract_name: config.extract_name});
                    $('#extract_edit_modal').modal('hide');
                    agentView.list_extract();
                });

                // extract_cmdをロード
                await cmdbox.callcmd('cmd','list', {match_opt:['scope','loadpath']}, (res)=>{
                    const val = $("[name='extract_cmd']").val();
                    $("[name='extract_cmd']").empty().append('<option></option>');
                    res.forEach(elm=>{$('[name="extract_cmd"]').append('<option value="'+elm["title"]+'">'+elm["title"]+'</option>');});
                    form.find('[name="extract_cmd"]').val(config.extract_cmd);
                },$('[name="title"]').val(),'extract_cmd');
                $('#extract_edit_modal').modal('show');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_extract = async () => {
    const form = $('#form_extract_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('extract', 'save', data, {match_mode: 'extract'});
        if (res && res.success) {
            $('#extract_edit_modal').modal('hide');
            agentView.list_extract();
        } else {
            alert('Failed to save Extract settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
