const mcpapps = {}
/**
 * ランダムな文字列を生成する
 * @param {number} length - 文字列の長さ
 * @returns {string} - ランダムな文字列
 **/
mcpapps.random_string = (length) => {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    return Array.from({length: length}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
};
mcpapps.pending = new Map();
/**
 * MCP サーバにメッセージを送信する
 * @param {object} message - 送信するメッセージ
 * @returns {void}
 */
mcpapps.post = (message) => window.parent.postMessage({ jsonrpc: "2.0", ...message }, "*");
/**
 * MCP サーバに通知を送信する
 * @param {string} method - 通知のメソッド名
 * @param {object} params - 通知のパラメータ
 */
mcpapps.notify = (method, params) => mcpapps.post({ method, params });
/**
 * MCP サーバにリクエストを送信する
 * @param {string} method - リクエストのメソッド名
 * @param {object} params - リクエストのパラメータ
 * @returns {Promise<any>} - リクエストの結果を返す Promise
 */
mcpapps.request = (method, params) => new Promise((resolve, reject) => {
    const id = mcpapps.random_string(16);
    mcpapps.pending.set(id, { resolve, reject });
    mcpapps.post({ id, method, params });
});
/**
 * 警告メッセージをコンテナに表示する
 * @param {string} text - 警告として表示するテキスト
 */
mcpapps.warn = (text) => {
    const el = document.createElement("div");
    el.className = "text-danger";
    el.textContent = text;
    mcpapps.main_container.appendChild(el);
}
/**
 * MCP サーバが返したツール結果を解析する
 * @param {object} result - MCP サーバからのツール結果
 * @returns - MCP サーバからのツール結果の構造化データ、なければ null
 */
mcpapps.answerOf = (result) => {
    return result?.structuredContent?.success?.data || null;
}
/**
 * HTML エスケープを行う
 * @param {string} s - エスケープする文字列
 * @returns {string} - エスケープ後の文字列
 */
mcpapps.esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
/**
 * ビューをコンテナに描画する
 * @param {HTMLElement} container - 描画先のコンテナ要素
 * @param {object} view - 描画するビューのデータ
 * @param {object} options - 描画オプション
 */
mcpapps.render = (container, result, options) => {
    container.innerHTML = '';
    const el = document.createElement('div');
    el.innerHTML = `<p class="mb-2">${mcpapps.esc(result)}</p>`;
    container.appendChild(el);
};
/**
 * ツール結果を表示する
 * @param {object} result - 表示するツール結果
 */
mcpapps.show = (result) => {
    const res = mcpapps.answerOf(result);
    if (!res) {
        mcpapps.warn("The processing results could not be loaded.");
        return;
    }
    mcpapps.render(mcpapps.main_container, result, {});
}
/**
 * ホスト側にメッセージを送信する
 * @param {string} text - 送信するテキスト
 */
mcpapps.send = async (text) => {
    try {
        await mcpapps.request("ui/message", {
            role:"user",
            content:[{type:"text", text}]
        });
    } catch (e) {
        mcpapps.warn(`The transmission failed. ${e.message}`);
    }
}
/**
 * テーマを設定する
 * @param {object} context - コンテキスト情報
 */
mcpapps.theme = (context) => {
    if (context?.theme) document.documentElement.dataset.bsTheme = context.theme;
}
/**
 * ホスト側からのメッセージを処理する
 * @param {object} message - JSON-RPC 2.0形式のメッセージ
 */
mcpapps.handleHostMessage = (message) => {
    if (!message || !message.jsonrpc) return;

    console.log("Host message:", message);

    // リクエストの場合（ホストがツール呼び出しを要求）
    if (message.method && message.id !== undefined) {
        mcpapps.handleRequest(message);
    }
    // レスポンスの場合
    else if (message.id !== undefined) {
        mcpapps.handleResponse(message);
    }
    // 通知の場合
    else if (message.method) {
        mcpapps.handleNotification(message);
    }
};
/**
 * ホスト側からのリクエストを処理する
 * @param {object} message - リクエストメッセージ
 */
mcpapps.handleRequest = async (message) => {
    const { id, method, params } = message;
    try {
        let result;
        if (method === 'tools/call') {
            // 実装予定：ここで実際にツールを実行
            result = { content: [{ type: "text", text: "Tool execution result" }] };
        } else {
            throw new Error(`Unknown method: ${method}`);
        }

        // レスポンスを送信
        window.parent.postMessage({
            jsonrpc: "2.0",
            id,
            result
        }, '*');
    } catch (error) {
        window.parent.postMessage({
            jsonrpc: "2.0",
            id,
            error: {
                code: -32603,
                message: error.message
            }
        }, '*');
    }
};
/**
 * ホスト側からのレスポンスを処理する
 * @param {object} message - レスポンスメッセージ
 */
mcpapps.handleResponse = (message) => {
    const { id, result, error } = message;
    const pending = mcpapps.pending.get(id);
    if (!pending) return;

    mcpapps.pending.delete(id);

    if (error) {
        pending.reject(new Error(error.message));
    } else {
        pending.resolve(result);
    }
};
/**
 * ホスト側からの通知を処理する
 * @param {object} message - 通知メッセージ
 */
mcpapps.handleNotification = (message) => {
    const { method, params } = message;
    
    if (method === "ui/notifications/tool-result") {
        mcpapps.show(params);
    } else if (method === "ui/notifications/host-context-changed") {
        mcpapps.theme(params);
    }
};

mcpapps.main_container = null;
mcpapps.init = () => {
    console.log("Initializing mcpapps...");
    const main_selector = '#main_mcpapps'
    mcpapps.main_container = document.querySelector(main_selector);
    if (!mcpapps.main_container) {
        const msg = `Container not found for selector: ${main_selector}`;
        console.error(msg);
        window.alert(msg);
        return;
    }
    window.addEventListener("message", (ev) => {
        mcpapps.handleHostMessage(ev.data);
    });
    // iframe のサイズ変更を監視してクライアントに通知する
    const resizeObserver = () => {
        mcpapps.notify("ui/notifications/size-changed", {
            width: document.body.scrollWidth,
            height: document.body.scrollHeight
        });
    };
    new ResizeObserver(resizeObserver).observe(document.body);
    // クライアントに対して初期化要求を送信する
    mcpapps.request("ui/initialize", {
        protocolVersion: "2026-01-26",
        appCapabilities: {},
        appInfo: {name:"cmdbox-agent_mcpapps_iframe", version:"1"}
    }).then((r) => {
        mcpapps.theme(r?.hostContext);
        mcpapps.notify("ui/notifications/initialized", {});
    }).catch((e) => mcpapps.warn(`Unable to connect to the client.${e.message}`));
}
window.addEventListener("DOMContentLoaded", mcpapps.init);
