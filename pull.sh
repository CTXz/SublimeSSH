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
#$4 = Target Host File
#$5 = Local Destination

# Pull
sshpass -p $3 scp -o StrictHostKeyChecking=no $1@$2:$4 $5

# SCP Succeeded
if [[ -f $5 ]]; then
	printf 1

# SCP failed!
else
	printf 0
fi