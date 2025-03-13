// RAW結果をモーダルダイアログに表示
const view_raw_func = (title, result) => {
    const result_modal = $('#result_modal');
    result_modal.find('.modal-title').text(title);
    result_modal.find('.modal-body').html('');
    const table = $('<table class="table table-bordered table-hover table-sm"></table>');
    const table_head = $('<thead class="table-dark bg-dark"></thead>');
    const table_body = $('<tbody></tbody>');
    table.append(table_head);
    table.append(table_body);
    result_modal.find('.modal-body').append(table);
    // list型の結果をテーブルに変換
    list2table = (data, title, table_head, table_body) => {
        data.forEach((row,i) => {
            const tr = $('<tr></tr>');
            if (typeof row === 'string'){
                tr.append($(`<td>${row}</td>`));
            }
            else {
                let found = false;
                for (const [key, val] of Object.entries(row)) {
                    if(i==0) {
                        table_head.append($(`<th scope="col">${key}</th>`));
                    }
                    try {
                        if (found) {
                            const url = URL.parse(val.replace(/curl.+[^(http)](https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+)/, '$1'));
                            const curl = val.replace(/^(curl.+[^(http)])(https?:\/\/[\w/:%#\$&\?\(\)~\.=\+\-]+)/, '$1');
                            const td = $(`<td>${curl}</td>`).appendTo(tr);
                            const ctx_Path_mt = document.cookie.match(/context_path="?([^;"]+)"?/);
                            const ctx_Path = ctx_Path_mt && ctx_Path_mt.length>0 ? ctx_Path_mt[1] : '/';
                            const href = `${window.location.protocol}//${window.location.host}${ctx_Path}${url.pathname.replace(new RegExp(`^${ctx_Path}`), '')}`;
                            const anc = $(`<a href="#">${href}</a>`).appendTo(td);
                            anc.off('click').on('click', (e) => {
                                if (!window.confirm(`May I execute '${title}' ?`)) return;
                                window.open(href, '_blank');
                            });
                            found = false;
                            continue;
                        }
                        if (val == 'curlcmd') found = true;
                    } catch (e) {}
                    tr.append($(`<td>${val}</td>`));
                }
            }
            table_body.append(tr);
        });
    }
    list2table(result, title, table_head, table_body);
    result_modal.modal('show');
}