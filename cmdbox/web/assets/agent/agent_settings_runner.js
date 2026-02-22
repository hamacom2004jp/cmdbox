agentView.get_runner_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'runner_save');
    const vform_names = ['runner_name', 'agent', 'session_store_type', 'session_store_pghost',
                        'session_store_pgport', 'session_store_pguser', 'session_store_pgpass', 'session_store_pgdbname',
                        'memory', 'rag', 'tts_engine', 'voicevox_model'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_runner_form = async () => {
    const form = $('#form_runner_edit');
    form.empty();
    const defs = await agentView.get_runner_form_def();
    const model = $('#runner_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_runner = async () => {
    // Runner追加ボタンのクリックイベント
    $('#btn_add_runner').off('click').on('click', async () => {
        await agentView.build_runner_form();
        $('#form_runner_edit [name="runner_name"]').prop('readonly', false);
        $('#form_runner_edit [name="session_store_type"]').trigger('change');
        $('#btn_del_runner').hide();
        $('#runner_edit_modal').modal('show');
        // Agentリストをロード
        await cmdbox.callcmd('agent','agent_list',{},(res)=>{
            $("[name='agent']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="agent"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'agent');
        // メモリーリストをロード
        await cmdbox.callcmd('agent','memory_list',{},(res)=>{
            $("[name='memory']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="memory"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'memory');
        // RAGリストをロード
        await cmdbox.callcmd('rag','list',{},(res)=>{
            $("[name='rag']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="rag"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'rag');
    });

    // Runner保存ボタンのクリックイベント
    $('#btn_save_runner').off('click').on('click', () => {
        agentView.save_runner();
    });

    // Runner選択ボタンのクリックイベント
    $('#btn_runner').off('click').on('click', async () => {
        await agentView.update_runner_list();
    });

    const container = $('#runner_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('agent', 'runner_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Runner list.</div>');
            console.warn(res);
            return;
        }

        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Runner connections found.</div>');
            return;
        }

        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'runner_load', { runner_name: item.name });
            if (!res || !res.success) {
                $(`
                    <li class="sf-list-danger-item">
                        <div>
                            <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${item.name}</span>
                            <span class="text-danger">${JSON.stringify(res)}</span>
                        </div>
                    </li>
                `).appendTo(container_ul);
                return;
            }
            const config = res.success || {};
            const itemEl = $(`
                <li class="sf-list-item">
                    <div>
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.runner_name}</span>
                        <span class="text-white-50">
                            Agent: ${config.agent || 'None'},
                            Session Store: ${config.session_store_type || 'None'},
                            VOICEVOX: ${config.voicevox_model || 'N/A'}
                        </span>
                    </div>
                </li>
            `).appendTo(container_ul);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_runner_form();
                const form = $('#form_runner_edit');
                form.find('[name="runner_name"]').val(config.runner_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'runner_name') return;
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
                $('#btn_del_runner').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.runner_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'runner_del', { runner_name: config.runner_name });
                    $('#runner_edit_modal').modal('hide');
                    agentView.list_runner();
                });

                $('#runner_edit_modal').modal('show');
                // コマンド実行
                await cmdbox.callcmd('agent','agent_list',{},(res)=>{
                    $("[name='agent']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="agent"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="agent"]').val(config.agent);
                },$('[name="title"]').val(),'agent');
                await cmdbox.callcmd('agent','memory_list',{},(res)=>{
                    $("[name='memory']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="memory"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="memory"]').val(config.memory);
                },$('[name="title"]').val(),'memory');
                await cmdbox.callcmd('rag','list',{},(res)=>{
                    $("[name='rag']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="rag"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="rag"]').val(config.rag);
                },$('[name="title"]').val(),'rag');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_runner = async () => {
    const form = $('#form_runner_edit');
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
        const res = await agentView.exec_cmd('agent', 'runner_save', data);
        if (res && res.success) {
            $('#runner_edit_modal').modal('hide');
            agentView.list_runner();
        } else {
            alert('Failed to save Runner settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

// Runner選択モーダルを表示
agentView.show_runner_select_modal = async () => {
    const container = $('#runner_select_list');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('agent', 'runner_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Runner list.</div>');
            console.warn(res);
            return;
        }
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Runner connections found.</div>');
            return;
        }
        const ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'runner_load', { runner_name: item.name });
            if (!res || !res.success) {
                const li = $(`<li class="d-flex sf-list-item"/>`).appendTo(ul);
                const div1 = $(`<div class="d-inline-block"/>`).appendTo(li);
                const head = $(`<span class="d-block glow-text-cyan system-font" style="font-size: 1em;"></span>`).appendTo(div1);
                head.html(`${item.name}`);
                const body = $(`<span class="text-danger"></span>`).appendTo(div1);
                body.html(`Failed to load`);
                return;
            }
            const config = res.success || {};

            const li = $(`<li class="d-flex sf-list-item"/>`).appendTo(ul);
            const div1 = $(`<div class="d-inline-block"/>`).appendTo(li);
            const head = $(`<span class="d-block glow-text-cyan system-font" style="font-size: 1em;"></span>`).appendTo(div1);
            head.html(`${config.runner_name}`);
            const body = $(`<span class="text-white-50"></span>`).appendTo(div1);
            body.html(`Agent: ${config.agent || 'None'},
                       Session Store: ${config.session_store_type || 'None'},
                       VOICEVOX: ${config.voicevox_model || 'None'}`);
            // リストアイテムクリックでrunner選択
            li.on('click', async () => {
                agentView.select_runner(config.runner_name);
                agentView.runner_conf = config;
            });
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    } finally {
        $('#runner_select_modal').modal('show');
    }
};

agentView.select_runner = async (runner_name) => {
    try {
        // display_runner_nameに選択されたrunnerの名前を表示
        $('#display_runner_name').html(`${runner_name}`);
        $('#display_runner_msg').html(`STARTING AGENT RUNNER ...`);
        cmdbox.show_loading();
        const item_data = await agentView.exec_cmd('agent', 'runner_load',{ runner_name: runner_name }, null, false);
        agentView.agent_runner = item_data.success;
        // TTSエンジンの起動
        //await agentView.say.start();
        cmdbox.show_loading();
        $('#display_runner_msg').html(`AGENT RUNNER IS READY`);
        // 送信ボタンを有効化
        agentView.btn_user_msg.prop('disabled', false).css('opacity', '1').css('cursor', 'pointer');
        // ファイル転送ボタンも有効化
        agentView.btn_filetrancefer.prop('disabled', false).css('opacity', '1').css('cursor', 'pointer');
        // MEMORYボタンも有効化
        agentView.btn_memories.prop('disabled', false).css('opacity', '1').css('cursor', 'pointer');
        // モーダルを閉じる
        $('#runner_select_modal').modal('hide');
        // メッセージ一覧をクリア
        agentView.chatMessages.html('');
        // 新しいセッションを作成
        agentView.ws && agentView.ws.close();
        agentView.chat(cmdbox.random_string(16));
    } finally {
        cmdbox.hide_loading();
    }
};
