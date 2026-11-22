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
    if (result?.response !== undefined) return mcpapps.answerOf(result.response);
    if (result?.structuredContent !== undefined) {
        return result.structuredContent?.success?.data ?? result.structuredContent;
    }
    if (result?.result !== undefined) return result.result;
    return result?.content ?? result ?? null;
};

/**
 * 文字列を指定された長さまで切り詰めます
 * @param {any} val - 切り詰める値
 * @param {number} resSize - 最大長（-1 の場合は切り詰めなし）
 * @returns {string} - 切り詰められた文字列
 */
mcpapps.cellChop = (val, resSize = 150) => {
    val = `${val || ''}`;
    if (val && resSize > 0 && val.length > resSize) {
        return `${val.substring(0, resSize)}...`;
    }
    return val;
};

/**
 * テーブル要素を作成します
 * @returns {HTMLTableElement} - 作成されたテーブル
 */
mcpapps.makeTableFunc = () => {
    const table = document.createElement('table');
    table.className = 'table table-sm table-bordered table-hover align-middle mb-0';
    const thead = document.createElement('thead');
    const tr = document.createElement('tr');
    thead.appendChild(tr);
    table.appendChild(thead);
    const tbody = document.createElement('tbody');
    table.appendChild(tbody);
    return table;
};

/**
 * 構造化データを安全なDOM要素に変換する
 * @param {any} value - 描画する値
 * @returns {HTMLElement} - 生成した要素
 */
mcpapps.renderNode = (value) => {
    if (value === null || value === undefined) {
        const muted = document.createElement('span');
        muted.className = 'text-muted';
        muted.textContent = 'null';
        return muted;
    }
    if (Array.isArray(value)) {
        // 配列内のすべての要素がオブジェクトの場合はテーブル形式で表示
        if (value.length > 0 && value.every(item => typeof item === 'object' && item !== null)) {
            const table = mcpapps.makeTableFunc();
            const thead = table.querySelector('thead tr');
            const tbody = table.querySelector('tbody');
            mcpapps.list2table(value, thead, tbody);
            return table;
        }
        // それ以外は縦棒で囲んで表示
        const list = document.createElement('div');
        list.className = 'd-grid gap-1';
        value.forEach((item) => {
            const row = document.createElement('div');
            row.className = 'border-start border-2 ps-2';
            row.appendChild(mcpapps.renderNode(item));
            list.appendChild(row);
        });
        return list;
    }
    if (typeof value === 'object') {
        const table = mcpapps.makeTableFunc();
        const thead = table.querySelector('thead tr');
        const tbody = table.querySelector('tbody');
        mcpapps.dict2table(value, thead, tbody);
        return table;
    }
    const text = document.createElement('span');
    text.textContent = mcpapps.cellChop(value, 150);
    return text;
};

/**
 * リスト型のデータをテーブルに変換して表示します
 * @param {Array} data - 表示するリスト型データ
 * @param {HTMLElement} tableHead - テーブルヘッダー要素
 * @param {HTMLElement} tableBody - テーブルボディ要素
 * @param {number} resSize - セル値の最大長
 */
mcpapps.list2table = (data, tableHead, tableBody, resSize = 150) => {
    data.forEach((row, i) => {
        if (!row) return;
        if (typeof row === 'object' && row['success'] && typeof row['success'] === 'object' && !Array.isArray(row['success'])) {
            mcpapps.dict2table(row['success'], i === 0 ? tableHead : null, tableBody, row['output_image'], resSize);
            return;
        }
        if (typeof row === 'string' || row instanceof String) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.textContent = mcpapps.cellChop(row, resSize);
            tr.appendChild(td);
            tableBody.appendChild(tr);
            return;
        }
        if (Array.isArray(row) && row.length > 0 && typeof row[0] !== 'object') {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.textContent = mcpapps.cellChop(JSON.stringify(row), resSize);
            tr.appendChild(td);
            tableBody.appendChild(tr);
            return;
        }
        const tr = document.createElement('tr');
        Object.keys(row).forEach(key => {
            const val = row[key];
            if (i === 0 && tableHead) {
                const th = document.createElement('th');
                th.className = 'th';
                th.scope = 'col';
                th.textContent = key;
                tableHead.appendChild(th);
            }
            if (val && val['success'] && Array.isArray(val['success'])) {
                const tbl = mcpapps.makeTableFunc();
                const td = document.createElement('td');
                td.appendChild(tbl);
                mcpapps.list2table(val['success'], tbl.querySelector('thead tr'), tbl.querySelector('tbody'), resSize);
                tr.appendChild(td);
            } else if (val && val['success'] && typeof val['success'] === 'object') {
                const tbl = mcpapps.makeTableFunc();
                const td = document.createElement('td');
                td.appendChild(tbl);
                mcpapps.dict2table(val['success'], tbl.querySelector('thead tr'), tbl.querySelector('tbody'), null, resSize);
                tr.appendChild(td);
            } else if (val && !Array.isArray(val) && typeof val === 'object') {
                const tbl = mcpapps.makeTableFunc();
                const td = document.createElement('td');
                td.appendChild(tbl);
                mcpapps.dict2table(val, tbl.querySelector('thead tr'), tbl.querySelector('tbody'), null, resSize);
                tr.appendChild(td);
            } else if (val && Array.isArray(val) && val.length > 0 && typeof val[0] === 'object') {
                const tbl = mcpapps.makeTableFunc();
                const td = document.createElement('td');
                td.appendChild(tbl);
                mcpapps.list2table(val, tbl.querySelector('thead tr'), tbl.querySelector('tbody'), resSize);
                tr.appendChild(td);
            } else {
                const td = document.createElement('td');
                td.style.overflowWrap = 'break-word';
                td.style.wordBreak = 'break-all';
                td.textContent = mcpapps.cellChop(val, resSize);
                tr.appendChild(td);
            }
        });
        tableBody.appendChild(tr);
    });
};

/**
 * 辞書型のデータをテーブルに変換して表示します
 * @param {Object} data - 表示する辞書型データ
 * @param {HTMLElement} tableHead - テーブルヘッダー要素
 * @param {HTMLElement} tableBody - テーブルボディ要素
 * @param {string} outputImage - base64 エンコード画像データ（オプション）
 * @param {number} resSize - セル値の最大長
 */
mcpapps.dict2table = (data, tableHead, tableBody, outputImage, resSize = 150) => {
    const tr = document.createElement('tr');
    if (outputImage) {
        if (tableHead) {
            const th = document.createElement('th');
            th.className = 'th';
            th.scope = 'col';
            th.textContent = 'output_image';
            tableHead.appendChild(th);
        }
        const img = document.createElement('img');
        img.className = 'img-thumbnail';
        img.src = `data:image/png;base64,${outputImage}`;
        img.style.width = '100px';
        img.style.height = 'auto';
        const anchor = document.createElement('a');
        anchor.href = `data:image/jpeg;base64,${outputImage}`;
        anchor.setAttribute('data-lightbox', 'output_image');
        anchor.appendChild(img);
        const td = document.createElement('td');
        td.appendChild(anchor);
        tr.appendChild(td);
    }
    tableBody.appendChild(tr);
    Object.keys(data).forEach(key => {
        let val = data[key];
        if (tableHead) {
            const th = document.createElement('th');
            th.className = 'th';
            th.scope = 'col';
            th.textContent = key;
            tableHead.appendChild(th);
        }
        const td = document.createElement('td');
        td.style.overflowWrap = 'break-word';
        td.style.wordBreak = 'break-all';
        if (val) {
            if (Array.isArray(val)) {
                if (val.length > 0 && typeof val[0] === 'object') {
                    const tbl = mcpapps.makeTableFunc();
                    mcpapps.list2table(val, tbl.querySelector('thead tr'), tbl.querySelector('tbody'), resSize);
                    td.appendChild(tbl);
                } else {
                    td.textContent = mcpapps.cellChop(JSON.stringify(val), resSize);
                }
            } else if (typeof val === 'object') {
                const tbl = mcpapps.makeTableFunc();
                mcpapps.dict2table(val, tbl.querySelector('thead tr'), tbl.querySelector('tbody'), null, resSize);
                td.appendChild(tbl);
            } else if (typeof val === 'string' || val instanceof String) {
                const chopped = key === 'warn' || key === 'error' ? String(val) : mcpapps.cellChop(val, resSize);
                td.textContent = chopped;
            } else {
                td.textContent = mcpapps.cellChop(val, resSize);
            }
        }
        tr.appendChild(td);
    });
};

/**
 * ビューをコンテナに描画する
 * @param {HTMLElement} container - 描画先のコンテナ要素
 * @param {object} result - MCPツール結果
 */
mcpapps.render = (container, result) => {
    container.replaceChildren();
    const content = mcpapps.answerOf(result);
    if (content === null || (Array.isArray(content) && content.length === 0)) {
        mcpapps.warn('The processing results could not be loaded.');
        return;
    }
    container.appendChild(mcpapps.renderNode(content));
};
/**
 * ツール結果を表示する
 * @param {object} result - 表示するツール結果
 */
mcpapps.show = (result) => {
    mcpapps.render(mcpapps.main_container, result);
};
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
};
/**
 * MCPサーバーのツールをホスト経由で呼び出す
 * @param {string} name - ツール名
 * @param {object} args - ツール引数
 * @returns {Promise<any>} - ツール結果
 */
mcpapps.callTool = (name, args = {}) => mcpapps.request("tools/call", {
    name,
    arguments: args
});
/**
 * ホストが提供するテーマ情報を適用します
 * @param {Object} context - コンテキスト情報
 * @param {string} context.theme - テーマ名（'light' または 'dark'）
 */
mcpapps.theme = (context) => {
    if (context?.theme) document.documentElement.dataset.bsTheme = context.theme;
}
/**
 * ホストが提供するアセットのベースURLを設定し、必要なCSSを読み込む
 * @param {string} baseurl - ホストが提供するアセットのベースURL
 */
mcpapps.assets = (baseurl) => {
    if (baseurl) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = `${baseurl}/assets/cmdbox/color_mode.css`;
        document.head.appendChild(link);

        const linkExt = document.createElement('link');
        linkExt.rel = 'stylesheet';
        linkExt.href = `${baseurl}/assets/cmdbox/color_mode_ext.css`;
        document.head.appendChild(linkExt);

        const agentLink = document.createElement('link');
        agentLink.rel = 'stylesheet';
        agentLink.href = `${baseurl}/assets/agent/agent.css`;
        document.head.appendChild(agentLink);

        const agentLinkExt = document.createElement('link');
        agentLinkExt.rel = 'stylesheet';
        agentLinkExt.href = `${baseurl}/assets/agent/agent_ext.css`;
        document.head.appendChild(agentLinkExt);
    }
};
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
        if (method === 'ui/get-size') {
            const main_mcpapps = document.querySelector('#main_mcpapps');
            result = {
                width: main_mcpapps.clientWidth+20 || Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
                height: main_mcpapps.clientHeight+20 || Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
            };
        } else if (method === 'tools/call') {
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

/**
 * MCP Apps iframe を初期化します
 * - コンテナ要素の取得
 * - ホスト側との通信リスナーの設定
 * - ツール呼び出しボタンおよびフォーム操作のイベント設定
 * - iframe のサイズ変更監視
 * - ホストに対して ui/initialize リクエストを送信
 */
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
        if (ev.source !== window.parent) return;
        mcpapps.handleHostMessage(ev.data);
    });
    mcpapps.main_container.addEventListener('click', async (event) => {
        const target = event.target.closest('[data-mcp-tool]');
        if (!target) return;
        event.preventDefault();
        try {
            const args = target.dataset.mcpToolArgs ? JSON.parse(target.dataset.mcpToolArgs) : {};
            mcpapps.show(await mcpapps.callTool(target.dataset.mcpTool, args));
        } catch (error) {
            mcpapps.warn(`Tool execution failed. ${error.message}`);
        }
    });
    mcpapps.main_container.addEventListener('submit', async (event) => {
        const form = event.target.closest('form[data-mcp-tool]');
        if (!form) return;
        event.preventDefault();
        try {
            mcpapps.show(await mcpapps.callTool(form.dataset.mcpTool, Object.fromEntries(new FormData(form))));
        } catch (error) {
            mcpapps.warn(`Tool execution failed. ${error.message}`);
        }
    });
    // iframe のサイズ変更を監視してクライアントに通知する
    const dimensions = () => ({
        width: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth),
        height: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
    });
    const resizeObserver = () => mcpapps.notify("ui/notifications/size-changed", dimensions());
    new ResizeObserver(resizeObserver).observe(document.body);
    // クライアントに対して初期化要求を送信する
    mcpapps.request("ui/initialize", {
        protocolVersion: "2026-01-26",
        appCapabilities: {},
        appInfo: {name:"cmdbox-agent_mcpapps_iframe", version:"1"}
    }).then((r) => {
        mcpapps.theme(r?.hostContext);
        mcpapps.assets(r?.hostCapabilities?.message?.baseurl);
        mcpapps.notify("ui/notifications/initialized", dimensions());
    }).catch((e) => mcpapps.warn(`Unable to connect to the client.${e.message}`));
};
window.addEventListener("DOMContentLoaded", mcpapps.init);
