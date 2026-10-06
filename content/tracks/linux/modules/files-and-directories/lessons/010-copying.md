---
id: linux.files.copying
title: Αντιγραφή αρχείων με ασφάλεια
level: beginner
objective: Να δημιουργείς αντίγραφο ενός αρχείου ή φακέλου χωρίς να αλλάζεις το αρχικό.
est_minutes: 5
skills: [linux.files.copy, linux.files.safe-changes]
commands: [cp, mv]
citations:
  - source: gnu-coreutils
    url: https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html
    doc_version: GNU coreutils 9.7 (Debian 13)
    last_verified: 2026-10-06
---
## Το πρόβλημα

Πρόκειται να αλλάξεις το `app.conf`. Αν κάτι πάει στραβά, θέλεις να μπορείς να γυρίσεις
πίσω. Πριν από κάθε αλλαγή σε σημαντικό αρχείο, κρατάς **αντίγραφο**.

## Η εντολή

Το `cp` (από το *copy*) αντιγράφει ένα αρχείο. Η σειρά των ορισμάτων είναι πάντα
**πρώτα η πηγή, μετά ο προορισμός**:

```bash
cp app.conf app.conf.bak
```

| Κομμάτι        | Ρόλος                      |
|----------------|----------------------------|
| `cp`           | η εντολή                   |
| `app.conf`     | πηγή (*SOURCE*)            |
| `app.conf.bak` | προορισμός (*DEST*)        |

Μετά την εντολή υπάρχουν **και τα δύο** αρχεία με το ίδιο περιεχόμενο.

## Φάκελοι

Για να αντιγράψεις φάκελο μαζί με όλο το περιεχόμενό του χρειάζεται το `-r` (*recursive*):

```bash
cp -r project project-backup
```

Χωρίς `-r`, το `cp` αρνείται και σου το λέει:

```text
cp: -r not specified; omitting directory 'project'
```

## Προσοχή

- Αν ο προορισμός υπάρχει ήδη, το `cp` τον **αντικαθιστά χωρίς ερώτηση**. Το `-i` σε ρωτάει πρώτα.
- Το `cp` είναι πρόγραμμα του **GNU coreutils**, όχι μέρος του kernel ή του shell.
