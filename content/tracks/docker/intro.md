---
track: docker
title: Τι είναι το Docker
citations:
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-overview/", section: "Docker overview", doc_version: "Docker docs 2026", last_verified: 2026-10-07 }
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/", section: "What is a container?", doc_version: "Docker docs 2026", last_verified: 2026-10-07 }
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/", section: "What is an image?", doc_version: "Docker docs 2026", last_verified: 2026-10-07 }
  - { source: docker-docs, url: "https://docs.docker.com/engine/security/", section: "Docker Engine security", doc_version: "Docker docs 2026", last_verified: 2026-10-07 }
---
## Το πρόβλημα που λύνει

«Στο δικό μου μηχάνημα δουλεύει!» Μια εφαρμογή χρειάζεται συγκεκριμένη έκδοση γλώσσας, βιβλιοθήκες,
ρυθμίσεις. Ο server έχει άλλες εκδόσεις, ο συνάδελφος άλλες — και κάτι σπάει.

Το **Docker** πακετάρει την εφαρμογή **μαζί με όλα όσα χρειάζεται** σε ένα **image**. Το ίδιο image
τρέχει με τον ίδιο τρόπο στο laptop σου, στον server και στο cloud.

## Τι είναι

Σύμφωνα με την επίσημη τεκμηρίωση, το Docker είναι «μια ανοιχτή πλατφόρμα για την ανάπτυξη,
τη μεταφορά και την εκτέλεση εφαρμογών». Σου επιτρέπει να διαχωρίσεις την εφαρμογή από την
υποδομή, ώστε ο κώδικας να φτάνει πιο γρήγορα από τον υπολογιστή σου στην παραγωγή.

## Οι τρεις βασικές έννοιες

- **Image** — ένα πακέτο μόνο-για-ανάγνωση με την εφαρμογή και ό,τι χρειάζεται (σαν «καλούπι»).
- **Container** — μια απομονωμένη εκτέλεση ενός image. Από ένα image τρέχουν όσα containers θέλεις.
- **Registry** — εκεί αποθηκεύονται και διανέμονται τα images (π.χ. Docker Hub).

## Πώς δουλεύει — και γιατί χρειάζεσαι Linux

Το Docker είναι γραμμένο στη γλώσσα **Go** και βασίζεται σε λειτουργίες του **Linux kernel**:

- τα **namespaces** δίνουν σε κάθε container τον δικό του απομονωμένο «χώρο» (διεργασίες, δίκτυο, αρχεία),
- τα **cgroups** περιορίζουν πόση μνήμη και CPU μπορεί να πάρει.

Γι' αυτό ένα container **δεν** είναι εικονική μηχανή: δεν έχει δικό του kernel, μοιράζεται τον kernel του
host. Ξεκινά σε δευτερόλεπτα και είναι πολύ ελαφρύτερο. (Σε Mac και Windows, το Docker Desktop τρέχει
ένα μικρό Linux στο παρασκήνιο ακριβώς γι' αυτό τον λόγο.)

Η αρχιτεκτονική είναι client-server: η εντολή `docker` (client) μιλά με τον **Docker daemon**, που κάνει
τη βαριά δουλειά — χτίζει, τρέχει και διανέμει containers.

## Πού το βλέπεις στην πράξη

- Τοπικά, για να σηκώσεις μια βάση δεδομένων ή ολόκληρη εφαρμογή με μία εντολή.
  (Αυτή η πλατφόρμα τρέχει έτσι: proxy, API και βάση σε τρία containers.)
- Σε CI/CD, για να τρέχουν τα tests στο ίδιο περιβάλλον κάθε φορά.
- Σε servers και στο **Kubernetes**, που τρέχει containers σε μεγάλη κλίμακα — η επόμενη ενότητα.
