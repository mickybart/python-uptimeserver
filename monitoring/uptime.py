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

from .storage import MongoStorage
from .services import MongoService, IngressService
import sys
import time
from .config import Config

# This file is to provide an overview about the statistic API:
# - to calculate SLA
# - to show a service status
# - to custom time range to calculate SLA
# - to display incidents on a service
# - ...

if __name__ == "__main__":
    config = Config()
    
    storage = MongoStorage(config.getstorage("uri"), \
            config.getstorage("db"))
    
    if not storage.isReady():
        print("Storage is not ready !")
        sys.exit(1)
    
    # Services
    mongo = MongoService("Atlas ypcloud-io-dev", "mongodb://localhost:27017")
    ingress = IngressService("testurl", "testurl", "https://testurl.ypcloud.io")

    selected_svc = mongo

    print("++ Get ALL Status")
    storage.stats_get_all_status()

    ns="testurl"
    print("\n++ Get ALL status for ns : %s" % (ns))
    storage.stats_get_all_status_for_ns(ns)

    start_date = time.time() - 366*24*60*60
    print("\n++ Get ALL yearly sla")
    storage.stats_get_all_yearly_sla(start_date)
    
    start_date = time.time() - 366*24*60*60
    print("\n++ Get specific Service yearly sla")
    storage.stats_get_svc_yearly_sla(selected_svc, start_date)
    
    start_date = time.time() - 30.5*24*60*60
    print("\n++ Get ALL monthly sla")
    storage.stats_get_all_monthly_sla(start_date)
    
    start_date = time.time() - 30.5*24*60*60
    print("\n++ Get specific Service monthly sla")
    storage.stats_get_svc_monthly_sla(selected_svc, start_date)

    start_date = time.time() - 7*24*60*60
    print("\n++ Get ALL weekly sla")
    storage.stats_get_all_weekly_sla(start_date)

    start_date = time.time() - 7*24*60*60
    print("\n++ Get specific Service weekly sla")
    storage.stats_get_svc_weekly_sla(selected_svc, start_date)

    duration = 1*24*60*60
    start_date = time.time() - duration
    print("\n++ Get ALL sla during a custom duration (eg: 1 day, but can be 1 sec to multiple years)")
    storage.stats_get_all_sla(start_date, duration)

    duration = 1*24*60*60
    start_date = time.time() - duration
    print("\n++ Get specific Service sla during a custom duration (eg: 1 day, but can be 1 sec to multiple years)")
    sla = storage.stats_get_svc_sla(selected_svc, start_date, duration)
    print("%s [SLA: %.2f %%]" % (str(selected_svc), sla))

    duration = 1*24*60*60
    start_date = time.time() - duration
    print("\n++ Get ALL downtime during a custom duration (eg: previous 1 day)")
    storage.stats_get_all_downtimes(start_date, duration)

    duration = 1*24*60*60
    start_date = time.time() - duration
    print("\n++ Get specific Service downtime during a custom duration (eg: previous 1 day)")
    storage.stats_get_svc_downtimes(selected_svc, start_date, duration)
