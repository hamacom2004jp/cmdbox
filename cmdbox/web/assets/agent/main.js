$(() => {
    fetch('assets/agent/agent_sidebar_content.html').then(res => res.text()).then(html => {
        try {
            // SVGロゴ初期化
            init_svglogo();
            $('.split-pane').splitPane();
            // --- サイドバー初期化 ---
            agentView.navSidebar = $('#navSidebar');
            agentView.navSidebar.find('.nav-sidebar-content').remove();
            agentView.navSidebar.append(html);
            agentView.btnToggleSidebar = $('#btn_toggle_sidebar');
            agentView.sidebarExpanded = false;

            agentView.btnToggleSidebar.on('click', () => {
                agentView.sidebarExpanded = !agentView.sidebarExpanded;
                if (agentView.sidebarExpanded) {
                    agentView.navSidebar.addClass('expanded');
                } else {
                    agentView.navSidebar.removeClass('expanded');
                }
            });
            // agent初期化
            agentView.initView();
            // バージョン情報モーダル初期化
            cmdbox.init_version_modal();
            // モーダルボタン初期化
            cmdbox.init_modal_button();
        } finally {
            cmdbox.hide_loading();
        }
    });
});
// ノード変更を監視
const buttons = ['nav-sidebar-content','btn_histories'];
buttons.forEach(btnId => {
    const btn = document.querySelector(`#${btnId}`);
    if (btn) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(m => {
                console.log(`⚠️ ${btnId} changed:`, m);
                console.trace(); // 呼び出し元を表示
            });
        });
        observer.observe(btn, { attributes: true });
    }
});
