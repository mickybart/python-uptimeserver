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
Providers

Providers permit to have an automatic way to create services based on a remote source.
The provider will add/remove/modify services on the Monitoring with hook functions.

The remote source can be Kubernetes (for IngressProvider), a file, an unix socket, else
"""

from kubernetes import client, config, watch
from .services import IngressService
import threading
import time

class Provider(threading.Thread):
    """Base class for Provider implementation
    
    The provider is designed to work with a ServicesMonitoring.
    
    The class which inherit Provider need to implement:
    def stopProvider(self):
    def run(self):
    
    """
    #name = None
    #monitoring
    #category

    def __init__(self, name, monitoring, category = None):
        """Provider constructor
        
        Args:
            name (String): unique name of the provider
            monitoring (ServicesMonitoring): monitoring where to create new Services to check
            
        Kwargs:
            category (String): Used during a service creation (eg: ns, infra, client1 ...)
        
        """
        threading.Thread.__init__(self)
        self.name = name
        self.monitoring = monitoring
        self.category = category

    def services_add(self, services):
        """Add services
        
        Args:
            services (list): list of Services to add
        
        """
        for service in services:
            self.monitoring.add(service, self.name)

    def services_remove(self, services):
        """Remove services
        
        Args:
            services (list): list of Services to remove
        
        """
        for service in services:
            self.monitoring.remove(service, self.name)

    def services_cleanup(self):
        """Remove all services of this provider"""
        self.monitoring.remove_provider(self.name)

    def services_remove_delegation(self, hook, extra):
        """Remove services decided by the hook function
        
        Args:
            hook (function): function that will decide to remove or not a service
            extra (object): should be an object readeable for the hook function. This permit to pass some information to the hook from the provider/service.
        
        """
        self.monitoring.remove_delegation(hook, extra, self.name)

    def __str__(self):
        return "Provider: " + self.name

    def stopProvider(self):
        print("Please implement this method !")

    def run(self):
        print("Please implement this method !")

class IngressProvider(Provider):
    """Ingress Provider
    
    Permit to collect ingress events/entries to create Services to monitor.
    We are using Kubernetes in this provider.
    
    """
    #k8s = None
    #w = None
    #isRunning = False
    #ingress_config = None
    restart_timeout = 30
    watch_timeout_seconds = 86400

    def __init__(self, name, context, monitoring, category = None, ingress_config=None):
        super().__init__(name, monitoring, category)
        
        self.ingress_config = ingress_config

        # Kubernetes API
        self.k8s = client.ExtensionsV1beta1Api(api_client=config.new_client_from_config(context=context))
        self.w = None
        self.isRunning = False

    def ingress_event_to_services(self, event, ns, name, services):
        """Transform an event to an IngressService
        
        Args:
            event (yaml): Kubernetes Ingress event
            ns (String): Namespace
            name (String): Name of the ingress object
            services (list): Add new services to this list (the return)
        
        """
        # For all rules
        for rule in event['object'].spec.rules:
            host = rule.host
    
            # For all paths
            for http_path in rule.http.paths:
                path = http_path.path
    
                # Set Healthcheck URL
                if not path.startswith("/"):
                    path = "/" + path
                if not path.endswith("/"):
                    path = path + "/"
                url = "https://" + host + path + "health"
                
                if self.ingress_config is not None and self.ingress_config.exclude(url):
                    print("Exclude: %s" % url)
                    continue
                else:
                    print("       => %s" % (url))
                
                if self.ingress_config is not None:
                    headers = self.ingress_config.headers(url)
                else:
                    headers = {}
                
                # Create and add the service
                if self.category is not None:
                    services.append(IngressService(ns, name, url, category=self.category, headers=headers))
                else:
                    services.append(IngressService(ns, name, url, headers=headers))

    def ingress_event_deleted(self, event, ns, name):
        """Remove Ingress Services from ServicesMonitoring"""
        services = []
        self.ingress_event_to_services(event, ns, name, services)
        self.services_remove(services)
    
    def ingress_event_added(self, event, ns, name):
        """Add Ingress Services to ServicesMonitoring"""
        services = []
        self.ingress_event_to_services(event, ns, name, services)
        self.services_add(services)
    
    def ingress_event_modified(self, event, ns, name):
        """Modify Ingress Services in ServicesMonitoring
        
        In fact this is mainly a remove/re-add mecanism because we don't have the status of the
        event before it was modified.
        
        """
        
        # extra is used to know what we need to compare/delete and to be thread-safe
        extra = dict()
        extra["ns"] = ns
        extra["name"] = name

        self.services_remove_delegation(self.ingress_event_modified_remove_hook, extra)
        self.ingress_event_added(event, ns, name)

    def ingress_event_modified_remove_hook(self, service, extra):
        """Remove a Service based on extra criteria
        
        This function is called by the ServicesMonitoring as a hook of the remove_delegation
        
        Returns:
        bool. The return code::
            
            True: Remove the service
            False: Do NOT remove the service
        
        """
        if type(service) is IngressService and service.ns == extra["ns"] and service.name == extra["name"]:
            return True

        return False
    
    def dispatch_ingress_event(self, event):
        """Dispatch new events
        
        Args:
            event (yaml): Kubernetes Ingress event
        
        """
        
        if event['object'].kind != 'Ingress':
            # We just manage ingress event. You should filter the watcher to ingress only !
            return
    
        name = event['object'].metadata.name
        ns = event['object'].metadata.namespace
        action = event['type'] # ADDED | MODIFIED | DELETED
    
        print("%s Event: %s %s ns=%s" % (self.name, action, name, ns))
    
        # Dispatch per action
        if action == "ADDED":
            self.ingress_event_added(event, ns, name)
        elif action == "DELETED":
            self.ingress_event_deleted(event, ns, name)
        elif action == "MODIFIED":
            self.ingress_event_modified(event, ns, name)
    
    def ingress_events(self):
        """Ingress events loop"""
        
        print("\ningress_event call\n")
        self.w = watch.Watch()
        for event in self.w.stream(self.k8s.list_ingress_for_all_namespaces, timeout_seconds=self.watch_timeout_seconds):
            self.dispatch_ingress_event(event)
        self.w = None

    def stopProvider(self):
        """see Provider class"""
        print(str(self) + " stopping")
        if self.w is not None:
            self.w.stop()
        self.w = None
        self.isRunning = False

    def run(self):
        """see Provider class"""
        print(str(self) + " started")
        self.isRunning = True

        while self.isRunning:
            # Clean up Ingress Services
            self.services_cleanup()

            # Parse ingress events
            self.ingress_events()
            
            # Avoid storm in case of a k8s issue
            time.sleep(self.restart_timeout)

        print(str(self) + " stopped")

class IngressProviderConfig:
    def exclude(self, url):
        return False
    
    def headers(self, url):
        return {}
    
