---
id: cloud.basics.storage-scaling
title: Αποθήκευση, load balancing και κλιμάκωση
level: intermediate
objective: Να ξέρεις πού κρατάς αρχεία στο cloud και πώς μια εφαρμογή αντέχει περισσότερη κίνηση.
est_minutes: 5
skills: [cloud.infra]
citations:
  - { source: aws-docs, url: "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html", section: "Amazon S3: What is Amazon S3?", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: azure-docs, url: "https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction", section: "Azure Blob Storage", doc_version: "Azure docs 2026", last_verified: 2026-10-10 }
  - { source: aws-docs, url: "https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html", section: "What is Elastic Load Balancing?", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: aws-docs, url: "https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html", section: "What is Amazon EC2 Auto Scaling?", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: terraform-docs, url: "https://developer.hashicorp.com/terraform/intro", section: "What is Terraform?", doc_version: "Terraform docs 2026", last_verified: 2026-10-10 }
---
## Object storage

Για αρχεία όπως φωτογραφίες, backups ή στατικά αρχεία ενός site χρησιμοποιούμε **object storage**,
π.χ. Amazon S3 ή Azure Blob Storage.

- Τα αρχεία λέγονται **objects** και μπαίνουν σε **buckets** (κάτι σαν κουτιά).
- Κάθε object έχει ένα **key**, το όνομά του μέσα στο bucket, π.χ. `photos/puppy.jpg`.
- Τα buckets είναι **ιδιωτικά** από προεπιλογή: κανείς δεν τα βλέπει αν δεν δώσεις εσύ πρόσβαση.
- Πληρώνεις όσο χρησιμοποιείς και ο χώρος μεγαλώνει όσο χρειάζεται.

## Load balancer

Ένας **load balancer** μοιράζει την κίνηση σε πολλούς servers, ακόμα και σε διαφορετικές Availability
Zones. Ελέγχει συνεχώς αν οι servers απαντούν (**health checks**) και στέλνει κίνηση μόνο σε όσους είναι
υγιείς. Έτσι, αν πέσει ένας, οι χρήστες δεν το καταλαβαίνουν.

## Autoscaling

Με το **autoscaling** ορίζεις:

| Ρύθμιση | Τι σημαίνει |
|---|---|
| ελάχιστο | ποτέ λιγότεροι servers από αυτούς |
| μέγιστο | ποτέ περισσότεροι από αυτούς |
| επιθυμητό | πόσοι τρέχουν τώρα |

Με κανόνες κλιμάκωσης, οι servers αυξάνονται όταν ανεβαίνει η κίνηση και μειώνονται όταν πέφτει.
Αν κάποιος χαλάσει, αντικαθίσταται αυτόματα. Όταν δουλεύει μαζί με load balancer, κάθε νέος server
μπαίνει αυτόματα στον load balancer.

## Infrastructure as Code

Όλα τα παραπάνω μπορείς να τα στήσεις με κλικ στην κονσόλα του παρόχου. Στην πράξη όμως τα γράφουμε
σε **αρχεία**, με εργαλεία όπως το **Terraform**. Τα αρχεία μπαίνουν σε git, ελέγχονται πριν
εφαρμοστούν, και στήνουν την ίδια υποδομή όσες φορές χρειαστεί.
