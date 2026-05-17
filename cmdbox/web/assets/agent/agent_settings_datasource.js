agentView.get_datasource_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('datasource', 'save');
    const vform_names = ['dsname', 'dbtype', 'scope', 'client_data',
                         'db_host', 'db_port', 'db_user', 'db_password', 'db_name', 'db_timeout', 'db_path'];
    return opts.filter(o => vform_names.includes(o.opt));
};

agentView.build_datasource_form = async () => {
    const form = $('#form_datasource_edit');
    form.empty();
    const defs = await agentView.get_datasource_form_def();
    const model = $('#datasource_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_datasource = async () => {
    // Datasource追加ボタンのクリックイベント
    $('#btn_add_datasource').off('click').on('click', async () => {
        await agentView.build_datasource_form();
        $('#form_datasource_edit [name="dsname"]').prop('readonly', false);
        $('#form_datasource_edit [name="dbtype"]').trigger('change');
        $('#form_datasource_edit [name="scope"]').trigger('change');
        $('#btn_del_datasource').hide();
        cmdbox.process_i18n($('#datasource_edit_modal'));
        $('#datasource_edit_modal').modal('show');
    });

    // Datasource保存ボタンのクリックイベント
    $('#btn_save_datasource').off('click').on('click', () => {
        agentView.save_datasource();
    });

    const container = $('#datasource_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('datasource', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger i18n p-3">Failed to load Datasource list.</div>');
            console.warn(res);
            return;
        }

        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3 i18n">No datasource configurations found.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('datasource', 'load', { dsname: item.name });
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
            const config = res.success && res.success.data || {};

            const itemEl = $(`
                <li class="sf-list-item" style="cursor: pointer;">
                    <div>
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${item.name}</span>
                        <span>${config.dbtype || item.dbtype}</span>
                    </div>
                </li>
            `).appendTo(container_ul);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_datasource_form();
                const form = $('#form_datasource_edit');
                form.find('[name="dsname"]').val(config.dsname || item.name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'dsname') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0 && config[key] != null) input.val(`${config[key]}`);
                });
                // choice_showによる表示切り替えをトリガー
                form.find('.choice_show').each((i, elem) => { $(elem).change(); });

                // 削除ボタンのハンドラー
                $('#btn_del_datasource').show().off('click').on('click', async () => {
                    if (!await cmdbox.confirm(`Are you sure you want to delete '${item.name}'?`, true, true)) return;
                    const res = await agentView.exec_cmd('datasource', 'del', { dsname: item.name });
                    if (res && res.success) {
                        $('#datasource_edit_modal').modal('hide');
                        agentView.list_datasource();
                    } else {
                        cmdbox.message(res, true, true);
                    }
                });
                cmdbox.process_i18n($('#datasource_edit_modal'));
                $('#datasource_edit_modal').modal('show');
            });
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_datasource = async () => {
    const form = $('#form_datasource_edit');
    const data = {};
    form.find(':input').each((i, elem) => {
        const val = $(elem).val();
        if (val) data[elem.name] = val;
    });

    try {
        const res = await agentView.exec_cmd('datasource', 'save', data);
        if (res && res.success) {
            $('#datasource_edit_modal').modal('hide');
            agentView.list_datasource();
        } else {
            cmdbox.message(res, true, true);
        }
    } catch (e) {
        console.error(e);
        cmdbox.message(`Error: ${e.message}`, true, true);
    }
};
