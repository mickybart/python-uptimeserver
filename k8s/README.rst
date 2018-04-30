k8s resources
=============

Uptime Server Deployment
------------------------

.. code:: bash
    
    export NS="uptime"
    
    # create namespace
    kubectl create ns $NS
    
    # deployment
    kubectl -n $NS apply -f kubernetes-uptime-server-deployment.yaml
    
    # rbac role for IngressProvider or KubernetesService
    # you can setup a service account with those permission to have a dedicated service account for Uptime Server
    # this account can be set in a dedicated kube config (and used into kubeconfig.txt to create the docker image)
    kubectl apply -f kubernetes-rbac-uptime-server.yaml
    kubectl create serviceaccount uptime-server
    
    
    
