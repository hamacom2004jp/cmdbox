const agent = {};
agent.chat_reconnectInterval_handler = null;
agent.chat_callback_ping_handler = null;
agent.init_form = async () => {
    const container = $('#message_container');
    const histories = $('#histories');
    const messages = $('#messages');
    const agent_chat = (session_id) => {
        // ws再接続のためのインターバル初期化
        if (agent.chat_reconnectInterval_handler) {
            clearInterval(agent.chat_reconnectInterval_handler);
        }
        // wsのpingのためのインターバル初期化
        if (agent.chat_callback_ping_handler) {
            clearInterval(agent.chat_callback_ping_handler);
        }
        const btn_user_msg = $('#btn_user_msg');
        const user_msg = $('#user_msg');
        let message_id = null;
        btn_user_msg.prop('disabled', true); // 初期状態で送信ボタンを無効化
        // 送信ボタンのクリックイベント
        btn_user_msg.off('click').on('click', async () => {
            const msg = user_msg.val();
            if (msg.length <= 0) return;
            user_msg.val('');
            // 入力内容をユーザーメッセージとして表示
            const user_msg_row = $(`<div class="message" style="float:right;"></div>`).appendTo(messages);
            const user_message = $(`<div class="message user-message d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(user_msg_row);
            $(`<div class="d-inline-block"></div>`).appendTo(user_message).text(msg);
            $(`<a class="d-inline-block align-top" style="fill:gray;"><svg class="align-top ms-3" width="32" height="32" viewBox="0 0 16 16">`
                +`<use href="#svg_signin_ico"></use></svg></a>`).appendTo(user_msg_row);
            agent.create_history(histories, session_id, msg);
            // エージェント側のメッセージ読込中を表示
            if (!message_id) {
                message_id = cmdbox.random_string(16);
                const bot_message = $(`<div class="message bot-message"></div>`).appendTo(messages);
                $(`<img class="icon-logo align-top me-3" src="${cmdbox.logoicon_src}" width="32" height="32"/>`).appendTo(bot_message);
                const txt = $(`<div id="${message_id}" class="d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(bot_message);
                cmdbox.show_loading(txt);
            }
            // メッセージを送信
            ws.send(msg);
            // セッション一覧を再表示
            agent.list_sessions();
            // メッセージ一覧を一番下までスクロール
            container.scrollTop(container.prop('scrollHeight'));
        });
        // ws接続
        const protocol = window.location.protocol.endsWith('s:') ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = window.location.port;
        const path = window.location.pathname;
        const ws = new WebSocket(`${protocol}://${host}:${port}${path}/chat/ws`);
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
                const bot_message = $(`<div class="message bot-message"></div>`).appendTo(messages);
                $(`<img class="icon-logo align-top me-3" src="${cmdbox.logoicon_src}" width="32" height="32"/>`).appendTo(bot_message);
                txt = $(`<div id="${message_id}" class="d-inline-block" style="width:calc(100% - 48px);"></div>`).appendTo(bot_message);
            } else {
                txt = $(`#${message_id}`);
            }
            txt.html('');
            message_id = null;
            try {
                // エージェントからのメッセージをresult表示できるかやってみる
                let rand = cmdbox.random_string(16);
                let j = packet.message.match(/```json([^(```)]+)```/);
                j = JSON.parse(j[1]);
                for (const funcName in j) {
                    for (const ckey in j[funcName]) {
                        if (ckey == 'content') {
                            j[funcName] = JSON.parse(j[funcName][ckey]);
                            break;
                        }
                    }
                }
                let msg = packet.message.replace(/^([^(```json)*]+)```json([^(```)]+)```(.+)$/, `$1<span id="${rand}"/>$3`);
                txt.html(msg);
                if (txt.find("#rand").length > 0) {
                    render_result_func(txt.find("#rand"), j, 100);
                } else {
                    // 置換に失敗していた場合
                    txt.html('');
                    render_result_func(txt, j, 100);
                }
            } catch (e) {
                // JSONパースできなかったらそのまま表示
                let msg = packet.message.replace(/\n/g, '<br>');
                txt.html(msg);
            }
            // メッセージ一覧を一番下までスクロール
            container.scrollTop(container.prop('scrollHeight'));
            const msg_width = messages.prop('scrollWidth');
            if (msg_width > 800) {
                // メッセージ一覧の幅が800pxを超えたら、メッセージ一覧の幅を調整
                document.documentElement.style.setProperty('--cmdbox-width', `${msg_width}px`);
            }
        };
        ws.onopen = () => {
            const ping = () => {ws.send('ping');};
            btn_user_msg.prop('disabled', false);
            agent.chat_callback_ping_handler = setInterval(() => {ping();}, 5000);
        };
        ws.onerror = (e) => {
            console.error(`Websocket error: ${e}`);
            clearInterval(agent.chat_callback_ping_handler);
        };
        ws.onclose = () => {
            clearInterval(agent.chat_callback_ping_handler);
            agent.chat_reconnectInterval_handler = setInterval(() => {
                agent_chat(session_id);
            }, 5000);
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
        agent_chat(session_id);
    });
    // テキストエリアのリサイズに合わせてメッセージ一覧の高さを調整
    container.scrollTop(container.prop('scrollHeight'));
    // セッション一覧を表示
    agent.list_sessions();
    // 新しいセッションでチャットを開始
    const session_id = cmdbox.random_string(16);
    agent_chat(session_id);
};
agent.list_sessions = async () => {
    return;
    const histories = $('#histories');
    const res = await fetch('agent/session/list', {method: 'GET'});
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
    $(`<button class="btn d-inline-block align-top pt-1 btn_hover" style="fill:gray;"><svg class="align-top" width="16" height="16" viewBox="0 0 16 16">`
        +`<use href="#btn_three_dots_vertical"></use></svg></button>`).off('click').on('click',(e)=>{}).appendTo(history);
    return history;
};
agent.delete_session = async () => {
    const formData = new FormData();
    const res = await fetch('agent/session/list', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
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
});
