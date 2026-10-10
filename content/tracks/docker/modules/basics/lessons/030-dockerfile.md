---
id: docker.basics.dockerfile
title: Dockerfile και build
level: intermediate
objective: Να γράφεις ένα απλό Dockerfile και να χτίζεις το δικό σου image.
est_minutes: 6
skills: [docker.images]
commands: [docker-image-build, docker-container-run]
citations:
  - { source: docker-docs, url: "https://docs.docker.com/reference/dockerfile/", section: "Dockerfile reference", doc_version: "Docker docs 2026", last_verified: 2026-10-10 }
  - { source: docker-docs, url: "https://docs.docker.com/reference/cli/docker/buildx/build/", section: "docker buildx build", doc_version: "Docker CLI 29.5.2", last_verified: 2026-10-10 }
---
## Τι είναι το Dockerfile

Ένα **Dockerfile** είναι ένα αρχείο κειμένου με οδηγίες, τη μία κάτω από την άλλη, που λένε στο
Docker πώς να χτίσει ένα image. Για μια μικρή εφαρμογή Python:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Οι βασικές οδηγίες

| Οδηγία | Τι κάνει |
|---|---|
| `FROM` | το image πάνω στο οποίο χτίζεις (συνήθως η πρώτη γραμμή) |
| `WORKDIR` | ο φάκελος όπου θα γίνονται τα επόμενα βήματα |
| `COPY` | αντιγράφει αρχεία από τον υπολογιστή σου μέσα στο image |
| `RUN` | τρέχει μια εντολή **την ώρα του build** και κρατά το αποτέλεσμα στο image |
| `CMD` | η εντολή που τρέχει **όταν ξεκινά** ένα container (αν γράψεις πολλά `CMD`, ισχύει το τελευταίο) |
| `EXPOSE` | γράφει ποια θύρα χρησιμοποιεί η εφαρμογή. Δεν ανοίγει τη θύρα: γι' αυτό χρειάζεται το `-p` |

Οι οδηγίες δεν κάνουν διάκριση πεζών και κεφαλαίων, αλλά συνηθίζεται να γράφονται με κεφαλαία.

## Χτίζοντας το image

```bash
docker build -t myapp:1.0 .
```

Το `-t` δίνει όνομα και tag στο image. Η τελεία στο τέλος είναι το **build context**: ο φάκελος
που στέλνεται στο build και από τον οποίο το `COPY` παίρνει τα αρχεία.

## Γιατί έχει σημασία η σειρά

Κάθε οδηγία φτιάχνει ένα layer, και το Docker κρατά τα layers στην cache. Όταν αλλάζει ένα αρχείο,
ξαναγίνονται μόνο τα βήματα από εκείνο το σημείο και κάτω. Γι' αυτό στο παράδειγμα αντιγράφουμε
πρώτα μόνο το `requirements.txt` και εγκαθιστούμε: αν αλλάξει μόνο ο κώδικας, η εγκατάσταση δεν
ξανατρέχει.

## Το `.dockerignore`

Με ένα αρχείο `.dockerignore` αφήνεις έξω από το build context αρχεία που δεν χρειάζονται, όπως
`.git` ή αρχεία με κωδικούς. Το build γίνεται πιο γρήγορο και δεν μπαίνουν κατά λάθος μυστικά στο image.
