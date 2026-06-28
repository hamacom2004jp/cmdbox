const limiter_plan_page = {};

/**
 * limiter plan save コマンドのフォーム定義を取得
 */
limiter_plan_page.get_plan_form_def = async () => {
    const opts = await cmdbox.get_cmd_choices('limiter', 'plan_save');
    const vform_names = ['plan_name', 'plan_title', 'plan_desc', 'limiters',
        'plan_start', 'plan_end', 'open_date', 'suspend_date', 'notice_date',
        'billing_type', 'billing_period_unit', 'billing_period_qty',
        'billing_limiter', 'billing_min_amount', 'billing_max_amount', 'billing_unit_price', 'billing_currency'];
    const ret = opts.filter(o => vform_names.includes(o.opt));
    return ret;
};

/**
 * プランの編集フォームを動的に構築
 */
limiter_plan_page.build_plan_form = async () => {
    const form = $('#plan_form_content');
    form.empty();
    const defs = await limiter_plan_page.get_plan_form_def();
    const modal = $('#plan_modal');
    defs.forEach((row, i) => {
        cmdbox.add_form_func(i, modal, form, row, null);
    });
};

/**
 * 数値を人が読みやすい形式に変換
 */
limiter_plan_page.fmt_num = (n) => {
    if (n == null) return '-';
    if (typeof n === 'number') return n.toLocaleString();
    return n;
};

/**
 * バイト数を人が読みやすい形式に変換
 */
limiter_plan_page.fmt_bytes = (n) => {
    if (n == null) return '-';
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
    return `${(n / 1024 / 1024 / 1024).toFixed(2)} GB`;
};

/**
 * 時間差を人間が読みやすい形式に変換（例：2 hours ago）
 */
limiter_plan_page.fmt_time_ago = (datestr) => {
    if (!datestr) return '';
    try {
        // "2024-01-01 10:30:45" または "2024-01-01T10:30:45" をパース
        const dt = new Date(datestr.replace(' ', 'T'));
        if (isNaN(dt.getTime())) return '';
        
        const now = new Date();
        const diff_ms = now.getTime() - dt.getTime();
        const diff_s = Math.floor(diff_ms / 1000);
        
        if (diff_s < 60) return `${diff_s} seconds ago`;
        const diff_m = Math.floor(diff_s / 60);
        if (diff_m < 60) return `${diff_m} minute${diff_m !== 1 ? 's' : ''} ago`;
        const diff_h = Math.floor(diff_m / 60);
        if (diff_h < 24) return `${diff_h} hour${diff_h !== 1 ? 's' : ''} ago`;
        const diff_d = Math.floor(diff_h / 24);
        return `${diff_d} day${diff_d !== 1 ? 's' : ''} ago`;
    } catch (e) {
        return '';
    }
};

/**
 * datetime文字列を「年/月/日-時:分:秒」形式に変換（例：2026/06/21-14:33:56）
 */
limiter_plan_page.fmt_datetime = (datestr) => {
    if (!datestr) return '-';
    try {
        // "2026-06-21T14:33:56.908974" → "2026/06/21-14:33:56"
        const parts = datestr.split('T');
        if (parts.length !== 2) return datestr;
        const date_part = parts[0].replace(/-/g, '/'); // "2026/06/21"
        const time_part = parts[1].split('.')[0]; // "14:33:56"
        return `${date_part}-${time_part}`;
    } catch (e) {
        return datestr || '-';
    }
};

/**
 * 進捗バーを生成して返す
 */
limiter_plan_page.make_progress = (label, current, max, fmt_func, service=null) => {
    if (max == null) {
        // 上限なし: 現在値だけ表示
        return $(`<div class="mb-1">
            <div class="d-flex justify-content-between">
                <small class="text-secondary i18n">${label}</small>
                <small class="text-info">${fmt_func ? fmt_func(current) : limiter_plan_page.fmt_val(current)}</small>
            </div>
        </div>`);
    }
    service = service || 0;
    const pct = max > 0 ? Math.min(100, Math.round((current || 0) / (max + service) * 100)) : 0;
    const color = pct >= 90 ? 'bg-danger' : pct >= 70 ? 'bg-warning' : 'bg-info';
    const cur_str = fmt_func ? fmt_func(current || 0) : (current || 0);
    const max_str = fmt_func ? fmt_func(max + service) : max + service;
    const service_str = fmt_func ? fmt_func(service) : service;
    return $(`<div class="mb-1">
        <div class="d-flex justify-content-between">
            <small class="text-secondary i18n">${label} ${service ? `(Service: ${service_str})` : ''}</small>
            <small class="text-info">${cur_str} / ${max_str} (${pct}%)</small>
        </div>
        <div class="progress" style="height:6px;">
            <div class="progress-bar ${color}" role="progressbar" style="width:${pct}%" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
    </div>`);
};

/**
 * null値を '-' に変換
 */
limiter_plan_page.fmt_val = (v) => (v == null || v === '') ? '-' : v;

/**
 * datetime文字列から datetime-local input 用の文字列に変換
 */
limiter_plan_page.to_dt_local = (s) => {
    if (!s) return '-';
    // "2024-01-01 00:00:00" または "2024-01-01T00:00:00" を "2024-01-01T00:00:00" に
    return s.replace(' ', 'T').substring(0, 19);
};

/**
 * プラン一覧タブのデータを読み込んで描画
 */
limiter_plan_page.load_plans = async () => {
    cmdbox.show_loading();
    const payload = {
        mode: 'limiter',
        cmd: 'plan_list',
        kwd: null
    };
    
    let res;
    try {
        res = await cmdbox.sv_exec_cmd(payload);
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    if (!res) { cmdbox.message({ warn: 'No response from server.' }, true, true); return; }
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success']) {
        cmdbox.message(res, true, true);
        return;
    }
    await limiter_plan_page.render_plans(first['success']['data'] || []);
    cmdbox.process_i18n($('#plans_area'), true);
};

/**
 * プラン一覧の描画
 */
limiter_plan_page.render_plans = async (plans) => {
    const area = $('#plans_area').empty();
    if (!plans || plans.length === 0) {
        area.append('<div class="col-12 text-muted p-3 i18n">No plans found.</div>');
        return;
    }
    const is_plan_save = await cmdbox.check_cmd('limiter', 'plan_save');
    for (const plan of plans) {
        const col = $(`<div class="col-12 col-md-6 col-xl-4"></div>`).appendTo(area);
        const card = $(`<div class="card h-100 border-start border-4" style="border-left-color:var(--bs-success)!important;"></div>`).appendTo(col);
        const card_header = $(`<div class="doc-header d-flex align-items-center gap-2"></div>`).appendTo(card);
        
        card_header.append(`<i class="fas fa-lg fa-layer-group"></i><strong>${plan.plan_title || ''}</strong><span> ${' ( '+plan.name+' )' || ''}</span>`);
        if (plan.billing_type) {
            const billing_badge = plan.billing_type === 'period' ? 'bg-info' : 'bg-warning';
            card_header.append(`<span class="badge rounded-pill ${billing_badge} ms-auto">${plan.billing_type}</span>`);
        }

        const card_body = $(`<div class="card-body p-2"></div>`).appendTo(card);
        // 説明
        if (plan.plan_desc) {
            card_body.append(`<div class="mb-2">${plan.plan_desc}</div>`);
        }
        const plan_div = $(`<div class="mb-1 pt-2 border-top"></div>`).appendTo(card_body);
        // プラン期間
        if (plan.plan_start || plan.plan_end) {
            plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Plan Period</small><small class="text-info">${limiter_plan_page.to_dt_local(plan.plan_start)} ~ ${limiter_plan_page.to_dt_local(plan.plan_end)}</small></div>`);
        }
        
        // リミッター詳細を読み込んで表示
        try {
            const res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'plan_load', plan_name: plan.name });
            const data_list = Array.isArray(res) ? res : [res];
            const first = data_list[0];
            if (first && first['success']) {
                const plan_detail = first['success']['data'] || {};
                
                // 日付情報を表示
                if (plan_detail.open_date) {
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Open Date</small><small class="text-info">${limiter_plan_page.to_dt_local(plan_detail.open_date)}</small></div>`);
                }
                if (plan_detail.suspend_date) {
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Suspend Date</small><small class="text-info">${limiter_plan_page.to_dt_local(plan_detail.suspend_date)}</small></div>`);
                }
                if (plan_detail.notice_date) {
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Notice Date</small><small class="text-info">${limiter_plan_page.to_dt_local(plan_detail.notice_date)}</small></div>`);
                }
                
                // 請求情報を表示
                if (plan_detail.billing_period_unit && plan_detail.billing_period_qty) {
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Billing Unit</small><small class="text-info">${plan_detail.billing_period_qty} ${plan_detail.billing_period_unit}</small></div>`);
                }
                if (plan_detail.billing_limiter) {
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Billing Credits</small><small class="text-info">${plan_detail.billing_limiter}</small></div>`);
                }
                if (plan_detail.billing_min_amount || plan_detail.billing_max_amount) {
                    const min_str = plan_detail.billing_min_amount ? `${limiter_plan_page.fmt_num(plan_detail.billing_min_amount)}` : '-';
                    const max_str = plan_detail.billing_max_amount ? `${limiter_plan_page.fmt_num(plan_detail.billing_max_amount)}` : '-';
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Price Range</small><small class="text-info">${min_str} ~ ${max_str} ${plan_detail.billing_currency || ''}</small></div>`);
                }
                if (plan_detail.billing_unit_price) {
                    const price_str = limiter_plan_page.fmt_num(plan_detail.billing_unit_price);
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Unit Price</small><small class="text-info">${price_str} ${plan_detail.billing_currency || ''}</small></div>`);
                }
                // 現在の請求金額を表示
                if (plan_detail.current_billing_amount !== undefined && plan_detail.current_billing_amount !== null) {
                    const current_amount_str = limiter_plan_page.fmt_num(plan_detail.current_billing_amount);
                    plan_div.append(`<div class="d-flex justify-content-between"><small class="text-secondary i18n">Current Billing Amount</small><small class="badge text-bg-warning">${current_amount_str} ${plan_detail.billing_currency || ''}</small></div>`);
                }
                // リミッター詳細を表示
                if (plan_detail.limiters && Array.isArray(plan_detail.limiters) && plan_detail.limiters.length > 0) {
                    const limiters_area = $(`<div class="mt-2 pt-2 border-top"></div>`).appendTo(card_body);
                    for (const limiter_obj of plan_detail.limiters) {
                        if (typeof limiter_obj === 'object' && !limiter_obj.error) {
                            limiter_plan_page._render_limiter_item_in_plan(limiters_area, limiter_obj);
                        }
                    }
                }
            }
        } catch (e) {
            // エラーの場合は無視してプラン一覧を続行
            console.log('Failed to load plan details:', e);
        }
        
        if (is_plan_save) {
            // 操作ボタン
            const btn_row = $(`<div class="d-flex gap-2 mt-3"></div>`).appendTo(card_body);
            const btn_edit = $(`<button type="button" class="btn btn-sm btn-outline-info i18n">Edit</button>`).appendTo(btn_row);
            const btn_del = $(`<button type="button" class="btn btn-sm btn-outline-danger i18n">Delete</button>`).appendTo(btn_row);
            btn_edit.on('click', async () => await limiter_plan_page.open_edit_modal(plan.name));
            btn_del.on('click', () => limiter_plan_page.delete_plan(plan.name));
        }
    }
    cmdbox.hide_loading();
};

/**
 * プラン編集モーダルを開く (name=null で新規作成)
 */
limiter_plan_page.open_edit_modal = async (name) => {
    const modal = $('#plan_modal');
    const is_new = !name;

    // フォーム構築
    cmdbox.show_loading();
    try {
        await limiter_plan_page.build_plan_form();
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    modal.find('#cmd_plan_del').addClass('d-none');
    if (is_new) {
        modal.find('.modal-title').text('New Plan');
        // デフォルト値を設定
        const form = $('#plan_form_content');
        form.find('[name="billing_type"]').val('period');
        cmdbox.process_i18n(modal);
        cmdbox.hide_loading();
        modal.modal('show');
        modal.find('.choice_show').change();
        return;
    }
    
    // 既存のプラン設定をロード
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'plan_load', plan_name: name });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success']) {
        cmdbox.hide_loading();
        cmdbox.message(res, true, true);
        return;
    }
    const cfg = first['success']['data'] || {};
    modal.find('.modal-title').text(`Edit Plan: ${name}`);
    modal.find('#cmd_plan_del').removeClass('d-none');

    // 設定値を form にセット
    const form = $('#plan_form_content');
    Object.keys(cfg).forEach(key => {
        const input = form.find(`[name="${key}"]`);
        if (input.length > 0) {
            if (key === 'plan_start' || key === 'plan_end' || key === 'open_date' || 
                key === 'suspend_date' || key === 'notice_date') {
                // datetime 型は変換が必要
                input.val(limiter_plan_page.to_dt_local(cfg[key]));
            } else if (key === 'limiters') {
                // limiters は callcmd ブロックで別途処理するのでここではスキップ
            } else {
                input.val(cfg[key]);
            }
        }
    });
    // limiters の行数を先に確保してからリストをロード（list_cmd.js と同じパターン）
    const limiter_names = cfg.limiters ? cfg.limiters.map(l => typeof l === 'string' ? l : l.limiter_name).filter(n => n) : [];
    let limiters = form.find('[name="limiters"]');
    limiter_names.forEach((v, i) => {
        const e = limiters.parent().find('.add_buton')[i];
        if (e) $(e).click();
    });
    limiters = form.find('[name="limiters"]');
    limiters.empty().append('<option></option>');
    limiter_names.forEach(elm => {
        limiters.append(`<option value="${elm}">${elm}</option>`);
    });
    limiters.each((i, e) => {
        if (limiter_names[i]) $(e).val(limiter_names[i]);
        else $(e).parent().parent().remove();
    });
    // billing_limiterリスト
    if(cfg.billing_limiter) {
        const billing_limiter = form.find('[name="billing_limiter"]');
        billing_limiter.empty().append('<option></option>');
        limiter_names.forEach(elm => {
            billing_limiter.append(`<option value="${elm}">${elm}</option>`);
        });
        billing_limiter.val(cfg.billing_limiter);
    }
    modal.find('.choice_show').change();
    cmdbox.process_i18n(modal);
    cmdbox.hide_loading();
    modal.modal('show');
};

/**
 * プラン一覧内のリミッター表示
 */
limiter_plan_page._render_limiter_item_in_plan = (parent, lm) => {
    const item = $(`<div class="border rounded p-2 mb-2 bg-body-tertiary small"></div>`).appendTo(parent);
    
    // Limiter name
    const name_row = $(`<div class="d-flex align-items-center gap-1 mb-1"></div>`).appendTo(item);
    name_row.append(`<i class="fas fa-lock fa-sm text-info"></i><strong>${lm.limiter_title || ''}</strong><span class="me-auto"> (${lm.limiter_name})</span>`);
    
    // Target info
    name_row.append(`<span class="badge rounded-pill text-bg-primary">mode</span><strong>${lm.target_mode || '-'}</strong>`);
    name_row.append(`<span class="badge rounded-pill text-bg-success ms-2">cmd</span><strong>${lm.target_cmd || '-'}</strong>`);

    // 制限設定（プログレスバー付き）
    const counter = lm.counter || {};
    const limits_area = $(`<div class="mt-2"></div>`).appendTo(item);
    
    // 設定されているものについてのみプログレスバーを表示
    if (lm.max_total_count) {
        limiter_plan_page.make_progress('Count', counter.total_count, lm.max_total_count, limiter_plan_page.fmt_num).appendTo(limits_area);
    }
    if (lm.max_total_time) {
        limiter_plan_page.make_progress('Time (s)', counter.total_time, lm.max_total_time, (v) => v != null ? `${typeof v === 'number' ? v.toFixed(1) : v}s` : '-').appendTo(limits_area);
    }
    if (lm.max_total_input) {
        limiter_plan_page.make_progress('Input', counter.total_input, lm.max_total_input, limiter_plan_page.fmt_bytes).appendTo(limits_area);
    }
    if (lm.max_total_process) {
        limiter_plan_page.make_progress('Process', counter.total_process, lm.max_total_process, limiter_plan_page.fmt_bytes).appendTo(limits_area);
    }
    if (lm.max_total_output) {
        limiter_plan_page.make_progress('Output', counter.total_output, lm.max_total_output, limiter_plan_page.fmt_bytes).appendTo(limits_area);
    }
    if (lm.max_total_credits) {
        limiter_plan_page.make_progress('Credits', counter.total_credits, lm.max_total_credits, limiter_plan_page.fmt_num, lm.service_credits).appendTo(limits_area);
    }
    if (lm.max_registrations) {
        limiter_plan_page.make_progress('Registrations', counter.total_registrations, lm.max_registrations, limiter_plan_page.fmt_num).appendTo(limits_area);
    }
    if (counter.last_reset) {
        const time_ago = limiter_plan_page.fmt_time_ago(counter.last_reset);
        const formatted_datetime = limiter_plan_page.fmt_datetime(counter.last_reset);
        limiter_plan_page.make_progress('Last reset', `${formatted_datetime} (${time_ago})`, null).appendTo(limits_area);
    }
};

/**
 * プランを保存
 */
limiter_plan_page.save_plan = async () => {
    const form = $('#plan_form_content');
    const data = {};
    form.serializeArray().forEach(item => {
        if (item.value) {
            // limiters は改行区切りの複数値
            if (item.name === 'limiters') {
                if (!data['limiters']) data['limiters'] = [];
                data['limiters'].push(item.value.trim());
            } else {
                data[item.name] = item.value;
            }
        }
    });

    if (!data.plan_name || !data.plan_name.trim()) {
        cmdbox.message({ warn: 'Plan Name is required.' }, true, true);
        return;
    }
    
    // limiters を配列から文字列配列に変換（重複を除去）
    if (data.limiters) {
        data.limiters = [...new Set(data.limiters.map(l => l.trim()).filter(l => l))];
    }

    const payload = {
        mode: 'limiter',
        cmd: 'plan_save',
        ...data
    };

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd(payload);
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success'] || !first['success']['data']) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first['success']['data'], true, true);
    $('#plan_modal').modal('hide');
    await limiter_plan_page.refresh_all();
};

/**
 * プランを削除
 */
limiter_plan_page.delete_plan = async (name) => {
    if (!name) return;
    const confirmed = await cmdbox.confirm({ warn: `Delete plan "${name}"?` }, true);
    if (!confirmed) return;

    cmdbox.show_loading();
    let res;
    try {
        res = await cmdbox.sv_exec_cmd({ mode: 'limiter', cmd: 'plan_del', plan_name: name });
    } catch (e) {
        cmdbox.hide_loading();
        cmdbox.message({ error: e.toString() }, true, true);
        return;
    }
    cmdbox.hide_loading();
    const data_list = Array.isArray(res) ? res : [res];
    const first = data_list[0];
    if (!first || !first['success'] || !first['success']['data']) {
        cmdbox.message(res, true, true);
        return;
    }
    cmdbox.message(first['success']['data'], true, true);
    $('#plan_modal').modal('hide');
    await limiter_plan_page.refresh_all();
};

/**
 * プラン一覧を再読み込み
 */
limiter_plan_page.refresh_all = async () => {
    await limiter_plan_page.load_plans();
};
