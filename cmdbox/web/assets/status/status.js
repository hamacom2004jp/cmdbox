/**
 * Status Page Logic
 * Contains all statusPage object definitions and methods
 */

const statusPage = {
    activeMenu: 'server',
    timer: null,
    autoRefreshInterval: 60000,
    logTailOffset: {},
    logTailCache: {},
    logTailNewStart: {},
    logGrepQuery: ''
};

// ローカルストレージで利用するキーを定義する
statusPage.storageKeys = {
    activeMenu: 'statusPage_activeMenu',
    autoRefreshInterval: 'statusPage_auto_refresh_interval',
    svlogScope: 'statusPage_svlog_scope',
    svlogFilePrefix: 'statusPage_svlog_file_'
};

// ローカルストレージから値を取得する（失敗時は既定値を返す）
statusPage.readStorage = (key, fallback = '') => {
    try {
        const v = localStorage.getItem(key);
        return v == null ? fallback : v;
    } catch (e) {
        return fallback;
    }
};

// ローカルストレージへ値を書き込む（失敗時は無視する）
statusPage.writeStorage = (key, value) => {
    if (!key || value == null || value === '') return;
    try {
        localStorage.setItem(key, String(value));
    } catch (e) {
        // ignore localStorage errors
    }
};

// 数値を3桁区切りで整形する
statusPage.fmtNum = (n) => {
    if (n == null || Number.isNaN(Number(n))) return '-';
    return Number(n).toLocaleString();
};

// 日時文字列をロケール形式に整形する
statusPage.fmtDate = (v) => {
    if (!v) return '-';
    const dt = new Date(v);
    if (Number.isNaN(dt.getTime())) return String(v);
    return dt.toLocaleString();
};

// バイト数を人間向けの単位に変換する
statusPage.fmtBytes = (n) => {
    if (n == null || Number.isNaN(Number(n))) return '-';
    const size = Number(n);
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
    return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
};

// コマンド応答から配列データを取り出す
statusPage.asRows = (res) => {
    if (!res) return [];
    const first = Array.isArray(res) ? res[0] : res;
    if (!first || !first.success) return [];
    // success が直接配列（server list など）または data プロパティを持つ場合
    if (Array.isArray(first.success)) return first.success;
    if (first.success.data && Array.isArray(first.success.data)) return first.success.data;
    return [];
};

// 文字列を HTML エスケープする
statusPage.escapeHtml = (text) => {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// 指定メニューを表示して選択状態を保存する
statusPage.showMenu = (menu) => {
    statusPage.activeMenu = menu;
    $('.menu-content').removeClass('active');
    $(`#content_${menu}`).addClass('active');
    $('.btn-nav-action').removeClass('active');
    $(`#menu_${menu}`).addClass('active');
    statusPage.writeStorage(statusPage.storageKeys.activeMenu, menu);
};

// サイドバーの開閉とメニュー切り替えイベントを初期化する
statusPage.initSidebar = () => {
    const sidebar = $('#navSidebar');
    const body = $('body');

    $('#btn_toggle_sidebar').off('click').on('click', () => {
        const expanded = !sidebar.hasClass('expanded');
        sidebar.toggleClass('expanded', expanded);
        body.toggleClass('status-sidebar-expanded', expanded);
    });

    ['server', 'systemlog', 'session', 'limiter', 'storage', 'audit'].forEach((menu) => {
        $(`#menu_${menu}`).off('click').on('click', async () => {
            statusPage.showMenu(menu);
            await statusPage.refreshActive(false);
        });
    });
};

// scope とファイルパスから tail 管理用キーを作る
statusPage.tailKey = (scope, svpath) => `${scope}:${svpath}`;

// file_list 応答から .logs 配下のファイル一覧を抽出する
statusPage.getLogListRows = (res) => {
    const first = Array.isArray(res) ? res[0] : res;
    if (!first || !first.success || typeof first.success !== 'object') return [];
    const files = [];
    Object.values(first.success).forEach((node) => {
        const children = node && node.children ? node.children : {};
        Object.values(children).forEach((child) => {
            if (!child || child.is_dir) return;
            const p = String(child.path || '');
            if (!p.startsWith('/.logs/')) return;
            files.push(p);
        });
    });
    files.sort((a, b) => a.localeCompare(b));
    return files;
};

// System Log のファイル一覧を取得して選択状態を復元する
statusPage.loadLogFileList = async () => {
    const scope = $('#svlog_scope').val() || 'server';
    const fileStorageKey = `${statusPage.storageKeys.svlogFilePrefix}${scope}`;
    statusPage.writeStorage(statusPage.storageKeys.svlogScope, scope);
    const oldFile = $('#svlog_file').val() || '';
    const savedFile = statusPage.readStorage(fileStorageKey, '');
    const res = await cmdbox.sv_exec_cmd({
        mode: 'client',
        cmd: 'file_list',
        scope: scope,
        svpath: '/.logs',
        fwpath: '/.logs',
        listregs: '.*\\.log(?:\\..+)?$'
    });
    const files = statusPage.getLogListRows(res);
    const sel = $('#svlog_file').empty();
    if (files.length === 0) {
        sel.append('<option value="">(no log files)</option>');
        $('#btn_svlog_download').prop('disabled', true);
        return '';
    }
    files.forEach((p) => {
        $('<option></option>').val(p).text(p).appendTo(sel);
    });
    let nextFile = files[0];
    if (oldFile && files.includes(oldFile)) nextFile = oldFile;
    else if (savedFile && files.includes(savedFile)) nextFile = savedFile;
    sel.val(nextFile);
    statusPage.writeStorage(fileStorageKey, nextFile);
    // ボタンの有効/無効を切り替える
    $('#btn_svlog_download').prop('disabled', !nextFile);
    if (nextFile !== oldFile) {
        statusPage.logTailOffset[statusPage.tailKey(scope, nextFile)] = -1;
    }
    return nextFile;
};

// 選択中ログの差分を取得し、tail 表示を更新する
statusPage.loadLogTail = async (isinit=false) => {
    const scope = $('#svlog_scope').val() || 'server';
    const fileStorageKey = `${statusPage.storageKeys.svlogFilePrefix}${scope}`;
    let svpath = $('#svlog_file').val() || '';
    if (!svpath) {
        svpath = await statusPage.loadLogFileList();
    }
    if (!svpath) {
        $('#svlog_meta').text('no log file');
        $('#svlog_tail').text('');
        return;
    }
    $('#svlog_updated').text(new Date().toLocaleString());
    const key = statusPage.tailKey(scope, svpath);
    statusPage.writeStorage(statusPage.storageKeys.svlogScope, scope);
    statusPage.writeStorage(fileStorageKey, svpath);
    const currentOffset = Number.isFinite(Number(statusPage.logTailOffset[key])) ? Number(statusPage.logTailOffset[key]) : -1;
    const res = await cmdbox.sv_exec_cmd({
        mode: 'client',
        cmd: 'file_tail',
        scope: scope,
        svpath: svpath,
        fwpath: '/.logs',
        offset: currentOffset,
        lines: 200,
        max_bytes: 131072,
        encoding: 'utf-8'
    });
    const first = Array.isArray(res) ? res[0] : res;
    if (!first || !first.success) {
        $('#svlog_meta').text('failed to load log tail');
        return;
    }
    const data = first.success;
    const nextOffset = Number.isFinite(Number(data.offset)) ? Number(data.offset) : currentOffset;
    if (!data.not_modified) {
        const incoming = String(data.data || '');
        const prev = String(statusPage.logTailCache[key] || '');
        const prevLines = prev.length > 0 ? prev.split(/\r?\n/) : [];
        let nextText = prev;
        let newStart = -1;
        if (currentOffset >= 0 && !data.rotated && incoming.length > 0) {
            const joined = prev.length > 0 ? `${prev}${prev.endsWith('\n') ? '' : '\n'}${incoming}` : incoming;
            const maxLines = 2000;
            const lines = joined.split(/\r?\n/);
            const incomingStart = prevLines.length;
            if (lines.length > maxLines) {
                const dropped = lines.length - maxLines;
                nextText = lines.slice(-maxLines).join('\n');
                newStart = Math.max(0, incomingStart - dropped);
            } else {
                nextText = joined;
                newStart = incomingStart;
            }
        } else {
            nextText = incoming;
            newStart = -1;
        }
        statusPage.logTailCache[key] = nextText;
        statusPage.logTailNewStart[key] = newStart;
        statusPage.renderLogTail(isinit);
    }
    statusPage.logTailOffset[key] = nextOffset;
    const sizeStr = statusPage.fmtBytes(data.file_size || 0);
    const rotated = data.rotated ? ' (rotated)' : '';
    $('#svlog_meta').text(`${scope}:${svpath} / ${sizeStr}${rotated} / offset=${nextOffset}`);
};

// 表示済みログに対してのみ grep 相当の絞り込みを適用して描画する
statusPage.renderLogTail = (isinit=false) => {
    const scope = $('#svlog_scope').val() || 'server';
    const svpath = $('#svlog_file').val() || '';
    const key = statusPage.tailKey(scope, svpath);
    const raw = String(statusPage.logTailCache[key] || '');
    const newStart = Number.isFinite(Number(statusPage.logTailNewStart[key])) ? Number(statusPage.logTailNewStart[key]) : -1;
    const q = String(statusPage.logGrepQuery || '').trim();
    const lines = raw.split(/\r?\n/);
    let view = lines.map((line, idx) => ({ line, idx }));
    if (q.length > 0) {
        const qLower = q.toLowerCase();
        view = view.filter((v) => v.line.toLowerCase().includes(qLower));
    }

    const appendLine = (parent, line, keyword) => {
        if (!keyword) {
            parent.append(document.createTextNode(line));
            return;
        }
        const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const re = new RegExp(`(${escaped})`, 'ig');
        const parts = line.split(re);
        parts.forEach((part) => {
            if (part.length === 0) return;
            if (part.toLowerCase() === keyword.toLowerCase()) {
                $('<span class="tail-log-kwd"></span>').text(part).appendTo(parent);
            } else {
                parent.append(document.createTextNode(part));
            }
        });
    };

    const tail = $('#svlog_tail');
    //tail.empty();
    view.forEach((v, i) => {
        const isNew = newStart >= 0 && v.idx >= newStart;
        if (isNew || isinit) {
            const lineWrap = $('<span class="tail-log-new"></span>').appendTo(tail);
            appendLine(lineWrap, v.line, q);
        } else {
            return;
            appendLine(tail, v.line, q);
        }
        if (i < view.length - 1) {
            tail.append(document.createTextNode('\n'));
        }
    });
    if (tail.length > 0) {
        tail.scrollTop(tail.prop('scrollHeight'));
    }
};

// System Log の scope/file セレクタ変更イベントを初期化する
statusPage.initServerLogControls = () => {
    // ダウンロードボタンを初期状態で無効に
    $('#btn_svlog_download').prop('disabled', true);
    
    const savedScope = statusPage.readStorage(statusPage.storageKeys.svlogScope, '');
    if (savedScope && $('#svlog_scope option[value="' + savedScope + '"]').length > 0) {
        $('#svlog_scope').val(savedScope);
    }

    $('#svlog_scope').off('change').on('change', async () => {
        const scope = $('#svlog_scope').val() || 'server';
        const svpath = $('#svlog_file').val() || '';
        statusPage.writeStorage(statusPage.storageKeys.svlogScope, scope);
        $('#svlog_tail').text('');
        statusPage.logGrepQuery = '';
        $('#svlog_grep').val('');
        // ダウンロードボタンを一時的に無効に
        $('#btn_svlog_download').prop('disabled', true);
        if (svpath) {
            const key = statusPage.tailKey(scope, svpath);
            statusPage.logTailOffset[key] = -1;
        }
        await statusPage.loadLogFileList();
        await statusPage.loadLogTail(true);
    });
    $('#svlog_file').off('change').on('change', async () => {
        const scope = $('#svlog_scope').val() || 'server';
        const svpath = $('#svlog_file').val() || '';
        // ボタンの有効/無効を切り替える
        $('#btn_svlog_download').prop('disabled', !svpath);
        if (!svpath) return;
        const fileStorageKey = `${statusPage.storageKeys.svlogFilePrefix}${scope}`;
        statusPage.writeStorage(statusPage.storageKeys.svlogScope, scope);
        statusPage.writeStorage(fileStorageKey, svpath);
        statusPage.logTailOffset[statusPage.tailKey(scope, svpath)] = -1;
        $('#svlog_tail').text('');
        await statusPage.loadLogTail(true);
    });

    // 表示済みログに対してのみ絞り込みを実行する
    $('#btn_svlog_grep').off('click').on('click', () => {
        statusPage.logGrepQuery = $('#svlog_grep').val() || '';
        statusPage.renderLogTail();
    });
    $('#btn_svlog_grep_clear').off('click').on('click', () => {
        statusPage.logGrepQuery = '';
        $('#svlog_grep').val('');
        statusPage.renderLogTail();
    });
    $('#svlog_grep').off('keydown').on('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            statusPage.logGrepQuery = $('#svlog_grep').val() || '';
            statusPage.renderLogTail();
        }
    });

    // ダウンロードボタンのクリックイベント
    $('#btn_svlog_download').off('click').on('click', async () => {
        const scope = $('#svlog_scope').val() || 'server';
        const svpath = $('#svlog_file').val() || '';
        if (!svpath) return;

        try {
            $('#btn_svlog_download').prop('disabled', true);
            const constr = btoa(`${encodeURIComponent(svpath)}\t${scope}\t0`);
            const basePath = window.location.pathname.slice(0, window.location.pathname.lastIndexOf('/'));
            const downloadPath = `${basePath}/filer/download/${constr}?r=${cmdbox.random_string(8)}`;
            const filename = svpath.split('/').pop() || 'logfile.log';

            const link = $('<a target="_blank"></a>').attr('href', downloadPath).attr('download', filename);
            $('body').append(link);
            link[0].click();
            link.remove();
        } catch (e) {
            console.error('Error downloading log file:', e);
            cmdbox.message({'error': 'Error downloading log file'}, true, true);
        } finally {
            const svpath = $('#svlog_file').val() || '';
            $('#btn_svlog_download').prop('disabled', !svpath);
        }
    });
};

// 画面上部の自動更新間隔を復元する
statusPage.loadAutoRefreshInterval = async () => {
    try {
        const saved = statusPage.readStorage(statusPage.storageKeys.autoRefreshInterval, '');
        if (saved) {
            statusPage.autoRefreshInterval = parseInt(saved, 10);
            $('#status_auto_refresh_interval').val(statusPage.autoRefreshInterval);
        }
    } catch (e) {
        console.warn('Failed to load auto refresh interval:', e);
    }
};

// 画面上部の自動更新間隔を保存する
statusPage.saveAutoRefreshInterval = async (interval) => {
    try {
        statusPage.writeStorage(statusPage.storageKeys.autoRefreshInterval, interval);
    } catch (e) {
        console.warn('Failed to save auto refresh interval:', e);
    }
};

// 自動更新間隔セレクタの変更イベントを初期化する
statusPage.initAutoRefreshSelector = () => {
    $('#status_auto_refresh_interval').off('change').on('change', function () {
        const interval = parseInt($(this).val(), 10);
        statusPage.autoRefreshInterval = interval;
        statusPage.saveAutoRefreshInterval(interval);
        statusPage.startAutoRefresh();
    });
};

// サーバー状況を取得してテーブルに描画する
statusPage.loadServer = async () => {
    const rows = statusPage.asRows(await cmdbox.sv_exec_cmd({ mode: 'server', cmd: 'list' }));
    $('#sv_total').text(statusPage.fmtNum(rows.length));
    $('#sv_updated').text(new Date().toLocaleString());

    const receiveTotal = rows.reduce((acc, row) => acc + Number(row.receive_cnt || 0), 0);
    $('#sv_receive').text(statusPage.fmtNum(receiveTotal));

    const body = $('#sv_rows').empty();
    rows.forEach((row) => {
        const tr = $(`<tr>
            <td>${row.svname || '-'}</td>
            <td>${row.status || '-'}</td>
            <td class="text-end">${statusPage.fmtNum(row.active_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.success_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.warn_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.error_cnt)}</td>
            <td></td>
        </tr>`);
        
        const activeTasksTd = tr.find('td:last');
        activeTasksTd.text('');
        if (row.active_tasks && (Array.isArray(row.active_tasks) ? row.active_tasks.length : Object.keys(row.active_tasks).length)) {
            const tasks = Array.isArray(row.active_tasks) ? row.active_tasks : [row.active_tasks];
            const table = $('<table class="table table-sm mb-0">'
                           + '<thead><tr><th>Task</th><th>Status</th><th>ID</th><th>Start Time</th><th>Proc Time</th><th>Message</th></tr></thead>'
                           + '<tbody></tbody></table>');
            const tbody = table.find('tbody');
            tasks.forEach(task => {
                const obj = typeof task === 'string' ? JSON.parse(task) : task;
                $(`<tr>
                    <td class="small">${obj.task || '-'}</td>
                    <td class="small">${obj.status || '-'}</td>
                    <td class="small">${obj.id || '-'}</td>
                    <td class="small">${obj.start_tm || '-'}</td>
                    <td class="small">${obj.proc_cnt ? (obj.proc_cnt * 1000).toFixed(0) + ' ms' : '-'}</td>
                    <td class="small">${obj.msg || '-'}</td>
                </tr>`).appendTo(tbody);
            });
            activeTasksTd.append(table);
        }
        body.append(tr);
    });
    if (rows.length === 0) {
        body.append('<tr><td colspan="7" class="text-body-secondary">no data</td></tr>');
    }
};

// System Log の一覧とtail表示をまとめて更新する
statusPage.loadSystemLog = async (isinit=false) => {
    await statusPage.loadLogFileList();
    await statusPage.loadLogTail(isinit);
};

// Limiter 情報を取得して利用率一覧を描画する
statusPage.loadLimiter = async () => {
    const calcRatio = (current, max) => {
        const c = Number(current);
        const m = Number(max);
        if (!Number.isFinite(c) || !Number.isFinite(m) || m <= 0) return null;
        return c / m;
    };
    const createConstraints = (lm) => {
        const counter = lm && lm.counter ? lm.counter : {};
        const defs = [
            { key: 'total_count', label: 'Count', max_key: 'max_total_count' },
            { key: 'total_time', label: 'Time', max_key: 'max_total_time' },
            { key: 'total_input', label: 'Input', max_key: 'max_total_input' },
            { key: 'total_process', label: 'Process', max_key: 'max_total_process' },
            { key: 'total_output', label: 'Output', max_key: 'max_total_output' },
            { key: 'total_credits', label: 'Credits', max_key: 'max_total_credits' },
            { key: 'total_registrations', label: 'Registrations', max_key: 'max_registrations' }
        ];
        return defs.map((d) => ({
            label: d.label,
            current: counter[d.key] || 0,
            max: lm[d.max_key] || 0,
            ratio: calcRatio(counter[d.key], lm[d.max_key])
        }));
    };

    const rows = statusPage.asRows(await cmdbox.sv_exec_cmd({
        mode: 'limiter',
        cmd: 'targets',
        scope: 'server',
        reflesh_counter: true
    }));

    const limiters = [];
    rows.forEach((target) => {
        (target.limiters || []).forEach((lm) => {
            const constraints = createConstraints(lm);
            const maxRatio = Math.max(...constraints.map(c => c.ratio || 0));
            limiters.push({
                name: lm.limiter_name || '-',
                constraints: constraints,
                maxRatio: maxRatio,
                lastReset: lm.counter ? lm.counter.last_reset : null
            });
        });
    });

    $('#lm_total').text(statusPage.fmtNum(limiters.length));
    $('#lm_50to80').text(statusPage.fmtNum(limiters.filter((lm) => lm.maxRatio >= 0.5 && lm.maxRatio < 0.8).length));
    $('#lm_over80').text(statusPage.fmtNum(limiters.filter((lm) => lm.maxRatio >= 0.8).length));
    $('#lm_updated').text(new Date().toLocaleString());

    const body = $('#lm_rows').empty();
    
    if (limiters.length === 0) {
        body.append('<table class="table table-sm table-flat table-hover"><tbody><tr><td colspan="8" class="text-body-secondary">no data</td></tr></tbody></table>');
        return;
    }

    // テーブルヘッダーを作成
    let tableHtml = `<table class="table table-sm table-flat table-hover">
        <thead><tr>
            <th>Limiter</th>
            <th class="text-end">Count</th>
            <th class="text-end">Time</th>
            <th class="text-end">Input</th>
            <th class="text-end">Process</th>
            <th class="text-end">Output</th>
            <th class="text-end">Credits</th>
            <th class="text-end">Registrations</th>
        </tr></thead>
        <tbody>`;

    limiters.forEach((lm) => {
        const constraintMap = {};
        lm.constraints.forEach((c) => {
            constraintMap[c.label] = c;
        });

        const labels = ['Count', 'Time', 'Input', 'Process', 'Output', 'Credits', 'Registrations'];
        let row = `<tr><td>${lm.name}</td>`;

        labels.forEach((label) => {
            const constraint = constraintMap[label];
            let cellContent = '—';
            if (constraint && constraint.max > 0) {
                const pct = Math.round(constraint.ratio * 1000) / 10;
                const cls = pct >= 90 ? 'text-danger' : (pct >= 80 ? 'text-warning' : '');
                cellContent = `<span class="${cls}">${pct}% ( ${constraint.current} / ${constraint.max} )</span>`;
            }
            row += `<td class="text-end">${cellContent}</td>`;
        });

        row += `</tr>`;
        tableHtml += row;
    });

    tableHtml += `</tbody></table>`;
    body.append(tableHtml);
};

// 指定スコープのストレージ集計を取得する
statusPage.loadStorageScope = async (scope) => {
    const res = await cmdbox.sv_exec_cmd({
        mode: 'client',
        cmd: 'file_list',
        scope: scope,
        svpath: '/',
        summary: true,
        listregs: '.*'
    });
    const first = Array.isArray(res) ? res[0] : res;
    const totalOut = { scope: scope, level: 'total', name: `${scope} (total)`, files: 0, dirs: 0, bytes: 0, latest: 0 };
    if (!first || !first.success || typeof first.success !== 'object') {
        return [totalOut];
    }
    // ルートノードから全体の統計を取得
    const rootNode = first.success['_'];
    if (rootNode) {
        totalOut.files = rootNode.files_cnt || 0;
        totalOut.dirs = rootNode.dirs_cnt || 0;
        totalOut.bytes = rootNode.dirs_size || 0;
        if (rootNode.dirs_last) {
            const t = new Date(rootNode.dirs_last).getTime();
            if (!Number.isNaN(t)) totalOut.latest = t;
        }
    }
    // 全体統計のみを返す
    return [totalOut];
};

// 全スコープのストレージ集計を取得して表示する
statusPage.loadStorage = async () => {
    const scopes = ['server', 'client', 'current'];
    const allRows = [];
    
    for (const scope of scopes) {
        try {
            const rows = await statusPage.loadStorageScope(scope);
            allRows.push(...rows);
        } catch (e) {
            allRows.push({ scope: scope, level: 'total', name: `${scope} (error)`, files: 0, dirs: 0, bytes: 0, latest: 0, error: String(e) });
        }
    }
    
    const totalFiles = allRows.filter(r => r.level === 'total').reduce((a, r) => a + r.files, 0);
    const totalDirs = allRows.filter(r => r.level === 'total').reduce((a, r) => a + r.dirs, 0);
    const totalBytes = allRows.filter(r => r.level === 'total').reduce((a, r) => a + r.bytes, 0);
    
    $('#st_files').text(statusPage.fmtNum(totalFiles));
    $('#st_dirs').text(statusPage.fmtNum(totalDirs));
    $('#st_size').text(statusPage.fmtBytes(totalBytes));
    $('#st_updated').text(new Date().toLocaleString());
    
    const body = $('#st_rows').empty();
    allRows.forEach((row) => {
        const cls = row.level === 'total' ? 'storage-row-total' : 'storage-row-folder';
        const indent = row.level === 'total' ? '' : '  ├─ ';
        body.append(`<tr class="${cls}">
            <td><span class="storage-name">${indent}${row.name}</span></td>
            <td class="text-end">${statusPage.fmtNum(row.files)}</td>
            <td class="text-end">${statusPage.fmtNum(row.dirs)}</td>
            <td class="text-end">${statusPage.fmtBytes(row.bytes)}</td>
            <td>${row.latest > 0 ? new Date(row.latest).toLocaleString() : '-'}</td>
        </tr>`);
    });
    
    if (allRows.length === 0) {
        body.append('<tr><td colspan="5" class="text-body-secondary">no data</td></tr>');
    }
};

// 監査ログの最新統計を取得して表示する
statusPage.loadAudit = async () => {
    const payload = { limit: 200, sort: { clmsg_date: 'DESC' } };
    const res = await fetch('audit/rawlog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const content = await res.json();
    const rows = (content && content.success && Array.isArray(content.success.data)) ? content.success.data : [];

    $('#ad_recent').text(statusPage.fmtNum(rows.length));
    const users = new Set(rows.map((row) => row.clmsg_user).filter((v) => v));
    $('#ad_users').text(statusPage.fmtNum(users.size));
    $('#ad_latest').text(rows.length > 0 ? statusPage.fmtDate(rows[0].clmsg_date || rows[0].svmsg_date) : '-');
    $('#ad_updated').text(new Date().toLocaleString());

    const typeCount = {};
    rows.forEach((row) => {
        const t = String(row.audit_type || 'unknown');
        typeCount[t] = (typeCount[t] || 0) + 1;
    });

    const body = $('#ad_rows').empty();
    Object.keys(typeCount).sort((a, b) => typeCount[b] - typeCount[a]).forEach((k) => {
        body.append(`<tr><td>${k}</td><td class="text-end">${statusPage.fmtNum(typeCount[k])}</td></tr>`);
    });
    if (Object.keys(typeCount).length === 0) {
        body.append('<tr><td colspan="2" class="text-body-secondary">no data</td></tr>');
    }
};

// Web セッション一覧を取得して表示する
statusPage.loadSession = async () => {
    try {
        const res = await cmdbox.sv_exec_cmd({
            mode: 'web',
            cmd: 'session_list'
        });
        const first = Array.isArray(res) ? res[0] : res;
        if (!first || !first.success) {
            $('#sess_total').text('-');
            $('#sess_updated').text('-');
            $('#sess_rows').empty().append('<tr><td colspan="4" class="text-body-secondary">Failed to load session data</td></tr>');
            return;
        }
        const data = first.success;
        const sessions = (data.sessions && Array.isArray(data.sessions)) ? data.sessions : [];
        $('#sess_total').text(statusPage.fmtNum(data.session_count || 0));
        $('#sess_updated').text(new Date().toLocaleString());
        const body = $('#sess_rows').empty();
        if (sessions.length === 0) {
            body.append('<tr><td colspan="4" class="text-body-secondary">no active sessions</td></tr>');
            return;
        }
        sessions.forEach((session) => {
            body.append(`<tr>
                <td class="small">${statusPage.escapeHtml(session.session_id || '-')}</td>
                <td class="small">${statusPage.escapeHtml(session.uid || '-')}</td>
                <td class="small">${statusPage.escapeHtml(session.name || '-')}</td>
                <td class="small">${statusPage.escapeHtml((session.groups || []).join(', '))}</td>
                <td class="small">${statusPage.escapeHtml(session.email || '-')}</td>
                <td class="small">${statusPage.escapeHtml(session.last || '-')}</td>
                <td class="small">${statusPage.escapeHtml(session.remaining || '-')}</td>
                <td class="small">${statusPage.escapeHtml(session.clmsg_id || '-')}</td>
            </tr>`);
        });
    } catch (e) {
        $('#sess_total').text('-');
        $('#sess_updated').text('-');
        $('#sess_rows').empty().append(`<tr><td colspan="4" class="text-danger small">${statusPage.escapeHtml(e.toString())}</td></tr>`);
    }
};

// 現在選択中メニューに応じて表示内容を更新する
statusPage.refreshActive = async (isinit=false) => {
    // リフレッシュボタンの状態を変更して読み込み中を示す
    const btn = $('#btn_status_refresh');
    btn.prop('disabled', true);
    const icon = btn.find('i');
    icon.addClass('fa-spin');
    
    try {
        if (statusPage.activeMenu === 'server') await statusPage.loadServer();
        else if (statusPage.activeMenu === 'systemlog') await statusPage.loadSystemLog(isinit);
        else if (statusPage.activeMenu === 'session') await statusPage.loadSession();
        else if (statusPage.activeMenu === 'limiter') await statusPage.loadLimiter();
        else if (statusPage.activeMenu === 'storage') await statusPage.loadStorage();
        else if (statusPage.activeMenu === 'audit') await statusPage.loadAudit();
    } catch (e) {
        cmdbox.message({ error: e.toString() }, true, true);
    } finally {
        // リフレッシュボタンを元に戻す
        btn.prop('disabled', false);
        icon.removeClass('fa-spin');
    }
};

// 自動更新タイマーを開始（既存タイマーは再作成）する
statusPage.startAutoRefresh = () => {
    if (statusPage.timer) clearInterval(statusPage.timer);
    statusPage.timer = setInterval(() => {
        statusPage.refreshActive(false);
    }, statusPage.autoRefreshInterval);
};
