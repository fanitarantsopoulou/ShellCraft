---
id: linux.files.moving
title: Μετακίνηση και μετονομασία
level: beginner
objective: Να μετονομάζεις και να μετακινείς αρχεία και να ξεχωρίζεις πότε χρειάζεται mv και πότε cp.
est_minutes: 4
skills: [linux.files.move]
commands: [mv, cp]
citations:
  - source: gnu-coreutils
    url: https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html
    doc_version: GNU coreutils 9.7 (Debian 13)
    last_verified: 2026-10-06
---
## Το πρόβλημα

Έγραψες το `draft.txt` και είναι έτοιμο. Θέλεις να λέγεται `final.txt` — χωρίς να μείνει
πίσω και δεύτερο αντίγραφο.

## Η εντολή

Στο Linux η μετονομασία είναι απλώς **μετακίνηση με νέο όνομα**. Γι' αυτό την κάνει το `mv` (*move*):

```bash
mv draft.txt final.txt
```

Μετά την εντολή υπάρχει **μόνο** το `final.txt`.

## Μετακίνηση σε φάκελο

Αν ο προορισμός είναι υπάρχων φάκελος, το αρχείο μπαίνει μέσα του με το ίδιο όνομα:

```bash
mv report.txt archive/
```

Αποτέλεσμα: `archive/report.txt`.

## cp ή mv;

| Θέλω…                          | Εντολή |
|--------------------------------|--------|
| να κρατήσω και το αρχικό       | `cp`   |
| να μη μείνει το αρχικό         | `mv`   |
