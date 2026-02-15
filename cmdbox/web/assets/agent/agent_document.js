agentView.showDocument = (title, content, message_id) => {
    let modal = $(`#${message_id} .modal`);
    if (modal.length <= 0) {
        const html = `<div id="${message_id}" class="modal fade" tabindex="-1" aria-hidden="true" style="z-index: 1100;">
            <div class="modal-dialog modal-dialog-centered modal-lg modal-dialog-scrollable">
                <div class="modal-content sf-modal doc-card" style="height:auto;">
                    <div class="modal-header doc-header">
                        <h5 class="modal-title glow-text-cyan system-font"><i class="fas fa-database me-2"></i>${title}</h5>
                        <button type="button" class="btn btn-sf-icon btn_window_stack">
                            <i class="fa-regular fa-window-restore"></i>
                        </button>
                        <button type="button" class="btn btn-sf-icon btn_window">
                            <i class="fa-regular fa-window-maximize"></i>
                        </button>
                        <button type="button" class="btn btn-sf-icon btn_window_close" data-bs-dismiss="modal" aria-label="Close">
                            <i class="fas fa-times fa-lg"></i>
                        </button>
                    </div>
                    <div class="modal-body doc-body docViewerContent">
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary btn_window_close" data-bs-dismiss="modal">CLOSE</button>
                    </div>
                </div>
            </div>
        </div>`;
        modal = $(html).appendTo('body');
        // modal setting
        const dialog = modal.find('.modal-dialog');
        const content = modal.find('.modal-content');
        dialog.draggable({cursor:'move',cancel:'.modal-body'});
        modal.find('.btn_window_stack').off('click').on('click', () => {
            modal.find('.btn_window_stack').css('margin-left', '0px').hide();
            modal.find('.btn_window').css('margin-left', 'auto').show();
            dialog.removeClass('modal-fullscreen');
            content.css('height', 'auto');
        });
        modal.find('.btn_window').off('click').on('click', () => {
            modal.find('.btn_window_stack').css('margin-left', 'auto').show();
            modal.find('.btn_window').css('margin-left', '0px').hide();
            dialog.css('top', '').css('left', '').addClass('modal-fullscreen');
            content.css('height', 'calc(100% - var(--bs-modal-margin) * 2)');
        });
        modal.on('hidden.bs.modal', () => { agentView.closeDocument(message_id); });
        modal.find('.btn_window_stack').css('margin-left', '0px').hide();
        modal.find('.btn_window').css('margin-left', 'auto').show();
    }
    modal.find('.docViewerContent').html(content);
    agentView.aiCoreContainer.addClass('dimmed');
    modal.modal('show');
};

agentView.closeDocument = (message_id) => {
    let modal = $(`#${message_id} .modal`);
    modal.modal('hide');
    modal.remove();
    agentView.aiCoreContainer.removeClass('dimmed');
};
