---
track: cloud
title: Τι είναι το cloud
citations:
  - { source: nist, url: "https://csrc.nist.gov/pubs/sp/800/145/final", section: "NIST SP 800-145: The NIST Definition of Cloud Computing", doc_version: "SP 800-145 (2011)", last_verified: 2026-10-07 }
  - { source: aws-docs, url: "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html", section: "Overview of Amazon Web Services", doc_version: "AWS whitepaper, June 2026", last_verified: 2026-10-07 }
  - { source: aws-docs, url: "https://aws.amazon.com/compliance/shared-responsibility-model/", section: "AWS Shared Responsibility Model", doc_version: "AWS 2026", last_verified: 2026-10-07 }
  - { source: azure-docs, url: "https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview", section: "Azure availability zones", doc_version: "Azure docs 2026", last_verified: 2026-10-07 }
  - { source: gcp-docs, url: "https://cloud.google.com/docs/geography-and-regions", section: "Google Cloud geography and regions", doc_version: "Google Cloud docs 2026", last_verified: 2026-10-07 }
---
## Με μια φράση

**Cloud** σημαίνει ότι νοικιάζεις υπολογιστική ισχύ, αποθήκευση και δίκτυο από έναν πάροχο μέσω
του internet, **όταν τα χρειάζεσαι** και **πληρώνοντας όσο τα χρησιμοποιείς** — αντί να αγοράζεις και να
συντηρείς δικούς σου servers.

## Ο επίσημος ορισμός (NIST)

Το NIST (το αμερικανικό ινστιτούτο προτύπων) ορίζει το cloud με **πέντε βασικά χαρακτηριστικά**:

- **On-demand self-service** — παίρνεις πόρους μόνος σου, αυτόματα, χωρίς να μιλήσεις με άνθρωπο.
- **Broad network access** — πρόσβαση μέσω δικτύου από κάθε είδους συσκευή.
- **Resource pooling** — οι πόροι του παρόχου μοιράζονται δυναμικά σε πολλούς πελάτες.
- **Rapid elasticity** — οι πόροι μεγαλώνουν ή μικραίνουν γρήγορα, ακόμη και αυτόματα, με τη ζήτηση.
- **Measured service** — η χρήση μετριέται (και συνήθως χρεώνεται ανά χρήση).

## Πώς ξεκίνησε

Το **2006** η Amazon Web Services (AWS) άρχισε να προσφέρει υποδομή IT σε επιχειρήσεις ως υπηρεσίες
μέσω web — αυτό που σήμερα λέμε cloud computing. Η μεγάλη αλλαγή: αντί για ακριβή αγορά servers
εβδομάδες ή μήνες πριν, σηκώνεις εκατοντάδες servers σε λίγα λεπτά και πληρώνεις μεταβλητό κόστος.
Σήμερα οι μεγαλύτεροι πάροχοι είναι η **AWS**, το **Microsoft Azure** και το **Google Cloud**.

## Τα τρία μοντέλα υπηρεσίας

| Μοντέλο | Τι παίρνεις | Τι διαχειρίζεσαι εσύ | Παράδειγμα |
|---|---|---|---|
| **IaaS** | εικονικές μηχανές, δίσκους, δίκτυα | λειτουργικό, εφαρμογές | μια VM με Debian |
| **PaaS** | πλατφόρμα για να ανεβάσεις κώδικα | την εφαρμογή σου | «ανέβασε τον κώδικα, τρέχει» |
| **SaaS** | έτοιμη εφαρμογή | σχεδόν τίποτα | web-based email |

Ως προς το **πού** βρίσκεται η υποδομή, το NIST ξεχωρίζει **public**, **private**, **community** και
**hybrid** cloud (συνδυασμός τους).

## Regions και Availability Zones

Οι πάροχοι έχουν data centers σε όλο τον κόσμο, οργανωμένα σε **regions** (γεωγραφικές περιοχές).
Κάθε region έχει πολλές **Availability Zones**: φυσικά χωριστά data centers με δικό τους ρεύμα και δίκτυο.
Αν βάλεις την εφαρμογή σου σε δύο AZs, συνεχίζει να δουλεύει ακόμη κι αν η μία πάθει βλάβη.

## Ποιος ευθύνεται για τι

Στο **μοντέλο κοινής ευθύνης**, ο πάροχος προστατεύει την υποδομή (κτίρια, hardware, virtualization).
Ό,τι βάζεις **εσύ** πάνω της — το λειτουργικό μιας VM, τα updates, τις εφαρμογές, τα δεδομένα και ποιος
έχει πρόσβαση — είναι δική σου ευθύνη.

## Πώς δένουν όλα μαζί

Αυτό που θα συναντήσεις στην πράξη συνδυάζει όλες τις ενότητες αυτής της πλατφόρμας: εικονικές
μηχανές με **Linux** στο cloud, εφαρμογές πακεταρισμένες σε **Docker** images, και **Kubernetes**
clusters — συχνά ως διαχειριζόμενη υπηρεσία του παρόχου — που τα τρέχουν σε μεγάλη κλίμακα.
