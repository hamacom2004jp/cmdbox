const mcpapps_host = {};

// JSON-RPC 2.0準拠のMCPプロトコル実装
mcpapps_host.setupMCPApp = async (iframeElement, serverInfo) => {
    let nextRequestId = 1;
    const pendingRequests = {};
    const listeners = {};
    const app_title = document.getElementById('app_title').textContent;
    const app_version = document.getElementById('app_version').textContent;

    const bridge = {
        // メッセージリスナーを登録
        on: (method, callback) => {
            if (!listeners[method]) {
                listeners[method] = [];
            }
            listeners[method].push(callback);
        },

        // JSON-RPC 2.0リクエストを送信（レスポンス待機）
        request: (method, params) => {
            return new Promise((resolve, reject) => {
                const id = nextRequestId++;
                pendingRequests[id] = { resolve, reject, timeout: setTimeout(() => {
                    delete pendingRequests[id];
                    reject(new Error(`Request timeout for ${method}`));
                }, 10000) };

                iframeElement.contentWindow.postMessage({
                    jsonrpc: "2.0",
                    id,
                    method,
                    params
                }, '*');
            });
        },

        // JSON-RPC 2.0通知を送信（レスポンス不要）
        notify: (method, params) => {
            iframeElement.contentWindow.postMessage({
                jsonrpc: "2.0",
                method,
                params
            }, '*');
        },

        // メッセージハンドラー
        connect: async () => {
            window.addEventListener('message', (event) => {
                if (event.source !== iframeElement.contentWindow) return;

                const message = event.data;
                if (!message || !message.jsonrpc) return;

                console.log("iframeからのメッセージ:", message);

                // リクエストの場合
                if (message.method && message.id !== undefined) {
                    bridge._handleRequest(message);
                }
                // レスポンスの場合
                else if (message.id !== undefined) {
                    bridge._handleResponse(message);
                }
                // 通知の場合
                else if (message.method) {
                    bridge._handleNotification(message);
                }
            });

            console.log("MCP Appとの通信が確立されました");
        },

        _handleRequest: async (message) => {
            const { id, method, params } = message;
            try {
                let result;
                if (method === 'ui/initialize') {
                    result = await mcpapps_host.executeToolOnServer(params.name, params.arguments);
                } else if (method === 'tools/call') {
                    result = await mcpapps_host.executeToolOnServer(params.name, params.arguments);
                } else {
                    throw new Error(`Unknown method: ${method}`);
                }

                // レスポンスを送信
                iframeElement.contentWindow.postMessage({
                    jsonrpc: "2.0",
                    id,
                    result
                }, '*');
            } catch (error) {
                // エラーレスポンスを送信
                iframeElement.contentWindow.postMessage({
                    jsonrpc: "2.0",
                    id,
                    error: {
                        code: -32603,
                        message: error.message
                    }
                }, '*');
            }
        },

        _handleResponse: (message) => {
            const { id, result, error } = message;
            const pending = pendingRequests[id];
            if (!pending) return;

            clearTimeout(pending.timeout);
            delete pendingRequests[id];

            if (error) {
                pending.reject(new Error(error.message));
            } else {
                pending.resolve(result);
            }
        },

        _handleNotification: (message) => {
            const { method, params } = message;
            if (listeners[method]) {
                listeners[method].forEach(callback => {
                    try {
                        callback(params);
                    } catch (error) {
                        console.error(`Error in listener for ${method}:`, error);
                    }
                });
            }
        }
    };

    // リサイズ通知をリッスン
    bridge.on('notifications/resources/updated', (params) => {
        console.log("Resources updated:", params);
    });

    // 接続を確立
    await bridge.connect();

    return bridge;
};

mcpapps_host.executeToolOnServer = async function(toolName, args) {
    // cmdbox側のMCPクライアント経由で実際のMCPサーバーにツール実行を転送
    console.log(`Executing tool: ${toolName}`, args);
    return { content: [{ type: "text", text: "実行結果" }] };
};