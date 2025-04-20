const audit = {};
// 監査ログ一覧
audit.rawlog = async () => {
    const modal = $('#search_modal');
    const rawlog_area = $('#rawlog_area').html('');
    const [title, opt] = cmdbox.get_param(modal);
    cmdbox.show_loading();
    const data = await audit.query(opt);
    if (!data) {
        cmdbox.hide_loading();
        modal.modal('hide');
        return;
    }
    audit.tracelog(JSON.parse(JSON.stringify(data)));
    data.forEach((row) => {
        if (row['clmsg_id']) {
            row['clmsg_id'] = `<a href="#" data-id="${row['clmsg_id']}" onclick="audit.clmsg_id_click_func(this);">${row['clmsg_id']}</a>`;
        }
    });
    render_result_func(rawlog_area, data, 110);
    await audit.metrics();
    modal.modal('hide');
    cmdbox.hide_loading();
};
// 監査ログのclmsg_idをクリックしたときの処理
audit.clmsg_id_click_func = (elem) => {
    const clmsg_id = $(elem).attr('data-id');
    const area = $(`#trace_area`);
    const trace_tab = document.querySelector('#main_tabs #trace-tab')
    bootstrap.Tab.getOrCreateInstance(trace_tab).show()
    area.animate({scrollTop: $(`#${clmsg_id}`).offset().top - area.offset().top + area.scrollTop()}, 500);
};
// 監査ログのトレース
audit.tracelog = async (data) => {
    const rawlog_area = $('#trace_area').html('');
    const table = $('<table class="table table-bordered table-hover table-sm"></table>').appendTo(rawlog_area);
    const table_head = $('<thead><tr></tr></thead>').appendTo(table).find('tr');
    const table_body = $('<tbody></tbody>').appendTo(table);
    table_head.append($('<th class="th" scope="col">clmsg_user</th>'));
    table_head.append($('<th class="th" scope="col">trace log</th>'));
    const row_dict = {};
    for (const row of data) {
        const clmsg_id = row['clmsg_id'];
        if (clmsg_id == null || clmsg_id == '') continue;
        if (!row_dict[clmsg_id]) {
            row_dict[clmsg_id] = {clmsg_id:clmsg_id, clmsg_user:row['clmsg_user'], clmsg_date:row['clmsg_date'], row:[]};
        }
        if (!row_dict[clmsg_id]['clmsg_date']) {
            row_dict[clmsg_id]['clmsg_date'] = row['clmsg_date'];
        }
        if (!row_dict[clmsg_id]['clmsg_user']) {
            row_dict[clmsg_id]['clmsg_user'] = row['clmsg_user'];
        }
        delete row['clmsg_id'];
        delete row['clmsg_user'];
        row_dict[clmsg_id]['row'].push(row);
    }
    Object.values(row_dict).sort((a,b) => {
        a['clmsg_date'] > b['clmsg_date'] ? 1 : -1;
    }).forEach((attr, i) => {
        const tr = $('<tr></tr>').appendTo(table_body);
        $(`<td>${attr['clmsg_user']}</td>`).appendTo(tr);
        const div = $(`<td><span id="${attr['clmsg_id']}">clmsg_id : ${attr['clmsg_id']}</span><div/></td>`).appendTo(tr).find('div');
        render_result_func(div, attr['row'], 100);
    });
};
// 検索
audit.query = async (opt) => {
    const res = await fetch(`audit/rawlog`,
        {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(opt)});
    if (res.status != 200) {
        cmdbox.message(`${res.status}: ${res.statusText}`);
        return;
    }
    try {
        const content = JSON.parse(await res.text());
        if (!content['success']) {
            cmdbox.message(content);
            return;
        }
        return content['success']['data'];
    } catch (e) {
        cmdbox.message({'error': e.message});
        return;
    }
};
// メトリクスの表示
audit.metrics = async () => {
    const metrics_area = $('#metrics_area');
    metrics_area.html('');
    audit.list_audit_metrics().then((res) => {
        if (!res['success']) return;
        res['success'].forEach(async (row) => {
            const modal = $('#search_modal');
            const [_, opt] = cmdbox.get_param(modal);
            opt['select'] = row['vertical'];
            opt['select'][row['horizontal']] = '-';
            opt['select_date_format'] = row['horizontal_date_format'];
            opt['groupby'] = [row['horizontal']];
            opt['groupby_date_format'] = row['horizontal_date_format'];
            opt['sort'][row['horizontal']] = 'DESC';
            Object.keys(row).forEach((key) => {
                if (!key.startsWith('filter_')) return;
                opt[key] = row[key];
            });
            let data = await audit.query(opt);
            if (!data) data = [];
            data = data.reverse();
            // 時系列グラフの追加
            const card = $(`<div class="col-${row['col_size']} p-1"><div class="card card-hover"><div class="card-body"></div></div></div>`).appendTo(metrics_area);
            const card_body = card.find('.card-body');
            const title = $(`<div class="d-flex">`
                            + `<button id="edit_metrics" type="button" class="btn p-0 me-3">`
                              + `<svg width="32" height="32" fill="currentColor" class="bi bi-plus-lg"><use href="#svg_edit_btn"></use></svg></button>`
                                + `<h5 class="d-inline-block m-0">${row['title']}</h5></div>`).appendTo(card_body);
            const edit_btn = card_body.find('#edit_metrics');
            const graph = $(`<div class="chart"></div>`).appendTo(card_body);
            const series = [];
            for (const vk of Object.keys(row['vertical'])) {
                if (vk == row['horizontal']) continue;
                const sel = {name:vk, data:[...data.map(d => d[vk])]};
                series.push(sel);
            }
            const categories = [...data.map(d => d[row['horizontal']])];
            const chart_opt = {
                chart: {
                    type: row['chart_type'],
                    stacked: row['chart_stacked'],
                },
                stroke: {
                    show: true,
                    curve: row['stroke_curve'],
                    width: row['stroke_width'],
                },
                series: series,
                tooltip: {
                    theme: false
                },
                xaxis: {
                    categories: categories
                }
            }
            const chart = new ApexCharts(graph.get(0), chart_opt);
            chart.render();
            graph.find('.apexcharts-toolbar').on('click', (e) => {
                e.stopPropagation();
                e.preventDefault();
            });
            edit_btn.off('click').on('click', (e) => {
                const title = row['title'];
                audit.metrics_modal_func(title);
                e.stopPropagation();
            });
        });
    });
};
// メトリクスのモーダルダイアログを表示
audit.metrics_modal_func = (title) => {
    const modal = $('#metrics_modal');
    modal.find('.modal-title').text(title ? `Edit Metrics : ${title}` : 'New Metrics');
    const row_content = modal.find('.row_content');
    row_content.empty();
    audit.load_audit_metrics(title?title:null).then(async (res) => {
        const axis = ['','audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_src', 'clmsg_title', 'clmsg_user', 'clmsg_body', 'clmsg_tag', 'svmsg_id', 'svmsg_date'];
        const chart_type = ['','line', 'area', 'bar'];
        const stroke_curve = ['','smooth', 'straight', 'stepline'];
        const data = res['success']?res['success']:{};
        const rows = [
            {opt:'title', type:'str', default:title?title:'', required:true, multi:false, hide:false, choice:null},
            {opt:'chart_type', type:'str', default:data['chart_type']?data['chart_type']:'line', required:true, multi:false, hide:false, choice:chart_type,
                discription_en: 'Specifies the type of graph.',
                discription_ja: 'グラフのタイプを指定します。',
                choice_show: {
                    'line':['stroke_curve','stroke_width'],
                    'area':['stroke_curve','chart_stacked','stroke_width'],
                    'bar':['chart_stacked']}},
            {opt:'stroke_curve', type:'str', default:data['stroke_curve']?data['stroke_curve']:'straight', required:false, multi:false, hide:false, choice:stroke_curve,
                discription_en: 'Specifies the type of line.',
                discription_ja: '線のタイプを指定します。'},
            {opt:'chart_stacked', type:'bool', default:data['chart_stacked']?data['chart_stacked']:false, required:false, multi:false, hide:false, choice:[false, true],
                discription_en: 'Specifies whether to stack the graph.',
                discription_ja: 'グラフを積み上げるかどうかを指定します。'},
            {opt:'stroke_width', type:'int', default:data['stroke_width']?data['stroke_width']:2, required:false, multi:false, hide:false, choice:[...Array(5).keys()].map(i => i+1),
                discription_en: 'Specifies the width of the line.',
                discription_ja: '線の幅を指定します。'},
            {opt:'col_size', type:'int', default:data['col_size']?data['col_size']:6, required:true, multi:false, hide:false, choice:[...Array(12).keys()].map(i => i+1),
                discription_en: 'Specifies the size of the graph display width.',
                discription_ja: 'グラフの表示幅のサイズを指定します。'},
            {opt:'horizontal', type:'str', default:data['horizontal']?data['horizontal']:'clmsg_date', required:true, multi:false, hide:false, choice:axis,
                discription_en: 'Specify the items to be displayed on the horizontal axis.',
                discription_ja: '横軸の表示項目を指定します。',
                choice_show: {
                    'clmsg_date':['horizontal_date_format'],
                    'svmsg_date':['horizontal_date_format']}},
            {opt:'horizontal_date_format', type:'str', default:data['horizontal_date_format']?data['horizontal_date_format']:'%Y/%m/%d',
                required:false, multi:false, hide:false, choice:['','%Y/%m/%d %H:%M', '%Y/%m/%d %H', '%Y/%m/%d', '%Y/%m', '%Y', '%m', '%w'],
                discription_en: 'Specify the date format to be displayed on the horizontal axis.',
                discription_ja: '横軸の表示日付フォーマットを指定します。'},
        ];
        data['vertical'] = data['vertical'] || {'clmsg_id':'count'};
        Object.keys(data['vertical']).forEach((key) => {
            const def = {};
            def[key] = data['vertical'][key];
            rows.push({opt:'vertical', type:'dict', default:def, required:true, multi:true, hide:false,
                choice:{key:axis, val:['-','count','sum','avg','min','max']}});
        });
        const base_rows = await cmdbox.get_cmd_choices('audit', 'search');
        base_rows.filter(row => row['opt'].startsWith('filter')).forEach((row) => {
            row['hide'] = true;
            if (data[row['opt']]) {
                const val = data[row['opt']];
                if (Array.isArray(val) && val.length > 0) {
                    val.forEach((v) => {
                        if (!v || v=='') return;
                        r = {...row};
                        r['default'] = v;
                        rows.push(r);
                    });
                }
                else if (typeof val=='object') {
                    Object.keys(val).forEach((k) => {
                        if (!k || k=='') return;
                        if (!val[k] || val[k]=='') return;
                        r = {...row};
                        r['default'][k] = val[k];
                        rows.push(r);
                    });
                }
                else {
                    row['default'] = val;
                }
            }
            rows.push(row);
        });
        rows.forEach((row, i) => cmdbox.add_form_func(i, modal, row_content, row, null, 12, 6));
        title && modal.find('[name="title"]').prop('readonly', true);
        modal.find('.choice_show').change();
    });
    // 保存実行
    modal.find('#metrics_save').off('click').on('click', async () => {
        const [title, opt] = cmdbox.get_param(modal);
        if (!title || title == '') {
            cmdbox.message({'warn': 'Title is required'});
            return;
        }
        if (!opt['chart_type'] || opt['chart_type'] == '') {
            cmdbox.message({'warn': 'chart_type is required'});
            return;
        }
        if (!opt['col_size'] || opt['col_size'] == '') {
            cmdbox.message({'warn': 'col_size is required'});
            return;
        }
        if (!opt['horizontal'] || opt['horizontal'] == '') {
            cmdbox.message({'warn': 'horizontal is required'});
            return;
        }
        if (!opt['vertical'] || opt['vertical'] == '') {
            cmdbox.message({'warn': 'vertical is required'});
            return;
        }
        if (!window.confirm('Do you want to save?')) return;
        await audit.save_audit_metrics(title, opt);
        await audit.metrics();
        modal.modal('hide');
    });
    // 削除実行
    modal.find('#metrics_del').off('click').on('click', async () => {
        if (!window.confirm('Do you want to delete?')) return;
        await audit.del_audit_metrics(title);
        await audit.metrics();
        modal.modal('hide');
    });
    if (!title) modal.find('#metrics_del').hide();
    else modal.find('#metrics_del').show();
    modal.modal('show');
};
// 監査ログのフィルターフォームの初期化
audit.init_form = async () => {
    // フォームの初期化
    const modal = $('#search_modal');
    const row_content = modal.find('.row_content');
    const res = await fetch('audit/mode_cmd', {method: 'GET'});
    if (res.status != 200) cmdbox.message(`${res.status}: ${res.statusText}`);
    const msg = await res.json();
    if (!msg['success']) {
        cmdbox.message(msg);
        return;
    }
    const args = msg['success'];
    const py_get_cmd_choices = await cmdbox.get_cmd_choices(args['mode'], args['cmd']);
    row_content.html('');
    // 検索ボタンを表示
    $('#do_search').off('click').on('click', async (e) => {
        await audit.rawlog();
        const condition = {};
        row_content.find(':input').each((i, el) => {
            const elem = $(el);
            const id = elem.attr('id');
            const val = elem.val();
            if (!id || id == '') return;
            if (!val || val == '') return;
            condition[id] = {'name': elem.attr('name'), 'value': val,
                          'param_data_index': elem.attr('param_data_index'),
                          'param_data_type': elem.attr('param_data_type'),
                          'param_data_multi': elem.attr('param_data_multi')};
        });
        cmdbox.save_user_data('audit', 'condition', JSON.stringify(condition));
    });
    // 主なフィルター条件のフォームを表示
    const nml_conditions = ['filter_audit_type', 'filter_clmsg_id', 'filter_clmsg_src', 'filter_clmsg_title', 'filter_clmsg_title', 'filter_clmsg_user',
                        'filter_clmsg_tag', 'filter_svmsg_sdate', 'filter_svmsg_edate']
    py_get_cmd_choices.filter(row => nml_conditions.includes(row.opt)).forEach((row, i) => cmdbox.add_form_func(i, modal, row_content, row, null, 12, 6));
    const adv_link = $('<div class="text-center card-hover col-12 mb-3"><a href="#">[ advanced options ]</a></div>').appendTo(row_content);
    adv_link.off('click').on('click', (e) => {row_content.find('.adv').toggle();});
    // 高度なフィルター条件のフォームを表示
    const adv_conditions = ['filter_clmsg_body', 'filter_clmsg_sdate', 'filter_svmsg_edate',
                            'filter_svmsg_id', 'sort', 'offset', 'limit'];
    const adv_row_content = $('<div class="row_content"></div>').appendTo(row_content);
    py_get_cmd_choices.filter(row => adv_conditions.includes(row.opt)).forEach((row, i) => cmdbox.add_form_func(i, modal, adv_row_content, row, null, 12, 12));
    adv_row_content.children().each((i, elem) => {$(elem).addClass('adv').hide();}).appendTo(row_content);
    adv_row_content.remove();
    let condition = await cmdbox.load_user_data('audit', 'condition');
    condition = condition && condition['success'] ? JSON.parse(condition['success']) : {};
    Object.keys(condition).forEach((id) => {
        const data = condition[id];
        if (!data) return;
        let elem = row_content.find(`#${id}`);
        if (elem.length > 0) {
            elem.val(data['value']);
            return;
        }
        const last_elem = row_content.find(`[name="${data['name']}"]:last`);
        const add_btn = last_elem.next('.add_buton');
        if (add_btn.length <= 0) return;
        add_btn.click();
        elem = row_content.find(`[name="${data['name']}"]:last`);
        elem.val(val);
    });
    row_content.find(':input').each((i, elem) => {
        const id = $(elem).attr('id');
        if (!id || id == '') return;
        const val = localStorage.getItem(id);
        if (!val || val == '') return
        $(elem).val(val);
    });
    $('#search_rawlog').off('click').on('click', (e) => {
        modal.modal('show');
    });
    $('#search_trace').off('click').on('click', (e) => {
        modal.modal('show');
    });
};
audit.list_audit_metrics = async () => {
    const formData = new FormData();
    const res = await fetch('audit/metrics/list', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
audit.load_audit_metrics = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('audit/metrics/load', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
audit.save_audit_metrics = async (title, opt) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('opt', JSON.stringify(opt));
    const res = await fetch('audit/metrics/save', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
};
audit.del_audit_metrics = async (title) => {
    const formData = new FormData();
    formData.append('title', title);
    const res = await fetch('audit/metrics/delete', {method: 'POST', body: formData});
    if (res.status != 200) cmdbox.message({'error':`${res.status}: ${res.statusText}`});
    return await res.json();
}
$(() => {
    // カラーモード対応
    cmdbox.change_color_mode();
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
        // フィルターフォーム初期化
        await audit.init_form();
        // 監査ログ一覧表示
        await audit.rawlog();
        // メトリクス表示
        $('#add_metrics').off('click').on('click', (e) => {
            audit.metrics_modal_func();
        });
    });
});
