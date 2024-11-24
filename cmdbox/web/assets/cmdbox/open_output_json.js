// output_jsonファイルを選択して表示する
const open_output_json_func = (target_id) => {
    // ファイル選択後に結果画面を開く
    const view_output_json_func = (current_path) => {
        load_result(current_path).then((result) => {
            view_result_func(current_path, result);
            cmdbox.hide_loading();
        });
    };
    fmodal.filer_modal_func(target_id, 'output_json', '', false, true, view_output_json_func);
};
const load_result = async (current_path) => {
    const formData = new FormData();
    formData.append('current_path', current_path);
    const res = await fetch('gui/load_result', {method: 'POST', body: formData});
    return await res.json();
}