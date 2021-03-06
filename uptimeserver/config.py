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
config module

Permit to manage global configurations
"""

import json
import base64

class Config:
    """Configuration for Monitoring and sub-modules
    
    This class can be overriden and so adapted by every compagnies to
    set different policy about what to monitor and in which way.
    
    You should check this main function :
        configure
        
    Constructor
    
    Args:
        secret (json): json with all secrets and configuration used by the config.
    """
    
    kubeconfig_path = '/root/.kube/config'
    
    providers = []
    services = []
    
    def __init__(self, secret):
        self.secret = secret
    
    def getgeneric(self, section, key, default):
        if key is not None:
            return self.secret[section].get(key, default)
        
        return self.secret[section]
    
    def getstorage(self, key=None, default=None):
        return self.getgeneric("storage", key, default)
    
    def getserver(self, key=None, default=None):
        return self.getgeneric("server", key, default)
    
    def getmonitoring(self, key=None, default=None):
        return self.getgeneric("monitoring", key, default)
    
    def getconsolidations(self):
        return self.secret["consolidations"]
    
    def configure(self, server, monitoring):
        """ Configure the server and monitoring
        
        eg: This is where the monitoring of services will be set.
        
        Args:
            server (Server): The server
            monitoring (ServicesMonitoring): The monitoring orchestrator
        """
        # Providers
        for provider in self.providers:
            server.providers_add(provider)
        
        # Services
        for service in self.services:
            monitoring.add(service)

    def writekubeconfig(self, target=None):
        """Write the kube file configuration
        
        Keyword Arguments:
            target (str): path of the config file
        
        Raises:
            Exception: Issue to decode or write the file
        """
        if not target:
            target = self.kubeconfig_path
        
        with open(target, 'wb') as f:
            f.write(base64.b64decode(self.secret["kubeconfig"]))
        
    def load_json(json_file):
        """Load JSON file
        
        Args:
            json_file (str): filename of a json file
            
        Returns:
            dict: content of the file
        """
        try:
            with open(json_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
