const cell_chop = (val, res_size) => {
    val = `${val || ''}`;
    res_size = res_size ? res_size : 150;
    if(val && res_size>0 && val.length > res_size){
        return `${val.substring(0, res_size)}...`;
    }
    return val;
}
// 実行結果をモーダルダイアログに表示
const view_result_func = (title, result, res_size) => {
    const result_modal = $('#result_modal');
    result_modal.find('.modal-title').text(title);
    if (!result || result.length <= 0) {
        result_modal.modal('show');
        return;
    }
    res_size = res_size || 150;
    result_modal.find('.modal-body').html('');
    render_result_func(result_modal.find('.modal-body'), result, res_size);
    result_modal.modal('show');
    cmdbox.hide_loading();
}

const render_result_func = (target_elem, result, res_size) => {
    if (!result || Array.isArray(result) && result.length<=0) return;
    const mk_table_func = () => {
        const table = $('<table class="table table-bordered table-hover table-sm"></table>');
        $('<thead><tr></tr></thead>').appendTo(table);
        $('<tbody></tbody>').appendTo(table);
        return table;
    }
    const table = mk_table_func();
    target_elem.append(table);
    // list型の結果をテーブルに変換
    const list2table = (data, table_head, table_body) => {
        data.forEach((row, i) => {
            if(row['success'] && typeof row['success'] == "object" && !Array.isArray(row['success'])){
                dict2table(row['success'], i==0?table_head:null, table_body, row['output_image']);
                return;
            }
            if(typeof row == 'string' || row instanceof String){
                const tr = $('<tr></tr>');
                table_body.append(tr);
                tr.append($(`<td>${cell_chop(row, res_size)}</td>`));
                return;
            }
            if(Array.isArray(row) && row.length > 0 && typeof row[0] != "object"){
                const tr = $('<tr></tr>');
                table_body.append(tr);
                val = cell_chop(JSON.stringify(row), res_size);
                tr.append($(`<td>${row}</td>`));
                return;
            }
            const tr = $('<tr></tr>');
            table_body.append(tr);
            Object.keys(row).forEach(key => {
                const val = row[key];
                if(i==0) {
                    table_head.append($(`<th class="th" scope="col">${key}</th>`));
                }
                if(val && val['success'] && Array.isArray(val['success'])){
                    const tbl = mk_table_func()
                    const td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    list2table(val['success'], tbl.find('thead'), tbl.find('tbody'));
                }
                else if(val && val['success'] && typeof val['success'] == "object"){
                    const tbl = mk_table_func()
                    const td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    dict2table(val['success'], tbl.find('thead'), tbl.find('tbody'));
                }
                else if(val && !Array.isArray(val) && typeof val == "object"){
                    const tbl = mk_table_func()
                    const td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    dict2table(val, tbl.find('thead'), tbl.find('tbody'));
                }
                else if(val && Array.isArray(val) && val.length > 0 && typeof val[0] == "object"){
                    const tbl = mk_table_func()
                    const td = $('<td></td>');
                    td.append(tbl);
                    tr.append(td);
                    list2table(val, tbl.find('thead'), tbl.find('tbody'));
                }
                else{
                    tr.append($(`<td>${cell_chop(val, res_size)}</td>`));
                }
            });
        });
    }
    // dict型の結果をテーブルに変換
    const dict2table = (data, table_head, table_body, output_image) => {
        const tr = $('<tr></tr>');
        if(output_image){
            if(table_head)table_head.append($('<th class="th" scope="col">output_image</th>'));
            const img = $('<img class="img-thumbnail">').attr('src', `data:image/png;base64,${output_image}`);
            img.css('width','100px').css('height','auto');
            const anchor = $(`<a href="data:image/jpeg;base64,${output_image}" data-lightbox="output_image"></a>`).append(img);
            tr.append($('<td></td>').append(anchor));
        }
        table_body.append(tr);
        Object.keys(data).forEach(key => {
            let val = data[key];
            if(table_head)table_head.append($(`<th class="th" scope="col">${key}</th>`));
            if (key != 'warn' && val) {
                if(Array.isArray(val)){
                    if(val.length > 0 && typeof val[0] == "object"){
                        const tbl = mk_table_func()
                        const td = $('<td></td>');
                        td.append(tbl);
                        list2table(val, tbl.find('thead'), tbl.find('tbody'));
                        val = td.html();
                    } else {
                        val = cell_chop(JSON.stringify(val), res_size);
                    }
                }
                else if (typeof val == "object") {
                    const tbl = mk_table_func()
                    const td = $('<td></td>');
                    td.append(tbl);
                    dict2table(val, tbl.find('thead'), tbl.find('tbody'));
                    val = td.html();
                }
                else if (typeof val === 'string' || val instanceof String) {
                    val = cell_chop(val, res_size);
                }
            }
            tr.append($(`<td style="overflow-wrap:break-word;word-break:break-all;">${val}</td>`));
        });
    }
    const table_head = table.find('thead tr')
    const table_body = table.find('tbody')
    // 結果をテーブルに変換
    if(result['success'] && Array.isArray(result['success'])){
        list2table(result['success'], table_head, table_body);
    }
    else if(result['success'] && typeof result['success'] == "object"){
        dict2table(result['success'], table_head, table_body, result['output_image']);
    }
    else if(Array.isArray(result)){
        list2table(result, table_head, table_body);
    }
    else if(typeof result === "string" || result instanceof String){
        target_elem.html(result);
    }
    else {
        dict2table(result, table_head, table_body);
    }
}
