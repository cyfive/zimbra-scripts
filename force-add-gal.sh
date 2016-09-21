#!/bin/bash

# Force add shared GAL to all mail accounts
# Author: Stanislav V. Emets
# email: emetssv@mail.ru

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

#Full name of galsync account
zm_gal_account=galsync.xxxxx@example.com


zm_gal_folder=_InternalGAL


zm_mail_domain=example.com

#Path where add GAL
zm_share_name=/Contacts/Shared

ZMPROV=/opt/zimbra/bin/zmprov
ZMMAILBOX=/opt/zimbra/bin/zmmailbox

zm_all_accounts=`$ZMPROV sa "(mail=*@$zm_mail_domain)(zimbraAccountStatus=active)(!(mail=spam*))(!(mail=ham*))(!(mail=gal*))(!(mail=virus*))(!(mail=admin*))"`

for zm_account in  $zm_all_accounts; do
	#проверка подключена ли GAL уже у пользователя
	zm_alredy_exists=`$ZMMAILBOX -z -m $zm_account gaf | grep $zm_gal_account`
	if [ -z "$zm_alredy_exists" ]; then
		$ZMMAILBOX -z -m $zm_gal_account mfg "$zm_gal_folder" account $zm_account r
		$ZMMAILBOX -z -m $zm_account cm "$zm_share_name" $zm_gal_account "$zm_gal_folder"
	fi
done
