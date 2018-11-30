# Copyright (c) 2013, New Indictrnas and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import ldap
import frappe
from frappe.model.document import Document


class LDAPSettings(Document):
    pass


# def set_ldap_connection(server_details):
#     if server_details:
#         # self signed ca path
#         ca_path = server_details.get('tls_ca_path')

#         try:
#             if server_details.get('ldap_server'):
#                 ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
#                 connection = ldap.initialize(server_details.get('ldap_server'))

#                 if ca_path:
#                     connection.set_option(ldap.OPT_REFERRALS, 0)
#                     connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
#                     connection.set_option(ldap.OPT_X_TLS_CACERTFILE, ca_path)
#                     connection.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
#                     connection.set_option(ldap.OPT_X_TLS_DEMAND, True)
#             else:
#                 frappe.msgprint("Please setup server details", raise_exception=1)
#         except ldap.LDAPError, e:
#             frappe.msgprint("Connection Filed!!! Contact System Manager", raise_exception=1)

#         return connection
