---
id: docker.basics.running
title: Τρέχοντας containers
level: beginner
objective: Να ξεκινάς ένα container στο παρασκήνιο, να ανοίγεις θύρα προς τον υπολογιστή σου και να βλέπεις τι κάνει.
est_minutes: 6
skills: [docker.containers]
commands: [docker-container-run, docker-container-ls, docker-container-logs, docker-container-exec, docker-container-stop, docker-container-rm]
citations:
  - { source: docker-docs, url: "https://docs.docker.com/reference/cli/docker/container/run/", section: "docker container run", doc_version: "Docker CLI 29.5.2", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/engine/network/port-publishing/", section: "Docker: Port publishing and mapping", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/reference/cli/docker/container/logs/", section: "docker container logs", doc_version: "Docker CLI 29.5.2", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/reference/cli/docker/container/exec/", section: "docker container exec", doc_version: "Docker CLI 29.5.2", last_verified: 2026-10-10 }
---
## Η εντολή `docker run`

Με το `docker run` δημιουργείς και ξεκινάς ένα container από ένα image:

```bash
docker run -d -p 8080:80 --name web nginx
```

| Κομμάτι | Τι κάνει |
|---|---|
| `-d` | τρέχει στο παρασκήνιο, ώστε να σου μείνει ελεύθερο το τερματικό |
| `-p 8080:80` | η θύρα 8080 του υπολογιστή σου οδηγεί στη θύρα 80 του container |
| `--name web` | δίνει όνομα στο container, για να το βρίσκεις εύκολα |
| `nginx` | το image |

Οι επιλογές μπαίνουν **πριν** από το όνομα του image. Ό,τι γράψεις μετά το image περνάει στο container.

## Γιατί χρειάζεται το `-p`

Από προεπιλογή, οι θύρες ενός container **δεν** φαίνονται έξω από τον υπολογιστή που το τρέχει.
Με το `-p ΘΥΡΑ_HOST:ΘΥΡΑ_CONTAINER` ανοίγεις μια θύρα προς τα έξω. Με το παραπάνω παράδειγμα,
ανοίγεις τον browser στο `http://localhost:8080`.

## Τι κάνει το container μου;

```bash
docker ps              # ποια containers τρέχουν
docker ps -a           # και όσα έχουν σταματήσει
docker logs -f web     # η έξοδος της εφαρμογής, ζωντανά
docker exec -it web sh # ανοίγεις shell μέσα στο container
```

Το `exec` τρέχει μια εντολή σε container που **ήδη τρέχει**. Το `-i` κρατά ανοιχτή την είσοδο και το
`-t` δίνει τερματικό, γι' αυτό μαζί (`-it`) σου δίνουν διαδραστικό shell.

## Σταμάτημα και διαγραφή

```bash
docker stop web
docker rm web
```

Ένα container που τρέχει δεν διαγράφεται: πρώτα το σταματάς. Αν θέλεις να σβήνεται μόνο του όταν
τελειώσει, το ξεκινάς με `--rm`.
