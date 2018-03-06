# Copyright (c) 2018 Yellow Pages Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper module

Permit to provide some dev tools
"""

import time

class DaemonHelper:
    def sleep_with_stop_switch(self, sleep_time, obj, sleep_inc=5):
        """Sleep but wake up some time to check if a stop was requested
        
        If stop_switch is set to True, we will quit the sleep.
        
        This is useful for long sleep and thread not set as a daemon.
        
        Args:
            sleep_time (int): duration in seconds
            obj (object): object with a stop_switch bool variable
            
        Keyword Arguments:
            sleep_inc (int): deep sleep time in seconds
        
        """
        
        if sleep_time > 0:
            sleep_done = 0
            while(sleep_done < sleep_time):
                # try to stop early if requested
                if obj.stop_switch:
                    break

                if (sleep_time - sleep_done < sleep_inc):
                    time.sleep(sleep_time - sleep_done)
                else:
                    time.sleep(sleep_inc)
                sleep_done = sleep_done + sleep_inc
                
