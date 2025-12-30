const agent = {};
agent.chat_reconnectInterval_handler = null;
agent.chat_callback_ping_handler = null;
agent.create_user_message = (messages, msg) => {
    const user_msg_row = $(`<div class="message" style="float:right;"></div>`).appendTo(messages);
    const user_message = $(`<div class="message user-message d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(user_msg_row);
    $(`<div class="d-inline-block"></div>`).appendTo(user_message).text(msg);
    $(`<a class="d-inline-block align-top" style="fill:gray;"><svg class="align-top ms-3" width="32" height="32" viewBox="0 0 16 16">`
        +`<use href="#svg_signin_ico"></use></svg></a>`).appendTo(user_msg_row);
};
agent.create_agent_message = (messages, message_id) => {
    if ($(`#${message_id}`).length > 0) {
        return $(`#${message_id}`);
    }
    const bot_message = $(`<div class="message bot-message"></div>`).appendTo(messages);
    $(`<img class="icon-logo align-top me-3" src="${cmdbox.logoicon_src}" width="32" height="32"/>`).appendTo(bot_message);
    const txt = $(`<div id="${message_id}" class="d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(bot_message);
    return txt;
}
agent.format_agent_message =  async (container, messages, txt, message) => {
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
                agent.say.say(msg);
                txt.append(msg);
                break;
            }
            start = message.substring(0, start.index);
            if (start) {
                const msg = start.replace(/\n/g, '<br/>');
                agent.say.say(msg);
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
            agent.recursive_json_parse(jobj);
            render_result_func(txt.find(`#${rand}`), jobj, 256);
        } catch (e) {
            const msg = message.replace(/\n/g, '<br/>');
            txt.append(msg);
            break;
        }
    }
    // メッセージ一覧を一番下までスクロール
    container.scrollTop(container.prop('scrollHeight'));
    const msg_width = messages.prop('scrollWidth');
    if (msg_width > 800) {
        // メッセージ一覧の幅が800pxを超えたら、メッセージ一覧の幅を調整
        document.documentElement.style.setProperty('--cmdbox-width', `${msg_width}px`);
    }
};
agent.recursive_json_parse = (jobj) => {
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
                agent.recursive_json_parse(jobj[key]);
            } catch (e) {
                console.debug(`Fail parsing JSON string: ${jobj[key]}`, e);
            }
        }
        if (typeof jobj[key] === 'object' && !Array.isArray(jobj[key])) {
            // オブジェクトの場合は再帰的に処理
            agent.recursive_json_parse(jobj[key]);
        }
    });
};
agent.say = {};
agent.say.model = 'ずんだもんノーマル';
agent.say.start = async ()=> {
    const data = await agent.exec_cmd('agent', 'runner_load', {runner_name: $('#runner_name_input').val()});
    if (data && data.success) {
        agent.say.model = data.success.voicevox_model || 'ずんだもんノーマル';
    }
    return agent.exec_cmd('tts', 'start', {'tts_engine': 'voicevox', 'voicevox_model': agent.say.model}).then((data) => {
        if (!data['success']) throw data['warn'] || data;
        return data['success'];
    });
};
agent.say.stop = async () => {
    return agent.exec_cmd('tts', 'stop', {'tts_engine': 'voicevox', 'voicevox_model': agent.say.model}).then((data) => {
        if (!data['success']) throw data['warn'] || data;
        return data['success'];
    });
};
agent.say.isStart = () => {
    const btn_say = $('#btn_say');
    return btn_say.hasClass('say_on')
};
agent.say.say = (tts_text) => {
    if (!agent.say.isStart()) return;
    return agent.exec_cmd('tts', 'say', {
        'tts_engine': 'voicevox',
        'voicevox_model': agent.say.model,
        'tts_text': tts_text.replace(/<br\s*\/?>/g, '\n') // <br>タグを改行に変換
    }).then(async (data) => {
        if (!data['success']) throw data;
        // 音声データを再生
        const binary_string = window.atob(data['success']['data']);
        const bytesArray  = new Uint8Array(binary_string.length);
        for (let i = 0; i < binary_string.length; i++) {
            bytesArray[i] = binary_string.charCodeAt(i);
        }
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioContext.decodeAudioData(bytesArray.buffer);
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.start(0);
    });
};
agent.init_form = async () => {
    const container = $('#message_container');
    const histories = $('#histories');
    const messages = $('#messages');
    const ping_interval = 5000; // pingの間隔
    const max_reconnect_count = 60000/ping_interval*1; // 最大再接続回数
    agent.chat_reconnect_count = 0;
    agent.chat = (session_id) => {
        cmdbox.show_loading();
        // ws再接続のためのインターバル初期化
        if (agent.chat_reconnectInterval_handler) {
            clearInterval(agent.chat_reconnectInterval_handler);
        }
        // wsのpingのためのインターバル初期化
        if (agent.chat_callback_ping_handler) {
            clearInterval(agent.chat_callback_ping_handler);
        }
        messages.attr('data-session_id', session_id);
        const btn_say = $('#btn_say');
        const btn_user_msg = $('#btn_user_msg');
        const btn_rec = $('#btn_rec');
        const user_msg = $('#user_msg');
        agent.message_id = null;
        btn_user_msg.prop('disabled', true); // 初期状態で送信ボタンを無効化
        // 送信ボタンのクリックイベント
        btn_user_msg.off('click').on('click', async () => {
            const msg = user_msg.val();
            if (msg.length <= 0) return;
            user_msg.val('');
            // 入力内容をユーザーメッセージとして表示
            agent.create_user_message(messages, msg);
            agent.create_history(histories, session_id, msg);
            // エージェント側のメッセージ読込中を表示
            if (!agent.message_id) {
                agent.message_id = cmdbox.random_string(16);
                const txt = agent.create_agent_message(messages, agent.message_id);
                cmdbox.show_loading(txt);
            }
            if (!agent.ws) {
                cmdbox.message({'warn':'The connection to the runner has not yet been established.'});
                return;
            }
            // メッセージを送信
            agent.ws.send(msg);
            // セッション一覧を再表示
            agent.list_sessions();
            // メッセージ一覧を一番下までスクロール
            container.scrollTop(container.prop('scrollHeight'));
        });
        // sayボタンのクリックイベント
        btn_say.off('click').on('click', async () => {
            if (agent.say.isStart()) {
                await agent.say.stop().then((msg) => {
                    btn_say.removeClass('say_on');
                    btn_say.find('use').attr('href', '#btn_megaphone');
                }).catch((err) => {
                    cmdbox.message(err);
                    err = err['warn'] || err;
                    if (err.startsWith('VoiceVox model is not running:')) {
                        btn_say.removeClass('say_on');
                        btn_say.find('use').attr('href', '#btn_megaphone');
                    }
                });
                return;
            }
            await agent.say.start().then((msg) => {
                agent.say.say(msg);
                btn_say.addClass('say_on');
                btn_say.find('use').attr('href', '#btn_megaphone_fill');
            }).catch((err) => {
                cmdbox.message(err);
                err = err['warn'] || err;
                if (err.startsWith('VoiceVox model is already running:')) {
                    btn_say.addClass('say_on');
                    btn_say.find('use').attr('href', '#btn_megaphone_fill');
                }
            });
        });
        // recボタンのクリックイベント
        btn_rec.off('click').on('click', async () => {
            // 録音を終了
            if (btn_rec.hasClass('rec_on')) {
                btn_rec.removeClass('rec_on');
                btn_rec.find('use').attr('href', '#btn_mic');
                // 録音中を停止
                if (agent.recognition) {
                    agent.recognition.stop();
                    const transcript = user_msg.val();
                    transcript && btn_user_msg.click(); // 録音が終了したら自動的にメッセージを送信
                }
                return;
            }
            // 録音を開始
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            if (!SpeechRecognition) {
                cmdbox.message({'error':'Speech Recognition API is not supported in this browser.'});
                return;
            }
            btn_rec.addClass('rec_on');
            btn_rec.find('use').attr('href', '#btn_mic_fill');
            let finalTranscript = user_msg.val();
            agent.recognition = new SpeechRecognition();
            agent.recognition.lang = 'ja-JP'; // 言語設定
            agent.recognition.interimResults = true; // 中間結果を取得する
            agent.recognition.maxAlternatives = 1; // 最小の候補数
            agent.recognition.continuous = false; // 連続認識を無効にする
            agent.recognition.onresult = (event) => {
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
                user_msg.val(finalTranscript + interimTranscript);
            };
            agent.recognition.onerror = (event) => {
                console.error(`Speech Recognition error: ${event.error}`);
                if (event.error === 'no-speech') {
                    agent.recognition.restart();
                    return; // no-speechエラーは無視して再度認識を開始
                }
                btn_rec.removeClass('rec_on');
                btn_rec.find('use').attr('href', '#btn_mic');
                cmdbox.message({'error':`Speech Recognition error: ${event.error}`});
            };
            agent.recognition.onend = () => {
                // 連続認識を無効にしているので、認識が終了したら再稼働させる。
                console.log(`onend event triggered.`);
                agent.recognition.restart();
            };
            agent.recognition.restart = () => {
                if (btn_rec.hasClass('rec_on')) {
                    setTimeout(() => {
                        try {
                            agent.recognition.start();
                        } catch (error) {
                            console.error(`Error restarting recognition: ${error}`);
                        }
                    }, 100);
                }
            };
            agent.recognition.start();
        });
        // ws接続
        const protocol = window.location.protocol.endsWith('s:') ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = window.location.port;
        const path = window.location.pathname;
        const runner_name = $('#runner_name_input').val();
        cmdbox.hide_loading();
        if (!runner_name || runner_name.length <= 0) return;
        if (agent.ws && agent.ws.readyState === WebSocket.OPEN) return;
        cmdbox.show_loading();
        if (agent.ws) agent.ws.close();
        agent.ws = new WebSocket(`${protocol}://${host}:${port}${path}/chat/ws/${runner_name}/${session_id}`);
        // エージェントからのメッセージ受信時の処理
        agent.ws.onmessage = async (event) => {
            const packet = JSON.parse(event.data);
            if (!agent.message_id || $(`#${agent.message_id}`).length <= 0) {
                // エージェント側の表示枠が無かったら追加
                agent.message_id = cmdbox.random_string(16);
            }
            if (packet && packet['warn']) {
                const txt = agent.create_agent_message(messages, agent.message_id);
                await agent.format_agent_message(container, messages, txt, `${packet['warn']}`);
                agent.message_id = null;
                return;
            }
            if (packet.turn_complete) {
                agent.message_id = null;
                return;
            }
            if (!packet.message || packet.message.length <= 0) {
                agent.message_id = null;
                return;
            }
            console.log(packet);
            let txt = agent.create_agent_message(messages, agent.message_id);
            await agent.format_agent_message(container, messages, txt, packet.message);
            agent.message_id = null;
        };
        agent.ws.onopen = () => {
            const ping = () => {
                agent.ws.send('ping');
                agent.chat_reconnect_count = 0; // pingが成功したら再接続回数をリセット
            };
            btn_say.prop('disabled', false);
            btn_user_msg.prop('disabled', false);
            btn_rec.prop('disabled', false);
            agent.chat_callback_ping_handler = setInterval(() => {ping();}, ping_interval);
        };
        agent.ws.onerror = (event) => {
            console.error(event);
            clearInterval(agent.chat_callback_ping_handler);
        };
        agent.ws.onclose = () => {
            clearInterval(agent.chat_callback_ping_handler);
            if (agent.chat_reconnect_count >= max_reconnect_count) {
                clearInterval(agent.chat_reconnectInterval_handler);
                cmdbox.message({'error':'Connection to the agent has failed for several minutes. Please reload to resume reconnection.'});
                location.reload(true);
                return;
            }
            agent.chat_reconnect_count++;
            agent.chat_reconnectInterval_handler = setInterval(() => {
                agent.chat(session_id);
            }, ping_interval);
        };
        cmdbox.hide_loading();
    };
    const user_msg = $('#user_msg');
    user_msg.off('keydown').on('keydown', (e) => {
        // Ctrl+Enterで送信
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            $('#btn_user_msg').click();
            container.css('height', `calc(100% - ${user_msg.prop('scrollHeight')}px - 42px)`);
            return
        }
    });
    user_msg.off('input').on('input', (e) => {
        // テキストエリアのリサイズに合わせてメッセージ一覧の高さを調整
        container.css('height', `calc(100% - ${user_msg.prop('scrollHeight')}px - 42px)`);
    });
    const btn_newchat = $('#btn_newchat');
    btn_newchat.off('click').on('click', async () => {
        // メッセージ一覧をクリア
        messages.html('');
        // 新しいセッションを作成
        agent.ws && agent.ws.close();
        agent.chat(cmdbox.random_string(16));
    });
    // テキストエリアのリサイズに合わせてメッセージ一覧の高さを調整
    container.scrollTop(container.prop('scrollHeight'));
    // runnnerリストを更新
    await agent.update_runner_list();
    // 新しいセッションでチャットを開始
    agent.chat(cmdbox.random_string(16));
};
agent.list_sessions = async (session_id) => {
    const runner_name = $('#runner_name_input').val();
    if (!runner_name || runner_name.length <= 0) return [];
    const res = await agent.exec_cmd('agent', 'session_list', {
        'runner_name': runner_name,
        'session_id': session_id
    });
    const histories = $('#histories');
    if (!res || !res['success']) return [];
    if (!res['success']['data'] || typeof res['success']['data'] !== 'object') return [];
    if (session_id) return res['success']['data'];
    histories.html('');
    res['success']['data'].forEach(async (row) => {
        if (!row['events'] || row['events'].length <= 0) return;
        const msg = row['events'][0]['text'];
        const history = agent.create_history(histories, row['session_id'], msg);
    });
}
agent.create_history = (histories, session_id, msg) => {
    if (histories.find(`#${session_id}`).length > 0) return;
    msg = cell_chop(msg, 300);
    const history = $(`<a id="${session_id}" href="#" class="history pt-2 pb-1 d-block btn_hover"></a>`).prependTo(histories);
    $(`<span class="d-inline-block align-top ms-2 me-2" style="fill:gray;"><svg class="align-top" width="24" height="24" viewBox="0 0 16 16">`
        +`<use href="#svg_justify_left"></use></svg></span>`).appendTo(history);
    $(`<div class="d-inline-block mb-2" style="width:calc(100% - 88px);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"></div>`).appendTo(history).text(msg);
    const btn = $(`<button class="btn d-inline-block align-top pt-1 btn_hover" style="fill:gray;"><svg class="align-top" width="16" height="16" viewBox="0 0 16 16">`
        +`<use href="#btn_three_dots_vertical"></use></svg><ul class="dropdown-menu"/></button>`).appendTo(history);
    btn.find('.dropdown-menu').append(`<li><a class="dropdown-item delete" href="#">Delete</a></li>`);
    btn.off('click').on('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        histories.find('.dropdown-menu').hide();
        btn.find('.dropdown-menu').css('left','calc(100% - 180px)').show();
    });
    btn.find('.dropdown-menu .delete').off('click').on('click',(e)=>{
        if (!window.confirm('Are you sure you want to delete this session?')) return;
        // セッション削除ボタンのクリックイベント
        e.preventDefault();
        e.stopPropagation();
        agent.delete_session(session_id).then((res) => {
            const messages = $('#messages');
            history.remove();
            const sid = messages.attr('data-session_id');
            if (sid == session_id) {
                // 削除したセッションが現在のセッションだった場合は、メッセージ一覧をクリア
                messages.html('');
                agent.ws && agent.ws.close();
                agent.chat(cmdbox.random_string(16));
            }
            agent.list_sessions();
        });
    });
    history.off('click').on('click', async (e) => {
        // セッションを選択したときの処理
        e.preventDefault();
        agent.ws && agent.ws.close();
        agent.chat(session_id);
        const data = await agent.list_sessions(session_id);
        if (data.length<=0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        const session = data[0];
        if (!session['events'] || session['events'].length <= 0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        const container = $('#message_container');
        const messages = $('#messages');
        messages.html('');
        for (const event of session['events']) {
            if (!event['text'] || event['text'].length <= 0) continue;
            if (event['author'] == 'user') {
                // ユーザーメッセージ
                agent.create_user_message(messages, event['text']);
            } else {
                // エージェントメッセージ
                txt = agent.create_agent_message(messages, cmdbox.random_string(16));
                await agent.format_agent_message(container, messages, txt, event['text']);
            }
        }
    });
    return history;
};
agent.delete_session = async (session_id) => {
    return agent.exec_cmd('agent', 'session_del', {
        'runner_name': $('#runner_name_input').val(),
        'session_id': session_id
    });
}

agent.disabled = false;
agent.exec_cmd = async (mode, cmd, opt={}, error_func=null, loading=true) => {
    const user = await cmdbox.user_info();
    if(!user) {
        if (!agent.disabled) {
            cmdbox.message({'error':'User information could not be retrieved. AI features are unavailable.'});
            agent.disabled = true;
            $('#ai_chat_button').hide();
        }
        return;
    }
    const opt_def = cmdbox.get_server_opt(false, $('#filer_form'));
    opt = {...opt_def, ...opt, 'mode':mode, 'cmd':cmd, 'user_name':user['name'], 'capture_stdout':true};
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
            console.error(res);
            //cmdbox.message(res);
            return res;
        }
        return res[0];
    });
}
agent.get_llm_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'llm_save');
    const vform_names = ['llmname', 'llmprov', 'llmapikey', 'llmendpoint', 'llmmodel', 'llmapiversion',
                        'llmprojectid', 'llmsvaccountfile', 'llmlocation', 'llmtemperature', 'llmseed'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_llm_form = async () => {
    const form = $('#form_llm_edit');
    form.empty();
    const defs = await agent.get_llm_form_def();
    const model = $('#llm_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agent.list_llm = async () => {
    const container = $('#llm_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    
    try {
        const res = await agent.exec_cmd('agent', 'llm_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load LLM list.</div>');
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="text-muted p-3">No LLM configurations found.</div>');
            return;
        }

        list.forEach(async item => {
            const res = await agent.exec_cmd('agent', 'llm_load', { llmname: item.name });
            if (!res || !res.success) {
                const itemEl = $(`
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                        <div>
                            <h6 class="mb-1">${item.name}</h6>
                            <small class="text-danger">${JSON.stringify(res)}</small>
                        </div>
                    </div>
                `);
                container.append(itemEl);
                return;
            }
            const config = res.success || {};
            const itemEl = $(`
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                    <div>
                        <h6 class="mb-1">${config.llmname}</h6>
                        <small>${config.llmprov} / ${config.llmmodel}</small>
                    </div>
                </div>
            `);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agent.build_llm_form();
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
                    await agent.exec_cmd('agent', 'llm_del', { llmname: config.llmname });
                    $('#llm_edit_modal').modal('hide');
                    agent.list_llm();
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

agent.save_llm = async () => {
    const form = $('#form_llm_edit');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    try {
        const res = await agent.exec_cmd('agent', 'llm_save', data);
        if (res && res.success) {
            $('#llm_edit_modal').modal('hide');
            agent.list_llm();
        } else {
            alert('Failed to save LLM settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agent.get_mcpsv_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'mcpsv_save');
    const vform_names = ['mcpserver_name', 'mcpserver_url', 'mcpserver_delegated_auth', 'mcpserver_apikey',
                         'mcpserver_transport', 'mcp_tools'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_mcpsv_form = async () => {
    const form = $('#form_mcpsv_edit');
    form.empty();
    const defs = await agent.get_mcpsv_form_def();
    const model = $('#mcpsv_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};
agent.list_mcpsv = async () => {
    const container = $('#mcpsv_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    
    try {
        const res = await agent.exec_cmd('agent', 'mcpsv_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load MCPSV list.</div>');
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="text-muted p-3">No MCPSV connections found.</div>');
            return;
        }

        list.forEach(async item => {
            const res = await agent.exec_cmd('agent', 'mcpsv_load', { mcpserver_name: item.name });
            if (!res || !res.success) {
                const itemEl = $(`
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                        <div>
                            <h6 class="mb-1">${item.name}</h6>
                            <small class="text-danger">${JSON.stringify(res)}</small>
                        </div>
                    </div>
                `);
                container.append(itemEl);
                return;
            }
            const config = res.success || {};
            const itemEl = $(`
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                    <div>
                        <h6 class="mb-1">${config.mcpserver_name}</h6>
                        <small>${config.mcpserver_url}</small>
                    </div>
                </div>
            `);
            
            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agent.build_mcpsv_form();
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
                    await agent.exec_cmd('agent', 'mcpsv_del', { mcpserver_name: config.mcpserver_name });
                    $('#mcpsv_edit_modal').modal('hide');
                    agent.list_mcpsv();
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

agent.save_mcpsv = async () => {
    const form = $('#form_mcpsv_edit');
    const data = {};
    form.find(':input').each((i, elem) => {
        const val = $(elem).val();
        if (val) data[elem.name] = val;
    });

    try {
        const res = await agent.exec_cmd('agent', 'mcpsv_save', data);
        if (res && res.success) {
            $('#mcpsv_edit_modal').modal('hide');
            agent.list_mcpsv();
        } else {
            alert('Failed to save MCPSV settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agent.get_agent_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'agent_save');
    const vform_names = ['agent_name', 'agent_type',
                         'a2asv_baseurl', 'a2asv_delegated_auth', 'a2asv_apikey',
                         'llm', 'mcpservers', 'subagents',
                         'agent_description', 'agent_instruction'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_agent_form = async () => {
    const form = $('#form_agent_edit');
    form.empty();
    const defs = await agent.get_agent_form_def();
    const model = $('#agent_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agent.list_agent = async () => {
    const container = $('#agent_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agent.exec_cmd('agent', 'agent_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Agent list.</div>');
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="text-muted p-3">No Agent configurations found.</div>');
            return;
        }

        list.forEach(async item => {
            const res = await agent.exec_cmd('agent', 'agent_load', { agent_name: item.name });
            if (!res || !res.success) {
                const itemEl = $(`
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                        <div>
                            <h6 class="mb-1">${item.name}</h6>
                            <small class="text-danger">${JSON.stringify(res)}</small>
                        </div>
                    </div>
                `);
                container.append(itemEl);
                return;
            };
            const config = res.success || {};
            const itemEl = $(`
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                    <div>
                        <h6 class="mb-1">${config.agent_name}</h6>
                        <small>${config.agent_description || 'None'}</small>
                    </div>
                </div>
            `);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agent.build_agent_form();
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
                    await agent.exec_cmd('agent', 'agent_del', { agent_name: config.agent_name });
                    $('#agent_edit_modal').modal('hide');
                    agent.list_agent();
                });

                $('#agent_edit_modal').modal('show');
                // LLMリストをロード
                await cmdbox.callcmd('agent','llm_list',{},(res)=>{
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
                    config.mcpservers.forEach((v, i) => {
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
                    config.subagents.forEach((v, i) => {
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

agent.save_agent = async () => {
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
        const res = await agent.exec_cmd('agent', 'agent_save', data);
        if (res && res.success) {
            $('#agent_edit_modal').modal('hide');
            agent.list_agent();
        } else {
            alert('Failed to save Agent settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agent.get_runner_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('agent', 'runner_save');
    const vform_names = ['runner_name', 'agent', 'session_store_type', 'session_store_pghost',
                        'session_store_pgport', 'session_store_pguser', 'session_store_pgpass',
                        'session_store_pgdbname', 'tts_engine', 'voicevox_model'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_runner_form = async () => {
    const form = $('#form_runner_edit');
    form.empty();
    const defs = await agent.get_runner_form_def();
    const model = $('#runner_edit_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agent.list_runner = async () => {
    const container = $('#runner_list_container');
    container.html('<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');

    try {
        const res = await agent.exec_cmd('agent', 'runner_list');
        container.html('');
        if (!res || !res.success) {
            container.html('<div class="text-danger p-3">Failed to load Runner list.</div>');
            return;
        }
        
        const list = res.success['data'] || [];
        if (list.length === 0) {
            container.html('<div class="text-muted p-3">No Runner connections found.</div>');
            return;
        }

        list.forEach(async item => {
            const res = await agent.exec_cmd('agent', 'runner_load', { runner_name: item.name });
            if (!res || !res.success) {
                const itemEl = $(`
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                        <div>
                            <h6 class="mb-1">${item.name}</h6>
                            <small class="text-danger">${JSON.stringify(res)}</small>
                        </div>
                    </div>
                `);
                container.append(itemEl);
                return;
            }
            const config = res.success || {};
            const itemEl = $(`
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" style="cursor: pointer;">
                    <div>
                        <h6 class="mb-1">${config.runner_name}</h6>
                        <small>Agent: ${config.agent || 'None'}</small>
                    </div>
                </div>
            `);

            // リストアイテムクリックで編集
            itemEl.on('click', async () => {
                await agent.build_runner_form();
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
                    await agent.exec_cmd('agent', 'runner_del', { runner_name: config.runner_name });
                    $('#runner_edit_modal').modal('hide');
                    agent.list_runner();
                });

                $('#runner_edit_modal').modal('show');
                // コマンド実行
                await cmdbox.callcmd('agent','agent_list',{},(res)=>{
                    $("[name='agent']").empty().append('<option></option>');
                    res['data'].map(elm=>{$('[name="agent"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
                    form.find('[name="agent"]').val(config.agent);
                },$('[name="title"]').val(),'agent');
            });

            container.append(itemEl);
        });
    } catch (e) {
        console.error(e);
        container.html(`<div class="text-danger p-3">Error: ${e.message}</div>`);
    }
};

agent.save_runner = async () => {
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
        const res = await agent.exec_cmd('agent', 'runner_save', data);
        if (res && res.success) {
            $('#runner_edit_modal').modal('hide');
            agent.list_runner();
        } else {
            alert('Failed to save Runner settings.');
        }
    } catch (e) {
        console.error(e);
        alert(`Error: ${e.message}`);
    }
};

agent.get_tts_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('tts', 'install');
    const vform_names = ['tts_engine', 'voicevox_ver', 'voicevox_whl',
        'openjtalk_ver', 'openjtalk_dic', 'onnxruntime_ver', 'onnxruntime_lib', 'force_install'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_tts_form = async () => {
    const form = $('#form_tts_install');
    form.empty();
    const defs = await agent.get_tts_form_def();
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

agent.list_tts = async () => {
    // フォームが空の場合のみ構築する（再描画を避けるため）
    if ($('#form_tts_install').children().length === 0) {
        await agent.build_tts_form();
    }
    if ($('#form_tts_uninstall').children().length === 0) {
        await agent.build_tts_uninstall_form();
    }
};

agent.install_tts = async () => {
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
        const res = await agent.exec_cmd('tts', 'install', data, null, false);
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

agent.get_tts_uninstall_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('tts', 'uninstall');
    const vform_names = ['tts_engine'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

agent.build_tts_uninstall_form = async () => {
    const form = $('#form_tts_uninstall');
    form.empty();
    const defs = await agent.get_tts_uninstall_form_def();
    const model = $('#tts_settings');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, model, form, row, null);
    });
};

agent.uninstall_tts = async () => {
    const form = $('#form_tts_uninstall');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) data[item.name] = item.value;
    });

    if (!confirm('Are you sure you want to uninstall the TTS engine?')) return;

    try {
        cmdbox.show_loading();
        data['timeout'] = 300;
        const res = await agent.exec_cmd('tts', 'uninstall', data, null, false);
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
agent.html = `
    <!-- エージェントモーダル -->
    <div id="agent_modal" class="modal" tabindex="-1">
        <div class="modal-dialog modal-xl modal-dialog-scrollable" style="height: 90vh;">
            <div class="modal-content h-100">
                <div class="modal-header">
                    <h5 class="modal-title">AI Chat</h5>
                    <button type="button" class="btn btn_window_stack">
                        <svg class="bi bi-window-stack" width="16" height="16" fill="currentColor"><use href="#btn_window_stack"></use></svg>
                    </button>
                    <button type="button" class="btn btn_window">
                        <svg class="bi bi-window" width="16" height="16" fill="currentColor"><use href="#btn_window"></use></svg>
                    </button>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close" style="margin-left: 0px;">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body p-0 h-100 overflow-hidden">
                    <div id="agent_container" class="split-pane fixed-left h-100 w-100">
                        <!-- 履歴側ペイン -->
                        <div id="left_container" class="split-pane-component filer-pane-left" style="width:250px;">
                            <div id="newchat_container" class="w-100 d-flex justify-content-center pt-2">
                                <button id="btn_newchat" class="btn_hover btn me-3 p-2" type="button" style="border:0px;">
                                    <svg class="bi bi-plus" width="24" height="24" fill="currentColor"><use href="#btn_plus"></use></svg>
                                    <span class="btn_text">New Chat&nbsp;</span>
                                </button>
                            </div>
                            <h6 class="ps-2" style="float:left;">Histories</h6>
                            <div id="history_container" class="w-100 d-flex justify-content-center" style="height:calc(100% - 130px);overflow-y:auto;">
                                <div id="histories" class="w-100 p-2"></div>
                            </div>
                            <div id="settings_container" class="w-100 d-flex justify-content-end position-absolute bottom-0 pb-2 pe-3">
                                <button id="btn_settings" class="btn btn_hover p-2" type="button" style="border:0px;">
                                    <svg class="bi bi-gear" width="24" height="24" fill="currentColor"><use href="#btn_gear"></use></svg>
                                </button>
                            </div>
                        </div>
                        <!-- 左右のスプリッター -->
                        <div class="split-pane-divider filer-pane-divider" style="left:250px;"></div>
                        <!-- チャット側ペイン -->
                        <div id="right_container" class="split-pane-component chat-container" style="left:250px;">
                            <div id="message_container" class="w-100 d-flex justify-content-center" style="height:calc(100% - 80px);overflow-y:auto;">
                                <div id="messages" class="ps-2 pe-2" style="width:100%; max-width: 80%;"></div>
                            </div>
                            <div class="w-100 d-flex justify-content-center position-absolute bottom-0 pb-3" style="background-color: var(--bs-body-bg);">
                                <div class="chat-input mt-2" style="width:90%; max-width: 80%;">
                                    <div class="chat-group w-100 p-2 d-flex align-items-center">
                                        <div class="d-flex flex-column align-items-center">
                                            <div class="d-flex align-items-center">
                                                <button id="btn_say" class="btn btn_hover p-1" type="button" style="border:0px;" disabled="disabled">
                                                    <svg class="bi bi-say" width="24" height="24" fill="currentColor"><use href="#btn_megaphone"></use></svg>
                                                </button>
                                                <div class="dropdown d-inline-block ms-1 text-center">
                                                    <button id="btn_runner" class="btn btn_hover p-1 dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="border:0px;" title="Select Runner">
                                                        <svg class="bi bi-chat-text" width="24" height="24" fill="currentColor"><use href="#btn_chat_text"></use></svg>
                                                    </button>
                                                    <ul class="dropdown-menu" id="runner_menu"></ul>
                                                </div>
                                            </div>
                                            <div id="runner_name_display" style="font-size: 0.6rem; max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display:none;"></div>
                                            <input type="hidden" id="runner_name_input">
                                        </div>
                                        <textarea id="user_msg" class="form-control d-inline-block align-middle mx-2" rows="1" style="border:0px;box-shadow:none;resize:none;field-sizing:content;"></textarea>
                                        <button id="btn_user_msg" class="btn btn_hover p-1" type="button" style="border:0px;" disabled="disabled">
                                            <svg class="bi bi-send" width="24" height="24" fill="currentColor"><use href="#btn_send"></use></svg>
                                        </button>
                                        <button id="btn_rec" class="btn btn_hover p-1" type="button" style="border:0px;" disabled="disabled">
                                            <svg class="bi bi-mic" width="24" height="24" fill="currentColor"><use href="#btn_mic"></use></svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- 設定モーダル -->
    <div id="agent_settings_modal" class="modal" tabindex="-1">
        <div class="modal-dialog modal-lg modal-dialog-scrollable" style="height: 80vh;">
            <div class="modal-content h-100">
                <div class="modal-header">
                    <h5 class="modal-title">Settings</h5>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body p-0 h-100 overflow-hidden">
                    <div id="settings_split_pane" class="split-pane fixed-left h-100 w-100">
                        <!-- 左側ペイン: 設定項目リスト -->
                        <div class="split-pane-component filer-pane-left" style="width:200px;">
                            <div class="list-group list-group-flush">
                                <a href="#" class="list-group-item list-group-item-action active" data-bs-target="#agent_settings">Agent Settings</a>
                                <a href="#" class="list-group-item list-group-item-action" data-bs-target="#llm_settings">LLM Settings</a>
                                <a href="#" class="list-group-item list-group-item-action" data-bs-target="#mcpsv_settings">MCPSV Settings</a>
                                <a href="#" class="list-group-item list-group-item-action" data-bs-target="#runner_settings">Runner Settings</a>
                                <a href="#" class="list-group-item list-group-item-action" data-bs-target="#tts_settings">TTS Settings</a>
                            </div>
                        </div>
                        <!-- スプリッター -->
                        <div class="split-pane-divider filer-pane-divider" style="left:200px;"></div>
                        <!-- 右側ペイン: 設定内容 -->
                        <div class="split-pane-component" style="left:200px; background-color: var(--bs-body-bg);">
                            <div class="p-3 h-100 overflow-auto">
                                <div id="agent_settings" class="settings-content">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="m-0">Agent Settings</h6>
                                        <button id="btn_add_agent" class="btn btn-sm btn-primary">
                                            <svg class="bi bi-plus" width="16" height="16" fill="currentColor"><use href="#btn_plus"></use></svg>
                                            Add Connection
                                        </button>
                                    </div>
                                    <div id="agent_list_container" class="list-group">
                                        <!-- Agent List Items will be injected here -->
                                    </div>
                                </div>
                                <div id="llm_settings" class="settings-content d-none">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="m-0">LLM Settings</h6>
                                        <button id="btn_add_llm" class="btn btn-sm btn-primary">
                                            <svg class="bi bi-plus" width="16" height="16" fill="currentColor"><use href="#btn_plus"></use></svg>
                                            Add Connection
                                        </button>
                                    </div>
                                    <div id="llm_list_container" class="list-group">
                                        <!-- LLM List Items will be injected here -->
                                    </div>
                                </div>
                                <div id="mcpsv_settings" class="settings-content d-none">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="m-0">MCPSV Settings</h6>
                                        <button id="btn_add_mcpsv" class="btn btn-sm btn-primary">
                                            <svg class="bi bi-plus" width="16" height="16" fill="currentColor"><use href="#btn_plus"></use></svg>
                                            Add Connection
                                        </button>
                                    </div>
                                    <div id="mcpsv_list_container" class="list-group">
                                        <!-- MCPSV List Items will be injected here -->
                                    </div>
                                </div>
                                <div id="runner_settings" class="settings-content d-none">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="m-0">Runner Settings</h6>
                                        <button id="btn_add_runner" class="btn btn-sm btn-primary">
                                            <svg class="bi bi-plus" width="16" height="16" fill="currentColor"><use href="#btn_plus"></use></svg>
                                            Add Connection
                                        </button>
                                    </div>
                                    <div id="runner_list_container" class="list-group">
                                        <!-- Runner List Items will be injected here -->
                                    </div>
                                </div>
                                <div id="tts_settings" class="settings-content d-none">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h6 class="m-0">TTS Settings</h6>
                                    </div>
                                    <div class="card">
                                        <div class="card-body">
                                            <h6 class="card-title">Install TTS Engine</h6>
                                            <form id="form_tts_install" class="row"></form>
                                            <div class="mt-3 text-end">
                                                <button id="btn_install_tts" class="btn btn-primary">Install</button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="card mt-3">
                                        <div class="card-body">
                                            <h6 class="card-title">Uninstall TTS Engine</h6>
                                            <form id="form_tts_uninstall" class="row"></form>
                                            <div class="mt-3 text-end">
                                                <button id="btn_uninstall_tts" class="btn btn-danger">Uninstall</button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    <!-- AIチャットボタン -->
    <div id="ai_chat_button" class="position-fixed bottom-0 end-0 m-3" style="z-index: 1080;">
        <button type="button" class="btn btn-primary rounded-pill shadow-lg d-flex align-items-center gap-2 px-3 py-2" onclick="$('#agent_modal').modal('show'); agent.init();">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-chat-dots-fill" viewBox="0 0 16 16">
                <path d="M16 8c0 3.866-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.584.296-1.925.864-4.181 1.234-.2.032-.352-.176-.273-.362.354-.836.674-1.95.77-2.966C.744 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7zM5 8a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm4 0a1 1 0 1 0-2 0 1 1 0 0 0 2 0zm3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
            </svg>
            <span class="fw-bold">AIと話す</span>
        </button>
    </div>

    <!-- LLM追加/編集モーダル -->
    <div id="llm_edit_modal" class="modal" tabindex="-1" style="z-index: 1090;">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add/Edit LLM</h5>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="form_llm_edit" class="row"></form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger me-auto" id="btn_del_llm" style="display:none;">Delete</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="btn_save_llm">Save</button>
                </div>
            </div>
        </div>
    </div>

    <!-- MCPSV追加/編集モーダル -->
    <div id="mcpsv_edit_modal" class="modal" tabindex="-1" style="z-index: 1090;">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add/Edit MCPSV</h5>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="form_mcpsv_edit" class="row"></form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger me-auto" id="btn_del_mcpsv" style="display:none;">Delete</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="btn_save_mcpsv">Save</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Agent追加/編集モーダル -->
    <div id="agent_edit_modal" class="modal" tabindex="-1" style="z-index: 1090;">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add/Edit Agent</h5>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="form_agent_edit" class="row"></form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger me-auto" id="btn_del_agent" style="display:none;">Delete</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="btn_save_agent">Save</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Runner追加/編集モーダル -->
    <div id="runner_edit_modal" class="modal" tabindex="-1" style="z-index: 1090;">
        <div class="modal-dialog modal-lg modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add/Edit Runner</h5>
                    <button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close">
                        <svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="form_runner_edit" class="row"></form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-danger me-auto" id="btn_del_runner" style="display:none;">Delete</button>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" id="btn_save_runner">Save</button>
                </div>
            </div>
        </div>
    </div>
`;

agent.css = `
    .card-hover:hover {
        box-shadow: 0 0 8px gray;
        cursor: pointer;
    }
    .filer-pane-divider {
        border: 1px solid var(--bs-border-color-translucent) !important;
        /**background-color: #F0F0F0 !important;*/
        border-radius: 1px;
        /*left: 50%;*/
    }
    .chat-container {
        overflow-y: auto;
        background-color: var(--bs-body-bg);
    }
    .message {
        padding: 10px;
        /**border: 1px solid var(--bs-border-color-translucent);*/
        margin-bottom: 10px;
        border-radius: 5px;
        clear: both;
    }
    .user-message {
        background-color: var(--bs-tertiary-bg);
        color: var(--bs-body-color);
        /**float: right;*/
        border-bottom-left-radius: 24px;
        border-bottom-right-radius: 24px;
        border-top-left-radius: 24px;
        border-top-right-radius: 4px;
    }
    .bot-message {
        background-color: var(--bs-body-bg);
        color: var(--bs-body-color);
        float: left;
    }
    .chat-input {
        border-radius: 16px;
        border: 1px solid var(--bs-border-color);
    }
    :root {
        --cmdbox-width: 800px;
    }
    pre {
        width: var(--cmdbox-width);
        overflow-wrap: break-all;
    }
    .btn_hover {
        border-radius: 24px !important;
    }
    .btn_hover:hover {
        background-color: var(--bs-tertiary-bg) !important;
    }
`;

agent.initialized = false;
agent.init = async () => {
    if (agent.initialized) return;
    agent.initialized = true;

    // CSSを追加
    $('head').append(`<style>${agent.css}</style>`);
    $('head').append('<link rel="stylesheet" href="assets/split-pane/split-pane.css">');

    // HTMLを追加
    $('body').append(agent.html);

    // JSを追加
    $.getScript('assets/split-pane/split-pane.js', () => {
        // スプリッター初期化
        $('.split-pane').splitPane();
    });
    
    // コマンド実行用のオプション取得
    // gui.html では既に取得済みかもしれないが、念のため
    // cmdbox.get_server_opt(true, $('.filer_form')).then(async (opt) => {
        agent.init_form();
    // });

    // モーダル表示時のイベント
    $('#agent_modal').off('shown.bs.modal').on('shown.bs.modal', () => {
        agent.list_sessions();
    });

    // dropdownメニューを閉じる
    const histories = $('#histories');
    $(document).on('click', (e) => {
        histories.find('.dropdown-menu').hide();
    }).on('contextmenu', (e) => {
        histories.find('.dropdown-menu').hide();
    });

    // 設定ボタンのクリックイベント
    $('#btn_settings').off('click').on('click', () => {
        // Agent一覧の表示
        agent.list_agent();
        $('#agent_settings_modal').modal('show');
    });
    // 設定メニューの切り替え
    $('#agent_settings_modal .list-group-item').off('click').on('click', function(e) {
        e.preventDefault();
        $('#agent_settings_modal .list-group-item').removeClass('active');
        $(this).addClass('active');
        const target = $(this).data('bs-target');
        $('.settings-content').addClass('d-none');
        $(target).removeClass('d-none');
        
        if (target === '#agent_settings') {
            agent.list_agent();
        } else if (target === '#llm_settings') {
            agent.list_llm();
        } else if (target === '#mcpsv_settings') {
            agent.list_mcpsv();
        } else if (target === '#tts_settings') {
            agent.list_tts();
        } else if (target === '#runner_settings') {
            agent.list_runner();
        }
    });
    
    // モーダルボタン初期化
    cmdbox.init_modal_button();

    // LLM追加ボタンのクリックイベント
    $('#btn_add_llm').off('click').on('click', async () => {
        await agent.build_llm_form();
        $('#form_llm_edit [name="llmname"]').prop('readonly', false);
        $('#form_llm_edit [name="llmprov"]').trigger('change');
        $('#btn_del_llm').hide();
        $('#llm_edit_modal').modal('show');
    });

    // LLM保存ボタンのクリックイベント
    $('#btn_save_llm').off('click').on('click', () => {
        agent.save_llm();
    });

    // MCPSV追加ボタンのクリックイベント
    $('#btn_add_mcpsv').off('click').on('click', () => {
        agent.build_mcpsv_form();
        $('#form_mcpsv_edit [name="mcpserver_name"]').prop('readonly', false);
        $('#btn_del_mcpsv').hide();
        $('#mcpsv_edit_modal').modal('show');
    });

    // MCPSV保存ボタンのクリックイベント
    $('#btn_save_mcpsv').off('click').on('click', () => {
        agent.save_mcpsv();
    });

    // Agent追加ボタンのクリックイベント
    $('#btn_add_agent').off('click').on('click', async () => {
        await agent.build_agent_form();
        $('#form_agent_edit [name="agent_name"]').prop('readonly', false);
        $('#btn_del_agent').hide();
        $('[name="agent_type"]').trigger('change');
        $('#agent_edit_modal').modal('show');
        // LLMリストをロード
        await cmdbox.callcmd('agent','llm_list',{},(res)=>{
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
        agent.save_agent();
    });

    // Runner追加ボタンのクリックイベント
    $('#btn_add_runner').off('click').on('click', async () => {
        await agent.build_runner_form();
        $('#form_runner_edit [name="runner_name"]').prop('readonly', false);
        $('#form_runner_edit [name="session_store_type"]').trigger('change');
        $('#btn_del_runner').hide();
        $('#runner_edit_modal').modal('show');
        // Agentリストをロード
        await cmdbox.callcmd('agent','agent_list',{},(res)=>{
            $("[name='agent']").empty().append('<option></option>');
            res['data'].map(elm=>{$('[name="agent"]').append('<option value="'+elm["name"]+'">'+elm["name"]+'</option>');});
        },$('[name="title"]').val(),'agent');
    });

    // Runner保存ボタンのクリックイベント
    $('#btn_save_runner').off('click').on('click', () => {
        agent.save_runner();
    });

    // Runner選択ボタンのクリックイベント
    $('#btn_runner').off('click').on('click', async () => {
        await agent.update_runner_list();
    });

    // TTSインストールボタンのクリックイベント
    $('#btn_install_tts').off('click').on('click', () => {
        agent.install_tts();
    });

    // TTSアンインストールボタンのクリックイベント
    $('#btn_uninstall_tts').off('click').on('click', () => {
        agent.uninstall_tts();
    });
};

agent.update_runner_list = async () => {
    const menu = $('#runner_menu');
    try {
        cmdbox.show_loading();
        const res = await agent.exec_cmd('agent', 'runner_list');
        if (res && res.success && res.success.data) {
            menu.html('');
            res.success.data.forEach(item => {
                const li = $(`<li><a class="dropdown-item" href="#" data-runner="${item.name}">${item.name}</a></li>`);
                li.find('a').off('click').on('click', async (e) => {
                    e.preventDefault();
                    const current_runner = $('#runner_name_input').val();
                    if (current_runner && item.name != current_runner && !confirm(`Switching runners will start a new chat. Continue?`)) {
                        return;
                    }
                    const promises = [];
                    cmdbox.show_loading();
                    $('#runner_menu a').each(async (i, a_elem) => {
                        const rn = $(a_elem).attr('data-runner');
                        if (rn) {
                            promises.push(agent.exec_cmd('agent', 'stop', { runner_name: rn }, null, false));
                        }
                    });
                    if (agent.say.isStart()) $('#btn_say').click();
                    await Promise.all(promises);
                    agent.select_runner(item.name);
                    const item_data = await agent.exec_cmd('agent', 'runner_load', { runner_name: item.name }, null, false);
                    if (item_data && item_data.success) {
                        agent.say.model = item_data.success.voicevox_model || 'ずんだもんノーマル';
                    }
                    // Start the agent runner
                    await agent.exec_cmd('agent', 'start', { runner_name: item.name }, null, false);
                    cmdbox.show_loading();
                    await agent.list_sessions();
                    const btn_newchat = $('#btn_newchat');
                    btn_newchat.click();
                });
                menu.append(li);
            });
            if (res.success.data.length > 0 && !agent.current_runner) {
                // Select first one by default if none selected
                //agent.select_runner(res.success.data[0].name);
            }
        } else {
            menu.html('<li><span class="dropdown-item text-muted">No runners found</span></li>');
        }
    } catch (e) {
        console.error(e);
        menu.html('<li><span class="dropdown-item text-danger">Error loading runners</span></li>');
    }
};

agent.select_runner = async (runner_name) => {
    agent.current_runner = runner_name;
    $('#btn_runner').attr('title', `Runner: ${runner_name}`);
    // Highlight the selected item
    $('#runner_menu .dropdown-item').removeClass('active');
    $(`#runner_menu .dropdown-item[data-runner="${runner_name}"]`).addClass('active');

    // Update display and hidden input
    $('#runner_name_display').text(runner_name).show();
    $('#runner_name_input').val(runner_name);
};

// 自動初期化（ボタン表示のため）
$(() => {
    // ボタンだけは先に表示したいが、init()で全部やるならinit()を呼ぶ
    // ただし、init()はモーダル表示時に呼ばれる想定だったが、
    // ボタン自体もJSで追加するので、ページロード時にinit()を呼んでボタンを表示させる必要がある。
    // しかしinit()内でモーダルも追加してしまうので、モーダルは非表示状態で追加される。
    // ボタンのonclickで $('#agent_modal').modal('show') するので問題ない。
    agent.init();
});
