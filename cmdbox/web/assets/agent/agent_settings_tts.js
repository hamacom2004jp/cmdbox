agentView.get_tts_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('tts', 'install');
    const vform_names = ['tts_engine', 'voicevox_ver', 'voicevox_whl',
        'openjtalk_ver', 'openjtalk_dic', 'onnxruntime_ver', 'onnxruntime_lib', 'force_install'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_tts_form = async () => {
    const form = $('#form_tts_install');
    form.empty();
    const defs = await agentView.get_tts_form_def();
    const model = $('#tts_settings'); // モーダルではなく、設定ペイン内の要素を渡す
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
    // 選択肢による表示非表示の設定
    form.find(`.choice_show`).each((i, elem) => {
        const input_elem = $(elem);
        input_elem.change();
    });
};

agentView.list_tts = async () => {
    // フォームが空の場合のみ構築する（再描画を避けるため）
    if ($('#form_tts_install').children().length === 0) {
        await agentView.build_tts_form();
    }
    if ($('#form_tts_uninstall').children().length === 0) {
        await agentView.build_tts_uninstall_form();
    }
};

agentView.install_tts = async () => {
    const form = $('#form_tts_install');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });
    // チェックボックスの処理 (serializeArrayではチェックされていないと含まれないため)
    form.find('input[type="checkbox"]').each((i, elem) => {
        data[elem.name] = $(elem).prop('checked');
    });
    if (data['force_install'] != 'true') delete data['force_install'];

    if (!confirm('Are you sure you want to install the TTS engine? This may take a while.')) return;

    try {
        cmdbox.show_loading();
        data['timeout'] = 900; // 15分のタイムアウトを設定
        const res = await agentView.exec_cmd('tts', 'install', data, null, false);
        cmdbox.hide_loading();
        
        if (res && res.success) {
            alert('TTS engine installation started/completed successfully. Check server logs for details.');
        } else {
            const msg = res && res.warn ? res.warn : 'Failed to install TTS engine.';
            alert(msg);
        }
    } catch (e) {
        cmdbox.hide_loading();
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agentView.get_tts_uninstall_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('tts', 'uninstall');
    const vform_names = ['tts_engine'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_tts_uninstall_form = async () => {
    const form = $('#form_tts_uninstall');
    form.empty();
    const defs = await agentView.get_tts_uninstall_form_def();
    const model = $('#tts_settings');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.uninstall_tts = async () => {
    const form = $('#form_tts_uninstall');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    if (!confirm('Are you sure you want to uninstall the TTS engine?')) return;

    try {
        cmdbox.show_loading();
        data['timeout'] = 300;
        const res = await agentView.exec_cmd('tts', 'uninstall', data, null, false);
        cmdbox.hide_loading();
        
        if (res && res.success) {
            alert('TTS engine uninstallation started/completed successfully. Check server logs for details.');
        } else {
            const msg = res && res.warn ? res.warn : 'Failed to uninstall TTS engine.';
            alert(msg);
        }
    } catch (e) {
        cmdbox.hide_loading();
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};
