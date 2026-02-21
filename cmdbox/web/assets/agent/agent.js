const agentView = {};
agentView.initView = () => {
    // --- 各コンテナのエレメント取得 ---
    agentView.chatContainer = $('#chatContainer');
    agentView.user_msg = $('#user_msg');
    agentView.btn_user_msg = $('#btn_user_msg');
    agentView.btn_rec = $('#btn_rec');
    agentView.btn_say = $('#btn_say');
    agentView.saveSettingsBtn = $('#saveSettingsBtn');
    agentView.aiCoreText = $('.core-text');
    agentView.aiCoreContainer = $('#aiCoreContainer');
    agentView.docViewerTitle = $('#docViewerTitle');
    agentView.docViewerContent = $('#docViewerContent');
    agentView.settingsModal = $('#agent_settings_modal');
    agentView.chatMessages = $('#messages');
    agentView.chatContainer = $('#chatContainer');
    agentView.memoryModal = $('#memoryModal');
    agentView.chatHistories = $('#session_tab ul.sf-list-group');
    agentView.fileTranceferModal = $('#fileTranceferModal');
    agentView.btn_filetrancefer = $('#btn_filetrancefer');
    agentView.btn_memories = $('#btn_memories');
    agentView.chat_reconnect_count = 0;

    // バージョン情報の取得と表示
    cmdbox.versions().then((versions) => {
        const version_html = `${versions['appid']}-${versions['version']}`;
        $('#appid_version').html(version_html);
    });
    // 現在時刻の取得と表示
    cmdbox.current_time().then((time_info) => {
        if (time_info) {
            const update_time = () => {
                const dt = new Date((time_info['timestamp'] * 1000 + (new Date().getTime() - time_info['timestamp'] * 1000)));
                const formatted_time = dt.toISOString().slice(0, 19).replace('T', ' ');
                $('#current_time').text(`${formatted_time} (${time_info['timezone']})`);
            };
            update_time();
            setInterval(update_time, 1000);
        }
    });
    // copyright表示
    cmdbox.copyright();
    // 設定モーダルの shown.bs.modal イベントハンドラ
    agentView.settingsModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        await agentView.list_agent();
    });
    // メモリーモーダルの shown.bs.modal イベントハンドラ
    agentView.memoryModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        await agentView.show_memories();
        await agentView.list_sessions();
    });
    // ファイル転送モーダルの shown.bs.modal イベントハンドラ
    agentView.fileTranceferModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        fsapi.onload();
    });
    // --- 音声出力と録音の状態 ---
    agentView.isRecording = false;
    // --- イベントハンドラ設定 ---
    // メッセージ送信ボタン
    // agent_runnerが設定されていない場合は送信ボタンを無効化
    agentView.btn_user_msg.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // ファイル転送ボタンも同様に無効化
    agentView.btn_filetrancefer.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // MEMORYボタンも同様に無効化
    agentView.btn_memories.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    agentView.user_msg.off('keydown').on('keydown', (e) => {
        // Ctrl+Enterで送信
        if (e.key === 'Enter' && e.ctrlKey && !agentView.btn_user_msg.prop('disabled')) {
            e.preventDefault();
            agentView.btn_user_msg.click();
            return
        }
    });
    // 音声入力ボタン
    agentView.btn_rec.off('click').on('click', () => {
        agentView.isRecording = !agentView.isRecording;
        if (agentView.isRecording) {
            agentView.btn_rec.css("color", "var(--accent-magenta)");
            agentView.user_msg.attr("placeholder", "Listening...");
        } else {
            agentView.btn_rec.css("color", "");
            agentView.user_msg.attr("placeholder", "Command...");
        }
    });
    // 音声出力トグル
    agentView.btn_say.off('click').on('click', () => {
        const icon = agentView.btn_say.find('i');
        if (!icon.hasClass('fa-volume-up')) {
            icon.addClass('fa-volume-up').removeClass('fa-volume-mute');
            agentView.btn_say.css("opacity", "1");
        } else {
            icon.addClass('fa-volume-mute').removeClass('fa-volume-up');
            agentView.btn_say.css("opacity", "0.5");
        }
    });
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
        } else if (target === '#memory_settings') {
            agentView.list_memory();
        } else if (target === '#runner_settings') {
            agentView.list_runner();
        } else if (target === '#rag_settings') {
            agentView.list_rag();
        } else if (target === '#extract_settings') {
            agentView.list_extract();
        } else if (target === '#tts_settings') {
            agentView.list_tts();
        }
    });


    // TTSインストールボタンのクリックイベント
    $('#btn_install_tts').off('click').on('click', () => {
        agentView.install_tts();
    });

    // TTSアンインストールボタンのクリックイベント
    $('#btn_uninstall_tts').off('click').on('click', () => {
        agentView.uninstall_tts();
    });

    // ユーザー情報の取得
    cmdbox.user_info().then((user) => {
        agentView.user = user;
    });

    // 初期メッセージ表示
    const message_id = cmdbox.random_string(16);
    const txt = agentView.create_agent_message(message_id);
    agentView.format_agent_message(txt,
        `インターフェースの初期化完了。<br/>` +
        `画面右上のタイトル「Click Here」をクリックしてAgent Runnerを選択してください。<br/>` + 
        `Agent Runnerが登録されていない場合は「CONFIG」をクリックして設定を追加してください。`);
    $(`#${message_id} .btn-toggle-message`).remove();

    // モーダルのドラッグ対応
    $('.modal-dialog').draggable({cursor:'move',cancel:'button, .modal-body, .modal-footer'});
    agentView.scrollToBottom();
}

agentView.disabled = false;
agentView.exec_cmd = async (mode, cmd, opt={}, error_func=null, loading=true) => {
    if(!agentView.user) {
        if (!agentView.disabled) {
            cmdbox.message({'error':'User information could not be retrieved. AI features are unavailable.'});
            agentView.disabled = true;
            $('#ai_chat_button').hide();
        }
        return;
    }
    const opt_def = cmdbox.get_server_opt(false, $('#filer_form'));
    opt = {...opt_def, ...opt, 'mode':mode, 'cmd':cmd, 'user_name':agentView.user['name'], 'capture_stdout':true};
    if (loading) cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(res => {
        if(res && Array.isArray(res) && res.length <=0) {
            if (loading) cmdbox.hide_loading();
            return res;
        }
        if (loading) cmdbox.hide_loading();
        if (res['success']) return res;
        if(!res[0] || !res[0]['success']) {
            if (error_func) {
                error_func(res);
                return;
            }
            console.warn(res);
            //cmdbox.message(res);
            return res;
        }
        return res[0];
    });
}

agentView.list_sessions = async (session_id) => {
    const runner_name = agentView.agent_runner ? agentView.agent_runner['runner_name'] : null;
    if (!runner_name || runner_name.length <= 0) return [];
    const res = await agentView.exec_cmd('agent', 'session_list', {
        'runner_name': runner_name,
        'session_id': session_id
    });
    if (!res || !res['success']) return [];
    if (!res['success']['data'] || typeof res['success']['data'] !== 'object') return [];
    const data = res['success']['data'];
    if (session_id) return data;
    agentView.chatHistories.html('');
    data.reverse().forEach(async (row) => {
        if (!row['events'] || row['events'].length <= 0) return;
        const runner_name = row['runner_name'];
        const session_id = row['session_id'];
        const user_name = row['user_name'];
        const update_time = row['last_update_time'] ? new Date(row['last_update_time'] * 1000) : '----/--/-- --:--:--';
        const msg = row['events'][0]['text'];
        const history = agentView.create_history(session_id, runner_name, user_name, update_time, msg);
    });
}
