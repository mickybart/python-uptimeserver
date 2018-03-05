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
config

Permit to manage global configurations
"""

from providers import IngressProvider, IngressProviderConfig
from services import *
import os
import re

class Config:
    default_env = "local"
    os_env = "UPTIME_ENV"
    
    env = {
        "local" : {
            "storage" : {
                "backend" : "MongoStorage",
                "uri": "mongodb://localhost:27017",
                "db": "cloud-uptime-local"
                },
            
            "server" : {
                "with_consolidation" : True
                },
            
            "consolidations" : {
                "sla" : {},
                "status" : {
                    "filter": {},
                    "down_since": 600
                    }
                },
            
            "monitoring": {
                "max_services": 15,
                "check_every_seconds": 60,
                "fast_retry_every_seconds" : 5
                }
            }
        }
            
    providers = []
    services = []
    
    def __init__(self):
        config_env = os.environ.get(self.os_env, self.default_env)
        print("Config: environment: %s" % config_env)
        if config_env not in self.env.keys():
            raise Exception("Environment UPTIME_ENV=%s not set in config.py" % config_env)
        
        self.active_env = config_env
    
    def getconfig(self):
        return self.env[self.active_env]
    
    def getgeneric(self, section, key, default):
        if key is not None:
            return self.getconfig()[section].get(key, default)
        
        return self.getconfig()[section]
    
    def getstorage(self, key=None, default=None):
        return self.getgeneric("storage", key, default)
    
    def getserver(self, key=None, default=None):
        return self.getgeneric("server", key, default)
    
    def getmonitoring(self, key=None, default=None):
        return self.getgeneric("monitoring", key, default)
    
    def getconsolidations(self):
        return self.getconfig()["consolidations"]
    
    def configure(self, server, monitoring):
        # Providers
        for provider in self.providers:
            server.providers_add(provider)
        
        # Services
        for service in self.services:
            monitoring.add(service)

