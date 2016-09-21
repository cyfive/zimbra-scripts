#!/bin/bash

# Import mail from Exchange to Zimbra
# Author: Stanislav V. Emets
# e-mail: emetssv@mail.ru

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

#Set to address of Zimbra server
zm_server=192.168.1.1

#Set to address of Exchange server
exch_server=192.168.1.2

users_list=`cat ./users.csv | tr -d " "`

#Path to imapsync
IMAPSYNC=/usr/bin/imapsync

for user_line in $users_list; do
	user_name=`echo "$user_line" | cut -d ";" -f 1`
	user_pass=`echo "$user_line" | cut -d ";" -f 2`
	$IMAPSYNC --host1 $exch_server --user1=$user_name --authmech1=PLAIN --password1=$user_pass --host2=$zm_server --authmech2=PLAIN --ssl2 --user2=$user_name --password2=$user_pass --justlogin --nolog > /dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "$user_name - тестовая авторизация прошла успешно."
		$IMAPSYNC --host1 $exch_server --user1=$user_name --authmech1=PLAIN --password1=$user_pass --host2=$zm_server --authmech2=PLAIN --ssl2 --user2=$user_name --password2=$user_pass --nocheckmessageexists --nofoldersizes --nofoldersizesatend
	else
		echo "$user_name - не прошла тестовая авторизация"
	fi
done
