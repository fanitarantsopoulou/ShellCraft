---
track: linux
title: Τι είναι το Linux
citations:
  - { source: kernel-docs, url: "https://docs.kernel.org/admin-guide/README.html", section: "Linux kernel README", doc_version: "Linux kernel docs", last_verified: 2026-10-07 }
  - { source: kernel-org, url: "https://mirrors.edge.kernel.org/pub/linux/kernel/Historic/old-versions/RELNOTES-0.01", section: "Linux 0.01 release notes (1991)", doc_version: "0.01", last_verified: 2026-10-07 }
  - { source: linux-foundation, url: "https://www.linuxfoundation.org/blog/blog/anniversary-of-first-linux-kernel-release-a-look-at-collaborative-value", section: "Linux Foundation: Anniversary of First Linux Kernel Release", doc_version: "Linux Foundation blog", last_verified: 2026-10-07 }
  - { source: kernel-docs, url: "https://docs.kernel.org/process/programming-language.html", section: "Kernel: Programming Language", doc_version: "Linux kernel docs", last_verified: 2026-10-07 }
  - { source: kernel-docs, url: "https://docs.kernel.org/process/license-rules.html", section: "Kernel: Licensing rules", doc_version: "Linux kernel docs", last_verified: 2026-10-07 }
  - { source: debian, url: "https://www.debian.org/intro/about", section: "Debian: About", doc_version: "debian.org", last_verified: 2026-10-07 }
  - { source: android, url: "https://source.android.com/docs/core/architecture/kernel", section: "Android: Kernel overview", doc_version: "AOSP docs", last_verified: 2026-10-07 }
  - { source: kubernetes-docs, url: "https://kubernetes.io/docs/concepts/windows/intro/", section: "Kubernetes: Windows containers", doc_version: "Kubernetes v1.37", last_verified: 2026-10-07 }
  - { source: docker-docs, url: "https://docs.docker.com/get-started/docker-overview/", section: "Docker overview", doc_version: "Docker docs 2026", last_verified: 2026-10-07 }
---
## Με μια φράση

Το **Linux** είναι ένας **kernel** (πυρήνας λειτουργικού συστήματος) ανοιχτού κώδικα. Ο kernel είναι
το κομμάτι που μιλά απευθείας με το hardware: μοιράζει τη μνήμη και τον επεξεργαστή στα προγράμματα,
διαχειρίζεται αρχεία, δίσκους και δίκτυο, και αποφασίζει ποιος έχει δικαίωμα να κάνει τι.

## Πώς ξεκίνησε

- Στις **25 Αυγούστου 1991** ο **Linus Torvalds** ανακοίνωσε ότι δουλεύει πάνω σε ένα νέο λειτουργικό,
  με το περίφημο «Hello, everybody out there…».
- Στις **5 Οκτωβρίου 1991** κυκλοφόρησε ο πρώτος kernel, η **έκδοση 0.01**. Οι σημειώσεις της
  τον περιγράφουν ως «a free minix-like kernel for i386(+) based AT-machines»: έναν
  **ελεύθερο** kernel για τους προσωπικούς υπολογιστές της εποχής, με όλο τον πηγαίο κώδικα μαζί.

## Ποιος ήταν ο σκοπός

Η τεκμηρίωση του kernel το λέει καθαρά: το Linux είναι **κλώνος του Unix**, γραμμένος **από την αρχή**
από τον Linus Torvalds με τη βοήθεια προγραμματιστών από όλο το internet, και θέλει να
ακολουθεί τα πρότυπα **POSIX** και **Single UNIX Specification**.

Με απλά λόγια: ένα λειτουργικό σαν το Unix, που όμως ο καθένας μπορεί να το χρησιμοποιήσει, να δει
τον κώδικά του και να τον βελτιώσει. Γι' αυτό κυκλοφορεί με την άδεια **GNU GPL έκδοση 2**.

Αυτή η ανοιχτότητα το έκανε τεράστιο: από τις **10.239 γραμμές** κώδικα της έκδοσης 0.01, ο kernel
έφτασε σε **πάνω από 19 εκατομμύρια** γραμμές στην έκδοση 4.1, με συνεισφορές από σχεδόν
**12.000 προγραμματιστές** και πάνω από **1.200 εταιρείες** (Linux Foundation).

## Σε τι γλώσσα είναι γραμμένο

Ο kernel είναι γραμμένος κυρίως σε **C** (η διάλεκτος GNU του C11, με τους compilers `gcc` ή `clang`).
Τα τελευταία χρόνια υποστηρίζει προαιρετικά και κώδικα σε **Rust**.

## Linux και «διανομές»

Ο kernel μόνος του δεν φτάνει για να δουλέψεις: χρειάζεσαι shell, εντολές όπως `ls` και `cp`,
διαχειριστή πακέτων κ.λπ. Μια **διανομή** (distribution) τα συνδυάζει όλα σε ένα πλήρες λειτουργικό.

Το **Debian** (αυτό που χρησιμοποιεί αυτή η πλατφόρμα) το περιγράφει σαν πύργο: στη βάση ο kernel,
από πάνω τα βασικά εργαλεία (πολλά από το έργο **GNU**, γι' αυτό λέγεται και GNU/Linux), και στην κορυφή
το Debian που τα οργανώνει ώστε να δουλεύουν μαζί, με πάνω από 70.000 πακέτα και τον package manager **APT**.
Άλλες γνωστές διανομές: Ubuntu, Fedora, Red Hat Enterprise Linux, Alpine.

## Πού τρέχει σήμερα

Το Linux είναι παντού, ακόμη κι αν δεν το βλέπεις:

- **Servers και cloud**: πάρα πολλές ιστοσελίδες, εφαρμογές και υπηρεσίες που χρησιμοποιείς καθημερινά
  τρέχουν σε Linux servers.
- **Containers**: το Docker χρησιμοποιεί λειτουργίες του Linux kernel (namespaces) για να απομονώνει τα containers.
- **Kubernetes**: το control plane του τρέχει **μόνο** σε Linux.
- **Κινητά**: ο kernel του **Android** βασίζεται σε Linux kernel (LTS).
- **Πολλές αρχιτεκτονικές**: από x86 PCs και servers μέχρι ARM συσκευές.

## Γιατί να το μάθεις

Όποιος δουλεύει με servers, Docker, Kubernetes ή cloud, θα βρεθεί σε ένα Linux τερματικό. Εκεί πρέπει
να ξέρεις να βρίσκεις αρχεία, να διαβάζεις logs, να καταλαβαίνεις δικαιώματα και να λύνεις προβλήματα.
Αυτό ακριβώς εξασκούν τα quiz αυτής της ενότητας.
