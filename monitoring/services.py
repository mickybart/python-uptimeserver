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
Services module

Class that permit to create a Service check.
"""

# KubernetesService
from kubernetes import client, config

# IngressService
import requests

# MongoService
import pymongo

# ElasticsearchService
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

class Service:
    """Base class for Service implementation
    
    All derived Service of this class need to implement:
    
    def __str__(self)
    def __eq__(self, other)
    def checkMe(self)
    
    checkMe() is the main function that will permit to check the status of the service.
    
    A storage can add some specific information on the service object with the storage_* functions
    
    Constructor
    
    Args:
        category (string): category fo the service (eg: infra, ns, client1 ...)
    
    Keyword Arguments:
        attempt_before_status_fail (int): Number of attempt before we set a service status to FAIL
    
    """
    #disabled = False
    #status = None
    #previous_status = None
    #storage = dict()
    #category = None
    #failure_counter = 0
    #attempt_before_status_fail
    OK = 0
    FAIL = 1

    def __init__(self, category, attempt_before_status_fail=3):
        self.disabled = False
        self.status = None
        self.previous_status = None
        self.storage = dict()
        self.category = category
        self.failure_counter = 0
        self.attempt_before_status_fail = attempt_before_status_fail

    def storage_add(self, key, value):
        """add a value to storage
        
        Used by storage backend to add some extra information on the service itself to track it
        
        Args:
            key (String): a dictionary key
            value (Object): an object to store on the dictionary
        
        """
        self.storage[key] = value

    def storage_remove(self, key):
        """remove a value from storage
        
        Used by storage backend to remove a tracked value
        
        Args:
            key (String): a dictionary key
        
        """
        if self.storage.get(key) is not None:
            del self.storage[key]

    def storage_get(self, key, default=None):
        """get a value from storage
        
        Used by storage backend to read a tracked value
        
        Args:
            key (String): a dictionary key
            
        Keyword Arguments:
            default (None): default value to return if the key is not available
            
        Returns:
            Object: A storage object or default if it doesn't exist
        
        """
        if self.storage.get(key) is None:
            return default
        else:
            return self.storage[key]
            
    def checkMe(self, status, extra=None):
        """Check the service
        
        Args:
            status (int): Service.FAIL or Service.OK
            
        Keyword Arguments:
            extra (dict): Details about the service status reported
        
        Returns:
            int, int, dict: Previous status, status, extra
        """
        
        # failure counter
        if status == Service.FAIL:
            self.failure_counter = self.failure_counter + 1
        elif self.failure_counter != 0:
            self.failure_counter = 0

        # previous status
        self.previous_status = self.status
        
        # new status
        if status == Service.OK or self.isSoftFailure():
            self.status = Service.OK
        else:
            self.status = Service.FAIL

        return (self.previous_status, status, extra)
    
    def isSoftFailure(self):
        """Is soft failure ?
        
        We are in a failure state but we still have some attempts to do
        
        Returns:
            bool: Failure not equal or superior to the number of attempt (True), or False otherwise
        """
        return self.failure_counter > 0 and not self.isHardFailure()
    
    def isHardFailure(self):
        """Is hard failure ?
        
        Enforce the failure
        
        Returns:
            bool: Still in failure after all attempts (True) or False otherwise
        
        """
        return self.failure_counter >= self.attempt_before_status_fail
    
    def reset_status(self):
        """Reset the status to an undefined one"""
        self.status = None

class IngressService(Service):
    """Kubernetes Ingress Service
    
    This class permit to store ingress entry and will check if an URL is up or down.
    This is mainly an https check but with extra arguments like namespace and name fields of an ingress yaml
    
    Constructor
    
    Args:
        ns (string): namespace
        name (string): name
        url (string): url
    
    Keyword Arguments:
        category (string): category (eg: ns, infra, client1, ...)
        headers: headers for the url
    
    """
    #ns = None
    #name = None
    #url = None
    #headers
    timeout = 2

    def __init__(self, ns, name, url, timeout=None, category="ns", headers={}):
        super().__init__(category)
        self.ns = ns
        self.name = name
        self.url = url
        if timeout is not None:
            self.timeout = timeout
        self.headers = headers

    def __str__(self):
        return "ns=" + self.ns + ", name=" + self.name + ", url=" + self.url

    def __eq__(self, other):
        return type(other) is IngressService and self.ns == other.ns and self.name == other.name and self.url == other.url

    def checkMe(self):
        ret = Service.FAIL
        extra = None

        try:
            r = requests.get(self.url, allow_redirects=True, timeout=self.timeout, headers=self.headers)
            if r.status_code == 200:
                ret = Service.OK
            extra = { "status_code": r.status_code, "text": r.text }
            r.connection.close()
        except Exception as e:
            extra = {"exception" : str(e)}

        return super().checkMe(ret, extra)

class MongoService(Service):
    """MongoDB Service
    
    This permit to check the connectivity to MongoDB by getting server info.
    
    Constructor
    
    Args:
        name (string): Name
        uri (string): connection string
    
    Keyword Arguments:
        timeout (int): MongoDB connection timeout
        category (string): category (eg: ns, infra, client1, ...)
    
    """
    #name = None
    #uri = None
    timeout = 5000

    def __init__(self, name, uri, timeout=None, category="infra"):
        super().__init__(category)
        self.name = name
        self.uri = uri
        if timeout is not None:
            self.timeout = timeout * 1000

    def __str__(self):
        return "name=" + self.name

    def __eq__(self, other):
        return type(other) is MongoService and self.name == other.name and self.uri == other.uri

    def checkMe(self):
        ret = Service.FAIL
        extra = None

        try:
            mongo_client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=self.timeout)
            if mongo_client.server_info() is not None:
                ret = Service.OK
            mongo_client.close()
        except Exception as e:
            extra = {"exception" : str(e)}

        return super().checkMe(ret, extra)

class KubernetesService(Service):
    """Kubernetes Service
    
    Check the availability of masters and nodes
    
    Constructor
    
    Args:
        name (string): Name
        context (string): Context set on kube config
        availability (int): percentage of nodes that need to be up and running
        
    Keyword Arguments:
        category (string): category (eg: ns, infra, client1, ...)
    """
    
    #name
    #context
    #availability
    
    def __init__(self, name, context, availability, category="infra"):
        super().__init__(category)
        self.name = name
        self.context = context
        self.availability = availability
        
    def __str__(self):
        return "name=" + self.name + ", context=" + self.context
    
    def __eq__(self, other):
        return type(other) is KubernetesService and self.name == other.name and self.context == other.context and self.availability == other.availability
    
    def checkMe(self):
        ret = Service.FAIL
        extra = None
        
        try:
            k8s = client.CoreV1Api(api_client=config.new_client_from_config(context=self.context))
            list_nodes = k8s.list_node(watch=False)
            unknowns = 0
            nodes = 0
            for item in list_nodes.items:
                if 'Unknown' in [x.status for x in item.status.conditions]:
                    unknowns = unknowns + 1
                nodes = nodes + 1
            
            if nodes > 0 and (100 - ( unknowns * 100 / nodes )) >= self.availability:
                ret = Service.OK
            else:
                # FAIL so inform about the number of nodes availables or not
                extra = {"ready": nodes - unknowns, "unknown": unknowns}
        except Exception as e:
            extra = {"exception" : str(e)}
        
        return super().checkMe(ret, extra)
    
class ElasticsearchService(Service):
    """Elasticsearch service
    
    Elasticsearch Ping
    
    Constructor
    
    Args:
        name (string): Name
        hosts (list|string): uri or list of hosts
        auth (dict): Authentication
    
    Keyword Arguments:
        port (int): connection port
        category (string): category (eg: ns, infra, client1, ...)
    
    """
    #name
    #hosts
    #port
    #ssl
    #auth
    
    def __init__(self, name, hosts, auth, port=443, ssl=True, category="infra"):
        super().__init__(category)
        self.name = name
        self.hosts = hosts
        self.port = port
        self.ssl = ssl
        self.auth = auth
        
        # Auth and override parameters
        self.auth_aws = False
        self.auth_cert = False
        self.auth_http = False
        
        auth_type = auth["type"]
        if auth_type == "aws":
            self.auth_aws = True
            self.port = 443
            self.ssl = True
        elif auth_type == "cert":
            self.auth_cert = True
            self.port = 443
            self.ssl = True
        elif auth_type == "http":
            self.auth_http = True
    
    def __str__(self):
        return "name=" + self.name
    
    def __eq__(self, other):
        return type(other) is ElasticsearchService and self.name == other.name and self.host == other.host and self.auth == other.auth and self.port == other.port and self.ssl == other.ssl
    
    def checkMe(self):
        ret = Service.FAIL
        extra = None
        
        try:
            if self.auth_aws:
                awsauth = AWS4Auth(self.auth["access_key"], self.auth["secret_key"], self.auth["region"], 'es')
                es = Elasticsearch( \
                    hosts=[{'host': self.hosts, 'port': self.port}], \
                    http_auth=awsauth, \
                    use_ssl=self.ssl, \
                    verify_certs=self.ssl, \
                    connection_class=RequestsHttpConnection)
            elif self.auth_cert:
                es = Elasticsearch( \
                    hosts=self.hosts, \
                    http_auth=(self.auth["user"], self.auth["secret"]), \
                    port=self.port, \
                    use_ssl=self.ssl, \
                    ca_certs=self.auth["ca"],
                    client_cert=self.auth["cert"],
                    client_key=self.auth["key"])
            elif self.auth_http:
                es = Elasticsearch( \
                    hosts=self.hosts, \
                    http_auth=(self.auth["user"], self.auth["secret"]), \
                    port=self.port, \
                    use_ssl=self.ssl)
            else:
                raise Exception("auth is not supported")
            
            if es.ping():
                ret = Service.OK
            
        except Exception as e:
            extra = {"exception" : str(e)}
        
        return super().checkMe(ret, extra)
