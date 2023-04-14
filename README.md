# monitor-app-kubernetes 
**App Info**: This simple application allows you to upload the file and monitors those uploaded file.
A guide on deploying this simple server's file monitoring app which uses flask and postgres. 

---

## Directory guide
- **monitor-app**: Flask application with Dockerfile to build the Docker image. This app monitors the information of uploaded file from the dashboard and provides the information of uploaded file in the dashboard. 
- **flask-kube**: Kubernetes manifests file to create Flask deployment with services and configmap
- **postgres-kube**: Kubernetes manifests file to create Stateful postgres DB application with service, configmap, persistent volume, and persistent volume claim

---

## Prerequisite
- Docker 
- Kubernetes cluster 

For testing purpose you may use Docker Desktop in which Kubernetes is installed.

---

## Build Docker Image
1. First clone this repository and change the application directory.
2. Build docker image (`docker build -t ${tagname} .`)
3. Push image to your dockerhub account. (`docker push ${tagname}`)
   
Note the image tag name here. This image tag name will be used in Kubernetes manifest file for flask.  
cmdline instructions to build and push docker image:  

```
cd monitor-app
docker build -t sushanku/flask-monitor-app:latest .
docker push sushanku/flask-monitor-app:latest
```

---

## Deploy flask app in your Kubernetes cluster
This flask app is first built with Docker and pushed it to the public dockerhub registry. Then, Kubernetes will pull the docker image from the dockerhub and create a deployment pods.  
You can increase the replica in deployment manifest file but the app stores some data like uploaded files and profile picture. For now to make it simple, let's deploy pods with 1 replica only.  
This app also needs the environment variables like Database host, port, username, password etc which is handled by configMap resources. configMap allows you to decouple your hardcorded environment variable in the application code. For username, password or any critical information it is best to use Kuberenetes secret resource or Hashicorp vault.  
To expose the app locally, `loadbalancer` service type is used. This exposes your appilcation in `localhost:5000`. You may learn more about exposing your services using different ports and service type here. [Networking Service](https://kubernetes.io/docs/concepts/services-networking/service/)

**Note:** Do not forget to change the volume path in postgres-volume.yaml.  
Make sure the directory exists. Here is the reference  `path: "/Users/example/Desktop/kubedata"`

Lets create the flask config, service and deployment 
```
kubectl apply -f flask-kube
```
The above kubectl apply command will apply all the manifests file in flask-kube directory.

---

## Deploy postgres DB in your Kubernetes cluster
This postgress app uses a statefulset controller to deploy the stateful pods which have the persistent storage and a network.  
  
This app also needs the environment variables like Database username and password etc which is handled by configMap resources.Same username and password info should be given to the configMap of the flask. configMap allows you to decouple your hardcorded environment variable in the application code. For username, password or any critical information it is best to use Kuberenetes secret resource or Hashicorp vault.  
  
To expose the postgres DB within a cluster, postgres service manifest file is created. This will create a service accessible within a cluster by a DNS name `postgres`. This DNS name is then fed into the Flask deployment which needs to know the DB_HOST as a environment variable.  
  
A PersistentVolume (PV) is a piece of storage in your cluster that helps to persist your container database to your local storage.For that you need to have a persistent volume and persistent volume claim. You may also use different types of other storage. Learn more about pv and pvc  [persistent-volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
  
Lets create the postgres pv, pvc, config, service and deployment 
```
kubectl apply -f flask-postgres
```
The above kubectl apply command will apply all the manifests file in postgres-kube directory.

---

## Endpoints
- **sign up**: http://localhost:5000/register  
  Sign Up page
- **login**: http://localhost:5000/login  
  Login page
- **file list**: http://localhost:5000/file_list.html  
  Page from where you can upload the file. This same page will display the uploaded file information(name, filesize, filetype, action to delete the file)
- **dashboard**: http://localhost:5000/dashboard.html  
  Dashboard where uploaded file count will be displayed on the basis of daily, weekly, monthly.

---

## TO DO's
These are the few suggestions for the enhancement of this application
- You may use kuberenetes resource `secret` for your DB username and DB password both in flask and postgres or You may use Hashicorp vault.
- Make a helm charts of this application and deploy it using helm
- Decouple the CI and CD part, CI=> Integrate your code using some pipeline(Jenkins, github action, gitlab ci/cd). CD=> Deploy using GitOps Approach(ArgoCD)
