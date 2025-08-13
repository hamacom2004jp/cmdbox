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
    const bot_message = $(`<div class="message bot-message"></div>`).appendTo(messages);
    $(`<img class="icon-logo align-top me-3" src="${cmdbox.logoicon_src}" width="32" height="32"/>`).appendTo(bot_message);
    const txt = $(`<div id="${message_id}" class="d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(bot_message);
    return txt;
}
agent.format_agent_message = (container, messages, txt, message) => {
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
agent.say.start = ()=> {
    const opt = cmdbox.get_server_opt(false, $('#filer_form'));
    opt['mode'] = 'tts';
    opt['cmd'] = 'start';
    opt['tts_engine'] = 'voicevox';
    opt['voicevox_model'] = agent.say.model;
    cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(res => {
        if (res && res['success']) res = [res];
        cmdbox.hide_loading();
        if (!res[0] || !res[0]['success']) {
            if (res[0] && res[0]['warn']) throw res[0]['warn'];
            else if (res['warn']) throw res['warn'];
            throw res;
        }
        if (res[0]['success']['data']) return res[0]['success']['data'];
        return res[0]['success'];
    });
};
agent.say.stop = () => {
    const opt = cmdbox.get_server_opt(false, $('#filer_form'));
    opt['mode'] = 'tts';
    opt['cmd'] = 'stop';
    opt['tts_engine'] = 'voicevox';
    opt['voicevox_model'] = agent.say.model;
    cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(res => {
        if (res && res['success']) res = [res];
        cmdbox.hide_loading();
        if (!res[0] || !res[0]['success']) {
            if (res[0] && res[0]['warn']) throw res[0]['warn'];
            else if (res['warn']) throw res['warn'];
            throw res;
        }
        if (res[0]['success']['data']) return res[0]['success']['data'];
        return res[0]['success'];
    });
};
agent.say.isStart = () => {
    const btn_say = $('#btn_say');
    return btn_say.hasClass('say_on')
};
agent.say.say = (tts_text) => {
    if (!agent.say.isStart()) return;
    const opt = cmdbox.get_server_opt(false, $('#filer_form'));
    opt['mode'] = 'tts';
    opt['cmd'] = 'say';
    opt['tts_engine'] = 'voicevox';
    opt['voicevox_model'] = agent.say.model;
    opt['tts_text'] = tts_text.replace(/<br\s*\/?>/g, '\n'); // <br>タグを改行に変換
    cmdbox.show_loading();
    return cmdbox.sv_exec_cmd(opt).then(async (res) => {
        if (res && res['success']) res = [res];
        cmdbox.hide_loading();
        if (!res[0] || !res[0]['success']) {
            if (res[0] && res[0]['warn']) throw res[0]['warn'];
            throw res;
        }
        if (!res[0]['success']['data']) {
            throw res[0]['success'];
        }
        // 音声データを再生
        const binary_string = window.atob(res[0]['success']['data']);
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
        let message_id = null;
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
            if (!message_id) {
                message_id = cmdbox.random_string(16);
                const txt = agent.create_agent_message(messages, message_id);
                cmdbox.show_loading(txt);
            }
            // メッセージを送信
            ws.send(msg);
            // セッション一覧を再表示
            agent.list_sessions();
            // メッセージ一覧を一番下までスクロール
            container.scrollTop(container.prop('scrollHeight'));
        });
        // sayボタンのクリックイベント
        btn_say.off('click').on('click', async () => {
            if (agent.say.isStart()) {
                agent.say.stop().then((msg) => {
                    //cmdbox.message(msg);
                    btn_say.removeClass('say_on');
                    btn_say.find('use').attr('href', '#btn_megaphone');
                }).catch((err) => {
                    cmdbox.message(err);
                    if (err.startsWith('VoiceVox model is not running:')) {
                        btn_say.removeClass('say_on');
                        btn_say.find('use').attr('href', '#btn_megaphone');
                    }
                });
                return;
            }
            agent.say.start().then((msg) => {
                //cmdbox.message(msg);
                agent.say.say(msg);
                btn_say.addClass('say_on');
                btn_say.find('use').attr('href', '#btn_megaphone_fill');
            }).catch((err) => {
                cmdbox.message(err);
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
                    transcript && $('#btn_user_msg').click(); // 録音が終了したら自動的にメッセージを送信
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
        const ws = new WebSocket(`${protocol}://${host}:${port}${path}/chat/ws/${session_id}`);
        // エージェントからのメッセージ受信時の処理
        ws.onmessage = (event) => {
            const packet = JSON.parse(event.data);
            console.log(packet);
            if (packet.turn_complete && packet.turn_complete) {
                return;
            }
            let txt;
            if (!message_id) {
                // エージェント側の表示枠が無かったら追加
                message_id = cmdbox.random_string(16);
                txt = agent.create_agent_message(messages, message_id);
            } else {
                txt = $(`#${message_id}`);
            }
            txt.html('');
            message_id = null;
            agent.format_agent_message(container, messages, txt, packet.message);
        };
        ws.onopen = () => {
            const ping = () => {
                ws.send('ping');
                agent.chat_reconnect_count = 0; // pingが成功したら再接続回数をリセット
            };
            btn_say.prop('disabled', false);
            btn_user_msg.prop('disabled', false);
            btn_rec.prop('disabled', false);
            agent.chat_callback_ping_handler = setInterval(() => {ping();}, ping_interval);
        };
        ws.onerror = (e) => {
            console.error(`Websocket error: ${e}`);
            clearInterval(agent.chat_callback_ping_handler);
        };
        ws.onclose = () => {
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
        const session_id = cmdbox.random_string(16);
        agent.chat(session_id);
    });
    // テキストエリアのリサイズに合わせてメッセージ一覧の高さを調整
    container.scrollTop(container.prop('scrollHeight'));
    // セッション一覧を表示
    agent.list_sessions();
    // 新しいセッションでチャットを開始
    const session_id = cmdbox.random_string(16);
    agent.chat(session_id);
};
agent.list_sessions = async (session_id) => {
    const formData = new FormData();
    session_id && formData.append('session_id', session_id);
    const histories = $('#histories');
    const res = await fetch('agent/session/list', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    res.json().then((res) => {
        if (!res['success']) return;
        histories.html('');
        res['success'].forEach(async (row) => {
            if (!row['events'] || row['events'].length <= 0) return;
            const msg = row['events'][0]['text'];
            const history = agent.create_history(histories, row['id'], msg);
        });
    });
}
agent.create_history = (histories, session_id, msg) => {
    if (histories.find(`#${session_id}`).length > 0) return;
    msg = cell_chop(msg, 300);
    const history = $(`<a id="${session_id}" href="#" class="history pt-2 pb-1 d-block btn_hover"></a>`).appendTo(histories);
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
            if (res['success']) {
                history.remove();
                const sid = messages.attr('data-session_id');
                if (sid == session_id) {
                    // 削除したセッションが現在のセッションだった場合は、メッセージ一覧をクリア
                    messages.html('');
                    agent.chat(cmdbox.random_string(16)); // 新しいセッションを開始
                }
                agent.list_sessions();
            } else {
                cmdbox.message({'error':res['error'] || 'Failed to delete session.'});
            }
        });
    });
    history.off('click').on('click', async (e) => {
        // セッションを選択したときの処理
        e.preventDefault();
        agent.chat(session_id);
        const formData = new FormData();
        formData.append('session_id', session_id);
        const res = await fetch('agent/session/list', {method: 'POST', body: formData});
        if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
        res.json().then((res) => {
            if (!res['success'] || res['success'].length<=0) {
                cmdbox.message({'error':'No messages found for this session.'});
                return;
            }
            const session = res['success'][0];
            if (!session['events'] || session['events'].length <= 0) {
                cmdbox.message({'error':'No messages found for this session.'});
                return;
            }
            const container = $('#message_container');
            const messages = $('#messages');
            messages.html('');
            session['events'].forEach((event) => {
                if (!event['text'] || event['text'].length <= 0) return;
                if (event['author'] == 'user') {
                    // ユーザーメッセージ
                    agent.create_user_message(messages, event['text']);
                } else {
                    // エージェントメッセージ
                    txt = agent.create_agent_message(messages, cmdbox.random_string(16));
                    agent.format_agent_message(container, messages, txt, event['text']);
                }
            });
        });
    });
    return history;
};
agent.delete_session = async (session_id) => {
    const formData = new FormData();
    formData.append('session_id', session_id);
    const res = await fetch('agent/session/delete', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
agent.llmsetting = async () => {
    const user = await cmdbox.user_info();
    if (!user) {
        cmdbox.message('user not found');
        return;
    }
    const llmsetting_modal = $('#llmsetting_modal').length?$('#llmsetting_modal'):$(`<div id="llmsetting_modal" class="modal" tabindex="-1" style="display: none;" aria-hidden="true"/>`);
    llmsetting_modal.html('');
    const daialog = $(`<div class="modal-dialog modal-lg ui-draggable ui-draggable-handle"/>`).appendTo(llmsetting_modal);
    const form = $(`<form id="llmsetting_form" class="modal-content novalidate"/>`).appendTo(daialog);
    const header = $(`<div class="modal-header"/>`).appendTo(form);
    header.append('<h5 class="modal-title">LLM Setting</h5>');
    header.append('<button type="button" class="btn btn_close p-0 m-0" data-bs-dismiss="modal" aria-label="Close" style="margin-left: 0px;">'
                 +'<svg class="bi bi-x" width="24" height="24" fill="currentColor"><use href="#btn_x"></use></svg>'
                 +'</button>');
    const body = $(`<div class="modal-body"/>`).appendTo(form);
    const row_content = $(`<div class="row row_content"/>`).appendTo(body);
    const appid = $(`.navbar-brand`).text();
    const llmsetting_choices = async () => {
        const res = await fetch('agent/llmsetting');
        if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
        return await res.json();
    };
    const llmsetting_rows = await llmsetting_choices();
    row_content.html('');
    // 表示オプションを追加
    llmsetting_rows.filter(row => !row.hide).forEach((row, i) => cmdbox.add_form_func(i, llmsetting_modal, row_content, row, null));
    // 高度なオプションを表示するリンクを追加
    const show_link = $('<div class="text-center card-hover mb-3"><a href="#">[ advanced options ]</a></div>');
    show_link.click(() => row_content.find('.row_content_hide').toggle());
    row_content.append(show_link);
    // 非表示オプションを追加
    llmsetting_rows.filter(row => row.hide).forEach((row, i) => cmdbox.add_form_func(i, llmsetting_modal, row_content, row, null));
    // フッターを追加
    const footer = $(`<div class="modal-footer"/>`).appendTo(form);
    // 閉じるボタンを追加
    const close_btn = $('<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>').appendTo(footer);
    llmsetting_modal.appendTo('body');
    daialog.draggable({cursor:'move',cancel:'.modal-body'});
    llmsetting_modal.modal('show');
};
$(() => {
  // カラーモード対応
  cmdbox.change_color_mode();
  // スプリッター初期化
  $('.split-pane').splitPane();
  // アイコンを表示
  cmdbox.set_logoicon('.navbar-brand');
  // copyright表示
  cmdbox.copyright();
  // バージョン情報モーダル初期化
  cmdbox.init_version_modal();
  // モーダルボタン初期化
  cmdbox.init_modal_button();
  // コマンド実行用のオプション取得
  cmdbox.get_server_opt(true, $('.filer_form')).then(async (opt) => {
    agent.init_form();
  });
  // dropdownメニューを閉じる
  const histories = $('#histories');
  $(document).on('click', (e) => {
    histories.find('.dropdown-menu').hide();
  }).on('contextmenu', (e) => {
    histories.find('.dropdown-menu').hide();
  });
});
