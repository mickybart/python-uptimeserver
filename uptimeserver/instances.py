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

"""
Instances module

Permit to manage some lock about multiple instances
"""

import threading
import time
import os
import signal

class OneInstanceLock(threading.Thread):
    """One active instance only
    
    OneInstanceLock permit to create an heartbeat based on Mongo backend to warranty
    that only one instance will be active on the same database.
    
    Currently, the implementation of the server do not support multiple instances if there is
    an overlapping of some services to check.
    
    This class permit to start the server with a lock and permit CI/CD integration, or standby server mode
    with automatic switch to active one if the previous active one is in failure...
    
    Constructor
    
    Args:
        server (Server): a server
    
    Keyword Arguments:
        alive (int): number of seconds to check if the server is alive
        inactive_during (int): number of seconds to wait before considering a server as dead
    """
    
    def __init__(self, server, alive=60, inactive_during=180):
        threading.Thread.__init__(self)
        self.server = server
        self.alive = alive
        self.inactive_during = inactive_during
        self.isActive = False
        self.isRunning = False
        
        self.instance_state = self.server.storage.db.get_collection("instance_state")
        if len(self.instance_state.index_information()) == 0:
            # collection does not exist
            # create it and create indexes
            self.server.storage.db.create_collection("instance_state")
            self.instance_state.create_index( "date" )
        
    def switch_this_instance_to_be_active(self):
        """Try to switch this instance as the active one
        
        Returns:
            bool: agree to switch (True) or not (False) 
        """
        result = self.instance_state.find_one({})
        if result is None:
            result = self.instance_state.insert_one({"date" : int(time.time())})
            self.id = result.inserted_id
        else:
            self.id = result["_id"]
        
        return self.heartbeat(self.inactive_during)
    
    def heartbeat(self, seconds_before):
        """Heartbeat check
        
        Args:
            seconds_before (int): lastest maximum expected heartbeat update in seconds
            
        Returns:
            bool: OK (True) or NOT (False)
        """
        when = int(time.time())
        
        try:
            result = self.instance_state.update_one({"_id": self.id, "date" : { "$lte" : when - seconds_before }}, { "$set" : {"date" : when} }, upsert=True)
            if result is not None:
                return True
        except:
            pass
        
        return False

    def run(self):
        """Start
        
        - Check if we can be the active instance or not
        - Check heartbeat
        - Stop us if heartbeat failed
        """
        try:
            self.isRunning = True
            
            print("Try to be the active instance ...")
            
            # Try to be the active instance
            while not self.switch_this_instance_to_be_active():
                time.sleep(self.alive)
            
            print("Sarting the server ...")
            
            # start Monitoring
            self.server.startMonitoring(nosignalhandling=True)
            
            print("Heartbeat loop ...")
            
            # Heartbeat
            time.sleep(self.alive + 1)
            while self.heartbeat(self.alive):
                time.sleep(self.alive + 1)
                
            print("Heartbeat issue, stopping the server ...")
        except:
            pass
        finally:
            # stop Monitoring
            self.server.stopMonitoring()
            self.isRunning = False
            # kill myself (temporary workaround)
            os.kill(os.getpid(), 9)
    
