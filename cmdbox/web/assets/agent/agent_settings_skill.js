agentView.get_skill_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('skill', 'install');
    const vform_names = ['skill_file', 'skill_name', 'overwrite'];
    return opts.filter(o => vform_names.includes(o.opt));
};

agentView.build_skill_form = async () => {
    const form = $('#form_skill_edit');
    form.empty();
    const defs = await agentView.get_skill_form_def();
    const model = $('#skill_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_skill = async () => {
    // Skill追加ボタンのクリックイベント
    $('#btn_add_skill').off('click').on('click', async () => {
        cmdbox.show_loading();
        try {
            await agentView.build_skill_form();
            const form = $('#form_skill_edit');
            form.find('[name="skill_name"]').prop('readonly', false).val('');
            form.find('[name="skill_file"]').prop('disabled', false).val('');
            form.find('[name="overwrite"]').prop('checked', false);
            $('#btn_install_skill').show();
            $('#btn_uninstall_skill').hide();
            cmdbox.process_i18n($('#skill_edit_modal'));
            $('#skill_edit_modal').modal('show');
        } finally {
            cmdbox.hide_loading();
        }
    });

    // Skillインストールボタン
    $('#btn_install_skill').off('click').on('click', () => {
        agentView.install_skill();
    });

    const container = $('#skill_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('skill', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger i18n p-3">Failed to load Skill list.</div>');
            console.warn(res);
            return;
        }

        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3 i18n">No installed skills found.</div>');
            return;
        }

        const container_ul = $('<ul class="sf-list-group"/>').appendTo(container);
        list.forEach((item) => {
            const itemEl = $(
                '<li class="sf-list-item" style="cursor: pointer;">'
                + '<div>'
                + `<span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${item.name}</span>`
                + `<span>${item.path || ''}</span>`
                + '</div>'
                + '</li>'
            ).appendTo(container_ul);

            itemEl.on('click', async () => {
                cmdbox.show_loading();
                try {
                    await agentView.build_skill_form();
                    const form = $('#form_skill_edit');
                    form.find('[name="skill_name"]').val(item.name).prop('readonly', true);
                    form.find('[name="skill_file"]').val('').prop('disabled', true);
                    form.find('[name="overwrite"]').prop('checked', false);

                    $('#btn_install_skill').hide();
                    $('#btn_uninstall_skill').show().off('click').on('click', async () => {
                        if (!await cmdbox.confirm(`Are you sure you want to uninstall '${item.name}'?`, true, true)) return;
                        const delRes = await agentView.exec_cmd('skill', 'uninstall', { skill_name: item.name });
                        if (delRes && delRes.success) {
                            $('#skill_edit_modal').modal('hide');
                            agentView.list_skill();
                        } else {
                            cmdbox.message(delRes, true, true);
                        }
                    });

                    cmdbox.process_i18n($('#skill_edit_modal'));
                    $('#skill_edit_modal').modal('show');
                } finally {
                    cmdbox.hide_loading();
                }
            });
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.install_skill = async () => {
    const form = $('#form_skill_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('skill', 'install', data);
        if (res && res.success) {
            $('#skill_edit_modal').modal('hide');
            agentView.list_skill();
        } else {
            cmdbox.message(res, true, true);
        }
    } catch (e) {
        console.error(e);
        cmdbox.message(`Error: ${e.message}`, true, true);
    }
};
