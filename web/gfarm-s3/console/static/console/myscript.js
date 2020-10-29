$(function() {

	$('[data-toggle="tooltip"]').tooltip();

	function f_add_entry() {
		var nes = new_entry("li_" + seq, "sl_" + seq, "sel:" + seq, "opt:" + seq, "r-x", true, seq);
		$("#acl_list_anchor").before(nes);
		$("#sl_" + seq).select2({data: data_groups_and_users});
		$('#msg').empty();
		$('#apl').prop('disabled', false);
		//window.onbeforeunload = function() { return '!'; };
		seq += 1;
	}

	$("#add_entry").on("click", f_add_entry);

//	window.onbeforeunload = function() { if ($('#msg') != "") { return '!'; } };

	function new_entry(id, select_id, select_name, opt_name, checked_perm, is_del_button, seq) {
		return ("<tr id=\"" + id + "\">" +
			"<td>" +
			del_button(id, is_del_button) +
			"</td>" +
			"<td>" +
			'<select class="select2_users col-10" id="' + select_id + '" name="' + select_name + '" theme="classic"></select>' +
			"</td>" +
			"<td class=\"width: 40px align-middle pl-2 pr-2\">" +
			slider_round(f_button("r", opt_name, "RO", checked_perm == "r-x", seq)) +
			"</td>" +
			"<td class=\"width: 40px align-middle pl-2 pr-2\">" +
			slider_round(f_button("w", opt_name, "RW", checked_perm == "rwx", seq)) +
			"</td>" +
			"</tr>");
	}

	function slider_round(s) {
		return ("<div><label class=\"switch\">" +
			s +
			"<span class=\"slider round\"></span></label></div>");
	}

	function f_button(typ, name, text, checked, seq) {
		var id, xid, xset, cond;
		if (typ == "r") {
			id = "cr_" + seq;
			xid = "cw_" + seq;
			xset = "false";
			cond = "!";
		}
		else {
			id = "cw_" + seq;
			xid = "cr_" + seq;
			xset = "true";
			cond = "";
		}

		var onclick = "if (" + cond + "$('#" + id + "').prop('checked')) { $('#" + xid + "').prop('checked', " + xset + "); }";
		return "<input type=\"checkbox\" class=\"default\" name=\"" + name + "\" id=\"" + id + "\" value=\"" + typ + "\" data-toggle=\"toggle\" onClick=\"" + onclick + "\"/>";
	}

	function del_button(id, f) {
		if (f) {
			var onclick = "$('#" + id + "').remove();"
			var x = "<svg width=\"2em\" height=\"2em\" viewBox=\"0 0 16 16\" class=\"bi bi-x\" fill=\"currentColor\" xmlns=\"http://www.w3.org/2000/svg\"><path fill-rule=\"evenodd\" d=\"M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z\"/></svg>";
			return "<button type=\"button\" class=\"btn btn-link btn-sm text-danger\" onClick=\"" + onclick + "\">" + x + "</button>";
		}
		else {
			return "<span class=\"align top\"></span>";
		}
	}

});
