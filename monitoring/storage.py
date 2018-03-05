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
Storage backend

Store the content of all services.
"""

import pymongo
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import time
from .services import *
from bson.objectid import ObjectId

class Storage:
    """Base class for Storage implementation

    This class should not be instantiate as all functions are not defined.
    You need it as an helper to create your own Storage backend
    
    Your own storage backend should implement at least:
    
    def stats_get_all_svc(self, query={})
    def stats_get_svc(self, service)
    def stats_get_all_downtimes_svc(self, service, start_date, duration)
    
    but you should consider to override:
    
    def isReady(self)
    def svc_all(self, service, status)  -- or any svc_* for specific management per Service type (MongoService, IngressService, ...)
    
    """

    def __init__(self):
        pass

    # STORE

    def update_status(self, service, status, extra=None):
        """Called by services when a status change is detected during a check

        Args:
            service (Service): Service that requested a status update
            status

        Kwargs:
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        Raises:

        """
        if type(service) is MongoService:
            return self.svc_mongo(service, status, extra)
        elif type(service) is IngressService:
            return self.svc_ingress(service, status, extra)
        elif type(service) is KubernetesService:
            return self.svc_kubernetes(service, status, extra)
        elif type(service) is ElasticsearchService:
            return self.svc_elasticsearch(service, status, extra)
        else:
            return False

    def svc_all(self, service, status, extra):
        """Manage the status change for the service

        Args:
            service (Service): Service that requested a status change
            status (int): new status
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        """
        date = datetime.today().strftime("[%Y-%m-%d %H:%M:%S]")
        
        print(date + " " + str(type(service)) + " : " + str(service) + " [" + str(service.failure_counter) + "] [" + str(service.previous_status) + " -> " + str(status) + "]")
        return True

    def svc_mongo(self, service, status, extra):
        """Manage the status change for a Mongo service

        Args:
            service (MongoService): Mongo Service that requested a status change
            status (int): new status
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        """
        return self.svc_all(service, status, extra)

    def svc_ingress(self, service, status, extra):
        """Manage the status change for a Kubernetes Ingress service

        Args:
            service (IngressService): Ingress service that requested a status change
            status (int): new status
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        """
        return self.svc_all(service, status, extra)
    
    def svc_kubernetes(self, service, status, extra):
        """Manage the status change for a Kubernetes service

        Args:
            service (KubernetesService): Kubernetes service that requested a status change
            status (int): new status
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        """
        return self.svc_all(service, status, extra)
    
    def svc_elasticsearch(self, service, status, extra):
        """Manage the status change for a Elasticsearch service

        Args:
            service (ElasticsearchService): ES service that requested a status change
            status (int): new status
            extra (object): extra data

        Returns:
            bool. The return code::

                True -- Success
                False -- Try later

        """
        return self.svc_all(service, status, extra)

    def isReady(self):
        """Storage is ready or not ?

        Permit to control if the storage is working and if we can use it.

        Returns:
            bool. The return code::

                True -- Ready
                False -- Something is wrong

        """
        return True
    
    # STATS: Date Manipulation
    
    def stats_day_duration(self):
        return timedelta(days=1).total_seconds()
    
    def stats_week_duration(self):
        return timedelta(days=7).total_seconds()
    
    def stats_month_duration(self, timestamp, end_date = False):
        date = datetime.fromtimestamp(timestamp)
        
        if not end_date:
            new_date = date + relativedelta(months=1)
            return (new_date - date).total_seconds()
        else:
            new_date = date + relativedelta(months=-1)
            return (date - new_date).total_seconds()
    
    def stats_year_duration(self, timestamp, end_date = False):
        date = datetime.fromtimestamp(timestamp)
        
        if not end_date:
            new_date = date + relativedelta(years=1)
            return (new_date - date).total_seconds()
        else:
            new_date = date + relativedelta(months=-1)
            return (date - new_date).total_seconds()
        
    def stats_first_date_of_week_number(self, year, num):
        """return the first monday date of the begining of the week number"""
        return datetime.strptime(str(year) + ' ' + str(num) + ' 1', '%G %V %u')
    
    def stats_week_number_of_date(self, date):
        return date.isocalendar()[1]

    # STATS API
    # Permit to provide some stats from the storage backend

    def stats_get_all_sla(self, start_date, duration, hook=None):
        """SLA for all services available on the backend
        
        Args:
            start_date (int): epoch timestamp
            duration (int): period of time in seconds
            
        Kwargs:
            hook (function): function to call for each sla computed

        The SLA will be calculate on the period between start_date
        and ( start_date + duration )

        """

        for service in self.stats_get_all_svc():
            sla = self.stats_get_svc_sla(service, start_date, duration)
            if hook is None:
                print("%s [SLA: %.2f %%]" % (str(service), sla))
            else:
                hook(service, sla)

    def stats_get_all_daily_sla(self, start_date, hook=None):
        """Daily SLA for all services
        
        Args:
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """

        self.stats_get_all_sla(start_date, self.stats_day_duration(), hook)

    def stats_get_all_weekly_sla(self, start_date, hook=None):
        """Weekly SLA for all services
        
        Args:
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """

        self.stats_get_all_sla(start_date, self.stats_week_duration(), hook)
    
    def stats_get_all_monthly_sla(self, start_date, hook=None):
        """ Monthly SLA for all services
        
        Args:
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        self.stats_get_all_sla(start_date, self.stats_month_duration(start_date), hook)
    
    def stats_get_all_yearly_sla(self, start_date, hook=None):
        """Yearly SLA for all services
        
        Args:
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        self.stats_get_all_sla(start_date, self.stats_year_duration(start_date), hook)

    def stats_get_svc_daily_sla(self, service, start_date, hook=None):
        """Daily SLA for a service
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        sla = self.stats_get_svc_sla(service, start_date, self.stats_day_duration())
        if hook is None:
            print("%s [SLA: %.2f %%]" % (str(service), sla))
        else:
            hook(service, sla)

    def stats_get_svc_weekly_sla(self, service, start_date, hook=None):
        """Weekly SLA for a service
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        sla = self.stats_get_svc_sla(service, start_date, self.stats_week_duration())
        if hook is None:
            print("%s [SLA: %.2f %%]" % (str(service), sla))
        else:
            hook(service, sla)
    
    def stats_get_svc_monthly_sla(self, service, start_date, hook=None):
        """Monthly SLA for a service
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        sla = self.stats_get_svc_sla(service, start_date, self.stats_month_duration(start_date))
        if hook is None:
            print("%s [SLA: %.2f %%]" % (str(service), sla))
        else:
            hook(service, sla)
    
    def stats_get_svc_yearly_sla(self, service, start_date, hook=None):
        """Yearly SLA for a service
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            
        Kwargs:
            hook (function): function to call for each sla computed

        """
        
        sla = self.stats_get_svc_sla(service, start_date, self.stats_year_duration(start_date))
        if hook is None:
            print("%s [SLA: %.2f %%]" % (str(service), sla))
        else:
            hook(service, sla)
        
    def stats_get_all_status(self):
        """Display a status list of ALL services"""
        for svc in self.stats_get_all_svc():
            print(svc)

    def stats_get_all_status_for_ns(self, ns):
        """Display a status list of ALL services on a specific namespace 
        
        Args:
            ns (String): Namespace filter
        
        """
        for svc in self.stats_get_all_svc({"ns" : ns}):
            print(svc)
    
    def stats_get_svc_status(self, service):
        """Display a status for a specific service

        Args:
            service (object): anything supported by the backend on the function self.stats_get_svc
            
        """
        result = self.stats_get_svc(service)
        print(result)
        
    def stats_get_svc_sla(self, service, start_date, duration):
        """Compute SLA for a service during a defined period
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            duration (int): number of seconds to analyze since start_date

        Returns:
            Number. An SLA number between 0 and 100. (%)
        
        """
        downtimes = self.stats_get_all_downtimes_svc(service, start_date, duration)
        
        down = 0
        for downtime in downtimes:
            end = downtime["down_end_date"]
            start = downtime["down_start_date"]
            if end == 0 or end > (start_date + duration):
                # fit to the end of the period
                end = start_date + duration
                
            if start < start_date:
                # fit to the start_date of the period
                start = start_date

            if end > start:
                down = down + int(end - start)
            else:
                # Should not happen !
                pass
        
        # should never happen except if the db is not consistent.
        # TODO: notify this invalid state
        if down > duration:
            down = duration

        return 100 - ( down * 100 / duration )

    def stats_get_svc_downtimes(self, service, start_date, duration):
        """Display a list of downtimes for a service during a defined period
        
        Args:
            service (object): anything supported by the backend on the function self.stats_get_all_downtimes_svc
            start_date (int): epoch timestamp
            duration (int): number of seconds to analyze since start_date
        
        """
        downtimes = self.stats_get_all_downtimes_svc(service, start_date, duration)
        for downtime in downtimes:
            print(downtime)

    def stats_get_all_downtimes(self, start_date, duration):
        """Display a list of downtimes for ALL services during a defined period
        
        Args:
            start_date (int): epoch timestamp
            duration (int): number of seconds to analyze since start_date
        
        """
        for svc in self.stats_get_all_svc():
            self.stats_get_svc_downtimes(svc, start_date, duration)

class MongoStorage(Storage):
    """Mongo Storage

    We store :
    - all services in uptime collection with the last status reported
    - all downtimes for every services in uptime_history collection

    We DON'T store:
    - all check status as we consider only 2 status for a service: OK and FAIL.
    """
    #uri = None
    #client = None
    #db = None
    #uptime = None
    #uptime_history = None
    timeout = 5000
    storage_id_svc = "_id_uptime"
    storage_id_downtime = "_id_uptime_history"

    def __init__(self, uri, db_name, timeout=None):
        """MongoStorage constructor 

        Args:
            uri (String): MongoDB uri with all options (ssl, auth, replicaset, etc)
            db_name (String): DB name for the backend

        Kwargs:
            timeout (int): timeout in second to wait an answer from Mongo (default is 5s)

        """
        super().__init__()
        self.uri = uri
        if timeout is not None:
            self.timeout = timeout * 1000

        try:
            # Init Mongo and create DB and collections objects
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=self.timeout)
            self.db = self.client[db_name]
            self.uptime = self.db.get_collection("uptime")
            self.uptime_history = self.db.get_collection("uptime_history")

            if len(self.uptime.index_information()) == 0:
                # collection "uptime" does not exist
                # create it and create indexes
                self.db.create_collection("uptime")
                self.uptime.create_index( [("category", pymongo.HASHED)] )
                self.uptime.create_index( [("ns", pymongo.HASHED)] )

            if len(self.uptime_history.index_information()) == 0:
                # collection "uptime_history"  does not exist
                # create it and create indexes
                self.db.create_collection("uptime_history")
                self.uptime_history.create_index("_id_uptime")

        except:
            self.client = None

    def isReady(self):
        """ see Storage class """
        try:
            # Is the server responding ?
            if self.client.server_info() is not None:
                return True
        except:
            pass

        return False

    def query_exec_find_svc(self, service):
        """Query the DB to find a service

        Args:
            service (Service): a specific service

        Returns:
            Object. The return code::
            
                dict -- Document of the service
                None -- Not available

        Raises:
            Exception: MongoDB issue

        """
        if type(service) is MongoService:
            query = {"category": service.category, "kind" : "Mongo", "description": service.name}
        elif type(service) is IngressService:
            query = {"category": service.category, "kind": "Ingress", "ns": service.ns, "description": service.url}
        elif type(service) is KubernetesService:
            query = {"category": service.category, "kind": "Kubernetes", "description": service.name}
        elif type(service) is ElasticsearchService:
            query = {"category": service.category, "kind": "Elasticsearch", "description": service.name}
        else:
            return None

        try:
            result = self.uptime.find_one(query)
        except:
            raise

        if result is not None:
            # Store the ObjectId on the service itself for caching
            service.storage_add(self.storage_id_svc, result["_id"])

        return result
    
    def query_exec_find_svc_by_id(self, id_svc):
        """Query the DB to find a service based on id

        Args:
            service (ObjectId): _id of the service

        Returns:
            Object. The return code::
            
                dict -- Document of the service
                None -- Not available

        Raises:
            Exception: MongoDB issue

        """
        try:
            result = self.uptime.find_one({"_id" : id_svc})
        except:
            raise
        
        return result

    def query_exec_new_svc(self, service):
        """Query the DB to create a new service

        Args:
            service (Service): service object

        Returns:
            Object. The return code::
            
                ObjectId -- _id of the service
                None -- type(service) is not supported

        Raises:
            Exception: MongoDB issue

        """
        if type(service) is MongoService:
            query = {"category": service.category, "kind" : "Mongo", "description": service.name, "status": Service.OK}
        elif type(service) is IngressService:
            query = {"category": service.category, "kind": "Ingress", "ns": service.ns, "description": service.url, "status": Service.OK}
        elif type(service) is KubernetesService:
            query = {"category": service.category, "kind": "Kubernetes", "description": service.name, "status": Service.OK}
        elif type(service) is ElasticsearchService:
            query = {"category": service.category, "kind": "Elasticsearch", "description": service.name, "status": Service.OK}
        else:
            return None

        try:
            result = self.uptime.insert_one(query)
        except:
            raise

        if result is not None:
            # Store the ObjectId on the service itself for caching
            service.storage_add(self.storage_id_svc, result.inserted_id)
            return result.inserted_id
        
        raise Exception("Failed to create a new service")

    def query_exec_find_current_downtime(self, service, id_svc):
        """Query the DB to find the current downtime of a service

        Args:
            service (Service): Service object
            id_svc (ObjectId): _id of the service

        Returns:
            dict. The return code::
            
                dict -- The current downtime record for the service
                {} -- No current downtime

        Raises:
            Exception: MongoDB issue

        """
        try:
            result = self.uptime_history.find_one({"_id_uptime" : id_svc, "down_end_date" : 0})
        except:
            raise

        if result is not None:
            service.storage_add(self.storage_id_downtime, result["_id"])
        
        return result

    def query_exec_new_downtime(self, service, id_svc, extra):
        """Query the DB to create a new service downtime

        Update the status of the service and create a new downtime record.
        Cache the downtime _id on the service object

        Args:
            service (Service): Service object
            id_svc (ObjectId): _id of the service
            extra (object): extra data

        Returns:
            ObjectId. The return code::
            
                ObjectId -- The current downtime _id

        Raises:
            Exception: MongoDB issue

        """
        try:
            # update status to down
            self.uptime.update_one({"_id" : id_svc}, { "$set": { "status" : Service.FAIL} })

            # add downtime entry
            if extra is None:
                result = self.uptime_history.insert_one({"_id_uptime": id_svc, "down_start_date": time.time(), "down_end_date": 0})
            else:
                result = self.uptime_history.insert_one({"_id_uptime": id_svc, "down_start_date": time.time(), "down_end_date": 0, "extra": extra})
        except:
            raise

        if result is not None:
            # store the downtime _id for re-use as the downtime is open
            service.storage_add(self.storage_id_downtime, result.inserted_id)
            return result.inserted_id

        raise Exception("Failed to create a new downtime")

    def query_exec_end_downtime(self, service, id_svc, id_downtime):
        """Query the DB to close a service downtime

        Update the status of the service and close the downtime record.
        Remove the downtime _id cache on the service object

        Args:
            service (Service): Service object
            id_svc (ObjectId): _id of the service
            id_downtime (ObjectId): _id of the downtime to close

        Returns:
            None. The return code::
            
                None -- Specific usage to reset the id_downtime to None directly. see caller code.

        Raises:
            Exception: MongoDB issue

        """
        try:
            # update status to up
            self.uptime.update_one({"_id" : id_svc}, { "$set": { "status" : Service.OK } })
            
            # end downtime
            result = self.uptime_history.update_one({"_id" : id_downtime}, { "$set": { "down_end_date" : time.time() } })
        except:
            raise
        
        # remove the cached _id as the downtime is closed
        service.storage_remove(self.storage_id_downtime)
        
        # We closed it so there is no more ObjectId to store.
        return None

    def svc_all(self, service, status, extra):
        """see Storage class"""

        super().svc_all(service, status, extra)
        try:
            new = False # Used to know if this is a new service on the DB or not
            id_svc = service.storage_get(self.storage_id_svc)
            id_downtime = service.storage_get(self.storage_id_downtime)

            # Check if the id_svc is cached and if not load it
            if id_svc is None:
                # try to find it
                result_svc = self.query_exec_find_svc(service)
                
                if result_svc is None:
                    # create it
                    id_svc = self.query_exec_new_svc(service)
                    new = True
                else:
                    id_svc = result_svc["_id"]
            else:
                # We need to get the status for later
                result_svc = self.query_exec_find_svc_by_id(id_svc)

            # Specific case for a new service
            if new:
                if status != Service.OK:
                    # Start a new downtime
                    self.query_exec_new_downtime(service, id_svc, extra)

                # go away as we have nothing else todo for a new service
                return True

            # We try to get the last down time available on the history collection (without end date).
            #
            # There is a lot of case where this is not needed to do it but as NoSQL does not support transaction,
            # we will take the chance to get the status on the db and to fix it if needed with a small computing cost.
            # so the code will seems not optimized but in fact it will permit to recover and fix the uptime_history db
            # that we always update AFTER the uptime one on the fly.
            #  => that means that it is possible to lost the real down time start date or the real down time end date somewhere
            #     and to fix it with inaccurate date. (specially if Mongo was down for a while between an update of uptime and uptime_history)
            # TODO: We can have a local cache of the history in case of a backend issue to permit us to update the backend in the
            #       future...

            if id_downtime is None:
                # try to find it
                result = self.query_exec_find_current_downtime(service, id_svc)
                if result is not None:
                    id_downtime = result["_id"]

            if result_svc["status"] == status:
                # The status on the db is the same than the one reported.
                if status == Service.OK:
                    # So we shouldn't have a valid id_downtime because we are supposed to don't have any down time with end date to 0
                    if id_downtime is not None:
                        # something wrong happend on a previous update of the DB (NoSQL is not transactional for remember...)
                        # so we will stop the down time now ... of course this is inaccurate
                        id_downtime = self.query_exec_end_downtime(service, id_svc, id_downtime)
                else:
                    # so we should have a valid id_downtime because a downtime is in progress
                    if id_downtime is None:
                        # something went wrong on a previsous update of the DB (NoSQL is not transactional for remember...)
                        # so we will add a new downtime on the history right now ... of course this is inaccurate
                        id_downtime = self.query_exec_new_downtime(service, id_svc, extra)
                
                # Nothing else todo as everything is inline with Monitoring and Storage
                return True
            
            # Normal operation on a status change with support for inconsistent state
            
            if status != Service.OK:
                # so we need to create a new document on history because this is a new downtime
                if id_downtime is not None:
                    # Something wrong happened on a previous update of the DB... we lost a back online of the service...
                    pass
                else:
                    id_downtime = self.query_exec_new_downtime(service, id_svc, extra)
            else:
                # so we need to close the previous downtime
                if id_downtime is None:
                    # Something wrong happened on a previous update of the DB... we lost this downtime...
                    pass
                else:
                    id_downtime = self.query_exec_end_downtime(service, id_svc, id_downtime)
        except:
            return False
        else:
            return True

    #
    # STATS (SLA, Status, incidents ...)
    #

    def query_exec_find_all_downtimes(self, service, down_start_date, duration):
        """Query the DB to find all downtimes of a service in a range of time

        Args:
            service (Service, dict, ObjectId): Service, MongoDB Document of the service, ObjectId of the service
            down_start_date (int): epoch timestamp
            duration (int): number of seconds to check if we have downtimes since down_start_date

        Returns:
            List. The return code::
            
                [{},{},...] -- List of Documents that represent a downtime between down_start_date and down_start_date + duration
                [] -- No downtime

        Raises:
            Exception: MongoDB issue

        """
        
        # get all history where : id_uptime of svc and ( ( down_start_date >= start_date or down_end_date = 0 ) and down_start_date <= start_date + 7j)
        
        if type(service) is ObjectId:
            id_svc = service
        elif type(service) is dict:
            id_svc = service["_id"]
        else:
            id_svc = self.query_exec_find_svc(service)["_id"]
        
        down_end_date = down_start_date + duration

        try:
            return self.uptime_history.find({  
                "$and" : [ 
                    { "_id_uptime" : id_svc }, 
                    { "$and" : [
                        { "down_start_date" : { "$lt" : down_end_date} },
                        { "$or" : [ { "down_end_date" : { "$gt" : down_start_date } }, { "down_end_date" : 0 } ]}
                        ]} 
                    ]
                })
        except:
            raise

        return []

    # STATS

    def stats_get_all_svc(self, query={}):
        """Get all services
        
        Kwargs:
            query (dict): Filter to pass to MongoDB query

        Returns:
            List. The return code::
            
                [{},{},...] -- List of Documents that represent the content of the uptime collection
                [] -- No service
        
        """
        try:
            return self.uptime.find(query)
        except:
            raise
        
    def stats_get_svc(self, service):
        """see query_exec_find_svc"""
        return self.query_exec_find_svc(service)
        
    def stats_get_all_downtimes_svc(self, service, start_date, duration):
        """see query_exec_find_all_downtimes"""
        return self.query_exec_find_all_downtimes(service, start_date, duration)

    # Clean Up

    def __del__(self):
        if self.client is not None:
            try:
                self.uptime = None
                self.uptime_history = None
                self.db = None
                self.client.close
            except:
                pass
    

