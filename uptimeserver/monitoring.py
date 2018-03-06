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
Monitoring module

Monitoring Manager, thread management etc.
"""

from .services import Service
from .helper import DaemonHelper
import threading
import time
from datetime import datetime

class ServicesMonitoring:
    """ServicesMonitoring is the Monitoring manager.
    
    It permits to :
    - add/remove Services to the monitoring queue
    - have multiple providers of Services.
    - avoid redondant checks
    - manage tasks (load repartition per thread)
    - start/stop monitoring
    - Manage fast retry after a first service FAIL detection
    - Notify the backend to update a service status
    
    This is thread safe and so it is possible to add/remove services from any other threads.
    It is possible to add/delete services on the fly (running state or not)
    
    Constructor
    
    Keyword Arguments:
        backend_notify (function address): Function that will be called to notify the backend of a "new" status
        max_services (int): Number of services to check per thread
        check_every_seconds (int): Check a service every X seconds
        fast_retry_every_seconds (int): Fast check retry when a service is going down after X seconds
    
    """
    #providers = dict()
    #tasks = []
    #lock = threading.Lock()
    #isRunning = False
    #backend_notify = None
    #fast_retry_every_seconds = 3

    def __init__(self, backend_notify = None, max_services = 10, check_every_seconds = 300, fast_retry_every_seconds = 3):
        self.providers = dict()
        self.tasks = []
        self.lock = threading.Lock()
        self.isRunning = False
        self.backend_notify = backend_notify
        self.max_services = max_services
        self.check_every_seconds = check_every_seconds
        self.fast_retry_every_seconds = fast_retry_every_seconds

    def add(self, service, provider="default"):
        """Add a service to the Monitoring
        
        Args:
            service (Service): a Service
        
        Keyword Arguments:
            provider (String): Name of the provider
        
        """
        
        # protect self.providers
        with self.lock:
            if self.providers.get(provider) is None:
                self.providers[provider] = []
    
            # Look for an existing service in a provider
            service_already_set_on_a_provider = False
            for key in self.providers:
                if service in self.providers[key]:
                    service_already_set_on_a_provider = True
                    break
    
            if not service_already_set_on_a_provider:
                # Add the service to the provider
                self.providers[provider].append(service)
                # Add the service to a task
                self.task_add(service)

    def remove(self, service, provider="default"):
        """Remove a service to the Monitoring
        
        Args:
            service (Service): a Service
        
        Keyword Arguments:
            provider (String): Name of the provider
        
        """
        
        # protect self.providers
        with self.lock:
            if self.providers.get(provider) is None:
                return

            if service in self.providers[provider]:
                # remove the service
                self.providers[provider].remove(service)
                # remove the service from a task
                self.task_remove(service)

    def remove_provider(self, provider="default"):
        """Remove all services of the provider to the Monitoring
        
        Keyword Arguments:
            provider (String): Name of the provider
        
        """
        
        # protect self.providers
        with self.lock:
            if self.providers.get(provider) is None:
                return

            for service in self.providers[provider]:
                # remove the service from a task
                self.task_remove(service)

            # remove the provider and all services on it
            del self.providers[provider]

    def remove_delegation(self, hook, extra, provider="default"):
        """Remove services based on the kook response
        
        Args:
            hook (function): function that will decide to remove or not a service
            extra (object): should be an object readeable for the hook function. This permit to pass some information to the hook from the provider/service.
        
        Keyword Arguments:
            provider (String): Name of the provider
        
        """
        
        # protect self.providers
        with self.lock:
            if self.providers.get(provider) is None:
                return

            # We need to work on a copy [:] to remove services on the real variable
            # during an iteration on it.
            for service in self.providers[provider][:]:
                if hook(service, extra):
                    # remove the service
                    self.providers[provider].remove(service)
                    # remove the service from a task
                    self.task_remove(service)

    def task_add(self, service):
        """Add the service to a task
        
        Args:
            service (Service): a Service
        
        """
        
        # try to add the service on an existing taks if we have enough room
        for task in self.tasks:
            if task.add(service):
                return

        # We don't have enough room and we need to create a new task to handle the service
        t = TaskMonitoring(self.backend_notify, self.max_services, self.check_every_seconds, self.fast_retry_every_seconds)
        t.add(service)
        self.tasks.append(t)

        # start the task if the monitoring is already running
        if self.isRunning:
            t.start()

    def task_remove(self, service):
        """Remove the service from a task
        
        Args:
            service (Service): a Service
            
        """
        task_ret = None

        # Find and remove the service from a task
        for task in self.tasks:
            if task.remove(service):
                task_ret = task
                break

        # if the task is empty, we can remove it to freedom unused resources
        if task_ret is not None and task_ret.isEmpty():
            task_ret.stopTasks()
            self.tasks.remove(task_ret)

    def startMonitoring(self):
        """Sarting all tasks"""
        
        # protect self.providers and self.isRunning
        with self.lock:
            if not self.isRunning:
                print("Sarting monitoring ...")
                self.isRunning = True
                for task in self.tasks:
                    task.start()
                print("Monitoring started")

    def stopMonitoring(self):
        """Stopping all tasks"""
        
        # protect self.providers and self.isRunning
        with self.lock:
            if self.isRunning:
                print("Stopping monitoring ...")
                self.isRunning = False
                print("tasks to remove: " + str(len(self.tasks)))
                for task in self.tasks:
                    task.stopTask()
                for task in self.tasks:
                    task.join()
                print("Monitoring stopped")

class TaskMonitoring(threading.Thread):
    """TaskMonitoring will check few services.
    
    A task is created and controlled only by the ServicesMonitoring.
    
    Constructor
    
    Keyword Arguments:
        backend_notify (function address): Function that will be called to notify the backend of a "new" status
        max_services (int): Number of services to check per thread
        check_every_seconds (int): Check a service every X seconds
        fast_retry_every_seconds (int): Fast check retry when a service is going down after X seconds
    """
    
    #backend_notify = None
    #max_services = 0
    #check_every_seconds = 300
    #fast_retry_every_seconds = 3
    #services = []
    #stop_switch = False
    #lock = threading.Lock()

    def __init__(self, backend_notify = None, max_services = 10, check_every_seconds = 300, fast_retry_every_seconds = 3):
        threading.Thread.__init__(self)
        self.backend_notify = backend_notify
        self.max_services = max_services
        self.check_every_seconds = check_every_seconds
        self.fast_retry_every_seconds = fast_retry_every_seconds
        self.services = []
        self.stop_switch = False
        self.lock = threading.Lock()

    def add(self, service):
        """Add a service
        
        Args:
            service (Service): a Service
            
        Returns:
            bool: Added (True) or Not enough room on the thread (False)
        """
        ret = False

        # protect self.services
        with self.lock:
            if (len(self.services) < self.max_services):
                # we have some room left so add the service to the queue
                self.services.append(service)
                ret = True

        return ret

    def remove(self, service):
        """Remove the service
        
        Args:
            service (Service): a Service
            
        Returns:
            bool: Service removed (True) or Not found (False)
        """
        ret = False

        # protect self.services
        with self.lock:
            # remove the service if we have it on the queue
            if service in self.services:
                self.services.remove(service)
                ret = True

        return ret

    def isEmpty(self):
        """Is empty ?
        
        Returns:
            bool: Empty queue (True) or not (False)
        
        """
        return (len(self.services) == 0)

    def stopTask(self):
        """Request the task to stop"""
        print("stopping task ...")
        self.stop_switch = True
        
    def checkService(self, service):
        """Check a service
        
        Permit to check a service, to retry a check, to notify the backend of a new state, ...
        
        Args:
            service (Service): a Service
        """
        
        previous_status, status, extra = service.checkMe()
        
        # do we need to update the backend or to recover from undetermined state (previous_status is None) ?
        if ( status == Service.OK and ( previous_status is None or previous_status == Service.FAIL ) ) or \
            ( service.isHardFailure() and ( previous_status is None or previous_status == Service.OK )):
                # Send to backend
                if self.backend_notify is not None \
                        and not self.backend_notify(service, status, extra):
                        # Notify failed so we reset status to None to get the chance to update
                        # the status on the next check for this service
                        service.reset_status()
        
        # fast retry ?
        if service.isSoftFailure():
            print("%s soft_failure [%d] for %s : %s" % (datetime.today().strftime("[%Y-%m-%d %H:%M:%S]"), service.failure_counter, str(type(service)), str(service)))
            # recursive call
            # TODO: improve it to have fastretry thread to don't delay checks of all other services in this task.
            #       with a fastretry thread we need to put on hold the check of this service in the task thread and
            #       to re-introduce once the status is enforced to be FAIL or OK
            time.sleep(self.fast_retry_every_seconds)
            self.checkService(service)

    def run(self):
        """Start the task"""
        
        print("starting task ...")

        self.stop_switch = False

        while not self.stop_switch:
            start_batch = time.time()

            # We are using a copy of services [:] to avoid conflict with add and remove function that can be triggered from another
            # thread. So the addition or suppression of service will be take into account only after this running batch and NOT in
            # real time
            for service in self.services[:]:
                # try to stop early if requested
                if self.stop_switch:
                    break
                self.checkService(service)

            end_batch = time.time()

            # Recalculate the time to sleep to provide something near the check_every_seconds for all checks
            
            if end_batch >= start_batch:
                sleep_time = int(self.check_every_seconds - ( end_batch - start_batch ))
            else:
                print("Something goes wrong with the time reported. We will use the check_every_seconds value to be safe")
                sleep_time = self.check_every_seconds

            if sleep_time < 0:
                print("The thread is full and the time to run every checks is longer than the check_every_seconds. Please review the number of check per thread or the check_every_seconds")
            else:
                DaemonHelper().sleep_with_stop_switch(sleep_time, self)

        print("task stopped")
