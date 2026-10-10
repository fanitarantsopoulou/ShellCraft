---
id: k8s.basics.services-namespaces
title: Services και Namespaces
level: beginner
objective: Να δίνεις σταθερή διεύθυνση σε Pods που αλλάζουν και να οργανώνεις τους πόρους σε namespaces.
est_minutes: 5
skills: [k8s.concepts]
commands: [kubectl-expose, kubectl-get]
citations:
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/services-networking/service/", section: "Service", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/", section: "Labels and Selectors", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/", section: "Namespaces", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
---
## Το πρόβλημα

Τα Pods έρχονται και φεύγουν, και κάθε νέο Pod παίρνει νέα IP. Πώς θα βρίσκει η μία εφαρμογή την
άλλη;

## Service

Ένα **Service** δίνει ένα **σταθερό όνομα και διεύθυνση** μπροστά από μια ομάδα Pods και μοιράζει
την κίνηση ανάμεσά τους. Ποια Pods είναι αυτά το λέει ο **selector**, με βάση τα labels τους:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

Το Service στέλνει την κίνηση σε όλα τα Pods με label `app: web`.

## Τύποι Service

| Τύπος | Από πού είναι προσβάσιμο |
|---|---|
| `ClusterIP` | μόνο μέσα από το cluster (η προεπιλογή) |
| `NodePort` | και απ' έξω, σε μια σταθερή θύρα κάθε node (`<IP node>:<NodePort>`) |
| `LoadBalancer` | απ' έξω, μέσω load balancer του παρόχου cloud |

Ο πιο γρήγορος τρόπος να φτιάξεις Service για ένα Deployment:

```bash
kubectl expose deployment web --port=80
```

## Namespaces

Τα **namespaces** χωρίζουν τους πόρους ενός cluster σε ομάδες, π.χ. ανά ομάδα ή περιβάλλον. Μέσα σε
ένα namespace τα ονόματα πρέπει να είναι μοναδικά, αλλά δύο namespaces μπορούν να έχουν πόρους με το
ίδιο όνομα. Κάθε cluster ξεκινά με μερικά έτοιμα:

| Namespace | Τι έχει |
|---|---|
| `default` | εκεί πάνε οι πόροι σου αν δεν πεις αλλιώς |
| `kube-system` | ό,τι φτιάχνει το ίδιο το Kubernetes |
| `kube-public` | πόροι που μπορούν να τους διαβάσουν όλοι |
| `kube-node-lease` | στοιχεία με τα οποία οι nodes δείχνουν ότι είναι ζωντανοί |

```bash
kubectl get pods -n kube-system
```
