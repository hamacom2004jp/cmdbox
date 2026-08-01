const agentView = {};
agentView.get_user_msg = () => agentView.user_msg.val();
agentView.set_user_msg = (value) => { agentView.user_msg.val(value); };
agentView.set_user_msg_placeholder = (value) => { agentView.user_msg.attr('placeholder', value); };
agentView.initView = () => {
    // --- 各コンテナのエレメント取得 ---
    agentView.chatContainer = $('#chatContainer');
    agentView.user_msg = $('#user_msg');
    agentView.btn_user_msg = $('#btn_user_msg');
    agentView.btn_rec = $('#btn_rec');
    agentView.btn_say = $('#btn_say');
    agentView.bot_reasoning = $('#bot_reasoning');
    agentView.sel_reasoning_effort = $('#sel_reasoning_effort');
    agentView.saveSettingsBtn = $('#saveSettingsBtn');
    agentView.aiCoreText = $('.core-text');
    agentView.aiCoreContainer = $('#aiCoreContainer');
    agentView.docViewerTitle = $('#docViewerTitle');
    agentView.docViewerContent = $('#docViewerContent');
    agentView.chatMessages = $('#messages');
    agentView.chatContainer = $('#chatContainer');
    agentView.historyModal = $('#historyModal');
    agentView.chatHistories = $('#session_tab ul.sf-list-group');
    agentView.fileTranceferModal = $('#fileTranceferModal');
    agentView.btn_new_chat = $('#btn_new_chat');
    agentView.btn_filetrancefer = $('#btn_filetrancefer');
    agentView.btn_histories = $('#btn_histories');
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
                $('#current_time').text(`${dt.toLocaleString()} (${time_info['timezone']})`);
            };
            update_time();
            setInterval(update_time, 1000);
        }
    });
    // copyright表示
    cmdbox.copyright();
    // 設定モーダルの初期化
    agentView.initSettingsView();

    // ヒストリーモーダルの shown.bs.modal イベントハンドラ
    agentView.historyModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        // 全選択ボタン
        $('#btn_select_all_sessions').off('click').on('click', () => {
            $('#session_tab .session_checkbox').each(function() {
                $(this).attr('checked','checked').prop('checked', true);
            });
        });
        // 全解除ボタン
        $('#btn_deselect_all_sessions').off('click').on('click', () => {
            $('#session_tab .session_checkbox').each(function() {
                $(this).attr('checked',null).prop('checked', false);
            });
        });
        // 一括削除ボタン
        $('#btn_delete_selected_sessions').off('click').on('click', () => {
            agentView.delete_selected_sessions();
        });
        
        await agentView.list_sessions();
        cmdbox.process_i18n(agentView.historyModal);
    });
    // ファイル転送モーダルの shown.bs.modal イベントハンドラ
    agentView.fileTranceferModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        fsapi.onload();
        cmdbox.process_i18n(agentView.fileTranceferModal);
    });
    // --- 音声出力と録音の状態 ---
    agentView.isRecording = false;
    // --- イベントハンドラ設定 ---
    // メッセージ送信ボタン
    // agent_runnerが設定されていない場合は送信ボタンを無効化
    agentView.btn_user_msg.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // 新しいチャットを始めるボタンも同様に無効化
    agentView.btn_new_chat.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // ファイル転送ボタンも同様に無効化
    agentView.btn_filetrancefer.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // Historiesボタンも同様に無効化
    agentView.btn_histories.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // 音声入力ボタンも同様に無効化
    agentView.btn_rec.prop('disabled', true).css('cursor', 'not-allowed');
    agentView.user_msg.off('keydown.cmdbox').on('keydown.cmdbox', (e) => {
        // Ctrl+Enterで送信
        if (e.key === 'Enter' && e.ctrlKey && !agentView.btn_user_msg.prop('disabled')) {
            e.preventDefault();
            agentView.btn_user_msg.click();
            return
        }
    });
    // 新しいチャットを始めるボタン
    agentView.btn_new_chat.off('click').on('click', async () => {
        if (!await cmdbox.confirm('Start a new chat? This will clear the current chat history.', true)) return;
        // メッセージ一覧をクリア
        agentView.chatMessages.html('');
        // 新しいセッションを作成
        agentView.ws && agentView.ws.close();
        agentView.chat(cmdbox.random_string(16));
    });
    // 音声入力ボタン
    agentView.rec_init();

    // 音声出力トグル
    agentView.btn_say.off('click').on('click', agentView.say_set);
    agentView.say_init();

    // Reasoningトグル
    agentView.bot_reasoning.off('click').on('click', agentView.reasoning_set);
    agentView.sel_reasoning_effort.off('change').on('change', agentView.reasoning_set);
    agentView.reasoning_init();

    // display_runner_name クリックイベント
    $('#display_runner_name').off('click').on('click', async () => {
        await agentView.show_runner_select_modal();
    });

    // RAGへの登録クリックイベント
    $('#btn_regist_rag').off('click').on('click', async () => {
        await agentView.regist_rag();
    });

    // ユーザー情報の取得
    cmdbox.user_info().then((user) => {
        agentView.user = user;
    });

    // 初期メッセージ表示
    const org_msgs = [
        'Interface initialization complete.',
        'Click the title "Click Here" at the top right of the screen to select an Agent Runner.', 
        'If no Agent Runner is registered, click "config" to add a configuration.'
    ];
    cmdbox.translation(org_msgs, false).then(data => {
        const new_msgs = [];
        org_msgs.forEach((m, i) => {new_msgs.push(data[m]);});
        const message_id = cmdbox.random_string(16);
        const txt = agentView.create_agent_message(message_id);
        agentView.format_agent_message(txt, new_msgs.join('<br/>'));
        $(`#${message_id} .btn-toggle-message`).remove();
    });

    // モーダルのドラッグ対応
    $('.modal-dialog').draggable({cursor:'move',cancel:'button, .modal-body, .modal-footer'});
    agentView.scrollToBottom();
}
// 音声認識トグル
agentView.rec_off = () => {
    agentView.isRecording = false;
    agentView.btn_rec.prop('checked', false);
    agentView.set_user_msg_placeholder("Input Message...");
    // localStorage.setItem('cmdbox-btn_rec', "false");
};
agentView.rec_on = () => {
    agentView.isRecording = true;
    agentView.btn_rec.prop('checked', true);
    agentView.set_user_msg_placeholder("Listening...");
    // localStorage.setItem('cmdbox-btn_rec', "true");
};
agentView.rec_set = () => {
    if (!agentView.btn_rec.prop('checked')) {
        agentView.rec_off();
    } else {
        agentView.rec_on();
    }
};
agentView.rec_init = () => {
    /*if (localStorage.getItem('cmdbox-btn_rec')) {
        const saved_value = localStorage.getItem('cmdbox-btn_rec');
        if (saved_value && saved_value === "true") {
            agentView.rec_on();
            return;
        }
    }*/
    agentView.rec_off();
};
// 音声合成トグル
agentView.say_off = () => {
    agentView.btn_say.prop('checked', false);
    agentView.chat_send(agentView.ws, 'call_tts_off');
    // 再生中の場合は停止
    if (agentView.say && agentView.say.isPlaying()) {
        agentView.say.stop();
    }
    localStorage.setItem('cmdbox-btn_say', "false");
};
agentView.say_on = () => {
    agentView.btn_say.prop('checked', true);
    agentView.chat_send(agentView.ws, 'call_tts_on');
    localStorage.setItem('cmdbox-btn_say', "true");
};
agentView.say_set = () => {
    if (!agentView.btn_say.prop('checked')) {
        agentView.say_off();
    } else {
        agentView.say_on();
    }
};
agentView.say_init = () => {
    if (localStorage.getItem('cmdbox-btn_say')) {
        const saved_value = localStorage.getItem('cmdbox-btn_say');
        if (saved_value && saved_value === "true") {
            agentView.say_on();
            return;
        }
    }
    agentView.say_off();
};
// Reasoningトグル
agentView.reasoning_off = () => {
    agentView.bot_reasoning.prop('checked', false);
    agentView.sel_reasoning_effort.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    agentView.chat_send(agentView.ws, 'call_reasoning_off');
    localStorage.setItem('cmdbox-sel_reasoning_effort', "call_reasoning_off");
};
agentView.reasoning_on = () => {
    agentView.bot_reasoning.prop('checked', true);
    agentView.sel_reasoning_effort.prop('disabled', false).css('opacity', '1').css('cursor', 'auto');
    agentView.chat_send(agentView.ws, `call_reasoning_${agentView.sel_reasoning_effort.val()}`);
    localStorage.setItem('cmdbox-sel_reasoning_effort', `call_reasoning_${agentView.sel_reasoning_effort.val()}`);
};
agentView.reasoning_set = () => {
    if (!agentView.bot_reasoning.prop('checked')) {
        agentView.reasoning_off();
    } else {
        agentView.reasoning_on();
    }
};
agentView.reasoning_init = () => {
    if (localStorage.getItem('cmdbox-sel_reasoning_effort')) {
        const saved_value = localStorage.getItem('cmdbox-sel_reasoning_effort');
        if (saved_value) {
            if (saved_value != 'call_reasoning_off') {
                agentView.sel_reasoning_effort.val(saved_value.replace('call_reasoning_', ''));
                agentView.reasoning_on();
                return;
            }
        }
    }
    agentView.reasoning_off();
};

agentView.disabled = false;
agentView.exec_cmd = async (mode, cmd, opt={}, error_func=null, loading=true, sse_cb=null) => {
    if(!agentView.user) {
        if (!agentView.disabled) {
            cmdbox.message({'error':'User information could not be retrieved. AI features are unavailable.'}, true);
            agentView.disabled = true;
            $('#ai_chat_button').hide();
        }
        return;
    }
    const opt_def = cmdbox.get_server_opt(false, $('#filer_form'));
    opt = {...opt_def, ...opt, 'mode':mode, 'cmd':cmd, 'user_name':agentView.user['name'], 'cache_clear':true};
    if (loading) cmdbox.show_loading();
    if (sse_cb) {
        const queryString = new URLSearchParams(opt).toString();
        const evtSource = new EventSource(`exec_sse_cmd?${queryString}`, {withCredentials: true,});
        evtSource.onmessage = function(event) {
            try {
                console.log('SSE message received:', event.data);
                const data = JSON.parse(event.data);
                sse_cb(data);
                if (data['success'] || data['error'] || data['warn']) {
                    evtSource.close();
                    if (loading) cmdbox.hide_loading();
                }
            } catch(e) {
                console.error('Error parsing SSE data:', e);
            }
        };
        evtSource.onerror = function(e) {
            evtSource.close();
            if (loading) cmdbox.hide_loading();
            if (error_func) error_func({'error': 'An error occurred during command execution.'});
        };
        return;
    }
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
            //cmdbox.message(res, true, true);
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

agentView.regist_rag = async () => {
    if (!agentView.runner_conf || !agentView.runner_conf.rag) {
        cmdbox.message({ 'error': 'Please select an Agent Runner first.' }, true);
        return false;
    }
    if (agentView.runner_conf.rag.length <= 0) {
        cmdbox.message({ 'error': 'No RAGs are selected for registration.' }, true);
        return false;
    }
    if (!await cmdbox.confirm(`Are you sure you want to register RAG '${agentView.runner_conf.rag}' to the system?`, true, true)) {
        return false;
    }
    const n = agentView.runner_conf.rag.length;
    for (i=0; i<n; i++) {
        const rag_name = agentView.runner_conf.rag[i];
        cmdbox.show_loading();
        cmdbox.progress(0, n, i, `Registering RAG '${rag_name}'...`, true, true);
        await agentView.exec_cmd('rag', 'regist', { rag_name: rag_name }, null, true, (data) => {
            if (data['process']) {
                const msg = data['process']['message'];
                const count = data['process']['count'] || 1;
                const index = data['process']['index'] || 1;
                cmdbox.progress(0, count, index, `${msg}`, true, false);
            }
        });
    }
}
