# monitor-app-kubernetes

**App Info**: This simple application allows you to upload files and monitor them.
A guide on deploying this Flask + Postgres file monitoring app on Kubernetes — now enhanced with **Kata Containers** and **gVisor** for stronger workload isolation.

---

## Directory guide

* **monitor-app**: Flask application with Dockerfile to build the Docker image
* **flask-kube**: Kubernetes manifests for Flask deployment, service, and configmap
* **postgres-kube**: Kubernetes manifests for PostgreSQL StatefulSet, service, PV, PVC, configmap

---

## Prerequisite

* Docker
* Kubernetes cluster

For testing, you may use Docker Desktop with Kubernetes enabled.

---

## Build Docker Image

```
cd monitor-app
docker build -t sushanku/flask-monitor-app:latest .
docker push sushanku/flask-monitor-app:latest
```

---

# 🚀 Deploy Flask App

```
kubectl apply -f flask-kube
```

This will:

* Create Deployment
* Create Service (`LoadBalancer`)
* Inject environment variables via ConfigMap

---

# 🐘 Deploy PostgreSQL

```
kubectl apply -f postgres-kube
```

This will:

* Create StatefulSet
* Create PV & PVC
* Create internal Service (`postgres`)

---

# 🔐 Advanced Runtime Isolation (Kata Containers & gVisor)

This project supports **two advanced container runtimes**:

| Runtime             | Isolation Type            | Use Case                                  |
| ------------------- | ------------------------- | ----------------------------------------- |
| **Kata Containers** | Lightweight VM (QEMU)     | Strong isolation (multi-tenant workloads) |
| **gVisor**          | User-space kernel (runsc) | Balanced security + performance           |

---

# 🧊 Kata Containers Setup

Kata Containers run each pod inside a **microVM**.

### Runtime Configuration (containerd)

Ensure containerd is configured:

```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.kata-qemu]
  runtime_type = "io.containerd.kata-qemu.v2"
```

---

### Example Deployment Config (Kata)

```yaml
runtimeClassName: kata-qemu
nodeSelector:
  kata: "true"
tolerations:
- key: "kata"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
```

---

# 🟣 gVisor Setup

⚠️ **Important:** gVisor must be installed on **every worker node** where it will run.

---

## Step 1: Install runsc (gVisor runtime)

Install `runsc` binary on each node.

---

## Step 2: Configure containerd

Edit:

```
/etc/containerd/config.toml
```

Add:

```toml
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.gvisor]
  runtime_type = "io.containerd.runsc.v1"
```

Restart containerd:

```
sudo systemctl restart containerd
```

---

## Step 3: Create RuntimeClass

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: gvisor
```

---

## Example Deployment Config (gVisor)

```yaml
runtimeClassName: gvisor
nodeSelector:
  gvisor: "true"
tolerations:
- key: "gvisor"
  operator: "Equal"
  value: "true"
  effect: "NoSchedule"
```

---

# ⚠️ Node Isolation Best Practice (VERY IMPORTANT)

When using **multiple runtimes (Kata + gVisor)**:

👉 **DO NOT schedule them on the same nodes without control**

---

## ✅ Recommended Approach

### Label nodes:

```bash
kubectl label node <node-name> kata=true
kubectl label node <node-name> gvisor=true
```

---

### Taint nodes:

```bash
kubectl taint nodes <kata-node> kata=true:NoSchedule
kubectl taint nodes <gvisor-node> gvisor=true:NoSchedule
```

---

## 🧠 Why this matters

* Prevents runtime conflicts
* Ensures predictable scheduling
* Avoids debugging nightmares
* Enforces workload isolation boundaries

---

## 🎯 Final Scheduling Model

| Node Type     | Runtime         | Workloads                  |
| ------------- | --------------- | -------------------------- |
| kata nodes    | Kata Containers | High-security workloads    |
| gvisor nodes  | gVisor          | Medium-security workloads  |
| default nodes | runc            | Trusted/internal workloads |

---

# 🔍 Verifying Runtime

### Check runtime:

```bash
sudo crictl inspect <container-id> | grep runtimeType
```

---

### Check VM (Kata):

```bash
ps aux | grep qemu
```

---

### Check kernel (important test):

```bash
kubectl exec -it <pod> -- uname -a
```

* Kata → different kernel (VM)
* gVisor → same kernel but sandboxed
* runc → host kernel

---

# 🌐 Endpoints

* [http://localhost:5000/register](http://localhost:5000/register)
* [http://localhost:5000/login](http://localhost:5000/login)
* [http://localhost:5000/file_list.html](http://localhost:5000/file_list.html)
* [http://localhost:5000/dashboard.html](http://localhost:5000/dashboard.html)

---

# 🧠 Summary

You now have a **multi-runtime Kubernetes cluster**:

* ✅ runc (default containers)
* 🟣 gVisor (user-space isolation)
* 🧊 Kata Containers (VM-level isolation)
