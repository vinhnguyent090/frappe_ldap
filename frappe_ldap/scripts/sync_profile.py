import ldap, sys, frappe
import itertools


from frappe.utils import nowdate,  nowtime, cstr
from frappe import sendmail
from frappe.utils import random_string
#from frappe_ldap.ldap.doctype.ldap_settings.ldap_settings import 
from frappe_ldap.templates.pages.ldapsync2 import LdapSyncUtils
from frappe.defaults import set_default, clear_cache


def check_profiles_daily():
    check_profiles_if("Daily")


def check_profiles_weekly():
    check_profiles_if("Weekly")


def check_profiles_monthly():
    check_profiles_if("Monthly")


def check_profiles_if(freq):
    if frappe.db.get_value("LDAP Settings", None, "sync_frequency")==freq:
        sync_ldap_users()


@frappe.whitelist(allow_guest=True)
def sync_ldap_users():
    
    utils = LdapSyncUtils()
    
    server_details = utils.server_details
    conn = utils.conn

    new_created = []

    users = get_ldap_users(conn,server_details)
    groups = get_ldap_groups(conn,server_details)

    roles = frappe._dict()
    for group in groups:

        frappe.errprint(group["name"])
        frappe.errprint(group["members"])

        for member in group["members"]:
            if not roles.get(member):
                roles[member] = []

            roles[member].append(group["name"])

    for user in users:
        
        pwd = random_string(10)
        
        if roles.get(user['username']):
            role = roles.get(user['username'])
        else:
            role = ['Default']  

        frappe.errprint(user['mail'])  
        frappe.errprint(role)
        
        groups = ''
        result = upsert_profile(user, pwd, groups, role)
        if result == "insert":
            new_created.append(user["mail"])

    
    # send email to admin about new users
    #admin_notification(new_created)

def get_ldap_groups(conn, server_details):
    groups = []

    group_filter = server_details.get('group_filter', '')
    base_dn = server_details.get('base_dn')

    try:
        # search for erpnext groups in ldap database
        result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, group_filter)
    except Exception, e:
        frappe.msgprint("Can not find groups: {0}".format(base_dn), raise_exception=1)
        conn.unbind_s()
        raise

    for dn, r in result:
        if r.get('cn'):
            members = []
            for member in r.get('uniqueMember'):
                member = member.split(",")
                uid = member[0].split("=")
                members.append(uid[1])

            groups.append({
                "name": str(r.get('cn')[0]),
                "members": members,
            })

    return groups

def get_ldap_users(conn, server_details):

    users = []

    user_filter = server_details.get('user_filter', '')
    base_dn = server_details.get('base_dn')

    try:
        # search for erpnext users in ldap database
        result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, user_filter)
    except Exception, e:
        frappe.msgprint("Can not find users: {0}".format(base_dn), raise_exception=1)
        conn.unbind_s()
        raise

    for dn, r in result:
        if r.get('mail'):
            full_name = str(r['cn'][0])
            full_name = full_name.split(' ')
            if len(full_name)  == 1:
                first_name = full_name[0]
                last_name = full_name[0]

            if len(full_name)  > 1:
                first_name = full_name[0]
                last_name = full_name[1]

            users.append({
                "mail": str(r['mail'][0]),
                "username": str(r['uid'][0]),
                "first_name": first_name,
                "last_name": last_name,
            })

    return users


def admin_notification(new_profiels):
    msg = get_message(new_profiels)
    receiver = frappe.db.sql("select parent from `tabHas Role` where role = 'System Manager' and parent not like '%administrator%'", as_list=1)[0]
    
    if len(new_profiels) >= 1:
        frappe.sendmail(recipients=receiver, sender=None, subject="[LDAP-ERP] Newly Created Profiles", message=cstr(msg))


def get_message(new_profiels):
    return """ Hello Admin. \n
            Profiles has been synced. \n
            Please check the assigned roles to them. \n
            List is as follws:\n %s """%'\n'.join(new_profiels)


def upsert_profile(user, pwd, groups, roles):
    """ Creates or updates user profile. """
    result = None

    profile = frappe.db.sql("select name from tabUser where username = '{0}' or email ='{1}'". format(user['username'], user['mail']) )
    if not profile:
        d = frappe.new_doc("User")
        d.owner = "Administrator"
        d.email = user['mail']
        d.username = user['username']
        d.first_name = user['first_name']
        d.last_name = user['last_name']
        d.enabled = 1
        d.new_password = pwd
        d.creation = nowdate() + ' ' + nowtime()
        d.user_type = "System User"
        d.save(ignore_permissions=True)
        result = "insert"
    else:
        frappe.db.sql("update tabUser set email='%s', first_name='%s', last_name='%s' where username='%s' or email ='%s'" %
                      (user['mail'], user['first_name'], user['last_name'], user['username'], user['mail']))
        result = "update"

    # update user's roles, as they might have changed from last login
    update_roles(user, get_role_list(roles))
    update_user_permissions(user, groups)

    return result


def update_roles(user, roles):
    user = frappe.get_doc("User", user['mail'])
    user_roles = user.get("roles") or []
    #current_roles = [d.role for d in user_roles if d.owner=="ldap" ]
    current_roles = [d.role for d in user_roles ]

    user.remove_roles(*list(set(current_roles) - set(roles)))
    user.add_roles(*roles)

    for role in roles:
        # change new roles ownership to ldap
        frappe.db.sql("update `tabHas Role` set owner='ldap' where parent='%s' and role='%s'" % (user.email, role))


def update_user_permissions(user, groups):
    """Sets projects permission based on ldap posix groups"""

    # current_permissions = list(itertools.chain.from_iterable(
    #     (frappe.db.sql("SELECT for_value FROM `tabUser Permission` WHERE owner='ldap' "
    #                     "AND user='%s' AND allow='Project'" % (user['mail'])))))

    # not_existing_permissions = list(set(current_permissions) - set(groups))
    # new_permissions = list(set(groups) - set(current_permissions))

    # # delete not existing project permissions
    # if not_existing_permissions:
    #     frappe.db.sql("DELETE FROM `tabUser Permission` WHERE user='%s' AND allow='Project' "
    #                   " AND for_value IN (%s) "
    #                   % (user['mail'], ','.join("'%s'" % p for p in not_existing_permissions)))

    # if new_permissions:
    #     for name in new_permissions:
    #         d = frappe.get_doc({
    #             "owner": "ldap",
    #             "doctype": "User Permission",
    #             "user": user['mail'],
    #             "allow": "Project",
    #             "for_value": name,
    #             "apply_for_all_roles": 0
    #         })

    #         d.insert(ignore_permissions=True)

    clear_cache(user['mail'])


def get_role_list(groups):
    """ Map ldap groups to erpnext roles using matched mapper."""
    role_list = []
    for group in groups:
        role_list.extend(frappe.db.sql("select role from `tabRole Mapper Details` where parent='%s'" % (group), as_list=1))
    return list(itertools.chain(*role_list))