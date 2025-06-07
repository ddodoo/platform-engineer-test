### CREATE K3D CLUSTER
`k3d cluster create -c k3d-config.yaml`


### INSTALL ARGOCD

```
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd -n argocd --create-namespace 

kubectl port-forward service/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```


### RUN FASTAPI APPLICATION

```
Navigate to your project directory

cd platform-engineer-test
```
### INSTALL DEPENDENCIES

`poetry install`

### ACTIVATE VIRTUAL ENVIRONMENT

`poetry shell`

### RUN APPLICATION

```python -m my_service.main

OR

uvicorn my_service.main:app --host 0.0.0.0 --port 9000 --reload

```



### TEST HEALTH CHECK

`curl http://127.0.0.1:9000/healthcheck`




### TEST ARGOCD ENDPOINTS

```
curl http://127.0.0.1:9000/api/v1/argocd/application_status | jq .
curl http://127.0.0.1:9000/api/v1/argocd/list_projects | jq .
```


### UPDATE /ETC/HOSTS FILE

```
127.0.0.1 my-registry.local
172.18.0.2 my-service.local
172.18.0.2 nginx.local

```

### TEST KUBERNETES INGRESS

###  http://my-service.local/api/v1/argocd/application_status
```
curl http://my-service.local/api/v1/argocd/application_status | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   117  100   117    0     0    111      0  0:00:01  0:00:01 --:--:--   111
{
  "applications": [
    {
      "application_name": "my-service",
      "status": "Synced"
    },
    {
      "application_name": "nginx",
      "status": "Synced"
    }
  ]
}
```

### http://my-service.local/api/v1/argocd/list_projects
```
 curl http://my-service.local/api/v1/argocd/list_projects | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    62  100    62    0     0    704      0 --:--:-- --:--:-- --:--:--   756
{
  "projects": [
    {
      "project_name": "default",
      "namespace": "argocd"
    }
  ]
}
```

### MY-SERVICE CODE REPOSITORY UPDATES
- my_service/api/v1/routers/argocd_querier_router.py
- my_service/config/config.py
- my_service/dependencies.py
- my_service/models/models.py


### CREATE .ENV IN ROOT DIRECTORY AND SET ENVIRONMENT VARIABLES

### .env file
```
ARGOCD_SERVER=argocd-server.argocd.svc.cluster.local
ARGOCD_PORT=80
ARGOCD_USERNAME="<REDACTED>"
ARGOCD_PASSWORD="<REDACTED>"
TOKEN_CACHE_TTL=600
LOG_LEVEL=DEBUG
```

# UPDATED K3D CONFIG 

```
apiVersion: k3d.io/v1alpha4
kind: Simple
metadata:
  name: fido-exam
servers: 1
agents: 3
registries:
  create:
    name: my-registry
    host: my-registry.local
    hostPort: "5000"
  config: |
    mirrors:
      "my-registry.local:5000":
        endpoint:
          - http://my-registry:5000
ports:
  - port: 8080:80
    nodeFilters:
      - loadbalancer
  - port: 443:443
    nodeFilters:
      - loadbalancer

```