agentView.initSettingsView = () => {
    agentView.settingsModal = $('#agent_settings_modal');
    // 設定モーダルの設定メニューの切り替え
    const settingsItems = agentView.settingsModal.find('.list-group-item');
    settingsItems.off('click').on('click', function(e) {
        e.preventDefault();
        settingsItems.removeClass('active');
        $(this).addClass('active');
        const target = $(this).data('bs-target');
        $('.settings-content').addClass('d-none');
        $(target).removeClass('d-none');
        
        if (target === '#agent_settings') {
            agentView.list_agent();
        } else if (target === '#llm_settings') {
            agentView.list_llm();
        } else if (target === '#mcpsv_settings') {
            agentView.list_mcpsv();
        } else if (target === '#embedding_settings') {
            agentView.list_embedding();
        } else if (target === '#runner_settings') {
            agentView.list_runner();
        } else if (target === '#rag_settings') {
            agentView.list_rag();
        } else if (target === '#extract_settings') {
            agentView.list_extract();
        } else if (target === '#tts_settings') {
            agentView.list_tts();
        } else if (target === '#datasource_settings') {
            agentView.list_datasource();
        }
    });
    // 権限チェックでコマンドが実行不能ならば設定メニューを非表示にする
    const promises = [];
    promises.push(cmdbox.check_cmd('agent', 'agent_load').then((res) => {
        !res && $('[data-bs-target="#agent_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('datasource', 'load').then((res) => {
        !res && $('[data-bs-target="#datasource_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('llm', 'load').then((res) => {
        !res && $('[data-bs-target="#llm_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('agent', 'mcpsv_load').then((res) => {
        !res && $('[data-bs-target="#mcpsv_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('tts', 'install').then((res) => {
        !res && $('[data-bs-target="#tts_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('agent', 'runner_load').then((res) => {
        !res && $('[data-bs-target="#runner_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('rag', 'load').then((res) => {
        !res && $('[data-bs-target="#rag_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('embed', 'load').then((res) => {
        !res && $('[data-bs-target="#embedding_settings"]').hide();
    }));
    promises.push(cmdbox.check_cmd('extract', 'load').then((res) => {
        !res && $('[data-bs-target="#extract_settings"]').hide();
    }));
    Promise.all(promises).then(() => {
        // 表示されている最初の設定メニューをクリックして表示する
        const firstVisibleSetting = $('[data-bs-target]').filter(':visible').first();
        if (firstVisibleSetting.length) {
            firstVisibleSetting.click();
        }
    });

    // 設定モーダルの shown.bs.modal イベントハンドラ
    agentView.settingsModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        await agentView.list_agent();
        cmdbox.process_i18n(agentView.settingsModal);
    });
};