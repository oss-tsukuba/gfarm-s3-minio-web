$(function() {

	var seq = 1;

	$('[data-toggle="tooltip"]').tooltip();

	function f_add_entry() {
		f_add_entry_2(data_groups_and_users, "r-x");
	}

	function add_existing_acl_entries() {
		for (i = 0; i < acl_2_split.length; i++) {
			e = acl_2_split[i];
			f_add_entry_2(f_select_e(e, data_groups_and_users), e.perm);
		}
	}

	function f_add_entry_2(sel2_data, checked_perm) {
		var li_id = "li_" + seq;
		var del_button_id = "button_" + seq;
		$("#acl_list").append(new_entry(li_id, "sel:" + seq, "opt:" + seq, del_button_id, checked_perm));
		$(".select2_users").select2({data: sel2_data});
		$("#" + del_button_id).on("click", function () { $("#" + li_id).remove(); });
		seq += 1;
	}


	function new_entry(id, select_name, opt_name, del_button_id, checked_perm) {
		return '<div class="d-flex form-control" id = "' + id + '">' +
			'<select class="select2_users flex-fill" name="' + select_name + '"></select> :' +
			'<div class="btn-group btn-group-toggle" data-toggle="buttons">' +
				f_button(opt_name, "RW", "rwx", checked_perm == "rwx") +
				f_button(opt_name, "RO", "r-x", checked_perm == "r-x") +
				f_button(opt_name, "--", "---", checked_perm == "---") +
			'</div>' +
			'<button type="button" class="btn btn-outline-danger btn-sm" id="' + del_button_id + '">Del</button>';
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

	function f_select_e(e, d) {
		return d.map(function (obj) {
			if (obj.id == e.id) {
				obj = Object.assign({}, obj);
				obj.selected = true;
			}
			return obj
		});
	}

	$("#add_entry").on("click", f_add_entry);

	add_existing_acl_entries();

});
