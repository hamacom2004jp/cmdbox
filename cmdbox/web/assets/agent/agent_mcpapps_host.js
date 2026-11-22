const mcpapps_host = {};

const REQUEST_TIMEOUT = 60000;
const JSON_RPC_VERSION = "2.0";
const JSON_RPC_ERROR_CODE = -32603;

/**
 * cmdbox.change_color_mode をグローバルにラップして、実行時にテーマ変更を通知します
 */
(() => {
    if (typeof cmdbox === 'undefined' || typeof cmdbox.change_color_mode !== 'function') {
        return;
    }
    
    const originalChangeColorMode = cmdbox.change_color_mode;
    let isWrapped = false;
    
    cmdbox.change_color_mode = async function(...args) {
        const result = await originalChangeColorMode.apply(this, args);
        const newTheme = document.documentElement.dataset.bsTheme || 'dark';
        // すべてのアクティブなブリッジにテーマ変更を通知
        if (typeof window.mcpapps_bridges !== 'undefined') {
            window.mcpapps_bridges.forEach(bridge => {
                bridge.notify('ui/notifications/host-context-changed', { theme: newTheme });
            });
        }
        return result;
    };
    const consolePanel = document.querySelector('.console-panel');
    if (consolePanel) {
        const resizeObserver = new ResizeObserver(() => {
            const iframes = consolePanel.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                // iframe のブリッジを取得してサイズをリクエスト
                if (iframe.mcpBridge) {
                    iframe.mcpBridge.request('ui/get-size', {}).then(result => {
                        if (result?.height && Number.isFinite(result.height)) {
                            if(iframe.style.height !== `${Math.round(result.height)}px`) {
                                iframe.style.height = `${Math.round(result.height)}px`;
                            }
                        }
                    }).catch(error => {
                        console.warn(`Failed to get size from iframe: ${error.message}`);
                    });
                }
            });
        });
        resizeObserver.observe(consolePanel);
    }
})();

/**
 * MCP Apps プロトコルの JSON-RPC 2.0 ブリッジを作成します
 * @param {HTMLIFrameElement} iframeElement - 通信対象の iframe 要素
 * @param {Object} options - ブリッジ設定オプション
 * @param {Object} options.serverInfo - MCP サーバー情報
 * @param {any} options.toolResult - 初期ツール結果（初期化時に iframe に送信）
 * @returns {Object} JSON-RPC ブリッジ（on, request, notify, connect, disconnect メソッドを持つ）
 */
function createMCPBridge(iframeElement, options = {}) {
    let nextRequestId = 1;
    const pendingRequests = {};
    const listeners = {};

    /**
     * iframe へ JSON-RPC メッセージを送信します
     * @param {Object} message - JSON-RPC メッセージオブジェクト
     */
    function postMessage(message) {
        iframeElement.contentWindow?.postMessage(message, '*');
    }

    /**
     * JSON-RPC 2.0 レスポンスを送信します
     * @param {number|string} id - リクエストの ID
     * @param {any} result - レスポンス結果
     */
    function sendResponse(id, result) {
        postMessage({ jsonrpc: JSON_RPC_VERSION, id, result });
    }

    /**
     * JSON-RPC 2.0 エラーレスポンスを送信します
     * @param {number|string} id - リクエストの ID
     * @param {Error} error - エラーオブジェクト
     */
    function sendError(id, error) {
        postMessage({
            jsonrpc: JSON_RPC_VERSION,
            id,
            error: {
                code: JSON_RPC_ERROR_CODE,
                message: error?.message || String(error)
            }
        });
    }

    /**
     * iframe のサイズを変更します
     * @param {Object} params - サイズ情報
     * @param {number} params.width - 希望幅（ピクセル）
     * @param {number} params.height - 希望高さ（ピクセル）
     */
    function resize(params = {}) {
        const width = Number(params.width);
        const height = Number(params.height);
        const maxWidth = iframeElement.parentElement?.clientWidth || window.innerWidth;
        /*if (Number.isFinite(width) && width > 0) {
            iframeElement.style.width = `${Math.min(Math.round(width), maxWidth)}px`;
        }*/
        if (Number.isFinite(height) && height > 0) {
            iframeElement.style.height = `${Math.max(1, Math.round(height))}px`;
        }
    }

    /**
     * ui/initialize リクエストを処理し、ホスト文脈を iframe に返します
     * @param {Object} message - JSON-RPC リクエストメッセージ
     */
    function initialize(message) {
        const protocolVersion = message.params?.protocolVersion || '2026-01-26';
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const port = window.location.port;
        const path = window.location.pathname.replace(/\/agent$/, '');
        sendResponse(message.id, {
            protocolVersion,
            hostCapabilities: {
                tools: {},
                message: {
                    baseurl: `${protocol}//${host}${port ? `:${port}` : ''}${path}`
                }
            },
            hostContext: {
                theme: document.documentElement.dataset.bsTheme || 'dark',
                containerDimensions: {
                    width: iframeElement.parentElement?.clientWidth || window.innerWidth,
                    height: iframeElement.parentElement?.clientHeight || null
                },
                locale: document.documentElement.lang || navigator.language
            },
            hostInfo: {
                name: 'cmdbox-agent',
                version: '1'
            }
        });
        if (options.toolResult) {
            notify('ui/notifications/tool-result', options.toolResult);
        }
    }

    /**
     * tools/call リクエストを処理し、MCP サーバーでツールを実行します
     * @param {Object} message - JSON-RPC リクエストメッセージ（params に name と arguments を含む）
     */
    function callTool(message) {
        mcpapps_host.executeToolOnServer(message.params || {}, options.serverInfo || {})
            .then((result) => sendResponse(message.id, result))
            .catch((error) => sendError(message.id, error));
    }

    /**
     * JSON-RPC リクエストメッセージを処理します
     * @param {Object} message - JSON-RPC リクエストメッセージ
     */
    function handleRequest(message) {
        if (message.method === 'ui/initialize') {
            initialize(message);
            return;
        }
        if (message.method === 'tools/call' || message.method === 'tool/call') {
            callTool(message);
            return;
        }
        sendError(message.id, new Error(`Unknown method: ${message.method}`));
    }

    /**
     * JSON-RPC レスポンスメッセージを処理し、待機中のリクエストを解決します
     * @param {Object} message - JSON-RPC レスポンスメッセージ
     */
    function handleResponse(message) {
        const pending = pendingRequests[message.id];
        if (!pending) return;
        clearTimeout(pending.timeout);
        delete pendingRequests[message.id];
        if (message.error) {
            pending.reject(new Error(message.error.message));
        } else {
            pending.resolve(message.result);
        }
    }

    /**
     * JSON-RPC 通知メッセージを処理します（レスポンス不要）
     * @param {Object} message - JSON-RPC 通知メッセージ
     */
    function handleNotification(message) {
        if (message.method === 'ui/notifications/size-changed' ||
            message.method === 'ui/notifications/initialized') {
            resize(message.params);
        }
        (listeners[message.method] || []).forEach((callback) => {
            try {
                callback(message.params);
            } catch (error) {
                console.error(`Error in listener for ${message.method}:`, error);
            }
        });
    }

    /**
     * window の message イベントハンドラー
     * @param {MessageEvent} event - postMessage から受信したイベント
     */
    function onMessage(event) {
        if (event.source !== iframeElement.contentWindow) return;
        const message = event.data;
        if (!message || message.jsonrpc !== JSON_RPC_VERSION) return;
        if (message.method && message.id !== undefined) {
            handleRequest(message);
        } else if (message.id !== undefined) {
            handleResponse(message);
        } else if (message.method) {
            handleNotification(message);
        }
    }

    /**
     * JSON-RPC リクエストを送信し、レスポンスを待機します
     * @param {string} method - JSON-RPC メソッド名
     * @param {Object} params - メソッドパラメータ
     * @returns {Promise<any>} - レスポンス結果
     */
    function request(method, params) {
        return new Promise((resolve, reject) => {
            const id = nextRequestId++;
            const timeout = setTimeout(() => {
                delete pendingRequests[id];
                reject(new Error(`Request timeout for ${method}`));
            }, REQUEST_TIMEOUT);
            pendingRequests[id] = { resolve, reject, timeout };
            postMessage({ jsonrpc: JSON_RPC_VERSION, id, method, params });
        });
    }

    /**
     * JSON-RPC 通知を送信します（レスポンス不要）
     * @param {string} method - JSON-RPC メソッド名
     * @param {Object} params - メソッドパラメータ
     */
    function notify(method, params) {
        postMessage({ jsonrpc: JSON_RPC_VERSION, method, params });
    }

    return {
        /**
         * JSON-RPC 通知に対するリスナーを登録します
         * @param {string} method - 通知のメソッド名
         * @param {Function} callback - コールバック関数
         */
        on(method, callback) {
            listeners[method] ||= [];
            listeners[method].push(callback);
        },
        /** JSON-RPC リクエストを送信してレスポンスを待機する */
        request,
        /** JSON-RPC 通知を送信する（レスポンス不要） */
        notify,
        /**
         * iframe との message リスナーを接続します
         * @returns {Promise<void>}
         */
        connect() {
            window.addEventListener('message', onMessage);
            // ブリッジをグローバルリストに登録（テーマ変更通知用）
            if (!window.mcpapps_bridges) {
                window.mcpapps_bridges = [];
            }
            window.mcpapps_bridges.push(this);
            return Promise.resolve();
        },
        /**
         * iframe との message リスナーを切断します
         */
        disconnect() {
            window.removeEventListener('message', onMessage);
            // ブリッジをグローバルリストから削除
            if (window.mcpapps_bridges) {
                const index = window.mcpapps_bridges.indexOf(this);
                if (index > -1) {
                    window.mcpapps_bridges.splice(index, 1);
                }
            }
        }
    };
}

/**
 * MCP Apps UI を iframe で初期化します
 * @param {HTMLIFrameElement} iframeElement - 初期化対象の iframe 要素
 * @param {Object} options - 初期化オプション
 * @param {Object} options.serverInfo - MCP サーバー情報（provider, mcpserver_name など）
 * @param {any} options.toolResult - 初期化完了後に iframe に配信するツール結果
 * @returns {Promise<Object>} - 初期化完了後のブリッジオブジェクト
 */
mcpapps_host.setupMCPApp = function(iframeElement, options = {}) {
    const bridge = createMCPBridge(iframeElement, options);
    iframeElement.mcpBridge = bridge;
    return bridge.connect().then(() => bridge);
};

/**
 * MCP サーバーでツールを実行します
 * @param {Object} params - ツール実行パラメータ
 * @param {string} params.name - 実行するツールの名前
 * @param {Object} params.arguments - ツールの引数
 * @param {Object} serverInfo - MCP サーバー情報
 * @param {string} serverInfo.mcpserver_name - MCP サーバー設定名
 * @param {string} serverInfo.provider - MCP サーバープロバイダー名（設定名の代替）
 * @returns {Promise<any>} - ツール実行結果
 * @throws {Error} ツール実行に失敗した場合
 */
mcpapps_host.executeToolOnServer = async function(params, serverInfo) {
    if (!params.name) throw new Error('Tool name is required.');
    const mcpserverName = serverInfo.mcpserver_name || serverInfo.provider;
    if (!mcpserverName) throw new Error('MCP server configuration is unavailable.');

    const configResponse = await agentView.exec_cmd('agent', 'mcpsv_load', {
        mcpserver_name: mcpserverName
    }, null, false);
    const config = configResponse?.success;
    if (!config) throw new Error(`MCP server '${mcpserverName}' could not be loaded.`);

    let apikey = config.mcpserver_apikey;
    if (config.mcpserver_delegated_auth) {
        const user = await cmdbox.user_info();
        const keys = Object.values(user?.apikeys || {}).flat();
        apikey = keys[0] || apikey;
    }
    const response = await agentView.exec_cmd('agent', 'mcp_client', {
        mcpserver_name: mcpserverName,
        mcpserver_url: config.mcpserver_url,
        mcpserver_apikey: apikey,
        mcpserver_transport: config.mcpserver_transport,
        operation: 'call_tool',
        tool_name: params.name,
        tool_args: params.arguments || {},
        mcp_timeout: 60
    }, null, false);
    if (!response?.success) throw new Error(response?.warn || `MCP tool '${params.name}' failed.`);
    return response.success;
};