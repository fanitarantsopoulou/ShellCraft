---
id: docker.basics.images-containers
title: Images και containers
level: beginner
objective: Να ξεχωρίζεις το image από το container και να ξέρεις από πού έρχονται τα images.
est_minutes: 5
skills: [docker.concepts]
commands: [docker-image-pull, docker-image-ls, docker-container-ls]
citations:
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/", section: "Docker: What is an image?", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/", section: "Docker: What is a container?", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-overview/", section: "Docker overview", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
---
## Image: το πακέτο

Ένα **image** είναι ένα έτοιμο πακέτο με όλα όσα χρειάζεται μια εφαρμογή για να τρέξει: αρχεία,
προγράμματα, βιβλιοθήκες και ρυθμίσεις. Για παράδειγμα, το image `postgres` έχει μέσα τη βάση
δεδομένων PostgreSQL, και ένα image Python έχει την Python.

Δύο πράγματα αξίζει να θυμάσαι:

- **Δεν αλλάζει.** Όταν φτιαχτεί ένα image, δεν τροποποιείται. Αν θέλεις αλλαγή, φτιάχνεις νέο image.
- **Είναι φτιαγμένο από layers.** Κάθε layer είναι μια ομάδα αλλαγών σε αρχεία. Έτσι ένα image
  μπορεί να χτιστεί πάνω σε ένα άλλο, χωρίς να ξεκινάς από το μηδέν.

## Container: αυτό που τρέχει

Ένα **container** είναι μια απομονωμένη διεργασία που τρέχει από ένα image. Από το ίδιο image μπορείς
να τρέξεις όσα containers θέλεις. Κάθε container:

- έχει **ό,τι χρειάζεται** μέσα του, χωρίς να βασίζεται σε προγράμματα του υπολογιστή σου,
- είναι **απομονωμένο** από τα υπόλοιπα,
- μπορείς να το **σβήσεις** χωρίς να επηρεάσεις τα άλλα,
- τρέχει **ίδια** στο laptop σου, σε έναν server ή στο cloud.

## Container ή εικονική μηχανή;

Μια εικονική μηχανή (VM) κουβαλά ολόκληρο λειτουργικό σύστημα με δικό της kernel. Τα containers
**μοιράζονται τον kernel** του υπολογιστή όπου τρέχουν, γι' αυτό είναι πολύ πιο ελαφριά. Συχνά τα δύο
δουλεύουν μαζί: μια VM στο cloud τρέχει πολλά containers.

## Από πού έρχονται τα images

Τα images αποθηκεύονται σε ένα **registry**. Το πιο γνωστό είναι το **Docker Hub**. Το όνομα ενός
image μπορεί να έχει και **tag**, δηλαδή έκδοση ή παραλλαγή:

```bash
docker pull nginx:alpine
```

| Κομμάτι | Τι είναι |
|---|---|
| `nginx` | το όνομα του image |
| `alpine` | το tag (αν δεν το γράψεις, εννοείται `latest`) |

Για να δεις τα images που έχεις κατεβάσει και τα containers που τρέχουν:

```bash
docker images
docker ps
```
