init_svglogo = async () => {
    const say_stop = () => {
        if (agentView && agentView.say && agentView.say.isPlaying()) {
            agentView.say.stop();
        }
    };
    const logo_fn = () => {
        cmdbox.appid('#logo_title').then(() => {
            $('#logo_title').text(`${document.title} Agent`);
            // logo_titleクリック時に再生を停止
            $('#logo_title').off('click').on('click', say_stop);
        });
    };
    fetch('assets/agent/agent_logo.svg').then(async res => {
        if (!res.ok) {
            logo_fn();
            return;
        };
        const logo = await res.text();
        cmdbox.appid('#logo_title').then(() => {
            $('#logo_title').html(logo);
            // logo_titleクリック時に再生を停止
            $('#logo_title').off('click').on('click', say_stop);
        });
    }).catch(e => {
        logo_fn();
        return null;
    });
};