$(function() {

//  function contains(str1, str2) {
//    return new RegExp(str2, "i").test(str1);
//  }

//	var seq = 1;

	$('[data-toggle="tooltip"]').tooltip();

	function f_add_entry() {
		//f_add_entry_2(data_groups_and_users, "r-x");
		$("#acl_list").append(new_entry("li_" + seq, "sl_" + seq, "sel:" + seq, "opt:" + seq, "r-x"));
		//$(".select2_users").select2({
		$("#sl_" + seq).select2({data: data_groups_and_users});
//query: select2_query_fun
//  ajax: {},
//  dataAdapter: CustomData
//		$("#" + del_button_id).on("click", function () { $("#" + li_id).remove(); });
		seq += 1;
	}

//	function add_existing_acl_entries() {
//		for (i = 0; i < acl_2_split.length; i++) {
//			e = acl_2_split[i];
//			f_add_entry_2(f_select_e(e, data_groups_and_users), e.perm);
//		}
//	}

//$("select").select2({
//});

//var pageSize = 10;
//sel2_data
//    CustomData.prototype.query = function (params, callback) {
//        if (!("page" in params)) {
//            params.page = 1;
//        }
//        var data = {};
//        //# you probably want to do some filtering, basing on params.term
//        data.results = sel2_data.slice((params.page - 1) * pageSize, params.page * pageSize);
//        data.pagination = {};
//        data.pagination.more = params.page * pageSize < sel2_data.length;
//        callback(data);
//    };

//	function f_add_entry_2(sel2_data, checked_perm) {
//		//var li_id = "li_" + seq;
//		//var del_button_id = "button_" + seq;
//		$("#acl_list").append(new_entry("li_" + seq, "sl_" + seq, "sel:" + seq, "opt:" + seq, checked_perm));
//		//$(".select2_users").select2({
//		$("#sl_" + seq).select2({data: sel2_data});
////query: select2_query_fun
////  ajax: {},
// // dataAdapter: CustomData
////		$("#" + del_button_id).on("click", function () { $("#" + li_id).remove(); });
//		seq += 1;
//	}

	function new_entry(id, select_id, select_name, opt_name, checked_perm) {
		return '<div class="d-flex form-control border-0" id = "' + id + '">' +
			'<select class="select2_users flex-fill" id = "' + select_id + '" name="' + select_name + '"></select> :' +
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

//	function f_select_e(e, d) {
//		return d.map(function (obj) {
//			if (obj.id == e.id) {
//				obj = Object.assign({}, obj);
//				obj.selected = true;
//			}
//			return obj
//		});
//	}

	$("#add_entry").on("click", f_add_entry);

//	add_existing_acl_entries();

});
