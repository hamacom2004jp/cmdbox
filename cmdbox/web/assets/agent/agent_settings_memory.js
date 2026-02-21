agentView.get_memory_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'memory_save');
    const vform_names = ['memory_name', 'memory_type', 'llm', 'embed', 'memory_description', 'memory_instruction',
                         'memory_store_pghost', 'memory_store_pgport', 'memory_store_pguser',
                         'memory_store_pgpass', 'memory_store_pgdbname',
                         'memory_vertexai_project', 'memory_vertexai_location', 'memory_vertexai_agent_engine_id'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_memory_form = async () => {
    const form = $('#form_memory_edit');
    form.empty();
    const defs = await agentView.get_memory_form_def();
    const model = $('#memory_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_memory = async () => {
    // Memory追加ボタンのクリックイベント
    $('#btn_add_memory').off('click').on('click', async () => {
        await agentView.build_memory_form();
        $('#form_memory_edit [name="memory_name"]').prop('readonly', false);
        $('#form_memory_edit [name="memory_type"]').trigger('change');
        $('#btn_del_memory').hide();
        $('#memory_edit_modal').modal('show');
        // LLMリストをロード
        await cmdbox.callcmd('llm','list',{},(res)=>{
            $("[name='llm']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="llm"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'llm');
        // Embedリストをロード
        await cmdbox.callcmd('embed','list',{},(res)=>{
            $("[name='embed']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'embed');
    });

    // Memory保存ボタンのクリックイベント
    $('#btn_save_memory').off('click').on('click', () => {
        agentView.save_memory();
    });

    const container = $('#memory_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('agent', 'memory_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Memory list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Memory configurations are loaded.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'memory_load', { memory_name: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.memory_name}</span>
                        <span class="text-white-50">${config.memory_type} / ${config.llm} / ${config.embed}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_memory_form();
                const form = $('#form_memory_edit');
                form.find('[name="memory_name"]').val(config.memory_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'memory_name') return;
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
                $('#btn_del_memory').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.memory_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'memory_del', { memory_name: config.memory_name });
                    $('#memory_edit_modal').modal('hide');
                    agentView.list_memory();
                });

                $('#memory_edit_modal').modal('show');
                // コマンド実行
                await cmdbox.callcmd('llm','list',{},(res)=>{
                    $("[name='llm']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="llm"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="llm"]').val(config.llm);
                },$('[name="title"]').val(),'llm');
                await cmdbox.callcmd('embed','list',{},(res)=>{
                    $("[name='embed']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="embed"]').val(config.embed);
                },$('[name="title"]').val(),'embed');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_memory = async () => {
    const form = $('#form_memory_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('agent', 'memory_save', data);
        if (res && res.success) {
            $('#memory_edit_modal').modal('hide');
            agentView.list_memory();
        } else {
            alert('Failed to save Memory settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agentView.show_memories = async () => {
    const runner_name = agentView.agent_runner ? agentView.agent_runner['runner_name'] : null;
    if (!runner_name || runner_name.length <= 0) {
        cmdbox.message({'error':'Runner name is not available.'});
        console.log('Runner name is not available.');
        return;
    }
    cmdbox.show_loading();
    try {
        const res = await agentView.exec_cmd('agent', 'memory_status', {
            runner_name:runner_name,
            memory_fetch_offset:0,
            memory_fetch_count:100,
            memory_fetch_summary:true,
        }, null, false);
        const memoryContent = $('#memory_content');
        const memory_performance = $('#memory_performance');
        if (!res || !res['success'] || !res['success']['data']) {
            cmdbox.message({'error':'Failed to load memory status.'});
            console.log('Failed to load memory status.', res);
            memoryContent.html('Failed to load memory status.');
            return;
        };
        const data = res['success']['data'];
        if (data.length <= 0) {
            memoryContent.html('No memory status data available.');
            return;
        }
        
        // メモリーステータス情報を表示用に構築
        const timeOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        const statusHtml = data[0]['text'];
        memoryContent.html(statusHtml.replace(/\n/g, '<br/>'));
        const start = data[0]['ts_start'] ? Intl.DateTimeFormat('ja-JP', timeOptions).format(new Date(data[0]['ts_start'])) : null;
        const end = data[0]['ts_end'] ? Intl.DateTimeFormat('ja-JP', timeOptions).format(new Date(data[0]['ts_end'])) : null;
        $('#memory_range_start').text(start || '---');
        $('#memory_range_end').text(end || '---');
        memory_performance.text(`${(data[0]['my_cnt'] / data[0]['all_cnt'] * 100).toFixed(1)} %` || '---');
    } catch (e) {
        console.error('Error loading memory status:', e);
    } finally {
        cmdbox.hide_loading();
    }
};
