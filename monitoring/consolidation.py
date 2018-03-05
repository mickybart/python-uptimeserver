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
Consolidation

The purpose is to compute stored raw data from monitoring to transform them.

"""

from datetime import datetime
from .helper import DaemonHelper
from .services import Service
import time
import threading

class Consolidation(threading.Thread):
    """Base class for Consolidation implementation
    
    Inherit class need to know and to work with the storage object.
    
    """
    
    #storage
    
    #stop_switch = False
    
    def __init__(self, storage):
        threading.Thread.__init__(self)
        
        self.storage = storage
        self.stop_switch = True
        
    def run(self):
        self.stop_switch = False
    
    def stopConsolidation(self):
        print("stopping consolidation ...")
        self.stop_switch = True

class ConsolidationSLA(Consolidation):
    """Base class for SLA Consolidation implementation
    
    self.date_* indicate the new consolidation starting point.
    that means that when we reach this new consolidation starting point, we can consolidate the previous period as
    we are starting a new one
    
    self.wip_date_* indicate the current start date to compute
    
    Inherit class need to implement:
    
    def hook_daily_sla(self, service, sla)
    def hook_weekly_sla(self, service, sla)
    def hook_monthly_sla(self, service, sla)
    def daily_sla_done(self)
    def weekly_sla_done(self)
    def monthly_sla_done(self)
    
    Those functions are used to store the sla or to notify that the daily/weekly/monthly compute is done
    
    """
    
    #date_daily_sla
    #wip_date_daily_sla

    #date_weekly_sla
    #wip_date_weekly_sla
    
    #date_monthly_sla
    #wip_date_monthly_sla
    
    def __init__(self, storage, waiting_seconds_between_batch=300):
        super().__init__(storage)
        
        self.waiting_seconds_between_batch = waiting_seconds_between_batch
        
        # Internal variables used to control the consolidation
        # date_* indicate the new consolidation starting point
        # that means that when we reach this new consolidation starting point, we can consolidate the previous period as
        # we are starting a new one
        
        now = datetime.today()
        week_num = self.storage.stats_week_number_of_date(now)
        
        today = datetime(now.year, now.month, now.day)
        monday_this_week = self.storage.stats_first_date_of_week_number(today.year, week_num)
        first_this_month = datetime(now.year, now.month, 1)
        
        self.date_daily_sla = self.next_date_daily_sla(today.timestamp())
        self.date_weekly_sla = self.next_date_weekly_sla(monday_this_week.timestamp())
        self.date_monthly_sla = self.next_date_monthly_sla(first_this_month.timestamp())
        
    # Date manipulaton for consolidation.
    # Month manipulation assume that the day is always set to 1 or at least < 29
    
    def next_date_daily_sla(self, timestamp):
        return timestamp + self.storage.stats_day_duration()
    
    def previous_date_daily_sla(self, timestamp):
        return timestamp - self.storage.stats_day_duration()
    
    def next_date_weekly_sla(self, timestamp):
        return timestamp + self.storage.stats_week_duration()
    
    def previous_date_weekly_sla(self, timestamp):
        return timestamp - self.storage.stats_week_duration()
    
    def next_date_monthly_sla(self, timestamp):
        return timestamp + self.storage.stats_month_duration(timestamp)
    
    def previous_date_monthly_sla(self, timestamp):
        return timestamp - self.storage.stats_month_duration(timestamp, end_date=True)
        
    def compute_daily_sla(self):
        """Compute the daily SLA"""
        
        # set the wip date
        self.wip_date_daily_sla = self.previous_date_daily_sla(self.date_daily_sla)
        
        print("consolidation: daily for %d [computing]" % (self.wip_date_daily_sla))
        
        try:
            # get all daily sla from Storage
            self.storage.stats_get_all_daily_sla(self.wip_date_daily_sla, self.hook_daily_sla)
            
            # done
            self.daily_sla_done()
        except:
            print("consolidation: daily for %d [FAILED]" % (self.wip_date_daily_sla))
        else:
            # success so we can set the next period
            self.date_daily_sla = self.next_date_daily_sla(self.date_daily_sla)
            print("consolidation: daily for %d [DONE]" % (self.wip_date_daily_sla))
        
    def compute_weekly_sla(self):
        """Compute the weekly SLA"""
        
        # set the wip date
        self.wip_date_weekly_sla = self.previous_date_weekly_sla(self.date_weekly_sla)
        
        print("consolidation: weekly for %d [computing]" % (self.wip_date_weekly_sla))
        
        try:
            # get all weekly sla from Storage
            self.storage.stats_get_all_weekly_sla(self.wip_date_weekly_sla, self.hook_weekly_sla)
            
            # done
            self.weekly_sla_done()
        except:
            print("consolidation: weekly for %d [FAILED]" % (self.wip_date_weekly_sla))
        else:
            # success so we can set the next period
            self.date_weekly_sla = self.next_date_weekly_sla(self.date_weekly_sla)
            print("consolidation: weekly for %d [DONE]" % (self.wip_date_weekly_sla))
    
    def compute_monthly_sla(self):
        """Compute the Monthly SLA"""
        
        # set the wip date
        self.wip_date_monthly_sla = self.previous_date_monthly_sla(self.date_monthly_sla)
        
        print("consolidation: monthly for %d [computing]" % (self.wip_date_monthly_sla))
        
        try:
            # get all monthly sla from Storage
            self.storage.stats_get_all_monthly_sla(self.wip_date_monthly_sla, self.hook_monthly_sla)
            
            # done
            self.monthly_sla_done()
        except:
            print("consolidation: monthly for %d [FAILED]" % (self.wip_date_monthly_sla))
        else:
            # success so we can set the next period
            self.date_monthly_sla = self.next_date_monthly_sla(self.date_monthly_sla)
            print("consolidation: monthly for %d [DONE]" % (self.wip_date_monthly_sla))
    
    def run(self):
        """Starting the thread"""
        
        print("starting consolidation ...")
        
        self.stop_switch = False
        
        while not self.stop_switch:
            start_batch = time.time()
            
            # General algorithm:
            #
            # date_* indicate the new consolidation starting point
            # that means that when we reach this new consolidation starting point, we can consolidate the previous period as
            # we are starting a new one.
            # If we are able to consolidate the previous period, we can update the date to the the next new consolidation starting point.
            
            # 1 Day compute
            
            if start_batch >= self.date_daily_sla:
                self.compute_daily_sla()
                
            # try to stop early if requested
            if self.stop_switch:
                break
            
            # 1 Week compute
            
            if start_batch >= self.date_weekly_sla:
                self.compute_weekly_sla()
                
            # try to stop early if requested
            if self.stop_switch:
                break
            
            # 1 Month compute
            
            if start_batch >= self.date_monthly_sla:
                self.compute_monthly_sla()
                
            # How many time do we need to wait ?
            
            end_batch = time.time()
            
            # Default waiting time to avoid overload and quick retry on a failing system
            sleep_time = self.waiting_seconds_between_batch
            
            # the next event is a day or a week or a month (depending errors reported)
            # this is not always the day that is the next event because the first day of the month, an issue can
            # occurs with the month or week treatment
            next_event = self.date_daily_sla
            if next_event > self.date_weekly_sla:
                next_event = self.date_weekly_sla
            if next_event > self.date_monthly_sla:
                next_event = self.date_monthly_sla
            
            # the next event is after the end of this batch
            if (end_batch < next_event):
                # duration to wait in seconds
                next_event_in = int(next_event - end_batch)
                if next_event_in > sleep_time:
                    sleep_time = next_event_in
                
            DaemonHelper().sleep_with_stop_switch(sleep_time, self)
    
        print("consolidation stopped")

class ConsolidationStatus(Consolidation):
    #down_time_duration
    #waiting_seconds_between_batch
    
    def __init__(self, storage, down_time_duration=600, waiting_seconds_between_batch=60):
        super().__init__(storage)
        
        self.down_time_duration = down_time_duration
        self.waiting_seconds_between_batch = waiting_seconds_between_batch
    
    def run(self):
        # update status
        
        print("starting consolidation status ...")
        
        self.stop_switch = False
        
        while not self.stop_switch:
            start_batch = time.time()
            
            self.compute_status()
            
            end_batch = time.time()
            
            if end_batch >= start_batch:
                sleep_time = int(self.waiting_seconds_between_batch - ( end_batch - start_batch ))
            else:
                # Something wrong happened !
                sleep_time = self.waiting_seconds_between_batch
            
            DaemonHelper().sleep_with_stop_switch(sleep_time, self)
        
        print("consolidation status stopped")

class MongoStorageConsolidationSLA(ConsolidationSLA):
    """ SLA Consolidation with MongoStorage Backend """
    
    def __init__(self, storage, waiting_seconds_between_batch=300):
        super().__init__(storage, waiting_seconds_between_batch)
        
        try:
            # Prepare collections. We are using the MongoStorage properties to get the db and connection.
            
            self.daily_uptime = self.storage.db.get_collection("daily_uptime")
            self.weekly_uptime = self.storage.db.get_collection("weekly_uptime")
            self.monthly_uptime = self.storage.db.get_collection("monthly_uptime")
            self.consolidation_state = self.storage.db.get_collection("consolidation_state")
            
            if len(self.daily_uptime.index_information()) == 0:
                # collection does not exist
                # create it and create indexes
                self.storage.db.create_collection("daily_uptime")
                self.daily_uptime.create_index( "_id_uptime" )
                self.daily_uptime.create_index( "date" )
                
            if len(self.weekly_uptime.index_information()) == 0:
                # collection does not exist
                # create it and create indexes
                self.storage.db.create_collection("weekly_uptime")
                self.weekly_uptime.create_index( "_id_uptime" )
                self.weekly_uptime.create_index( "date" )

            if len(self.monthly_uptime.index_information()) == 0:
                # collection does not exist
                # create it and create indexes
                self.storage.db.create_collection("monthly_uptime")
                self.monthly_uptime.create_index( "_id_uptime" )
                self.monthly_uptime.create_index( "date" )
            
            if len(self.consolidation_state.index_information()) == 0:
                # collection does not exist
                # create it and create indexes
                self.storage.db.create_collection("consolidation_state")
                
            # load consolidation_state
            result = self.consolidation_state.find_one({"state": "daily"})
            if result is not None:
                self.date_daily_sla = self.next_date_daily_sla(result["next"])
            
            result = self.consolidation_state.find_one({"state": "weekly"})
            if result is not None:
                self.date_weekly_sla = self.next_date_weekly_sla(result["next"])
            
            result = self.consolidation_state.find_one({"state": "monthly"})
            if result is not None:
                self.date_monthly_sla = self.next_date_monthly_sla(result["next"])
        except:
            raise
        
    def hook_daily_sla(self, service, sla):
        """Hook for daily SLA
        
        Insert on the DB the sla of the service
        
        Args:
            service (dict): service Document
            sla (float): 0.0-100.0 sla
        
        """
        
        # Add or update depending the status (that can be a recalculation, or restart after errors etc)
        result = self.daily_uptime.update_one({"_id_uptime": service["_id"], "date" : self.wip_date_daily_sla}, { "$set" : {"sla": sla}}, upsert=True)
        
    def daily_sla_done(self):
        """Daily compute is done"""
        
        # update the date in the db as done
        self.consolidation_state.update_one({"state": "daily"}, { "$set" : { "next": self.date_daily_sla }}, upsert=True)

    def hook_weekly_sla(self, service, sla):
        """Hook for weekly SLA
        
        Insert on the DB the sla of the service
        
        Args:
            service (dict): service Document
            sla (float): 0.0-100.0 sla
            
        """
        
        # Add or update depending the status (that can be a recalculation, or restart after errors etc)
        result = self.weekly_uptime.update_one({"_id_uptime": service["_id"], "date" : self.wip_date_weekly_sla}, { "$set" : {"sla": sla}}, upsert=True)
        
    def weekly_sla_done(self):
        """Weekly compute is done"""
        
        # update the date in the db as done
        self.consolidation_state.update_one({"state": "weekly"}, { "$set" : { "next": self.date_weekly_sla }}, upsert=True)

    def hook_monthly_sla(self, service, sla):
        """Hook for Montlhy SLA
        
        Insert on the DB the sla of the service
        
        Args:
            service (dict): service Document
            sla (float): 0.0-100.0 sla
            
        """
        
        # Add or update depending the status (that can be a recalculation, or restart after errors etc)
        result = self.monthly_uptime.update_one({"_id_uptime": service["_id"], "date" : self.wip_date_monthly_sla}, { "$set" : {"sla": sla}}, upsert=True)
        
    def monthly_sla_done(self):
        """Montlhy compute is done"""
        
        # update the date in the db as done
        self.consolidation_state.update_one({"state": "monthly"}, { "$set" : { "next": self.date_monthly_sla }}, upsert=True)


class MongoStorageConsolidationStatus(ConsolidationStatus):
    """ Status Consolidation with MongoStorage Backend """
    
    def __init__(self, storage, services_filter, down_time_duration=600, waiting_seconds_between_batch=60):
        super().__init__(storage, down_time_duration, waiting_seconds_between_batch)
        
        self.services_filter = services_filter
        
    def compute_status(self):
        """Compute status
        
        Update the status for some services to calculate which ones are down since more than "down_time_duration"
        
        """
        
        down_start_date = time.time() - self.down_time_duration
        
        try:
            for svc in self.storage.stats_get_all_svc(self.services_filter):
                resultat = self.storage.uptime_history.find_one({"_id_uptime" : svc["_id"], "down_end_date" : 0, "down_start_date" : { "$lte" : down_start_date }})
                
                if "status_public" in svc.keys():
                    status = svc["status_public"]
                else:
                    status = None
                
                if resultat is None:
                    # there is no downtime so status is OK
                    if status is None or status != Service.OK:
                        self.storage.uptime.update_one({"_id" : svc["_id"]}, { "$set" : {"status_public" : Service.OK} })
                else:
                    # there is a downtime so status is FAIL
                    if status is None or status == Service.OK:
                        self.storage.uptime.update_one({"_id" : svc["_id"]}, { "$set" : {"status_public" : Service.FAIL} })
        except:
            print("Issue to compute status")
