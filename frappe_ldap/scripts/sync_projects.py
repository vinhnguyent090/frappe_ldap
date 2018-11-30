# import os
# import frappe
# import itertools
# from frappe_ldap.templates.pages.ldapsync2 import LdapSyncUtils

# env = os.environ.get

# GROUP_SEARCH_BASE = env('LDAP_GROUP_DN')
# GROUP_SEARCH_SUBTREES = env('GROUP_SEARCH_SUBTREES', 'clients,projects,products')
# GROUP_SUBTREES = ['{},{}'.format(t, GROUP_SEARCH_BASE) for t in GROUP_SEARCH_SUBTREES.split(',')]


# def sync_ldap_projects():
#     utils = LdapSyncUtils()
#     groups = utils.get_ldap_groups()
#     existing = get_existing_projects()
#     new_projects = list(set(groups) - set(existing))

#     for project in new_projects:
#         d = frappe.new_doc("Project")
#         d.owner = "Administrator"
#         d.project_name = project

#         d.insert(ignore_permissions=True)


# def get_existing_projects():
#     projects = frappe.db.sql("SELECT name FROM tabProject")
#     return list(itertools.chain(*projects))
