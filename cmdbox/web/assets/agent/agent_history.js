agentView.cell_chop = (val, res_size) => {
    val = `${val || ''}`;
    res_size = res_size ? res_size : 150;
    if(val && res_size>0 && val.length > res_size){
        return `${val.substring(0, res_size)}...`;
    }
    return val;
};

agentView.create_history = (session_id, runner_name, user_name, update_time, msg) => {
    if (agentView.chatHistories.find(`#${session_id}`).length > 0) return;
    msg = agentView.cell_chop(msg, 300);
    const li = $(`<li id="${session_id}" class="d-flex sf-list-item"/>`).appendTo(agentView.chatHistories);
    const div1 = $(`<div class="d-inline-block"/>`).appendTo(li);
    const head = $(`<span class="d-block glow-text-cyan system-font" style="font-size: 1em;"></span>`).appendTo(div1);
    head.html(`${update_time instanceof Date ? update_time.toLocaleString() : update_time} - ${runner_name} - ${user_name}`);
    const body = $(`<span></span>`).appendTo(div1);
    body.html(msg);
    const div2 = $(`<div class="d-inline-block"/>`).appendTo(li);
    const btn_del = $(`<button class="btn btn-danger ms-auto">Delete</button>`).appendTo(div2);
    btn_del.off('click').on('click',(e)=>{
        if (!window.confirm('Are you sure you want to delete this session?')) return;
        // セッション削除ボタンのクリックイベント
        e.preventDefault();
        e.stopPropagation();
        agentView.delete_session(session_id).then(async (res) => {
            li.remove();
            const sid = agentView.chatMessages.attr('data-session_id');
            if (sid == session_id) {
                // 削除したセッションが現在のセッションだった場合は、メッセージ一覧をクリア
                agentView.chatMessages.html('');
                agentView.ws && agentView.ws.close();
                agentView.chat(cmdbox.random_string(16));
            }
            await agentView.list_sessions();
        });
    });
    li.off('click').on('click', async (e) => {
        // セッションを選択したときの処理
        e.preventDefault();
        agentView.ws && agentView.ws.close();
        agentView.chat(session_id);
        const data = await agentView.list_sessions(session_id);
        if (data.length<=0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        const session = data[0];
        if (!session['events'] || session['events'].length <= 0) {
            cmdbox.message({'error':'No messages found for this session.'});
            return;
        }
        agentView.chatMessages.html('');
        for (const event of session['events']) {
            if (!event['text'] || event['text'].length <= 0) continue;
            if (event['author'] == 'user') {
                // ユーザーメッセージ
                agentView.create_user_message(event['text']);
            } else {
                // エージェントメッセージ
                txt = agentView.create_agent_message(cmdbox.random_string(16));
                await agentView.format_agent_message(txt, event['text']);
            }
        }
    });
    return li;
};
agentView.delete_session = async (session_id) => {
    const runner_name = agentView.agent_runner ? agentView.agent_runner['runner_name'] : null;
    if (!runner_name || runner_name.length <= 0) return;
    return agentView.exec_cmd('agent', 'session_del', {
        'runner_name': runner_name,
        'session_id': session_id
    });
}
