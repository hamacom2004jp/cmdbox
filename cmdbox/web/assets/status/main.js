const statusPage = {
    activeMenu: 'server',
    timer: null,
    autoRefreshInterval: 60000
};

statusPage.fmtNum = (n) => {
    if (n == null || Number.isNaN(Number(n))) return '-';
    return Number(n).toLocaleString();
};

statusPage.fmtDate = (v) => {
    if (!v) return '-';
    const dt = new Date(v);
    if (Number.isNaN(dt.getTime())) return String(v);
    return dt.toLocaleString();
};

statusPage.fmtBytes = (n) => {
    if (n == null || Number.isNaN(Number(n))) return '-';
    const size = Number(n);
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    if (size < 1024 * 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
    return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`;
};

statusPage.asRows = (res) => {
    if (!res) return [];
    const first = Array.isArray(res) ? res[0] : res;
    if (!first || !first.success) return [];
    // success が直接配列（server list など）または data プロパティを持つ場合
    if (Array.isArray(first.success)) return first.success;
    if (first.success.data && Array.isArray(first.success.data)) return first.success.data;
    return [];
};

statusPage.showMenu = (menu) => {
    statusPage.activeMenu = menu;
    $('.menu-content').removeClass('active');
    $(`#content_${menu}`).addClass('active');
    $('.btn-nav-action').removeClass('active');
    $(`#menu_${menu}`).addClass('active');
};

statusPage.initSidebar = () => {
    const sidebar = $('#navSidebar');
    const body = $('body');

    $('#btn_toggle_sidebar').off('click').on('click', () => {
        const expanded = !sidebar.hasClass('expanded');
        sidebar.toggleClass('expanded', expanded);
        body.toggleClass('status-sidebar-expanded', expanded);
    });

    ['server', 'limiter', 'storage', 'audit'].forEach((menu) => {
        $(`#menu_${menu}`).off('click').on('click', async () => {
            statusPage.showMenu(menu);
            await statusPage.refreshActive();
        });
    });
};

statusPage.loadAutoRefreshInterval = async () => {
    try {
        const data = await cmdbox.load_user_data('status_page', 'auto_refresh_interval');
        if (data && data.auto_refresh_interval) {
            statusPage.autoRefreshInterval = parseInt(data.auto_refresh_interval, 10);
            $('#status_auto_refresh_interval').val(statusPage.autoRefreshInterval);
        }
    } catch (e) {
        console.warn('Failed to load auto refresh interval:', e);
    }
};

statusPage.saveAutoRefreshInterval = async (interval) => {
    try {
        await cmdbox.save_user_data('status_page', 'auto_refresh_interval', String(interval));
    } catch (e) {
        console.warn('Failed to save auto refresh interval:', e);
    }
};

statusPage.initAutoRefreshSelector = () => {
    $('#status_auto_refresh_interval').off('change').on('change', function () {
        const interval = parseInt($(this).val(), 10);
        statusPage.autoRefreshInterval = interval;
        statusPage.saveAutoRefreshInterval(interval);
        statusPage.startAutoRefresh();
    });
};

statusPage.renderConnection = async () => {
    const area = $('#status_connection');
    try {
        const res = await fetch('get_server_opt', { method: 'GET' });
        const opt = await res.json();
        area.text(`host=${opt.host}, port=${opt.port}, svname=${opt.svname}, data=${opt.data}, client_only=${opt.client_only}`);
    } catch (e) {
        area.text(`failed to load connection info: ${e}`);
    }
};

statusPage.loadServer = async () => {
    const rows = statusPage.asRows(await cmdbox.sv_exec_cmd({ mode: 'server', cmd: 'list' }));
    $('#sv_total').text(statusPage.fmtNum(rows.length));

    const receiveTotal = rows.reduce((acc, row) => acc + Number(row.receive_cnt || 0), 0);
    $('#sv_receive').text(statusPage.fmtNum(receiveTotal));

    const body = $('#sv_rows').empty();
    rows.forEach((row) => {
        body.append(`<tr>
            <td>${row.svname || '-'}</td>
            <td>${row.status || '-'}</td>
            <td class="text-end">${statusPage.fmtNum(row.active_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.success_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.warn_cnt)}</td>
            <td class="text-end">${statusPage.fmtNum(row.error_cnt)}</td>
        </tr>`);
    });
    if (rows.length === 0) {
        body.append('<tr><td colspan="5" class="text-body-secondary">no data</td></tr>');
    }
};

statusPage.safeRatio = (current, max) => {
    const c = Number(current);
    const m = Number(max);
    if (!Number.isFinite(c) || !Number.isFinite(m) || m <= 0) return null;
    return c / m;
};

statusPage.getLimiterConstraints = (lm) => {
        const counter = lm && lm.counter ? lm.counter : {};
        const constraints = [
            { key: 'total_count', label: 'Count', max_key: 'max_total_count' },
            { key: 'total_time', label: 'Time', max_key: 'max_total_time' },
            { key: 'total_input', label: 'Input', max_key: 'max_total_input' },
            { key: 'total_process', label: 'Process', max_key: 'max_total_process' },
            { key: 'total_output', label: 'Output', max_key: 'max_total_output' },
            { key: 'total_credits', label: 'Credits', max_key: 'max_total_credits' },
            { key: 'total_registrations', label: 'Registrations', max_key: 'max_registrations' }
        ];
        return constraints.map((c) => ({
            label: c.label,
            current: counter[c.key] || 0,
            max: lm[c.max_key] || 0,
            ratio: statusPage.safeRatio(counter[c.key], lm[c.max_key])
        }));
};

statusPage.loadLimiter = async () => {
    const rows = statusPage.asRows(await cmdbox.sv_exec_cmd({
        mode: 'limiter',
        cmd: 'targets',
        scope: 'server',
        reflesh_counter: true
    }));

    const limiters = [];
    rows.forEach((target) => {
        (target.limiters || []).forEach((lm) => {
            const constraints = statusPage.getLimiterConstraints(lm);
            const maxRatio = Math.max(...constraints.map(c => c.ratio || 0));
            limiters.push({
                name: lm.limiter_name || '-',
                constraints: constraints,
                maxRatio: maxRatio,
                lastReset: lm.counter ? lm.counter.last_reset : null
            });
        });
    });

    $('#lm_targets').text(statusPage.fmtNum(rows.length));
    $('#lm_total').text(statusPage.fmtNum(limiters.length));
    $('#lm_over80').text(statusPage.fmtNum(limiters.filter((lm) => lm.maxRatio >= 0.8).length));

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
                cellContent = `<span class="${cls}">${pct}%</span>`;
            }
            row += `<td class="text-end">${cellContent}</td>`;
        });

        row += `</tr>`;
        tableHtml += row;
    });

    tableHtml += `</tbody></table>`;
    body.append(tableHtml);
};

statusPage.flattenTree = (node, out) => {
    if (!node) return;
    const isDir = !!node.is_dir;
    if (isDir) out.dirs += 1;
    else {
        out.files += 1;
        out.bytes += Number(node.size || 0);
    }
    if (node.last) {
        const t = new Date(node.last).getTime();
        if (!Number.isNaN(t) && t > out.latest) out.latest = t;
    }
    const children = node.children || {};
    Object.keys(children).forEach((k) => statusPage.flattenTree(children[k], out));
};

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


statusPage.refreshActive = async () => {
    // リフレッシュボタンの状態を変更して読み込み中を示す
    const btn = $('#btn_status_refresh');
    btn.prop('disabled', true);
    const icon = btn.find('i');
    icon.addClass('fa-spin');
    
    try {
        if (statusPage.activeMenu === 'server') await statusPage.loadServer();
        else if (statusPage.activeMenu === 'limiter') await statusPage.loadLimiter();
        else if (statusPage.activeMenu === 'storage') await statusPage.loadStorage();
        else if (statusPage.activeMenu === 'audit') await statusPage.loadAudit();
        $('#status_last_updated').text(`Last update: ${new Date().toLocaleString()}`);
    } catch (e) {
        cmdbox.message({ error: e.toString() }, true, true);
    } finally {
        // リフレッシュボタンを元に戻す
        btn.prop('disabled', false);
        icon.removeClass('fa-spin');
    }
};

statusPage.startAutoRefresh = () => {
    if (statusPage.timer) clearInterval(statusPage.timer);
    statusPage.timer = setInterval(() => {
        statusPage.refreshActive();
    }, statusPage.autoRefreshInterval);
};

$(() => {
    cmdbox.set_logoicon('.navbar-brand');
    cmdbox.copyright();
    cmdbox.init_version_modal();
    cmdbox.init_modal_button();
    cmdbox.init_user_info_menu();
    statusPage.initSidebar();
    statusPage.initAutoRefreshSelector();

    $('#btn_status_refresh').off('click').on('click', async () => {
        await statusPage.refreshActive();
    });

    cmdbox.get_server_opt(true, $('.filer_form')).then(async () => {
        statusPage.showMenu('server');
        await statusPage.refreshActive();
        statusPage.loadAutoRefreshInterval().then(() => {
            statusPage.startAutoRefresh();
        });
        setTimeout(() => { cmdbox.process_i18n(); }, 100);
    });
});
