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

from uptimeserver.config import Config
from uptimeserver.providers import IngressProvider, IngressProviderConfig
from uptimeserver.services import *
import re

class CustomConfig(Config):
    def configure(self, server, monitoring):
        """configure the server and the monitoring
        
        We need to call super().configure() to finalize the configuration
        
        """
        
        # K8S Ingress
        #config = CustomIngressProviderConfig(self)
        #self.providers.append(IngressProvider("aws-k8s-ingress", self.secret["default_kubernetes_context"], monitoring, category="ns", ingress_config=config))
        #self.providers.append(IngressProvider("gce-k8s-ingress", self.secret["gce_kubernetes_context"], monitoring, category="ns", ingress_config=config))
        
        # Mongo
        #for mongo in self.secret["mongodb_clusters"]:
        #    self.services.append(MongoService(mongo["name"], mongo["uri"], category="infra"))
        
        # Kubernetes
        #for kubernetes in self.secret["kubernetes_clusters"]:
        #    self.services.append(KubernetesService(kubernetes["name"], kubernetes["context"], kubernetes["availability"], category="infra"))
            
        # Elasticsearch
        #for es in self.secret["elasticsearch_clusters"]:
        #    self.services.append(ElasticsearchService(es["name"], es["hosts"], es["auth"], port=es["port"], ssl=es["ssl"], category="infra"))
        
        super().configure(server, monitoring)
        
class CustomIngressProviderConfig(IngressProviderConfig):
    """ Custom Configuration for IngressProvider
    
    Constructor
    
    Args:
        config (Config): configuration
    """
    
    regex_global_ypcloud = re.compile(".*ypcloud.io.*")
    regex_sites_ypcloud = re.compile(".*(aws|gce).ypcloud.io.*")
    regex_kong_ypcloud = re.compile(".*ypapi.ypcloud.io.*")
    
    def __init__(self, config):
        self.config = config
    
    def exclude(self, url):
        if self.regex_sites_ypcloud.match(url) is not None or \
            self.regex_global_ypcloud.match(url) is None:
            return True
            
        return False
    
    def headers(self, url):
        if self.regex_kong_ypcloud.match(url) is not None:
            headers = {"apikey" : self.config.secret.get("KONG_HEALTH_APIKEY", "")}
        else:
            headers = {}
        
        return headers
