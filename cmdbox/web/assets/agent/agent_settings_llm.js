agentView.get_llm_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('llm', 'save');
    const vform_names = ['llmname', 'llmprov', 'llmapikey', 'llmendpoint', 'llmmodel', 'llmapiversion',
                        'llmprojectid', 'llmsvaccountfile', 'llmlocation', 'llmtemperature', 'llmseed'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_llm_form = async () => {
    const form = $('#form_llm_edit');
    form.empty();
    const defs = await agentView.get_llm_form_def();
    const model = $('#llm_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_llm = async () => {
    // LLM追加ボタンのクリックイベント
    $('#btn_add_llm').off('click').on('click', async () => {
        await agentView.build_llm_form();
        $('#form_llm_edit [name="llmname"]').prop('readonly', false);
        $('#form_llm_edit [name="llmprov"]').trigger('change');
        $('#btn_del_llm').hide();
        $('#llm_edit_modal').modal('show');
    });

    // LLM保存ボタンのクリックイベント
    $('#btn_save_llm').off('click').on('click', () => {
        agentView.save_llm();
    });

    const container = $('#llm_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('llm', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load LLM list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No LLM configurations found.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('llm', 'load', { llmname: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.llmname}</span>
                        <span>${config.llmprov} / ${config.llmmodel}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_llm_form();
                const form = $('#form_llm_edit');
                form.find('[name="llmname"]').val(config.llmname).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'llmname') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        input.val(config[key]);
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_llm').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.llmname}'?`)) return;
                    await agentView.exec_cmd('llm', 'del', { llmname: config.llmname });
                    $('#llm_edit_modal').modal('hide');
                    agentView.list_llm();
                });

                $('#llm_edit_modal').modal('show');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_llm = async () => {
    const form = $('#form_llm_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('llm', 'save', data);
        if (res && res.success) {
            $('#llm_edit_modal').modal('hide');
            agentView.list_llm();
        } else {
            alert('Failed to save LLM settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
