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
    agentView.sessionModal = $('#sessionModal');
    agentView.memoryModal = $('#memoryModal');
    agentView.chatHistories = $('#sessionModal .modal-body ul.sf-list-group');
    agentView.btn_histories = $('#btn_histories');
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
    // セッションモーダルの shown.bs.modal イベントハンドラ
    agentView.sessionModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        await agentView.list_sessions();
    });
    // メモリーモーダルの shown.bs.modal イベントハンドラ
    agentView.memoryModal.off('shown.bs.modal').on('shown.bs.modal', async () => {
        await agentView.show_memories();
    });
    // --- 音声出力と録音の状態 ---
    agentView.isRecording = false;
    // --- イベントハンドラ設定 ---
    // メッセージ送信ボタン
    // agent_runnerが設定されていない場合は送信ボタンを無効化
    agentView.btn_user_msg.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
    // HISTORIESボタンも同様に無効化
    agentView.btn_histories.prop('disabled', true).css('opacity', '0.5').css('cursor', 'not-allowed');
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
        } else if (target === '#tts_settings') {
            agentView.list_tts();
        }
    });
    // LLM追加ボタンのクリックイベント
    $('#btn_add_llm').off('click').on('click', async () => {
        await agentView.build_llm_form();
        $('#form_llm_edit [name="llmname"]').prop('readonly', false);
        $('#form_llm_edit [name="llmprov"]').trigger('change');
        $('#btn_del_llm').hide();
        $('#llm_edit_modal').modal('show');
    });

    // LLM保存ボタンのクリックイベント
    $('#btn_save_llm').off('click').on('click', () => {
        agentView.save_llm();
    });

    // MCPSV追加ボタンのクリックイベント
    $('#btn_add_mcpsv').off('click').on('click', () => {
        agentView.build_mcpsv_form();
        $('#form_mcpsv_edit [name="mcpserver_name"]').prop('readonly', false);
        $('#btn_del_mcpsv').hide();
        $('#mcpsv_edit_modal').modal('show');
    });

    // MCPSV保存ボタンのクリックイベント
    $('#btn_save_mcpsv').off('click').on('click', () => {
        agentView.save_mcpsv();
    });

    // Agent追加ボタンのクリックイベント
    $('#btn_add_agent').off('click').on('click', async () => {
        await agentView.build_agent_form();
        $('#form_agent_edit [name="agent_name"]').prop('readonly', false);
        $('#btn_del_agent').hide();
        $('[name="agent_type"]').trigger('change');
        $('#agent_edit_modal').modal('show');
        // LLMリストをロード
        await cmdbox.callcmd('llm','list',{},(res)=>{
            $("[name='llm']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="llm"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'llm');
        // MCPサーバーリストをロード
        await cmdbox.callcmd('agent','mcpsv_list',{},(res)=>{
            $("[name='mcpservers']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="mcpservers"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'mcpservers');
        // SubAgentリストをロード
        await cmdbox.callcmd('agent','agent_list',{},(res)=>{
            $("[name='subagents']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="subagents"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'subagents');
    });

    // Agent保存ボタンのクリックイベント
    $('#btn_save_agent').off('click').on('click', () => {
        agentView.save_agent();
    });

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
    });

    // Runner保存ボタンのクリックイベント
    $('#btn_save_runner').off('click').on('click', () => {
        agentView.save_runner();
    });

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

    // display_runner_name クリックイベント
    $('#display_runner_name').off('click').on('click', async () => {
        await agentView.show_runner_select_modal();
    });

    // Runner選択ボタンのクリックイベント
    $('#btn_runner').off('click').on('click', async () => {
        await agentView.update_runner_list();
    });

    // RAG追加ボタンのクリックイベント
    $('#btn_add_rag').off('click').on('click', async () => {
        await agentView.build_rag_form();
        $('#form_rag_edit [name="rag_name"]').prop('readonly', false);
        $('#form_rag_edit [name="rag_type"]').trigger('change');
        $('#btn_del_rag').hide();
        $('#rag_edit_modal').modal('show');
        // Embedリストをロード
        await cmdbox.callcmd('embed','list',{},(res)=>{
            $("[name='embed']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'embed');
        // Extractリストをロード
        await cmdbox.callcmd('cmd','list',{match_mode:'extract'},(res)=>{
            $("[name='extract']").empty().append('<option></option>');
            res.forEach(row=>{$("[name='extract']").append('<option value="'+row["title"]+'">'+row["title"]+'</option>');});
        },$('[name="title"]').val(),'extract');
    });

    // RAG保存ボタンのクリックイベント
    $('#btn_save_rag').off('click').on('click', () => {
        agentView.save_rag();
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
        `右側エリアの「Click Here」をクリックしてAgent Runnerを選択してください。<br/>` + 
        `Agent Runnerが登録されていない場合は「CONFIG」をクリックして設定を追加してください。`);
    $(`#${message_id} .btn-toggle-message`).remove();

    // モーダルのドラッグ対応
    $('.modal-dialog').draggable({cursor:'move',cancel:'button, .modal-body, .modal-footer'});
    agentView.scrollToBottom();
}

// Function to open document viewer
agentView.showDocument = (title, content, message_id) => {
    // create modal
    let modal = $(`#${message_id} .modal`);
    if (modal.length <= 0) {
        const html = `<div id="${message_id}" class="modal fade" tabindex="-1" aria-hidden="true" style="z-index: 1100;">
            <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                <div class="modal-content sf-modal doc-card" style="height:auto;">
                    <div class="modal-header doc-header">
                        <h5 class="modal-title glow-text-cyan system-font"><i class="fas fa-database me-2"></i>${title}</h5>
                        <button type="button" class="btn btn-sf-icon btn_window_stack">
                            <i class="fa-regular fa-window-restore"></i>
                        </button>
                        <button type="button" class="btn btn-sf-icon btn_window">
                            <i class="fa-regular fa-window-maximize"></i>
                        </button>
                        <button type="button" class="btn btn-sf-icon btn_window_close" data-bs-dismiss="modal" aria-label="Close">
                            <i class="fas fa-times fa-lg"></i>
                        </button>
                    </div>
                    <div class="modal-body doc-body docViewerContent">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary btn_window_close" data-bs-dismiss="modal">CLOSE</button>
                    </div>
                </div>
            </div>
        </div>`;
        modal = $(html).appendTo('body');
        // modal setting
        const dialog = modal.find('.modal-dialog');
        const content = modal.find('.modal-content');
        dialog.draggable({cursor:'move',cancel:'.modal-body'});
        modal.find('.btn_window_stack').off('click').on('click', () => {
            modal.find('.btn_window_stack').css('margin-left', '0px').hide();
            modal.find('.btn_window').css('margin-left', 'auto').show();
            dialog.removeClass('modal-fullscreen');
            content.css('height', 'auto');
        });
        modal.find('.btn_window').off('click').on('click', () => {
            modal.find('.btn_window_stack').css('margin-left', 'auto').show();
            modal.find('.btn_window').css('margin-left', '0px').hide();
            dialog.css('top', '').css('left', '').addClass('modal-fullscreen');
            content.css('height', 'calc(100% - var(--bs-modal-margin) * 2)');
        });
        modal.on('hidden.bs.modal', () => { agentView.closeDocument(message_id); });
        modal.find('.btn_window_stack').css('margin-left', '0px').hide();
        modal.find('.btn_window').css('margin-left', 'auto').show();
    }
    modal.find('.docViewerContent').html(content);
    // Animate Transitions
    agentView.aiCoreContainer.addClass('dimmed');
    modal.modal('show');
};

// Function to close document viewer
agentView.closeDocument = (message_id) => {
    let modal = $(`#${message_id} .modal`);
    modal.modal('hide');
    modal.remove();
    agentView.aiCoreContainer.removeClass('dimmed');
};

// --- Chat Logic ---
agentView.scrollToBottom = () => {
    agentView.chatContainer.scrollTop(agentView.chatContainer.prop("scrollHeight"));
};
agentView.chat = (session_id) => {
    const ping_interval = 5000; // pingの間隔
    const max_reconnect_count = 60000/ping_interval*1; // 最大再接続回数
    cmdbox.show_loading();
    // ws再接続のためのインターバル初期化
    if (agentView.chat_reconnectInterval_handler) {
        clearInterval(agentView.chat_reconnectInterval_handler);
    }
    // wsのpingのためのインターバル初期化
    if (agentView.chat_callback_ping_handler) {
        clearInterval(agentView.chat_callback_ping_handler);
    }
    agentView.chatMessages.attr('data-session_id', session_id);
    agentView.message_id = null;
    //agentView.btn_user_msg.prop('disabled', true); // 初期状態で送信ボタンを無効化
    // 送信ボタンのクリックイベント
    agentView.btn_user_msg.off('click').on('click', async () => {
        const msg = agentView.user_msg.val();
        if (msg.length <= 0) return;
        agentView.user_msg.val('');
        // 入力内容をユーザーメッセージとして表示
        agentView.create_user_message(msg);
        agentView.create_history(session_id, msg);
        // エージェント側のメッセージ読込中を表示
        if (!agentView.message_id) {
            agentView.message_id = cmdbox.random_string(16);
            const txt = agentView.create_agent_message(agentView.message_id);
            cmdbox.show_loading(txt);
        }
        if (!agentView.ws) {
            cmdbox.message({'warn':'The connection to the runner has not yet been established.'});
            return;
        }
        // メッセージを送信
        agentView.ws.send(msg);
        $('.ai-core').addClass('ai-core2');
        // メッセージ一覧を一番下までスクロール
        agentView.chatContainer.scrollTop(agentView.chatContainer.prop('scrollHeight'));
    });
    // recボタンのクリックイベント
    agentView.btn_rec.off('click').on('click', async () => {
        // 録音を終了
        if (agentView.btn_rec.hasClass('rec_on')) {
            agentView.btn_rec.removeClass('rec_on');
            agentView.btn_rec.find('use').attr('href', '#btn_mic');
            // 録音中を停止
            if (agentView.recognition) {
                agentView.recognition.stop();
                const transcript = agentView.user_msg.val();
                transcript && agentView.btn_user_msg.click(); // 録音が終了したら自動的にメッセージを送信
            }
            return;
        }
        // 録音を開始
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        if (!SpeechRecognition) {
            cmdbox.message({'error':'Speech Recognition API is not supported in this browser.'});
            return;
        }
        agentView.btn_rec.addClass('rec_on');
        agentView.btn_rec.find('use').attr('href', '#btn_mic_fill');
        let finalTranscript = agentView.user_msg.val();
        agentView.recognition = new SpeechRecognition();
        agentView.recognition.lang = 'ja-JP'; // 言語設定
        agentView.recognition.interimResults = true; // 中間結果を取得する
        agentView.recognition.maxAlternatives = 1; // 最小の候補数
        agentView.recognition.continuous = false; // 連続認識を無効にする
        agentView.recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                let transcript = event.results[i][0].transcript;
                console.log(`transcript: ${transcript}`);
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript = transcript;
                }
            }
            agentView.user_msg.val(finalTranscript + interimTranscript);
        };
        agentView.recognition.onerror = (event) => {
            console.error(`Speech Recognition error: ${event.error}`);
            if (event.error === 'no-speech') {
                agentView.recognition.restart();
                return; // no-speechエラーは無視して再度認識を開始
            }
            agentView.btn_rec.removeClass('rec_on');
            agentView.btn_rec.find('use').attr('href', '#btn_mic');
            cmdbox.message({'error':`Speech Recognition error: ${event.error}`});
        };
        agentView.recognition.onend = () => {
            // 連続認識を無効にしているので、認識が終了したら再稼働させる。
            console.log(`onend event triggered.`);
            agentView.recognition.restart();
        };
        agentView.recognition.restart = () => {
            if (agentView.btn_rec.hasClass('rec_on')) {
                setTimeout(() => {
                    try {
                        agentView.recognition.start();
                    } catch (error) {
                        console.error(`Error restarting recognition: ${error}`);
                    }
                }, 100);
            }
        };
        agentView.recognition.start();
    });
    // ws接続
    const protocol = window.location.protocol.endsWith('s:') ? 'wss' : 'ws';
    const host = window.location.hostname;
    const port = window.location.port;
    const path = window.location.pathname;
    const runner_name = agentView.agent_runner ? agentView.agent_runner['runner_name'] : null;
    cmdbox.hide_loading();
    if (!runner_name || runner_name.length <= 0) return;
    if (agentView.ws && agentView.ws.readyState === WebSocket.OPEN) return;
    cmdbox.show_loading();
    if (agentView.ws) agentView.ws.close();
    agentView.ws = new WebSocket(`${protocol}://${host}:${port}${path}/chat/ws/${runner_name}/${session_id}`);
    // エージェントからのメッセージ受信時の処理
    agentView.ws.onmessage = async (event) => {
        let packet;
        try {
            packet = JSON.parse(event.data);
        } catch (error) {
            console.warn('JSON parse error:', error);
            return;
        }
        let msg_container = $(`#${agentView.message_id}`);
        if (!agentView.message_id || msg_container.length <= 0) {
            // エージェント側の表示枠が無かったら追加
            agentView.message_id = cmdbox.random_string(16);
        }
        if (packet && packet['warn']) {
            const txt = agentView.create_agent_message(agentView.message_id);
            await agentView.format_agent_message(txt, `${packet['warn']}`);
            agentView.message_id = null;
            return;
        }
        if (packet.turn_complete) {
            agentView.message_id = null;
            return;
        }
        if (!packet.message || packet.message.length <= 0) {
            agentView.message_id = null;
            return;
        }
        console.log(packet);
        if (packet.flags && !packet.flags['final_response']) {
            // 「考え中」を表示
            if (!agentView.message_id) {
                agentView.message_id = cmdbox.random_string(16);
                msg_container = $(`#${agentView.message_id}`);
            }
            let msg_content = agentView.create_agent_message(agentView.message_id);
            msg_container = $(`#${agentView.message_id}`);
            msg_content.addClass('message-thinking');
            if (msg_content.children().length > 0) {
                msg_container.append('<div class="msg-content message-thinking"></div>');
                msg_content = agentView.create_agent_message(agentView.message_id);
                msg_container = $(`#${agentView.message_id}`);
            }
            if (!msg_content.hasClass('collapsed')) {
                msg_content.addClass('collapsed');
                msg_container.find('.btn-toggle-message').text('▶');
            }
            await agentView.format_agent_message(msg_content, packet.message);
            agentView.scrollToBottom();
            return;
        }
        $('.ai-core').removeClass('ai-core2');
        let msg_content = agentView.create_agent_message(agentView.message_id);
        msg_container = $(`#${agentView.message_id}`);
        if (msg_content.children().length > 0) {
            msg_container.append('<div class="msg-content"></div>');
            msg_content = agentView.create_agent_message(agentView.message_id);
            msg_container = $(`#${agentView.message_id}`);
        }
        await agentView.format_agent_message(msg_content, packet.message);
        if (msg_container.find('.message-thinking').length <= 0) {
            msg_container.find('.btn-toggle-message').remove();
        }
        msg_container.find('.spinner-grow').remove();
        await agentView.say.play(packet.wav_b64);
        agentView.message_id = null;
    };
    agentView.ws.onopen = () => {
        const ping = () => {
            agentView.ws.send('ping');
            agentView.chat_reconnect_count = 0; // pingが成功したら再接続回数をリセット
        };
        agentView.btn_say.prop('disabled', false);
        agentView.btn_user_msg.prop('disabled', false);
        agentView.btn_rec.prop('disabled', false);
        agentView.chat_callback_ping_handler = setInterval(() => {ping();}, ping_interval);
    };
    agentView.ws.onerror = (event) => {
        console.error(event);
        clearInterval(agentView.chat_callback_ping_handler);
    };
    agentView.ws.onclose = () => {
        clearInterval(agentView.chat_callback_ping_handler);
        if (agentView.chat_reconnect_count >= max_reconnect_count) {
            clearInterval(agentView.chat_reconnectInterval_handler);
            cmdbox.message({'error':'Connection to the agent has failed for several minutes. Please reload to resume reconnection.'});
            location.reload(true);
            return;
        }
        agentView.chat_reconnect_count++;
        agentView.chat_reconnectInterval_handler = setInterval(() => {
            agentView.chat(session_id);
        }, ping_interval);
    };
    cmdbox.hide_loading();
};
agentView.create_user_message = (msg) => {
    const msgDiv = $('<div/>').appendTo(agentView.chatMessages);
    msgDiv.addClass(`message message-user`);
    msgDiv.html(`
        <span class="msg-label msg-label-user">${agentView.user ? agentView.user['name'] : 'USER'}</span>
        <div class="msg-content">${msg}</div>
    `);
    agentView.scrollToBottom();
};
agentView.create_agent_message = (message_id) => {
    const msg_content = $(`#${message_id} .msg-content`);
    if (msg_content.length > 0) {
        return msg_content.last();
    }
    if ($(`#${message_id}`).length <= 0) {
        $(`<div id="${message_id}"/>`).appendTo(agentView.chatMessages);
    }
    const msgDiv = $(`#${message_id}`).addClass(`message message-agent`);
    msgDiv.html(`
        <span class="msg-label msg-label-agent">
            <button class="btn-toggle-message" title="Toggle message">▼</button>
            ${agentView.agent_runner ? agentView.agent_runner['agent'] : 'SYSTEM'}
        </span>
        <div class="msg-content"></div>
    `);
    msgDiv.find('.btn-toggle-message').off('click').on('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const content = msgDiv.find('.message-thinking');
        const btn = msgDiv.find('.btn-toggle-message');
        if (content.hasClass('collapsed')) {
            content.removeClass('collapsed');
            btn.text('▼');
        } else {
            content.addClass('collapsed');
            btn.text('▶');
        }
    });
    agentView.aiCoreText.css("textShadow", "0 0 30px #fff");
    setTimeout(() => {
        agentView.aiCoreText.css("textShadow", "0 0 20px var(--accent-cyan)");
    }, 500);
    agentView.scrollToBottom();
    return $(`#${message_id} .msg-content`).last();
}
agentView.format_agent_message =  async (txt, message) => {
    // メッセージが空の場合は何もしない
    if (!message || message.length <= 0) return;
    txt.html('');
    const regs_start = /```json/s;
    const regs_json = /```json(?!```)+/s;
    const regs_end = /```/s;
    while (message && message.length > 0) {
        try {
            // JSON開始部分を探す
            let start = message.match(regs_start);
            if (!start || start.length < 0) {
                // JSON開始部分が無い場合はそのまま表示
                const msg = message.replace(/\n/g, '<br/>');
                txt.append(msg);
                break;
            }
            start = message.substring(0, start.index);
            if (start) {
                const msg = start.replace(/\n/g, '<br/>');
                txt.append(msg);
            }
            message = message.replace(start+regs_start.source, '');

            // JSON内容部分を探す
            let jbody = message.match(regs_end);
            if (!jbody || jbody.length < 0) {
                // JSON内容部分が無い場合はそのまま表示
                const msg = message.replace(/\n/g, '<br/>');
                txt.append(msg);
                break;
            }
            jbody = message.substring(0, jbody.index);
            jobj = eval(`(${jbody})`);
            message = message.replace(jbody+regs_end.source, '');
            const rand = cmdbox.random_string(16);
            txt.append(`<span id="${rand}"/>`);
            agentView.recursive_json_parse(jobj);
            render_result_func(txt.find(`#${rand}`), jobj, 256);
            const th = txt.find(`.table .th:first`);
            if (th.length > 0) {
                const title = th.html();
                const content = th.parents('.table').parent().html();
                const th_txt = th.text();
                const span = $(`<span class="doc-link ms-1"><i class="fas fa-file-code me-1"></i>${th_txt}</span>`).prependTo(th.text(''));
                span.off('click').on('click', () => {
                    const message_id = txt.parents('.message').attr('id');
                    agentView.showDocument(title, content, message_id);
                });
            }
        } catch (e) {
            try {
                const msg = message.replace(/\n/g, '<br/>');
                txt.append(msg);
            } catch (e) {
                txt.append(`${e}`);
            }
            break;
        }
    }
    // メッセージ一覧を一番下までスクロール
    agentView.chatContainer.scrollTop(agentView.chatContainer.prop('scrollHeight'));
    const msg_width = agentView.chatMessages.prop('scrollWidth');
    if (msg_width > 800) {
        // メッセージ一覧の幅が800pxを超えたら、メッセージ一覧の幅を調整
        document.documentElement.style.setProperty('--cmdbox-width', `${msg_width}px`);
    }
};
agentView.recursive_json_parse = (jobj) => {
    Object.keys(jobj).forEach((key) => {
        if (!jobj[key]) return; // nullやundefinedは無視
        if (typeof jobj[key] === 'function') {
            delete jobj[key]; // 関数は削除
            return;
        }
        if (typeof jobj[key] === 'string') {
            try {
                const val = eval(`(${jobj[key]})`);
                if (val && typeof val === 'object' && !Array.isArray(val))
                    for (const v of Object.values(val))
                        if (v && typeof v === 'function') return; // 関数は無視
                else if (val && Array.isArray(val))
                    for (const v of val)
                        if (v && typeof v === 'function') return; // 関数は無視
                jobj[key] = val;
                agentView.recursive_json_parse(jobj[key]);
            } catch (e) {
                console.debug(`Fail parsing JSON string: ${jobj[key]}`, e);
            }
        }
        if (typeof jobj[key] === 'object' && !Array.isArray(jobj[key])) {
            // オブジェクトの場合は再帰的に処理
            agentView.recursive_json_parse(jobj[key]);
        }
    });
};

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
agentView.get_agent_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'agent_save');
    const vform_names = ['agent_name', 'agent_type',
                         'a2asv_baseurl', 'a2asv_delegated_auth', 'a2asv_apikey',
                         'llm', 'mcpservers', 'subagents',
                         'agent_description', 'agent_instruction'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_agent_form = async () => {
    const form = $('#form_agent_edit');
    form.empty();
    const defs = await agentView.get_agent_form_def();
    const model = $('#agent_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_agent = async () => {
    const container = $('#agent_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('agent', 'agent_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Agent list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No Agent configurations found.</div>');
            return;
        }

        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'agent_load', { agent_name: item.name });
            if (!res || !res.success) {
                $(`
                    <li class="sf-list-danger-item">
                        <div>
                            <span class="d-block glow-text-magenta system-font" style="font-size: 0.9em;">${item.name}</span>
                            <span class="text-white-50">${JSON.stringify(res)}</span>
                        </div>
                    </li>
                `).appendTo(container_ul);
                return;
            };
            const config = res.success || {};
            const itemEl = $(`
                <li class="sf-list-item" style="cursor: pointer;">
                    <div>
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.agent_name}</span>
                        <span class="text-white-50">${config.agent_description}</span>
                    </div>
                </li>
            `).appendTo(container_ul);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_agent_form();
                const form = $('#form_agent_edit');
                form.find('[name="agent_name"]').val(config.agent_name).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'agent_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (config[key]) {
                            if (Array.isArray(config[key]) && config[key].length > 1) {
                                config[key].slice(0,-1).forEach((v, i) => {
                                    const e = form.find(`[name="${key}"]`).parent().find('.add_buton')[i];
                                    $(e).click();
                                });
                            } else {
                                input.val(`${config[key]}`);
                            }
                        }
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_agent').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.agent_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'agent_del', { agent_name: config.agent_name });
                    $('#agent_edit_modal').modal('hide');
                    agentView.list_agent();
                });

                $('#agent_edit_modal').modal('show');
                // LLMリストをロード
                await cmdbox.callcmd('llm','list',{},(res)=>{
                    const val = $("[name='llm']").val();
                    $("[name='llm']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="llm"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="llm"]').val(config.llm);
                },$('[name="title"]').val(),'llm');
                // MCPサーバーリストをロード
                await cmdbox.callcmd('agent','mcpsv_list',{},(res)=>{
                    const val = $("[name='mcpservers']").val();
                    $("[name='mcpservers']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="mcpservers"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    config.mcpservers && config.mcpservers.forEach((v, i) => {
                        const e = form.find('[name="mcpservers"]')[i];
                        $(e).val(v);
                    });
                },$('[name="title"]').val(),'mcpservers');
                // SubAgentリストをロード
                await cmdbox.callcmd('agent','agent_list',{},(res)=>{
                    $("[name='subagents']").empty().append('<option></option>');
                    res['data'].map(elm=>{
                        if (elm["name"] === $('[name="agent_name"]').val()) return;
                        $('[name="subagents"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');
                    });
                    config.subagents && config.subagents.forEach((v, i) => {
                        const e = form.find('[name="subagents"]')[i];
                        $(e).val(v);
                    });
                },$('[name="title"]').val(),'subagents');
            });
            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_agent = async () => {
    const form = $('#form_agent_edit');
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
        const res = await agentView.exec_cmd('agent', 'agent_save', data);
        if (res && res.success) {
            $('#agent_edit_modal').modal('hide');
            agentView.list_agent();
        } else {
            alert('Failed to save Agent settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agentView.get_llm_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('llm', 'save');
    const vform_names = ['llmname', 'llmprov', 'llmapikey', 'llmendpoint', 'llmmodel', 'llmapiversion',
                        'llmprojectid', 'llmsvaccountfile', 'llmlocation', 'llmtemperature', 'llmseed'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_llm_form = async () => {
    const form = $('#form_llm_edit');
    form.empty();
    const defs = await agentView.get_llm_form_def();
    const model = $('#llm_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agentView.list_llm = async () => {
    const container = $('#llm_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agentView.exec_cmd('llm', 'list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load LLM list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No LLM configurations found.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('llm', 'load', { llmname: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.llmname}</span>
                        <span class="text-white-50">${config.llmprov} / ${config.llmmodel}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_llm_form();
                const form = $('#form_llm_edit');
                form.find('[name="llmname"]').val(config.llmname).prop('readonly', true);

                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'llmname') return;
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
                $('#btn_del_llm').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.llmname}'?`)) return;
                    await agentView.exec_cmd('llm', 'del', { llmname: config.llmname });
                    $('#llm_edit_modal').modal('hide');
                    agentView.list_llm();
                });

                $('#llm_edit_modal').modal('show');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_llm = async () => {
    const form = $('#form_llm_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agentView.exec_cmd('llm', 'save', data);
        if (res && res.success) {
            $('#llm_edit_modal').modal('hide');
            agentView.list_llm();
        } else {
            alert('Failed to save LLM settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

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
        memory_performance.text(`${(data[0]['my_cnt'] / data[0]['all_cnt'] * 100).toFixed(2)} %` || '---');
    } catch (e) {
        console.error('Error loading memory status:', e);
    } finally {
        cmdbox.hide_loading();
    }
};

agentView.get_mcpsv_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'mcpsv_save');
    const vform_names = ['mcpserver_name', 'mcpserver_url', 'mcpserver_delegated_auth', 'mcpserver_apikey',
                         'mcpserver_transport', 'mcp_tools'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agentView.build_mcpsv_form = async () => {
    const form = $('#form_mcpsv_edit');
    form.empty();
    const defs = await agentView.get_mcpsv_form_def();
    const model = $('#mcpsv_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};
agentView.list_mcpsv = async () => {
    const container = $('#mcpsv_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    
    try {
        const res = await agentView.exec_cmd('agent', 'mcpsv_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load MCPSV list.</div>');
            console.warn(res);
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="p-3">No MCPSV connections found.</div>');
            return;
        }
        const container_ul = $(`<ul class="sf-list-group"/>`).appendTo(container);
        list.forEach(async item => {
            const res = await agentView.exec_cmd('agent', 'mcpsv_load', { mcpserver_name: item.name });
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
                        <span class="d-block glow-text-cyan system-font" style="font-size: 0.9em;">${config.mcpserver_name}</span>
                        <span class="text-white-50">${config.mcpserver_url}</span>
                    </div>
                </li>
            `).appendTo(container_ul);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agentView.build_mcpsv_form();
                const form = $('#form_mcpsv_edit');
                form.find('[name="mcpserver_name"]').val(config.mcpserver_name).prop('readonly', true);
                
                // 各フィールドに値をセット
                Object.keys(config).forEach(key => {
                    if (key === 'mcpserver_name') return;
                    const input = form.find(`[name="${key}"]`);
                    if (input.length > 0) {
                        if (config[key]) input.val(`${config[key]}`);
                    }
                });
                // 選択肢による表示非表示の設定
                form.find(`.choice_show`).each((i, elem) => {
                    const input_elem = $(elem);
                    input_elem.change();
                });
                // Delete button handler
                $('#btn_del_mcpsv').show().off('click').on('click', async () => {
                    if (!confirm(`Are you sure you want to delete '${config.mcpserver_name}'?`)) return;
                    await agentView.exec_cmd('agent', 'mcpsv_del', { mcpserver_name: config.mcpserver_name });
                    $('#mcpsv_edit_modal').modal('hide');
                    agentView.list_mcpsv();
                });

                $('#mcpsv_edit_modal').modal('show');
                // コマンド実行
                const user = await cmdbox.user_info();
                let apikey = $('[name="mcpserver_apikey"]').val();
                if (!apikey && user && user['apikeys']) {
                    const keys = Object.keys(user['apikeys']);
                    if (keys.length > 0) apikey = user['apikeys'][keys[0]][0];
                }
                await cmdbox.callcmd('agent','mcp_client',{
                    'mcpserver_url':$('[name="mcpserver_url"]').val(),
                    'mcpserver_apikey':apikey,
                    'mcpserver_transport':$('[name="mcpserver_transport"]').val(),
                    'operation':'list_tools',
                },(res)=>{
                    $("[name='mcp_tools']").empty().append('<option></option>');
                    res.map(elm=>{$('[name="mcp_tools"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="mcp_tools"]').val(config.mcpserver_mcp_tools);
                },$('[name="title"]').val(),'mcp_tools');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agentView.save_mcpsv = async () => {
    const form = $('#form_mcpsv_edit');
    const data = {};
    form.find(':input').each((i, elem) => {
        const val = $(elem).val();
        if (val) data[elem.name] = val;
    });

    try {
        const res = await agentView.exec_cmd('agent', 'mcpsv_save', data);
        if (res && res.success) {
            $('#mcpsv_edit_modal').modal('hide');
            agentView.list_mcpsv();
        } else {
            alert('Failed to save MCPSV settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agentView.get_runner_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'runner_save');
    const vform_names = ['runner_name', 'agent', 'session_store_type', 'session_store_pghost',
                        'session_store_pgport', 'session_store_pguser', 'session_store_pgpass', 'session_store_pgdbname',
                        'memory', 'tts_engine', 'voicevox_model'];
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
                },$('[name="title"]').val(),'agent');
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
            li.on('click', async () => { agentView.select_runner(config.runner_name); });
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
        // HISTORIESボタンも有効化
        agentView.btn_histories.prop('disabled', false).css('opacity', '1').css('cursor', 'pointer');
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

agentView.get_rag_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('rag', 'save');
    const vform_names = ['rag_name', 'rag_type', 'source_dir', 'extract', 'embed',
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
                        <span class="text-white-50">${config.rag_type} / ${config.vector_store_type}</span>
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
                // コマンド実行
                await cmdbox.callcmd('embed','list',{},(res)=>{
                    $("[name='embed']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="embed"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="embed"]').val(config.embed);
                },$('[name="title"]').val(),'embed');

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

agentView.cell_chop = (val, res_size) => {
    val = `${val || ''}`;
    res_size = res_size ? res_size : 150;
    if(val && res_size>0 && val.length > res_size){
        return `${val.substring(0, res_size)}...`;
    }
    return val;
};

agentView.create_history = (session_id, runner_name, user_name, update_time, msg) => {
    if (agentView.chatHistories.find(`#${session_id}`).length > 0) return;
    msg = agentView.cell_chop(msg, 300);
    const li = $(`<li id="${session_id}" class="d-flex sf-list-item"/>`).appendTo(agentView.chatHistories);
    const div1 = $(`<div class="d-inline-block"/>`).appendTo(li);
    const head = $(`<span class="d-block glow-text-cyan system-font" style="font-size: 1em;"></span>`).appendTo(div1);
    head.html(`${update_time instanceof Date ? update_time.toLocaleString() : update_time} - ${runner_name} - ${user_name}`);
    const body = $(`<span class="text-white-50"></span>`).appendTo(div1);
    body.html(msg);
    const div2 = $(`<div class="d-inline-block"/>`).appendTo(li);
    const btn_del = $(`<button class="btn btn-danger ms-auto">Delete</button>`).appendTo(div2);
    btn_del.off('click').on('click',(e)=>{
        if (!window.confirm('Are you sure you want to delete this session?')) return;
        // セッション削除ボタンのクリックイベント
        e.preventDefault();
        e.stopPropagation();
        agentView.delete_session(session_id).then(async (res) => {
            li.remove();
            const sid = agentView.chatMessages.attr('data-session_id');
            if (sid == session_id) {
                // 削除したセッションが現在のセッションだった場合は、メッセージ一覧をクリア
                agentView.chatMessages.html('');
                agentView.ws && agentView.ws.close();
                agentView.chat(cmdbox.random_string(16));
            }
            await agentView.list_sessions();
        });
    });
    li.off('click').on('click', async (e) => {
        // セッションを選択したときの処理
        e.preventDefault();
        agentView.ws && agentView.ws.close();
        agentView.chat(session_id);
        const data = await agentView.list_sessions(session_id);
        if (data.length<=0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        const session = data[0];
        if (!session['events'] || session['events'].length <= 0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        agentView.chatMessages.html('');
        for (const event of session['events']) {
            if (!event['text'] || event['text'].length <= 0) continue;
            if (event['author'] == 'user') {
                // ユーザーメッセージ
                agentView.create_user_message(event['text']);
            } else {
                // エージェントメッセージ
                txt = agentView.create_agent_message(cmdbox.random_string(16));
                await agentView.format_agent_message(txt, event['text']);
            }
        }
    });
    return li;
};
agentView.delete_session = async (session_id) => {
    const runner_name = agentView.agent_runner ? agentView.agent_runner['runner_name'] : null;
    if (!runner_name || runner_name.length <= 0) return;
    return agentView.exec_cmd('agent', 'session_del', {
        'runner_name': runner_name,
        'session_id': session_id
    });
}

agentView.say = {};
agentView.say.isStart = () => {
    const icon = agentView.btn_say.find('i');
    return agentView.btn_say.hasClass('say_on') && icon.hasClass('fa-volume-up');
};
agentView.say.say = (tts_text) => {
    if (!agentView.say.isStart()) return;
    return agentView.exec_cmd('tts', 'say', {
        'tts_engine': 'voicevox',
        'voicevox_model': agentView.agent_runner.voicevox_model || 'ずんだもんノーマル',
        'tts_text': tts_text.replace(/<br\s*\/?>/g, '\n') // <br>タグを改行に変換
    }).then(async (data) => {
        if (!data['success']) throw data;
        await agentView.say.play(data['success']['data']);
    });
};
agentView.say.play = async (wav_b64) => {
    if (!wav_b64 || wav_b64.length <= 0) return;
    // 発話中のエフェクトを表示
    const aicore = $('.ai-core');
    aicore.css('box-shadow', '0 0 200px var(--area-bg-color-50)');
    aicore.css('animation', 'pulse 1.3s ease-in-out infinite');
    // 音声データを再生
    const binary_string = window.atob(wav_b64);
    const bytesArray  = new Uint8Array(binary_string.length);
    for (let i = 0; i < binary_string.length; i++) {
        bytesArray[i] = binary_string.charCodeAt(i);
    }
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(bytesArray.buffer);
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.onended = () => {
        audioContext.close();
        aicore.css('box-shadow', '');
        aicore.css('animation', '');
    }
    source.start(0);
};