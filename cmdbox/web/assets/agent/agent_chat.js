agentView.scrollToBottom = () => {
    agentView.chatContainer.scrollTop(agentView.chatContainer.prop("scrollHeight"));
};
agentView.chat_listeners = [];
/**
 * チャットメッセージを送信
 * @param {WebSocket} ws WebSocketオブジェクト
 * @param {string} msg 送信メッセージ
 */
agentView.chat_send = (ws, msg) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(msg);
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
            cmdbox.message({'warn':'The connection to the runner has not yet been established.'}, true);
            return;
        }
        // メッセージを送信
        agentView.chat_send(agentView.ws, msg);
        $('.ai-core').addClass('ai-core2');
        // メッセージ一覧を一番下までスクロール
        agentView.chatContainer.scrollTop(agentView.chatContainer.prop('scrollHeight'));
    });
    // recボタンのクリックイベント
    const rec_handler = async () => {
        agentView.rec_set();
        // 録音を終了
        if (!agentView.btn_rec.prop('checked')) {
            // 録音中を停止
            if (agentView.recognition) {
                agentView.recognition.stop();
                const transcript = agentView.user_msg.val();
                transcript && agentView.btn_user_msg.click(); // 録音が終了したら自動的にメッセージを送信
            }
            agentView.rec_off();
            return;
        }
        // 録音を開始
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        if (!SpeechRecognition) {
            cmdbox.message({'error':'Speech Recognition API is not supported in this browser.'}, true);
            agentView.rec_off();
            return;
        }
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
            agentView.rec_off();
            cmdbox.message({'error':`Speech Recognition error: ${event.error}`}, true);
        };
        agentView.recognition.onend = () => {
            // 連続認識を無効にしているので、認識が終了したら再稼働させる。
            console.log(`onend event triggered.`);
            agentView.recognition.restart();
        };
        agentView.recognition.restart = () => {
            if (agentView.btn_rec.prop('checked')) {
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
    };
    agentView.btn_rec.off('click').on('click', rec_handler);
    rec_handler();
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
        if (packet && packet['end']) {
            agentView.message_id = null;
            console.log(packet);
            return;
        }
        let msg_container = $(`#${agentView.message_id}`);
        if (!agentView.message_id || msg_container.length <= 0) {
            // エージェント側の表示枠が無かったら追加
            agentView.message_id = cmdbox.random_string(16);
        }
        // チャットリスナーにメッセージを渡す
        agentView.chat_listeners && agentView.chat_listeners.forEach(listener => listener(packet));
        if (packet && packet['warn']) {
            console.log(packet);
            const txt = agentView.create_agent_message(agentView.message_id);
            await agentView.format_agent_message(txt, `${packet['warn']}`);
            agentView.message_id = null;
            return;
        }
        const success = packet && packet['success'] || {};
        const hasStructured = !!(
            (success.function_calls && success.function_calls.length > 0) ||
            (success.function_responses && success.function_responses.length > 0) ||
            (success.artifact_delta && Object.keys(success.artifact_delta).length > 0) ||
            (success.artifacts && success.artifacts.length > 0)
        );
        if (success.flags && success.flags.turn_complete && !success.message && !hasStructured) {
            agentView.message_id = null;
            return;
        }
        if ((!success.message || success.message.length <= 0) && !hasStructured) {
            agentView.message_id = null;
            return;
        }
        console.log(packet);
        if (success.flags && !success.flags['final_response']) {
            // 「考え中」を表示
            if (agentView.message_id==null) {
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
            const msg_str = agentView.parse_message(success.message);
            await agentView.format_agent_message(msg_content, msg_str, success);
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
        const msg_str = agentView.parse_message(success.message);
        await agentView.format_agent_message(msg_content, msg_str, success);
        if (msg_container.find('.message-thinking').length <= 0) {
            msg_container.find('.btn-toggle-message').remove();
        }
        msg_container.find('.spinner-grow').remove();
        await agentView.say.play(success.wav_b64);
        agentView.message_id = null;
        // 読み込み中のスピナーを削除
        $('.msg-content').each((index, element) => {
            const content_elem = $(element);
            if (content_elem.children('.spinner-grow').length > 0) {
                content_elem.remove();
            }
        });
    };
    agentView.ws.onopen = () => {
        const ping = () => {
            agentView.chat_send(agentView.ws, 'ping');
            agentView.chat_reconnect_count = 0; // pingが成功したら再接続回数をリセット
        };
        agentView.btn_say.prop('disabled', false);
        agentView.btn_user_msg.prop('disabled', false);
        agentView.btn_rec.prop('disabled', false);
        agentView.chat_callback_ping_handler = setInterval(() => {ping();}, ping_interval);
        agentView.say_init();
        agentView.rec_init();
        agentView.reasoning_init();
    };
    agentView.ws.onerror = (event) => {
        console.error(event);
        clearInterval(agentView.chat_callback_ping_handler);
    };
    agentView.ws.onclose = () => {
        clearInterval(agentView.chat_callback_ping_handler);
        if (agentView.chat_reconnect_count >= max_reconnect_count) {
            clearInterval(agentView.chat_reconnectInterval_handler);
            cmdbox.message({'error':'Connection to the agent has failed for several minutes. Please reload to resume reconnection.'}, true);
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
agentView.parse_message = (message) => {
    if (!message || message.length <= 0) return '';
    try {
        message = message.trim();
        const msg_json = JSON.parse(message);
        const ret = [];
        const escapeHtml = (value) => {
            if (value === null || value === undefined) return '';
            return String(value)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        };
        const jsonToTable = (value) => {
            if (value === null || value === undefined) {
                return '<span class="text-muted">null</span>';
            }
            if (Array.isArray(value)) {
                if (value.length <= 0) {
                    return '<span class="text-muted">[]</span>';
                }
                if (typeof value[0] === 'object') {
                    const keys = Object.keys(value[0]);
                    const cols = keys.map((key) => {
                        return `<th class="th">${escapeHtml(key)}</th>`;
                    }).join('');
                    const rows = value.map((item, index) => {
                        const tds = keys.map((key) => {
                            return `<td>${jsonToTable(item[key])}</td>`;
                        }).join('');
                        return `<tr>${tds}</tr>`;
                    }).join('');
                    return `<table class="table table-sm table-bordered align-middle mb-2"><thead><tr>${cols}</tr></thead><tbody>${rows}</tbody></table>`;
                }
                if (value.length <= 1) {
                    return `<span>${escapeHtml(value[0])}</span>`;
                }
                const rows = value.map((item, index) => {
                    return `<tr><th class="th">${index}</th><td>${jsonToTable(item)}</td></tr>`;
                }).join('');
                return `<table class="table table-sm table-bordered align-middle mb-2"><tbody>${rows}</tbody></table>`;
            }
            if (typeof value === 'object') {
                const keys = Object.keys(value);
                if (keys.length <= 0) {
                    return '<span class="text-muted">{}</span>';
                }
                const cols = keys.map((key) => {
                    return `<th class="th">${escapeHtml(key)}</th>`;
                }).join('');
                const rows = keys.map((key) => {
                    return `<td>${jsonToTable(value[key])}</td>`;
                }).join('');
                return `<table class="table table-sm table-bordered align-middle mb-2"><thead><tr>${cols}</tr></thead><tbody><tr>${rows}</tr></tbody></table>`;
            }
            return `<span>${escapeHtml(value)}</span>`;
        };
        const rep = (str) => {
            str = str.replace(/\\n/g, '\n').replace(/\\t/g, '\t').replace(/\\r/g, '');
            const elem = $(str);
            elem.each((index, element) => {
                const el = $(element);
                el.html(marked.parse(el.html()));
            });
            if (elem.length > 0) str = elem.prop('outerHTML');
            return str;
        };
        msg_json && msg_json['message'] && ret.push(`${rep(msg_json['message'])}\n`);
        msg_json && msg_json['command'] && (ret.push(`**Command:**`) && ret.push(`- ${rep(msg_json['command'])}\n`));
        if (msg_json && msg_json['parameters_json'] && msg_json['parameters_json'] !== '{}') {
            try {
                const obj = JSON.parse(msg_json['parameters_json']);
                ret.push('**Parameters:**');
                ret.push(`<div class="json-table-wrap">${jsonToTable(obj)}</div>`);
            } catch (e) {
                ret.push('**Parameters:**');
                ret.push(`<div class="json-table-wrap"><pre>${escapeHtml(msg_json['parameters_json'])}</pre></div>`);
            }
        }
        if (msg_json && msg_json['result_json']) {
            try {
                const obj = JSON.parse(msg_json['result_json']);
                ret.push('**Result:**');
                ret.push(`<div class="json-table-wrap">${jsonToTable(obj)}</div>`);
            } catch (e) {
                ret.push('**Result:**');
                ret.push(`<div class="json-table-wrap"><pre>${escapeHtml(msg_json['result_json'])}</pre></div>`);
            }
        }
        msg_json && msg_json['error'] && (ret.push(`**Error:**`) && ret.push(`- ${rep(msg_json['error'])}\n`));
        return ret.join('\n');
    } catch (error) {
        return message;
    }
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
agentView.format_agent_message =  async (txt, message, success = null) => {
    // メッセージが空の場合は何もしない
    if ((!message || message.length <= 0) && !success) return;
    txt.html('');
    if (message && message.length > 0) {
        try {
            const msg_html = marked.parse(message);
            txt.append(msg_html);
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
                const msg_html = marked.parse(message);
                txt.append(msg_html);
            } catch (e) {
                txt.append(`${e}`);
            }
        }
    }
    agentView.render_structured_event(txt, success);
    // メッセージ一覧を一番下までスクロール
    agentView.chatContainer.scrollTop(agentView.chatContainer.prop('scrollHeight'));
    const msg_width = agentView.chatMessages.prop('scrollWidth');
    if (msg_width > 800) {
        // メッセージ一覧の幅が800pxを超えたら、メッセージ一覧の幅を調整
        document.documentElement.style.setProperty('--cmdbox-width', `${msg_width}px`);
    }
};

agentView.render_structured_event = (txt, success) => {
    if (!success) return;
    const payload = {};
    if (success.function_calls && success.function_calls.length > 0) {
        payload.function_calls = success.function_calls;
    }
    if (success.function_responses && success.function_responses.length > 0) {
        payload.function_responses = success.function_responses;
    }
    if (success.artifact_delta && Object.keys(success.artifact_delta).length > 0) {
        payload.artifact_delta = success.artifact_delta;
    }
    if (success.artifacts && success.artifacts.length > 0) {
        payload.artifacts = success.artifacts;
    }
    if (Object.keys(payload).length <= 0) return;

    const rand = cmdbox.random_string(16);
    txt.append(`<div class="mt-2"><span id="${rand}"></span></div>`);
    render_result_func(txt.find(`#${rand}`), payload, 256);
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
agentView.say.source = null;
agentView.say.audioContext = null;
agentView.say.isStart = () => {
    return agentView.btn_say.prop('checked');
};
agentView.say.isPlaying = () => {
    return agentView.say.source !== null && agentView.say.audioContext !== null;
};
agentView.say.stop = () => {
    if (agentView.say.source) {
        try {
            agentView.say.source.stop();
        } catch (e) {
            console.debug('Failed to stop audio source:', e);
        }
    }
    if (agentView.say.audioContext) {
        try {
            agentView.say.audioContext.close();
        } catch (e) {
            console.debug('Failed to close audio context:', e);
        }
    }
    agentView.say.source = null;
    agentView.say.audioContext = null;
    const aicore = $('.ai-core');
    aicore.css('box-shadow', '');
    aicore.css('animation', '');
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
    // 前の再生を停止
    if (agentView.say.isPlaying()) {
        agentView.say.stop();
    }
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
        agentView.say.source = null;
        agentView.say.audioContext = null;
        aicore.css('box-shadow', '');
        aicore.css('animation', '');
        try {
            audioContext.close();
        } catch (e) {
            console.debug('Failed to close audio context:', e);
        }
    }
    agentView.say.source = source;
    agentView.say.audioContext = audioContext;
    source.start(0);
};
