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

#$1 = User
#$2 = Remote Host
#$3 = Password

# Missing ssh
if  [ ! -f "/usr/bin/ssh" ]; then
	printf 2

# Missing sshpass
elif [ ! -f "/usr/bin/sshpass" ]; then
	printf 3


# Connection Established
elif [[ $(sshpass -p $3 ssh -o StrictHostKeyChecking=no -l $1 $2 "echo 1") == 1 ]]; then
	printf 1

# Connection failed
else
	printf 0
fi