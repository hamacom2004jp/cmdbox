init_svglogo = async () => {
    const logo_fn = () => {
        cmdbox.appid('#logo_title').then(() => {
            $('#logo_title').text(`${document.title} Agent`);
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
        });
    }).catch(e => {
        logo_fn();
        return null;
    });
};