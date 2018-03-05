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
Daemon

Configure and start a Monitoring server
"""

from monitoring.server import Server
from monitoring.config import Config

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

secret = Config.load_json("secret.json")
config = Config(secret)

# OR
#
# Custom config ?
# => in example below, we will add few services to monitor and a specific configuration for Ingress provider.
#
# from monitoring.providers import IngressProvider, IngressProviderConfig
# from monitoring.services import *
# import re
# 
# class CustomConfig(Config):
#     def configure(self, server, monitoring):
#         # K8S Ingress
#         config = CustomIngressProviderConfig()
#         self.providers.append(IngressProvider("aws-k8s-ingress", self.secret["default_kubernetes_context"], monitoring, category="ns", ingress_config=config))
#         
#         # Mongo
#         for mongo in self.secret["mongodb_clusters"]:
#             self.services.append(MongoService(mongo["name"], mongo["uri"], category="infra"))
#         
#         # Kubernetes
#         for kubernetes in self.secret["kubernetes_clusters"]:
#             self.services.append(KubernetesService(kubernetes["name"], kubernetes["context"], kubernetes["availability"], category="infra"))
#             
#         # Elasticsearch
#         for es in self.secret["elasticsearch_clusters"]:
#             self.services.append(ElasticsearchService(es["name"], es["hosts"], es["auth"], port=es["port"], ssl=es["ssl"], category="infra"))
#         
#         super().configure(server, monitoring)
#         
# class CustomIngressProviderConfig(IngressProviderConfig):
#     """ Custom Configuration for IngressProvider """
#     
#     regex_global_ypcloud = re.compile(".*ypcloud.io.*")
#     regex_sites_ypcloud = re.compile(".*(aws|gce).ypcloud.io.*")
#     regex_kong_ypcloud = re.compile(".*ypapi.ypcloud.io.*")
#     
#     def exclude(self, url):
#         if self.regex_sites_ypcloud.match(url) is not None or \
#             self.regex_global_ypcloud.match(url) is None:
#             return True
#             
#         return False
#     
#     def headers(self, url):
#         if self.regex_kong_ypcloud.match(url) is not None:
#             headers = {"apikey" : self.secret.get("KONG_HEALTH_APIKEY", "")}
#         else:
#             headers = {}
#         
#         return headers
# 
# config = CustomConfig(secret)

# server
server = Server(config, donotconfig=False)

# Start Monitoring
server.startMonitoring()
