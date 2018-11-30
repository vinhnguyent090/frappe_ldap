frappe.ui.form.on('LDAP Settings', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__('Sync Now'),
      cur_frm.cscript['Sync Now']);
    }
});

cur_frm.cscript['Sync Now'] = function() {
	return frappe.call({
		method: "frappe_ldap.scripts.sync_profile.sync_ldap_users",
		callback: function(r, rt) {
      frappe.msgprint("Sync complete")
		}
	});
}
