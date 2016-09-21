#!/usr/bin/python
# -*- coding: utf-8 -*-

#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Настройки скрипта

# Если пользователь в этой группе, то почта не создается
exclude_group =  'CN=no-email,OU=Users,DC=example,DC=com'

# OU в котором искать новых пользователей
scope   = 'OU=Users,DC=example,DC=com'

# Домен AD
domain = "example.com"

# LDAP сервер и порт
ldapserver="address-or-fqdn-dc"
port="389"

# Почтовый домен в Zimbra
emaildomain="example.com"

# Домен, имя пользователя и его пароль от которого будем искать в LDAP
ldapbinddomain="example"
ldapbind="ad-user-name"
ldappassword="ad-password"

# Путь до zmprov, НЕ МЕНЯЕМ если Zimbra стоит по умолчанию
pathtozmprov="/opt/zimbra/bin/zmprov"

#--------------------------------------------------------------------------------------------------
import ldap, string, os, time, sys 

def zm_is_active(p_account):
	global zm_locked
	
	if p_account+"\n" in zm_locked:
		return False
	else:
		return True

def ad_allow_email(p_groups):
	global exclude_group

	if exclude_group in p_groups:
		return False
	else:
		return True

# Получаем список всех пользователей на зимбре
f = os.popen(pathtozmprov +' sa \'(mail=*@%s)(zimbraAccountStatus=*)\'' % (emaildomain))
zm_all = []
zm_all = f.readlines()
f.close()

f = os.popen(pathtozmprov +' sa \'(mail=*@%s)(zimbraAccountStatus=locked)\'' % (emaildomain))
zm_locked = []
zm_locked = f.readlines()
f.close()

ad_locked = []

# Соединяемся с LDAP
l=ldap.initialize("ldap://"+ldapserver+"."+domain+":"+port)
l.simple_bind_s(ldapbinddomain+"\\"+ldapbind,ldappassword)

try:
	# Получаем всех не отключенных пользователей
	res = l.search_s(scope, ldap.SCOPE_SUBTREE, "(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))",  ['sAMAccountName', 'cn', 'displayName', 'givenName', 'sn', 'memberOf'])
except ldap.LDAPError, error_message:
	print error_message

for (dn, val) in res:
	sAMAccountName = val['sAMAccountName'][0].lower()
	cn = val['cn'][0].lower()
	try:
		displayName = val['displayName'][0].lower()
	except:
		displayName = ""

	try:
		givenName = val['givenName'][0].lower()
	except:
		givenName = ""

	try:
		sn = val['sn'][0].lower()
	except:
		sn = ""

	try:
		memberOf = val['memberOf']
	except:
		memberOf = "none"

	givenName.capitalize()
	sn.capitalize()

	zm_account = sAMAccountName+"@"+emaildomain

	if zm_account+"\n" not in zm_all: #Есть в АД, но нет в Zimbra, добавляем
		if ad_allow_email(memberOf):
			print("Добавляем новый почтовый ящик %s на сервер" % (zm_account))
			os.system(pathtozmprov+" ca %s \'\' displayName \'%s\' givenName \'%s\' sn \'%s\'" % (zm_account, displayName, givenName, sn))
			#print(pathtozmprov+" ca %s \'\' displayName \'%s\' givenName \'%s\' sn \'%s\'" % (zm_account, displayName, givenName, sn))
		else:
			print("Добавление почтового ящика %s пропущено, т.к. пользователь в группе %s " % (zm_account, exclude_group))
	else: #есть в zimbre
		if (not ad_allow_email(memberOf)) and (zm_is_active(zm_account)): #в зимбре активен но в группе exclude_group
			print("Почтовый ящик %s активен в зимбре но находится в группе %s, блокируем его." % (zm_account, exclude_group))
			os.system(pathtozmprov+" ma %s zimbraAccountStatus locked zimbraHideInGal TRUE" % (zm_account))
			ad_locked.append(zm_account);
		elif (ad_allow_email(memberOf)) and (not zm_is_active(zm_account)): #в зимбре не активен, но не в группе exclude_group
			print("Почтовый ящик %s заблокирован в зимбре но не находится в группе %s, разблокируем его." % (zm_account, exclude_group))
			os.system(pathtozmprov+" ma %s zimbraAccountStatus active zimbraHideInGal FALSE" % (zm_account))
			zm_locked.remove(zm_account+"\n")
		elif (not ad_allow_email(memberOf)) and (not zm_is_active(zm_account)):
			ad_locked.append(zm_account)

try:
	# Получаем всех отключенных пользователей
	res = l.search_s(scope, ldap.SCOPE_SUBTREE, "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))",  ['sAMAccountName'])
except ldap.LDAPError, error_message:
	print error_message

for (dn, val) in res:
	sAMAccountName = val['sAMAccountName'][0].lower()
	zm_account = sAMAccountName+"@"+emaildomain
	ad_locked.append(zm_account)
	if (zm_account+"\n" in zm_all) and (zm_is_active(zm_account)):
		print("Блокируем ящик %s, т.к. пользователь заблокирован в АД..." % (zm_account))
		os.system(pathtozmprov+" ma %s zimbraAccountStatus locked zimbraHideInGal TRUE" % (zm_account))

for zm_account in zm_locked:
	zm_account = zm_account.strip()
	if (zm_account not in ad_locked):
		print("Ящик %s заблокирован, но в АД нет, разблокируем" % (zm_account))
		os.system(pathtozmprov+" ma %s zimbraAccountStatus active zimbraHideInGal FALSE" % (zm_account))

l.unbind_s()

