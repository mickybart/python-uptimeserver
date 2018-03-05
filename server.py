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
Server

Configuring Services and Providers
Start/Stop Monitoring
"""

from storage import MongoStorage
from consolidation import MongoStorageConsolidationSLA, MongoStorageConsolidationStatus
from config import Config
from monitoring import ServicesMonitoring
import signal
import sys
import os

class Server:
    """Server is responsible to manage monitoring, providers and storage backend.
    
    A server is essentially composed by:
    - 1 Storage (storage backend)
    - X providers (components to add/remove/modify services on the fly)
    - X consolidations (components to consolidate some data based on uptime checks)
    - 1 ServicesMonitoring (monitoring management)
    
    A server will start/stop the Monitoring, Providers and Consolidations
    
    """
    #storage = None
    #monitoring = None
    #isRunning = False
    #providers = []
    #consolidations = []

    def __init__(self, config, donotconfig=False):
        """Server constructor
        
        Args:
            config (Config): Configuration
        
        """
        self.storage = None
        self.isRunning = False
        self.providers = []
        self.consolidations = []
        
        # mainly to configure the backend
        self.configure(config)
        
        # Services Monitoring
        self.monitoring = ServicesMonitoring(self.storage_get_notify(), \
            config.getmonitoring("max_services"), \
            config.getmonitoring("check_every_seconds"),
            config.getmonitoring("fast_retry_every_seconds"))
        
        # Configure the Server and Monitoring
        if not donotconfig:
            config.configure(self, self.monitoring)

    def exit(self, code, msg):
        """Exit the program
        
        Args:
            code (int): exit code
            msg (String): last message to display before the end of the program
        
        """
        print(msg)
        sys.exit(code)
        
    def configure(self, config):
        """Configure the server based on config provided
        
        Args:
            config (Config): Configuration
            
        Raises:
            Exception: Configuration error
        
        """
        
        # We only support MongoStorage for now
        if config.getstorage("backend") == "MongoStorage":
            self.configure_mongostorage(config, config.getserver("with_consolidation"))
            return
        
        raise Exception("No configuration done !")

    def configure_mongostorage(self, config, with_consolidation=False):
        """Set the storage backend with MongoStorage
        
        Args:
            config (Config): Configuration
        
        Kwargs:
            with_consolidation (bool): Use default consolidation associated to MongoStorage or not.
            
        Raises:
            Exception: Storage is not ready or already defined.
        
        """
        
        if self.storage is not None:
            raise Exception("Storage is already defined !")

        self.storage = MongoStorage(config.getstorage("uri"), config.getstorage("db"))
        if not self.storage.isReady():
            self.exit(1, "Storage is not ready !")
        
        if with_consolidation:
            self.consolidations.append(MongoStorageConsolidationSLA(self.storage))
            self.consolidations.append(MongoStorageConsolidationStatus(self.storage, \
                config.getconsolidations()["status"]["filter"], \
                config.getconsolidations()["status"]["down_since"]))

    def storage_get_notify(self):
        """Get the storage notify function
        
        Permit to get the notify function that can be used to define a Service.
        That will permit a Service to call it to notify about it status.
        
        Raises:
            Exception: If the storage is not defined
        
        """
        if self.storage is None:
            raise Exception("Storage not defined !")

        return self.storage.update_status

    def providers_add(self, provider):
        """Add a provider
        
        Args:
            provider (Provider): a provider
        
        """
        self.providers.append(provider)

    def providers_remove_all(self):
        """Remove all providers
        """
        self.providers[:] = []

    def running(self):
        """Is running ?"""
        return self.isRunning

    def terminate_signal(self, signal, frame):
        """terminate the program on a specific signal"""
        print("")
        self.stopMonitoring()
        #self.exit(0, "Bye !")
        os.kill(os.getpid(), 9)

    def startMonitoring(self):
        """Start the monitoring and all relative components (providers, consolidations ...)"""
        print("Starting ...")
        if self.monitoring is not None:
            for provider in self.providers:
                provider.start()
            for consolidation in self.consolidations:
                consolidation.start()
            self.monitoring.startMonitoring()
            self.isRunning = True
        
        signal.signal(signal.SIGINT, self.terminate_signal)
        print('Press Ctrl+C to exit')
        signal.pause()

    def stopMonitoring(self):
        """Stop the monitoring
        
        This action can be long depending what is going on (eg: consolidation in progress). We don't force a shutdown to
        try to have a clean shutdown on all components.
        
        """
        print("Stopping ...")
        if self.monitoring is not None:
            for provider in self.providers:
                provider.stopProvider()
            for consolidation in self.consolidations:
                consolidation.stopConsolidation()
            self.monitoring.stopMonitoring()
            for consolidation in self.consolidations:
                consolidation.join()
            self.isRunning = False
