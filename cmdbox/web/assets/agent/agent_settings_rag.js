agentView.get_rag_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('rag', 'save');
    const vform_names = ['rag_name', 'rag_type', 'source_dir', 'extract', 'embed', 'embed_vector_dim',
                         'vector_store_pghost', 'vector_store_pgport', 'vector_store_pguser', 'vector_store_pgpass', 'vector_store_pgdbname',
                         'graph_store_pghost', 'graph_store_pgport', 'graph_store_pguser', 'graph_store_pgpass', 'graph_store_pgdbname',
                        ];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_rag_form = async () => {
    const form = $('#form_rag_edit');
    form.empty();
    const defs = await agentView.get_rag_form_def();
    const model = $('#rag_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_rag = async () => {
    // RAG追加ボタンのクリックイベント
    $('#btn_add_rag').off('click').on('click', async () => {
        await agentView.build_rag_form();
        $('#form_rag_edit [name="rag_name"]').prop('readonly', false);
        $('#form_rag_edit [name="rag_type"]').trigger('change');
        $('#btn_del_rag').hide();
        $('#btn_build_rag').hide();
        $('#rag_edit_modal').modal('show');
        // Embedリストをロード
        await cmdbox.callcmd('embed','list',{},(res)=>{
            $("[name='embed']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'embed');
        // Extractリストをロード
        await cmdbox.callcmd('extract','list',{match_mode:'extract'},(res)=>{
            $("[name='extract']").empty().append('<option></option>');
            res['data'].map(elm=>{$("[name='extract']").append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'extract');
    });

    // RAG保存ボタンのクリックイベント
    $('#btn_save_rag').off('click').on('click', () => {
        agentView.save_rag();
    });

    const container = $('#rag_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('rag', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load RAG list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No RAG configurations are loaded.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('rag', 'load', { rag_name: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.rag_name}</span>
                        <span>${config.rag_type} / ${config.extract} / ${config.embed}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_rag_form();
                const form = $('#form_rag_edit');
                form.find('[name="rag_name"]').val(config.rag_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'rag_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (input.attr('type') === 'checkbox') {
                            input.prop('checked', config[key]);
                        } else if (key === 'source_dir' && Array.isArray(config[key])) {
                            // source_dirは複数値の可能性
                            input.val(config[key].join('\n'));
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
                $('#btn_del_rag').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.rag_name}'?`)) return;
                    await agentView.exec_cmd('rag', 'del', { rag_name: config.rag_name });
                    $('#rag_edit_modal').modal('hide');
                    agentView.list_rag();
                });
                $('#btn_build_rag').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to build '${config.rag_name}'?`)) return;
                    await agentView.build_rag();
                });
                // コマンド実行
                await cmdbox.callcmd('embed','list',{},(res)=>{
                    $("[name='embed']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="embed"]').val(config.embed);
                },$('[name="title"]').val(),'embed');
                await cmdbox.callcmd('extract','list',{match_mode:'extract'},(res)=>{
                    $("[name='extract']").empty().append('<option></option>');
                    res['data'].map(elm=>{$("[name='extract']").append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="extract"]').val(config.extract);
                },$('[name="title"]').val(),'extract');

                $('#rag_edit_modal').modal('show');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_rag = async () => {
    const form = $('#form_rag_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('rag', 'save', data);
        if (res && res.success) {
            $('#rag_edit_modal').modal('hide');
            agentView.list_rag();
        } else {
            alert('Failed to save RAG settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agentView.build_rag = async () => {
    const form = $('#form_rag_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('rag', 'build', data);
        if (res && res.success) {
            $('#rag_edit_modal').modal('hide');
            agentView.list_rag();
        } else {
            alert('Failed to build RAG settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};