---
id: k8s.basics.kubectl
title: "kubectl: τα βασικά"
level: beginner
objective: Να χρησιμοποιείς τις βασικές εντολές του kubectl για να βλέπεις, να αλλάζεις και να ελέγχεις εφαρμογές.
est_minutes: 5
skills: [k8s.kubectl]
commands: [kubectl-get, kubectl-describe, kubectl-logs, kubectl-apply, kubectl-delete, kubectl-scale]
citations:
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/reference/kubectl/quick-reference/", section: "kubectl Quick Reference", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/reference/kubectl/generated/kubectl_apply/", section: "kubectl apply", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/", section: "Debug Pods", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
---
## Τι είναι το kubectl

Το **kubectl** είναι το εργαλείο γραμμής εντολών με το οποίο μιλάς στο cluster. Κάθε εντολή του
πηγαίνει στο `kube-apiserver`.

## Βλέπω τι υπάρχει

```bash
kubectl get pods                # τα Pods του τρέχοντος namespace
kubectl get pods -A             # τα Pods όλων των namespaces
kubectl get pods -o wide        # με IP και node για το καθένα
kubectl get deployments,services
```

Τα ονόματα των πόρων έχουν και σύντομη μορφή, π.χ. `po` για Pods, `deploy` για Deployments και
`svc` για Services.

## Ψάχνω τι πάει στραβά

```bash
kubectl describe pod web-7d4b9  # λεπτομέρειες και Events
kubectl logs web-7d4b9          # η έξοδος της εφαρμογής
kubectl logs web-7d4b9 --previous
```

Όταν ένα Pod δεν ξεκινά, κοιτάς πρώτα τα **Events** στο τέλος του `describe`. Όταν ξεκινά αλλά
κρασάρει, κοιτάς τα `logs`. Με το `--previous` βλέπεις τι έγραψε πριν πέσει την προηγούμενη φορά.

## Αλλάζω πράγματα

```bash
kubectl apply -f deployment.yaml          # δημιουργεί ή ενημερώνει από αρχείο
kubectl scale deployment web --replicas=5 # αλλάζει πόσα Pods τρέχουν
kubectl delete deployment web             # σβήνει το Deployment και τα Pods του
```

Το `apply` είναι ο συνηθισμένος τρόπος: κρατάς τα YAML σου σε αρχεία (και σε git), και κάθε φορά
που τα αλλάζεις, το `apply` φέρνει το cluster στην κατάσταση των αρχείων.
