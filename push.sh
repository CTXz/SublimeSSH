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
#$5 = Target local file
#$6 = Remote host destination

OPTIONS="-o StrictHostKeyChecking=no" 

if [[ $1 == "0" ]]; then
	OPTIONS+=" -o ConnectTimeout=$1"
fi

# Push
sshpass -p $4 scp $OPTIONS $5 $2@$3:$6

# SCP Succeeded
if [[ $(sshpass -p $4 ssh $OPTIONS -l $2 $3 "find $6") == $6 && \
	 "$(cat $5)" == "$(sshpass -p $4 ssh $OPTIONS -l $2 $3 "cat $6")" ]]; then
	printf 1

# SCP failed!
else
	printf 0
fi