# Copyright 2016 Patrick Pedersen <ctx.xda@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash

#$1 = Timeout
#$2 = User
#$3 = Remote Host
#$4 = Password

OPTIONS="-o StrictHostKeyChecking=no"

if [[ $1 == "0" ]]; then
	OPTIONS+=" -o ConnectTimeout=$1"
fi

# Missing ssh
if  [ ! -f "/usr/bin/ssh" ]; then
	printf 2

# Missing sshpass
elif [ ! -f "/usr/bin/sshpass" ]; then
	printf 3


# Connection Established 
elif [[ $1 == "0" && $(sshpass -p $4 ssh -o StrictHostKeyChecking=no -l $2 $3 "echo 1") == 1 ]]; then
	printf 1

# Connection Established with timeout
elif [[ $(sshpass -p $4 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$1 -l $2 $3 "echo 1") == 1 ]]; then
	printf 1

# Connection failed
else
	printf 0
fi