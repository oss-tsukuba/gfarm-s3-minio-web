$(function() {

	$('[data-toggle="tooltip"]').tooltip();

	function f_add_entry() {
		$("#acl_list").append(new_entry("li_" + seq, "sl_" + seq, "sel:" + seq, "opt:" + seq, "r-x"));
		$("#sl_" + seq).select2({data: data_groups_and_users});
		seq += 1;
	}

	function new_entry(id, select_id, select_name, opt_name, checked_perm) {
		return '<div class="d-flex form-control border-0" id = "' + id + '">' +
			'<select class="select2_users flex-fill" id = "' + select_id + '" name="' + select_name + '" theme="classic"></select> :' +
			'<div class="btn-group btn-group-toggle" data-toggle="buttons">' +
				f_button(opt_name, "RW", "rwx", checked_perm == "rwx") +
				f_button(opt_name, "RO", "r-x", checked_perm == "r-x") +
				f_button(opt_name, "--", "---", checked_perm == "---") +
			'</div>' +
			'<button type="button" class="btn btn-outline-danger btn-sm" onClick="$('+ "'#" + id + "'" + ').remove();">Del</button>' +
			'</div>';
	}

	function f_button(name, text, value, checked) {
		var a = checked ? " active" : "";
		var c = checked ? " checked" : "";
		return	'<label class="btn btn-secondary btn-sm' + a + '">' +
			'<input type="radio" name="' + name + '" value="' + value + '"' + c + '>' +
			text +
			'</label>';
	}

	$("#add_entry").on("click", f_add_entry);

});
