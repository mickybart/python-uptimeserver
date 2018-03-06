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
Configure and start a Monitoring server
"""

from uptimeserver.server import Server
from config import CustomConfig

# secret.json file example :
# 
# {
#     "env" : {
#         "prod" : {
#             "storage" : {
#                 "backend" : "MongoStorage",
#                 "uri": "mongodb://<backend>",
#                 "db": "<backend database name>"
#                 },
#             
#             "server" : {
#                 "with_consolidation" : true
#                 },
#             
#             "consolidations" : {
#                 "sla" : {},
#                 "status" : {
#                     "filter": {"category" : "infra"},
#                     "down_since": 600
#                     }
#                 },
#             
#             "monitoring": {
#                 "max_services": 15,
#                 "check_every_seconds": 60,
#                 "fast_retry_every_seconds" : 5
#                 }
#             }
#         },
#         
#     "mongodb_clusters" : [
#         {
#             "name" : "MongoDB Dev",
#             "uri": "mongodb://<dev>"
#         },
#         {
#             "name" : "MongoDB Prod",
#             "uri": "mongodb://<prod>"
#         }
#         ],
#     
#     "kubernetes_clusters" : [
#         {
#             "name": "Kubernetes AWS",
#             "context": "uptime-server-aws-ctx",
#             "availability" : 80
#         },
#         {
#             "name": "Kubernetes GCE",
#             "context": "uptime-server-gce-ctx",
#             "availability" : 80
#         }
#         ],
#     
#     "default_kubernetes_context" : "uptime-server-aws-ctx",
# 
#     "elasticsearch_clusters" : [
#         {
#             "name": "Elasticsearch AWS",
#             "hosts": "<url>.us-east-1.es.amazonaws.com",
#             "ssl": true,
#             "port": 443,
#             "auth": {
#                         "type": "aws",
#                         "access_key": "...",
#                         "secret_key": "...",
#                         "region": "us-east-1"
#                     }
#         },
#         {
#             "name": "Elasticsearch (http anonymous)",
#             "hosts": ["192.168.0.1", "192.168.0.2", "192.168.0.3"],
#             "ssl": false,
#             "port": 9200,
#             "auth": {
#                         "type": "http",
#                         "user": "",
#                         "secret": ""
#                     }
#         }
#         ],
#     
#     "KONG_HEALTH_APIKEY" : "API key"
# }
# 

secret = CustomConfig.load_json("secret.json")
config = CustomConfig(secret)

# Start Monitoring
Server(config).startMonitoring()
