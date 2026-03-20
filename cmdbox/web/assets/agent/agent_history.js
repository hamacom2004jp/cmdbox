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
        let agent_message_id = null;
        for (const event of session['events']) {
            const author = event['author'];
            const msg = event['text'];
            if (!msg || msg.length <= 0) continue;
            if (author == 'user') {
                // ユーザーメッセージ
                agentView.create_user_message(msg);
            } else {
                // エージェントメッセージ
                if (!event['final_response']) {
                    if (!agent_message_id) {
                        agent_message_id = cmdbox.random_string(16);
                        msg_container = $(`#${agent_message_id}`);
                    }
                    let msg_content = agentView.create_agent_message(agent_message_id);
                    msg_container = $(`#${agent_message_id}`);
                    msg_content.addClass('message-thinking');
                    if (msg_content.children().length > 0) {
                        msg_container.append('<div class="msg-content message-thinking"></div>');
                        msg_content = agentView.create_agent_message(agent_message_id);
                        msg_container = $(`#${agent_message_id}`);
                    }
                    if (!msg_content.hasClass('collapsed')) {
                        msg_content.addClass('collapsed');
                        msg_container.find('.btn-toggle-message').text('▶');
                    }
                    await agentView.format_agent_message(msg_content, msg);
                } else {
                    let txt = agentView.create_agent_message(cmdbox.random_string(16));
                    await agentView.format_agent_message(txt, msg);
                    txt.parent().find('.btn-toggle-message').remove();
                    agent_message_id = null;
                }
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
