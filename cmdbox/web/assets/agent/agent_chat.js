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
