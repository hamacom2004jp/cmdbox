agentView.get_agent_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'agent_save');
    const vform_names = ['agent_name', 'agent_type',
                         'a2asv_baseurl', 'a2asv_delegated_auth', 'a2asv_apikey',
                         'llm', 'mcpservers', 'subagents',
                         'agent_description', 'agent_instruction'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_agent_form = async () => {
    const form = $('#form_agent_edit');
    form.empty();
    const defs = await agentView.get_agent_form_def();
    const model = $('#agent_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_agent = async () => {
    const container = $('#agent_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('agent', 'agent_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Agent list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Agent configurations found.</div>');
            return;
        }

        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'agent_load', { agent_name: item.name });
            if (!res || !res.success) {
                $(`
                    <li class="sf-list-danger-item">
                        <div>
                            <span class="d-block glow-text-magenta system-font" style="font-size: 0.9em;">${item.name}</span>
                            <span class="text-white-50">${JSON.stringify(res)}</span>
                        </div>
                    </li>
                `).appendTo(container_ul);
                return;
            };
            const config = res.success || {};
            const itemEl = $(`
                <li class="sf-list-item" style="cursor: pointer;">
                    <div>
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.agent_name}</span>
                        <span class="text-white-50">${config.agent_description}</span>
                    </div>
                </li>
            `).appendTo(container_ul);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_agent_form();
                const form = $('#form_agent_edit');
                form.find('[name="agent_name"]').val(config.agent_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'agent_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (config[key]) {
                            if (Array.isArray(config[key]) && config[key].length > 1) {
                                config[key].slice(0,-1).forEach((v, i) => {
                                    const e = form.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                                    $(e).click();
                                });
                            } else {
                                input.val(`${config[key]}`);
                            }
                        }
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_agent').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.agent_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'agent_del', { agent_name: config.agent_name });
                    $('#agent_edit_modal').modal('hide');
                    agentView.list_agent();
                });

                $('#agent_edit_modal').modal('show');
                // LLMリストをロード
                await cmdbox.callcmd('llm','list',{},(res)=>{
                    const val = $("[name='llm']").val();
                    $("[name='llm']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="llm"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="llm"]').val(config.llm);
                },$('[name="title"]').val(),'llm');
                // MCPサーバーリストをロード
                await cmdbox.callcmd('agent','mcpsv_list',{},(res)=>{
                    const val = $("[name='mcpservers']").val();
                    $("[name='mcpservers']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="mcpservers"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    config.mcpservers && config.mcpservers.forEach((v, i) => {
                        const e = form.find('[name="mcpservers"]')[i];
                        $(e).val(v);
                    });
                },$('[name="title"]').val(),'mcpservers');
                // SubAgentリストをロード
                await cmdbox.callcmd('agent','agent_list',{},(res)=>{
                    $("[name='subagents']").empty().append('<option></option>');
                    res['data'].map(elm=>{
                        if (elm["name"] === $('[name="agent_name"]').val()) return;
                        $('[name="subagents"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');
                    });
                    config.subagents && config.subagents.forEach((v, i) => {
                        const e = form.find('[name="subagents"]')[i];
                        $(e).val(v);
                    });
                },$('[name="title"]').val(),'subagents');
            });
            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_agent = async () => {
    const form = $('#form_agent_edit');
    const data = {};
    const array = form.serializeArray();
    
    // Helper to handle multiple values for same name (for mcpservers)
    const multiMap = {};
    array.forEach(item => {
        if (multiMap[item.name]) {
            if (!Array.isArray(multiMap[item.name])) {
                multiMap[item.name] = [multiMap[item.name]];
            }
            multiMap[item.name].push(item.value);
        } else {
            multiMap[item.name] = item.value;
        }
    });
    // Ensure mcpservers is array if present
    if (multiMap['mcpservers'] && !Array.isArray(multiMap['mcpservers'])) {
        multiMap['mcpservers'] = [multiMap['mcpservers']];
    }
    
    Object.assign(data, multiMap);

    try {
        const res = await agentView.exec_cmd('agent', 'agent_save', data);
        if (res && res.success) {
            $('#agent_edit_modal').modal('hide');
            agentView.list_agent();
        } else {
            alert('Failed to save Agent settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
