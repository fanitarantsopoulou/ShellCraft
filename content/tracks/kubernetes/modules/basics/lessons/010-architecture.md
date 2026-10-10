---
id: k8s.basics.architecture
title: Από τι αποτελείται ένα cluster
level: beginner
objective: Να ξέρεις τα βασικά κομμάτια ενός Kubernetes cluster και τι κάνει το καθένα.
est_minutes: 5
skills: [k8s.concepts]
citations:
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/overview/components/", section: "Kubernetes Components", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/overview/", section: "Kubernetes overview", doc_version: "Kubernetes v1.37", last_verified: 2026-10-10 }
---
## Η μεγάλη εικόνα

Ένα **cluster** Kubernetes έχει δύο μέρη:

- το **control plane**, τον «εγκέφαλο» που αποφασίζει τι πρέπει να τρέχει και πού,
- τους **nodes**, τις μηχανές όπου τρέχουν πραγματικά οι εφαρμογές σου.

## Το control plane

| Κομμάτι | Τι κάνει |
|---|---|
| `kube-apiserver` | η «πόρτα» του cluster: όλοι, και το `kubectl`, μιλάνε μαζί του |
| `etcd` | η βάση όπου κρατιούνται όλα τα δεδομένα του cluster |
| `kube-scheduler` | βρίσκει Pods που δεν έχουν ακόμα node και διαλέγει τον κατάλληλο |
| `kube-controller-manager` | τρέχει τους controllers, που φέρνουν το cluster στην κατάσταση που ζήτησες |
| `cloud-controller-manager` | συνδέεται με τον πάροχο cloud (προαιρετικό) |

## Οι nodes

Σε κάθε node τρέχουν:

| Κομμάτι | Τι κάνει |
|---|---|
| `kubelet` | φροντίζει να τρέχουν τα Pods του node και τα containers τους |
| `kube-proxy` | κρατά τους κανόνες δικτύου που χρειάζονται τα Services (προαιρετικό) |
| container runtime | το πρόγραμμα που τρέχει τα containers |

## Πώς συνεργάζονται

Γράφεις με το `kubectl` τι θέλεις να τρέχει. Το αίτημα φτάνει στο `kube-apiserver` και
αποθηκεύεται στο `etcd`. Ο scheduler διαλέγει node για κάθε νέο Pod, και το `kubelet` εκείνου του
node το ξεκινά. Οι controllers ελέγχουν συνεχώς ότι η πραγματική κατάσταση είναι αυτή που ζήτησες.
