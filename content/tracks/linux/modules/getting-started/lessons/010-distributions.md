---
id: linux.start.distributions
title: Διανομές Linux και οικογένειες
level: beginner
objective: Να ξέρεις τι είναι μια διανομή Linux, ποιες οικογένειες διανομών υπάρχουν και τι αλλάζει από τη μία στην άλλη.
est_minutes: 5
skills: [linux.distros]
citations:
  - { source: debian, url: "https://www.debian.org/intro/about", section: "Debian: Τι είναι το Debian", doc_version: "debian.org", last_verified: 2026-10-10 }
  - { source: debian, url: "https://www.debian.org/doc/manuals/debian-faq/pkg-basics.en.html", section: "Debian FAQ: Basics of the Debian package management system", doc_version: "Debian FAQ", last_verified: 2026-10-10 }
  - { source: ubuntu, url: "https://ubuntu.com/community/docs/governance/debian", section: "Ubuntu and Debian", doc_version: "ubuntu.com", last_verified: 2026-10-10 }
  - { source: centos, url: "https://www.centos.org/centos-stream/", section: "CentOS Stream", doc_version: "centos.org", last_verified: 2026-10-10 }
  - { source: rpm, url: "https://rpm.org/about.html", section: "About RPM", doc_version: "rpm.org", last_verified: 2026-10-10 }
  - { source: alpine, url: "https://www.alpinelinux.org/about/", section: "About Alpine Linux", doc_version: "alpinelinux.org", last_verified: 2026-10-10 }
  - { source: dnf, url: "https://github.com/rpm-software-management/dnf", section: "DNF (Dandified YUM)", doc_version: "DNF 4", last_verified: 2026-10-10 }
  - { source: opensuse, url: "https://doc.opensuse.org/documentation/leap/reference/html/book-reference/cha-sw-cl.html", section: "openSUSE: Managing software with command line tools (Zypper)", doc_version: "openSUSE Leap", last_verified: 2026-10-10 }
---
## Τι είναι μια διανομή

Το Linux, με την αυστηρή έννοια, είναι μόνο ο **kernel**. Για να δουλέψεις χρειάζεσαι και πολλά
ακόμα: shell, βασικές εντολές, προγράμματα, έναν τρόπο να εγκαθιστάς και να ενημερώνεις λογισμικό.

Μια **διανομή** (distribution ή «distro») τα μαζεύει όλα αυτά σε ένα έτοιμο λειτουργικό. Το Debian
το περιγράφει σαν πύργο: στη βάση ο kernel, από πάνω τα βασικά εργαλεία, και στην κορυφή η διανομή,
που τα οργανώνει ώστε να δουλεύουν μαζί.

## Οι μεγάλες οικογένειες

Πολλές διανομές βασίζονται σε κάποια άλλη. Έτσι σχηματίζονται «οικογένειες».

### Οικογένεια Debian

- **Debian**: φτιάχνεται από μια κοινότητα ανθρώπων που δουλεύουν μαζί για ένα ελεύθερο λειτουργικό.
- **Ubuntu**: βασίζεται στο Debian, με δική του διαδικασία κυκλοφορίας και εταιρική υποστήριξη.

Χρησιμοποιούν πακέτα **`.deb`**. Το εργαλείο **`dpkg`** εγκαθιστά ένα πακέτο, και το **APT**
(εντολή `apt`) είναι το πιο εύκολο εργαλείο από πάνω του: βρίσκει τα πακέτα και ό,τι άλλο χρειάζονται.

### Οικογένεια Red Hat

- **Fedora**: η διανομή της κοινότητας.
- **CentOS Stream**: βρίσκεται ανάμεσα στο Fedora και στο RHEL και ακολουθεί λίγο πιο μπροστά από το RHEL.
- **Red Hat Enterprise Linux (RHEL)**: η σταθερή διανομή για επιχειρήσεις.

Οι αλλαγές περνούν από το Fedora, μετά από το CentOS Stream και καταλήγουν στο RHEL.
Χρησιμοποιούν πακέτα **RPM** και εγκαθιστούν λογισμικό με την εντολή **`dnf`** (ο διάδοχος του παλιότερου `yum`).

### Οικογένεια SUSE

**openSUSE** και **SUSE Linux Enterprise**. Χρησιμοποιούν κι αυτές πακέτα **RPM**, αλλά εγκαθιστούν
λογισμικό με τη δική τους εντολή, το **`zypper`**.

### Ανεξάρτητες διανομές

Υπάρχουν και διανομές που δεν βασίζονται σε άλλη. Παράδειγμα είναι το **Alpine Linux**: πολύ μικρό
(ένα container του χρειάζεται περίπου 8 MB), γι' αυτό το βλέπεις συχνά σε Docker images. Έχει δικό
του διαχειριστή πακέτων, το **`apk`**.

## Τι είναι ίδιο και τι αλλάζει

Όλες οι διανομές έχουν τον ίδιο **Linux kernel** και ακολουθούν την ίδια λογική: αρχεία, φάκελοι,
δικαιώματα, διεργασίες, shell. Αυτά που μαθαίνεις σε αυτή την πλατφόρμα ισχύουν παντού.

Αυτό που αλλάζει κυρίως είναι το **πώς εγκαθιστάς λογισμικό**:

| Οικογένεια | Πακέτα | Εντολή εγκατάστασης |
|---|---|---|
| Debian, Ubuntu | `.deb` | `apt` |
| Fedora, CentOS Stream, RHEL | RPM | `dnf` |
| openSUSE, SUSE | RPM | `zypper` |
| Alpine | `apk` | `apk` |

Αλλάζουν επίσης οι εκδόσεις των προγραμμάτων και το πόσο συχνά βγαίνουν νέες εκδόσεις της διανομής.

## Σε αυτή την πλατφόρμα

Οι ασκήσεις και τα αποτελέσματα των εντολών προέρχονται από **Debian**.
