agentView.get_mcpsv_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'mcpsv_save');
    const vform_names = ['mcpserver_name', 'mcpserver_url', 'mcpserver_delegated_auth', 'mcpserver_apikey',
                         'mcpserver_transport', 'mcp_tools'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_mcpsv_form = async () => {
    const form = $('#form_mcpsv_edit');
    form.empty();
    const defs = await agentView.get_mcpsv_form_def();
    const model = $('#mcpsv_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_mcpsv = async () => {
    // MCPSV追加ボタンのクリックイベント
    $('#btn_add_mcpsv').off('click').on('click', () => {
        agentView.build_mcpsv_form();
        $('#form_mcpsv_edit [name="mcpserver_name"]').prop('readonly', false);
        $('#btn_del_mcpsv').hide();
        $('#mcpsv_edit_modal').modal('show');
    });

    // MCPSV保存ボタンのクリックイベント
    $('#btn_save_mcpsv').off('click').on('click', () => {
        agentView.save_mcpsv();
    });

    const container = $('#mcpsv_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    
    try {
        const res = await agentView.exec_cmd('agent', 'mcpsv_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load MCPSV list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No MCPSV connections found.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'mcpsv_load', { mcpserver_name: item.name });
            if (!res || !res.success) {
                $(`
                    <li class="sf-list-danger-item">
                        <div>
                            <span class="d-block glow-text-magenta system-font" style="font-size: 0.9em;">${item.name}</span>
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.mcpserver_name}</span>
                        <span>${config.mcpserver_url}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_mcpsv_form();
                const form = $('#form_mcpsv_edit');
                form.find('[name="mcpserver_name"]').val(config.mcpserver_name).prop('readonly', true);
                
                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'mcpserver_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (config[key]) input.val(`${config[key]}`);
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_mcpsv').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.mcpserver_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'mcpsv_del', { mcpserver_name: config.mcpserver_name });
                    $('#mcpsv_edit_modal').modal('hide');
                    agentView.list_mcpsv();
                });

                $('#mcpsv_edit_modal').modal('show');
                // コマンド実行
                const user = await cmdbox.user_info();
                let apikey = $('[name="mcpserver_apikey"]').val();
                if (!apikey && user && user['apikeys']) {
                    const keys = Object.keys(user['apikeys']);
                    if (keys.length > 0) apikey = user['apikeys'][keys[0]][0];
                }
                await cmdbox.callcmd('agent','mcp_client',{
                    'mcpserver_url':$('[name="mcpserver_url"]').val(),
                    'mcpserver_apikey':apikey,
                    'mcpserver_transport':$('[name="mcpserver_transport"]').val(),
                    'operation':'list_tools',
                },(res)=>{
                    $("[name='mcp_tools']").empty().append('<option></option>');
                    res.map(elm=>{$('[name="mcp_tools"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="mcp_tools"]').val(config.mcpserver_mcp_tools);
                },$('[name="title"]').val(),'mcp_tools');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_mcpsv = async () => {
    const form = $('#form_mcpsv_edit');
    const data = {};
    form.find(':input').each((i, elem) => {
        const val = $(elem).val();
        if (val) data[elem.name] = val;
    });

    try {
        const res = await agentView.exec_cmd('agent', 'mcpsv_save', data);
        if (res && res.success) {
            $('#mcpsv_edit_modal').modal('hide');
            agentView.list_mcpsv();
        } else {
            alert('Failed to save MCPSV settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
