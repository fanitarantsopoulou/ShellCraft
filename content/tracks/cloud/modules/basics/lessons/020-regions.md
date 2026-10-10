---
id: cloud.basics.regions
title: Regions και Availability Zones
level: beginner
objective: Να καταλαβαίνεις πώς οργανώνονται τα data centers ενός παρόχου και γιατί βάζουμε εφαρμογές σε πολλές zones.
est_minutes: 4
skills: [cloud.concepts]
citations:
  - { source: aws-docs, url: "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html", section: "AWS: Global infrastructure", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: azure-docs, url: "https://learn.microsoft.com/en-us/azure/reliability/availability-zones-overview", section: "Azure: What are availability zones?", doc_version: "Azure docs 2026", last_verified: 2026-10-10 }
  - { source: gcp-docs, url: "https://cloud.google.com/docs/geography-and-regions", section: "Google Cloud: Geography and regions", doc_version: "Google Cloud docs 2026", last_verified: 2026-10-10 }
---
## Region

Ένα **region** είναι μια γεωγραφική περιοχή του κόσμου όπου ο πάροχος έχει data centers, π.χ. μια
περιοχή στην Ευρώπη. Διαλέγεις region με βάση το πού είναι οι χρήστες σου, το κόστος και τους κανόνες
για το πού επιτρέπεται να βρίσκονται τα δεδομένα.

## Availability Zone

Κάθε region έχει πολλές **Availability Zones** (AZs). Μια AZ είναι ένα ή περισσότερα data centers
με **δικό τους ρεύμα, δίκτυο και συνδέσεις**, σε ξεχωριστό κτίριο από τις άλλες.

## Γιατί έχει σημασία

Αν η εφαρμογή σου τρέχει σε **μία** AZ και εκείνη πάθει βλάβη, η εφαρμογή πέφτει. Αν τρέχει σε
**δύο ή περισσότερες**, συνεχίζει να δουλεύει από τις υπόλοιπες. Έτσι πετυχαίνεις υψηλή
διαθεσιμότητα, κάτι που δύσκολα γίνεται με ένα μόνο data center.

Η ίδια ιδέα υπάρχει σε όλους τους μεγάλους παρόχους: AWS, Microsoft Azure και Google Cloud.
