Uptime Server
=============

Monitoring / Uptime / SLA solution for cloud services

`Code documentation (sphinx) <https://mickybart.github.io/python-uptimeserver/>`__

Docker
------

The docker folder provides everything to create an image that will run the uptime server.

uptimeserver module
-------------------

Installation
^^^^^^^^^^^^

This package is available for Python 3.5+.

Install the development version from github:

.. code:: bash

    pip3 install git+https://github.com/mickybart/python-uptimeserver.git

Prerequisite
^^^^^^^^^^^^

Examples in this README are using the secret.json file to inject some configuration.
Of course you can use any other solution provided by your infrastructure.

.. code:: python
    
    # Secrets structure
    #
    secrets = {
        "env" : {
            "prod" : {
                "storage" : {
                    "backend" : "MongoStorage",
                    "uri": "mongodb://<backend>",
                    "db": "<backend database name>"
                    },
                
                "server" : {
                    "with_consolidation" : true
                    },
                
                "consolidations" : {
                    "sla" : {},
                    "status" : {
                        "filter": {"category" : "infra"},
                        "down_since": 600
                        }
                    },
                
                "monitoring": {
                    "max_services": 15,
                    "check_every_seconds": 60,
                    "fast_retry_every_seconds" : 5
                    }
                }
            },
            
        "mongodb_clusters" : [
            {
                "name" : "MongoDB Dev",
                "uri": "mongodb://<dev>"
            },
            {
                "name" : "MongoDB Prod",
                "uri": "mongodb://<prod>"
            }
            ],
        
        "kubernetes_clusters" : [
            {
                "name": "Kubernetes AWS",
                "context": "uptime-server-aws-ctx",
                "availability" : 80
            },
            {
                "name": "Kubernetes GCE",
                "context": "uptime-server-gce-ctx",
                "availability" : 80
            }
            ],
        
        "default_kubernetes_context" : "uptime-server-aws-ctx",
    
        "elasticsearch_clusters" : [
            {
                "name": "Elasticsearch AWS",
                "hosts": "<url>.us-east-1.es.amazonaws.com",
                "ssl": true,
                "port": 443,
                "auth": {
                            "type": "aws",
                            "access_key": "...",
                            "secret_key": "...",
                            "region": "us-east-1"
                        }
            },
            {
                "name": "Elasticsearch (http anonymous)",
                "hosts": ["192.168.0.1", "192.168.0.2", "192.168.0.3"],
                "ssl": false,
                "port": 9200,
                "auth": {
                            "type": "http",
                            "user": "",
                            "secret": ""
                        }
            }
            ],
        
        "KONG_HEALTH_APIKEY" : "API key"
    }

Quick start
^^^^^^^^^^^

.. code:: python

    from uptimeserver.server import Server
    from uptimeserver.config import Config
    
    secret = Config.load_json("secret.json")
    
    config = Config(secret)
    
    Server(config).startMonitoring()

Custom Config
^^^^^^^^^^^^^

The class Config is the main way to customize the Uptime Server. The important function is configure.

Please read the Code documentation for more details.

.. code:: python

    from uptimeserver.server import Server
    from uptimeserver.config import Config
    
    secret = Config.load_json("secret.json")
    
    # Custom config
    
    from uptimeserver.providers import IngressProvider, IngressProviderConfig
    from uptimeserver.services import *
    import re
    
    class CustomConfig(Config):
        def configure(self, server, monitoring):
            # K8S Ingress
            config = CustomIngressProviderConfig()
            self.providers.append(IngressProvider("aws-k8s-ingress", self.secret["default_kubernetes_context"], monitoring, category="ns", ingress_config=config))
            
            # Mongo
            for mongo in self.secret["mongodb_clusters"]:
                self.services.append(MongoService(mongo["name"], mongo["uri"], category="infra"))
            
            # Kubernetes / Elasticsearch ...
            # see complete example on the docker folder
            
            super().configure(server, monitoring)
            
    class CustomIngressProviderConfig(IngressProviderConfig):
        """ Custom Configuration for IngressProvider """
        
        regex_global_ypcloud = re.compile(".*ypcloud.io.*")
        regex_sites_ypcloud = re.compile(".*(aws|gce).ypcloud.io.*")
        regex_kong_ypcloud = re.compile(".*ypapi.ypcloud.io.*")
        
        def exclude(self, url):
            if self.regex_sites_ypcloud.match(url) is not None or \
                self.regex_global_ypcloud.match(url) is None:
                return True
                
            return False
        
        def headers(self, url):
            if self.regex_kong_ypcloud.match(url) is not None:
                return {"apikey" : self.secret.get("KONG_HEALTH_APIKEY", "")}
    
            return {}
    
    config = CustomConfig(secret)
    
    Server(config).startMonitoring()

Storage backend
^^^^^^^^^^^^^^^

For now we only support Mongo Storage backend but new ones can be added.

Providers
^^^^^^^^^

You can dynamically add some services to the monitoring with the use of providers.

Provides:

- Ingress Provider : Get all URLs from kubernetes / ingress

We can imagine few other providers in the future like :

- File based provider : Services defined in a file
- unix socket provider : Services set by using unix socket for external programs
- DB provider : Services defined in a Database

Services
^^^^^^^^

A service check permit to check the status of a service. We only support FAIL and OK status with soft and hard failure (multiple attempt / retry to set a service as down).

Provides:

- IngressService : check URL from a kubernetes ingress object
- MongoService : check MongoDB connection
- KubernetesService : check kubernetes availability
- ElasticsearchService : check Elastic Search

Consolidation
-------------

Consolidation permit to transform data collected by uptime server.

We are mainly using it to create static daily/weekly/monthly SLA and to provide a public status for some services.

Consolidation is running automatically but you can control it with the Server or Config directly.

trigger manual consolidation for SLA
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This example will compute monthly sla.

.. code:: python
    
    from uptimeserver.storage import MongoStorage
    from uptimeserver.consolidation import MongoStorageConsolidationSLA
    from uptimeserver.config import Config
    from datetime import datetime
    
    config = Config()
    
    storage = MongoStorage(config.getstorage("uri"),
                config.getstorage("db"))
    storage.isReady()
    
    c = MongoStorageConsolidationSLA(storage)
    
    c.date_monthly_sla = datetime(2017,10,1).timestamp()
    c.compute_monthly_sla()

trigger manual consolidation for status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python
    
    from uptimeserver.storage import MongoStorage
    from uptimeserver.consolidation import MongoStorageConsolidationStatus
    from uptimeserver.config import Config
    
    config = Config()
    
    storage = MongoStorage(config.getstorage("uri"),
                config.getstorage("db"))
    
    c = MongoStorageConsolidationStatus(storage, {"category" : "infra"})
    c.compute_status()

Internal Notes
--------------

`Code documentation (sphinx) <https://mickybart.github.io/python-uptimeserver/>`__

Bugs or Issues
--------------

Please report bugs, issues or feature requests to `Github
Issues <https://github.com/mickybart/python-uptimeserver/issues>`__
