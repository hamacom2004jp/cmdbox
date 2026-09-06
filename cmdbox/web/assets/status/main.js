/**
 * Status Page Initialization
 * Page setup and event handler initialization
 */

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
        // ローカルストレージから前回のメニューを取得、なければ'server'をデフォルトに
        const savedMenu = localStorage.getItem('statusPage_activeMenu') || 'server';
        statusPage.showMenu(savedMenu);
        await statusPage.refreshActive();
        statusPage.loadAutoRefreshInterval().then(() => {
            statusPage.startAutoRefresh();
        });
        setTimeout(() => { cmdbox.process_i18n(); }, 100);
    });
});
