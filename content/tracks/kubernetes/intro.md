---
track: kubernetes
title: Τι είναι το Kubernetes
citations:
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/overview/", section: "Kubernetes overview", doc_version: "Kubernetes v1.37", last_verified: 2026-10-07 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/windows/intro/", section: "Windows containers in Kubernetes", doc_version: "Kubernetes v1.37", last_verified: 2026-10-07 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/workloads/pods/", section: "Pods", doc_version: "Kubernetes v1.37", last_verified: 2026-10-07 }
---
## Το πρόβλημα που λύνει

Με το Docker τρέχεις εύκολα **ένα** container. Τι γίνεται όμως όταν έχεις εκατοντάδες containers
σε δεκάδες servers;

- Ποιος αποφασίζει σε ποιον server θα τρέξει το καθένα;
- Τι γίνεται όταν ένας server πέσει στις 3 το πρωί;
- Πώς βγάζεις νέα έκδοση χωρίς να σταματήσει η υπηρεσία;
- Πώς μοιράζεις την κίνηση στα αντίγραφα της εφαρμογής;

Αυτό κάνει το **Kubernetes**: συντονίζει και διαχειρίζεται containers (orchestration) σε ένα **cluster** από μηχανές.

## Τι είναι

Σύμφωνα με την επίσημη τεκμηρίωση, το Kubernetes είναι μια πλατφόρμα ανοιχτού κώδικα που τρέχει παντού
και επεκτείνεται εύκολα, φτιαγμένη για να διαχειρίζεται εφαρμογές σε containers. Γράφεις σε αρχεία
**τι θέλεις να τρέχει** (declarative configuration) και το Kubernetes κάνει **αυτόματα** τα υπόλοιπα.

## Ένα ελληνικό όνομα

Το όνομα **Kubernetes** προέρχεται από τα ελληνικά και σημαίνει **κυβερνήτης** ή **πιλότος**: αυτός που
κρατά το τιμόνι του πλοίου. Το συχνό **K8s** βγαίνει μετρώντας τα 8 γράμματα ανάμεσα στο «K» και στο «s».

## Από πού ήρθε

Η **Google** έκανε το Kubernetes ανοιχτού κώδικα το **2014**, συνδυάζοντας πάνω από **15 χρόνια εμπειρίας**
από την εκτέλεση φορτίων παραγωγής σε μεγάλη κλίμακα με ιδέες και πρακτικές της κοινότητας.

## Η βασική ιδέα: επιθυμητή κατάσταση

Δεν λες στο Kubernetes «ξεκίνα αυτό το container». Του λες **πώς θέλεις να είναι** ο κόσμος: 
«θέλω 3 αντίγραφα του web, με αυτό το image», και αυτό φροντίζει συνεχώς να τον κρατά έτσι.
Αν χαθεί ένα Pod, δημιουργεί νέο. Αν αλλάξεις έκδοση, αντικαθιστά τα Pods σταδιακά.

## Τι σου δίνει

- **Service discovery και load balancing**: σταθερές διευθύνσεις και κατανομή κίνησης.
- **Self-healing**: επανεκκινεί containers που αποτυγχάνουν και αντικαθιστά όσα χάνονται.
- **Αυτόματα rollouts και rollbacks**: σταδιακές αναβαθμίσεις και επιστροφή αν κάτι πάει στραβά.
- **Scaling**: περισσότερα ή λιγότερα αντίγραφα της εφαρμογής, με μία εντολή ή αυτόματα.
- **Διαχείριση secrets και ρυθμίσεων**: χωρίς να ξαναχτίζεις images.

## Ο ρόλος του Linux

Τα μηχανήματα που εκτελούν τα Pods (worker nodes) μπορεί να είναι Linux ή Windows, αλλά το
**control plane** (ο «εγκέφαλος» του cluster) τρέχει **μόνο σε Linux**. Τα περισσότερα containers
που θα συναντήσεις είναι επίσης Linux containers.

## Οι λέξεις που θα ακούς

- **Cluster**: όλο το σύνολο (control plane και nodes).
- **Node**: μια μηχανή όπου τρέχουν Pods.
- **Pod**: η μικρότερη μονάδα, ένα ή περισσότερα containers μαζί.
- **Deployment**: κρατά τον επιθυμητό αριθμό Pods και κάνει αναβαθμίσεις.
- **Service**: σταθερή διεύθυνση μπροστά από Pods που αλλάζουν.
- **`kubectl`**: το εργαλείο γραμμής εντολών για να μιλάς με το cluster.
