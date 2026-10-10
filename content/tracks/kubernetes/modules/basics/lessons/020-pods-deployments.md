---
id: k8s.basics.pods-deployments
title: Pods και Deployments
level: beginner
objective: Να καταλαβαίνεις τι είναι ένα Pod και γιατί τα τρέχουμε σχεδόν πάντα μέσω Deployment.
est_minutes: 5
skills: [k8s.concepts]
commands: [kubectl-create-deployment, kubectl-get]
citations:
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/workloads/pods/", section: "Pods", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/", section: "Deployments", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
---
## Pod

Το **Pod** είναι η μικρότερη μονάδα που δημιουργείς και διαχειρίζεσαι στο Kubernetes. Είναι μια
ομάδα από **ένα ή περισσότερα containers** που μοιράζονται δίκτυο και αποθηκευτικό χώρο, και τρέχουν
πάντα μαζί, στον ίδιο node. Τις περισσότερες φορές ένα Pod έχει ένα μόνο container.

## Γιατί όχι σκέτα Pods

Ένα Pod που φτιάχνεις μόνο του, αν χαθεί (π.χ. χαλάσει ο node του), δεν ξαναδημιουργείται.
Γι' αυτό σχεδόν πάντα χρησιμοποιούμε **Deployment**.

## Deployment

Σε ένα Deployment περιγράφεις την **κατάσταση που θέλεις**, π.χ. «3 αντίγραφα του web με αυτό το
image», και το Kubernetes φέρνει την πραγματική κατάσταση εκεί, βήμα βήμα.

Πίσω από το Deployment υπάρχει ένα **ReplicaSet**, που φροντίζει να τρέχει πάντα ο σωστός αριθμός
Pods. Αν σβηστεί ένα, φτιάχνει αμέσως νέο.

```bash
kubectl create deployment web --image=nginx --replicas=3
kubectl get deployments
```

## Αναβαθμίσεις χωρίς διακοπή

Όταν αλλάζεις έκδοση image, το Deployment κάνει **rolling update**: φτιάχνει νέο ReplicaSet,
ανεβάζει σιγά σιγά τα νέα Pods και κατεβάζει τα παλιά. Έτσι η εφαρμογή συνεχίζει να απαντά όσο
γίνεται η αναβάθμιση.

## Το Deployment σε YAML

Συνήθως το Deployment γράφεται σε αρχείο. Αυτό είναι το YAML που παράγει το `kubectl` για ένα
Deployment με 2 αντίγραφα:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: demo
  name: demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
      - image: nginx:alpine
        name: nginx
```

Το `selector` λέει ποια Pods ανήκουν στο Deployment: όσα έχουν το label `app: demo`.
