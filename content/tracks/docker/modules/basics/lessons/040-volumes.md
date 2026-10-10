---
id: docker.basics.volumes
title: "Δεδομένα που μένουν: volumes"
level: intermediate
objective: Να κρατάς τα δεδομένα ενός container ακόμα και όταν το container διαγραφεί.
est_minutes: 4
skills: [docker.containers]
commands: [docker-container-run]
citations:
  - { source: docker-docs, url: "https://docs.docker.com/engine/storage/volumes/", section: "Docker: Volumes", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
---
## Το πρόβλημα

Ό,τι γράφει ένα container στα δικά του αρχεία **χάνεται** όταν διαγράψεις το container. Για μια βάση
δεδομένων αυτό είναι καταστροφή.

## Η λύση: volume

Ένα **volume** είναι χώρος αποθήκευσης που τον διαχειρίζεται το Docker και ζει **έξω** από τον κύκλο
ζωής των containers. Σβήνεις το container, το volume μένει, μέχρι να το διαγράψεις εσύ ρητά.

```bash
docker volume create appdata
docker run --rm -v appdata:/data alpine:3 sh -c 'echo saved > /data/note.txt'
docker run --rm -v appdata:/data alpine:3 cat /data/note.txt
```

Το πρώτο container γράφει ένα αρχείο και σβήνεται (`--rm`). Το δεύτερο, ένα εντελώς νέο container,
διαβάζει το ίδιο αρχείο από το volume και τυπώνει `saved`.

| Κομμάτι | Τι σημαίνει |
|---|---|
| `-v appdata:/data` | το volume `appdata` εμφανίζεται μέσα στο container στον φάκελο `/data` |

## Volume ή bind mount;

Με ένα **bind mount** συνδέεις έναν συγκεκριμένο φάκελο του υπολογιστή σου μέσα στο container.
Τα volumes προτιμώνται, εκτός αν χρειάζεσαι άμεση πρόσβαση σε αρχεία του υπολογιστή σου: τα
διαχειρίζεται το Docker και είναι πιο εύκολο να τα κρατήσεις αντίγραφα ή να τα μεταφέρεις.

Για να δεις και να σβήσεις volumes:

```bash
docker volume ls
docker volume rm appdata
```
