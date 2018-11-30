import os, frappe
import ldap


env = os.environ.get

# SERVER = env('LDAP_SERVER') or 'ldap://ldap.forumsys.com'
# PORT = env("LDAP_PORT") or '389'
# CA_PATH = env("LDAP_CA_PATH") or ''

# BIND_DN = env('LDAP_BIND_DN') or 'cn=read-only-admin,dc=example,dc=com'
# BIND_PASSWORD = env('LDAP_BIND_PASSWORD') or 'password'

# USER_SEARCH_BASE =  env('LDAP_USER_DN')
# USER_SEARCH_FILTER =  env('LDAP_USER_FILTER')

# GROUP_SEARCH_BASE = env('LDAP_GROUP_DN')
# GROUP_SEARCH_FILTER = env('LDAP_GROUP_FILTER')
# GROUP_SEARCH_SUBTREES = env('GROUP_SEARCH_SUBTREES', 'clients,projects,products')
# GROUP_SUBTREES = ['{},{}'.format(t, GROUP_SEARCH_BASE) for t in GROUP_SEARCH_SUBTREES.split(',')]


class LdapSyncUtils(object):

    def __init__(self):
        self.server_details = self.get_ldap_settings()
        self.conn = self.get_connection()

    def get_ldap_settings(self):
	    return frappe.db.get_value("LDAP Settings", None,
                               ['ldap_server','user_dn','base_dn', 'tls_ca_path', 'user_filter', 'group_filter', 'project_filter', 'pwd'], as_dict=1)

    def get_connection(self):
        if self.server_details:
            # self signed ca path
            ca_path = self.server_details.get('tls_ca_path')

            try:
                if self.server_details.get('ldap_server'):
                    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
                    connection = ldap.initialize(self.server_details.get('ldap_server'))

                    if ca_path:
                        connection.set_option(ldap.OPT_REFERRALS, 0)
                        connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
                        connection.set_option(ldap.OPT_X_TLS_CACERTFILE, ca_path)
                        connection.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
                        connection.set_option(ldap.OPT_X_TLS_DEMAND, True)
                else:
                    frappe.msgprint("Please setup server details", raise_exception=1)
            except ldap.LDAPError, e:
                frappe.msgprint("Connection Filed!!! Contact System Manager", raise_exception=1)

            return connection

    # def get_connection(self, dn=BIND_DN, password=BIND_PASSWORD):
    #     ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    #     connection = ldap.initialize(SERVER + ':' + PORT)

    #     if CA_PATH:
    #         connection.set_option(ldap.OPT_REFERRALS, 0)
    #         connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
    #         connection.set_option(ldap.OPT_X_TLS_CACERTFILE, CA_PATH)
    #         connection.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
    #         connection.set_option(ldap.OPT_X_TLS_DEMAND, True)

    #     try:
    #         connection.simple_bind_s(BIND_DN, BIND_PASSWORD)
    #     except Exception, e:
    #         frappe.msgprint(e, raise_exception=1)
    #         connect.unbind_s()

    #     return connection

    # def get_ldap_groups(self):
    #     """ Return names of all posixGroup."""
    #     result = self.conn.search_s(
    #              GROUP_SEARCH_BASE,
    #              ldap.SCOPE_SUBTREE,
    #              '(|(objectClass=posixGroup)(objectclass=groupOfNames)(objectclass=groupOfUniqueNames))',
    #              ['cn', 'entryDN', 'description']
    #              )

    #     groups = {}
    #     for dn, r in result:
    #         if any(r['entryDN'][0].endswith(sub) for sub in GROUP_SUBTREES):
    #             groups[r['cn'][0].lower()] = {
    #                 'cn': r['cn'][0],
    #                 'description': r['description'][0] if 'description' in r else r['cn'][0]
    #             }

    #     return groups

    # def get_user_ldap_groups(self, user_cn):
    #     """ Return names of all posixGroups to which user belongs."""
    #     user_dn = self._get_ldap_user(user_cn)
    #     print('User fetched from ldap', user_dn)

    #     posix_group = self._get_posix_groups(user_cn)
    #     print('PosixGroups fetched from ldap', posix_group)

    #     group_of_names = self._get_group_of_names(user_dn)
    #     print('Groups of names fetched from ldap', group_of_names)

    #     group_of_unique_names = self._get_group_of_unique_names(user_dn)
    #     print('Groups of unique names fetched from ldap', group_of_unique_names)

    #     return list(set(posix_group + group_of_names + group_of_unique_names))

    # def _get_posix_groups(self, user_cn, scope=ldap.SCOPE_SUBTREE, only_subtrees=True):
    #     result = self.conn.search_s(
    #         GROUP_SEARCH_BASE,
    #         scope,
    #         '(&(objectClass=posixGroup)(memberUid={}))'.format(user_cn),
    #         ['cn']
    #     )

    #     groups = []
    #     for dn, r in result:
    #         print 'dn', dn
    #         if any(dn.endswith(sub) for sub in GROUP_SUBTREES) or not only_subtrees:
    #             groups.append(r['cn'][0].lower())

    #     return groups

    # def _get_group_of_names(self, user_dn):
    #     result = self.conn.search_s(
    #         GROUP_SEARCH_BASE,
    #         ldap.SCOPE_SUBTREE,
    #         '(&(objectclass=groupOfNames)(member={}))'.format(user_dn),
    #         ['cn']
    #     )

    #     groups = []
    #     for dn, r in result:
    #         if any(dn.endswith(sub) for sub in GROUP_SUBTREES):
    #             groups.append(r['cn'][0].lower())

    #     return groups

    # def _get_group_of_unique_names(self, user_dn):
    #     result = self.conn.search_s(
    #         GROUP_SEARCH_BASE,
    #         ldap.SCOPE_SUBTREE,
    #         '(&(objectclass=groupOfUniqueNames)(uniqueMember={}))'.format(user_dn),
    #         ['cn']
    #     )

    #     groups = []
    #     for dn, r in result:
    #         if any(dn.endswith(sub) for sub in GROUP_SUBTREES):
    #             groups.append(r['cn'][0].lower())

    #     return groups

    # def _get_ldap_user(self, user_cn):
    #     result = self.conn.search_s(
    #         USER_SEARCH_BASE,
    #         ldap.SCOPE_SUBTREE,
    #         '(&(objectClass=posixAccount)(cn={}))'.format(user_cn),
    #         ['cn', 'entryDN']
    #     )

    #     print(result)
    #     return result[0][0] ## entryDn
