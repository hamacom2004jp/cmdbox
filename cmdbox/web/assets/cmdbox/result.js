$(() => {
    // ダークモード対応
    cmdbox.change_dark_mode(window.matchMedia('(prefers-color-scheme: dark)').matches);
    // アイコンを表示
    cmdbox.set_logoicon('.navbar-brand');
    // copyright表示
    cmdbox.copyright();
    // バージョン情報モーダル初期化
    cmdbox.init_version_modal();
    // モーダルボタン初期化
    cmdbox.init_modal_button();
    cmdbox.gui_callback_reconnectInterval_handler = null;
    cmdbox.gui_callback_ping_handler = null;
    const gui_callback = () => {
        if (cmdbox.gui_callback_reconnectInterval_handler) {
            clearInterval(cmdbox.gui_callback_reconnectInterval_handler);
        }
        if (cmdbox.gui_callback_ping_handler) {
            clearInterval(cmdbox.gui_callback_ping_handler);
        }
        const protocol = window.location.protocol.endsWith('s:') ? 'wss' : 'ws';
        const host = window.location.hostname;
        const port = window.location.port;
        const path = window.location.pathname;
        const ws = new WebSocket(`${protocol}://${host}:${port}${path}/callback`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const cmd = data['cmd'];
            const title = data['title'];
            let output = data['output'];
            if (cmd == 'js_return_stream_log_func') {
                const size_th = 1024*1024*5;
                const console_modal = $('#console_modal');
                if (typeof output != 'object') {
                    output = console_modal.find('.result-body').html() +'<br/>'+ output;
                }
                result_func(console_modal, 'stream log', output);
                console_modal.find('.btn_window').click();
            } else {
                result_func($('#result_form'), title, output);
            }
            cmdbox.hide_loading();
        };
        ws.onopen = () => {
            const ping = () => {ws.send('ping');};
            cmdbox.gui_callback_ping_handler = setInterval(() => {ping();}, 1000);
        };
        ws.onerror = (e) => {
            console.error(`Websocket error: ${e}`);
            clearInterval(cmdbox.gui_callback_ping_handler);
        };
        ws.onclose = () => {
            clearInterval(cmdbox.gui_callback_ping_handler);
            cmdbox.gui_callback_reconnectInterval_handler = setInterval(() => {
                gui_callback();
            }, 3000);
        };
    };
    gui_callback();
});
const result_func = (content_elem, title, result) => {
    content_elem.find('.modal-title').text(title);
    if (!result || result.length <= 0) {
        return;
    }
    content_elem.find('.result-body').html('');
    render_result_func(content_elem.find('.result-body'), result);
    cmdbox.hide_loading();
}
const get_client_data = async () => {
    const res = await fetch('gui/get_client_data', {method: 'GET'});
    return await res.text();
}
const bbforce_cmd = async () => {
    const res = await fetch('bbforce_cmd', {method: 'GET'});
    return await res.json();
}
