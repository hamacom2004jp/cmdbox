agentView.get_embedding_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('embed', 'save');
    const vform_names = ['embed_name', 'embed_device', 'embed_model'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_embedding_form = async () => {
    const form = $('#form_embedding_edit');
    form.empty();
    const defs = await agentView.get_embedding_form_def();
    const model = $('#embedding_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_embedding = async () => {
    // Embedding追加ボタンのクリックイベント
    $('#btn_add_embedding').off('click').on('click', async () => {
        await agentView.build_embedding_form();
        $('#form_embedding_edit [name="embedding_name"]').prop('readonly', false);
        $('#btn_del_embedding').hide();
        $('#embedding_edit_modal').modal('show');
    });

    // Embedding保存ボタンのクリックイベント
    $('#btn_save_embedding').off('click').on('click', () => {
        agentView.save_embedding();
    });

    const container = $('#embedding_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('embed', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Embedding list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Embedding models are loaded.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('embed', 'load', { embed_name: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.embed_name}</span>
                        <span class="text-white-50">${config.embed_model} / ${config.embed_device}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_embedding_form();
                const form = $('#form_embedding_edit');
                form.find('[name="embed_name"]').val(config.embed_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'embedding_name' || key === 'embed_name') return;
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
                $('#btn_del_embedding').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.embed_name}'?`)) return;
                    await agentView.exec_cmd('embed', 'del', { embed_name: config.embed_name });
                    $('#embedding_edit_modal').modal('hide');
                    agentView.list_embedding();
                });

                $('#embedding_edit_modal').modal('show');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_embedding = async () => {
    const form = $('#form_embedding_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('embed', 'save', data);
        if (res && res.success) {
            $('#embedding_edit_modal').modal('hide');
            agentView.list_embedding();
        } else {
            alert('Failed to save Embedding settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
