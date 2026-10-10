---
id: cloud.basics.networking
title: "Δίκτυα στο cloud: VPC, subnets, security groups"
level: intermediate
objective: Να στήνεις στο μυαλό σου ένα ιδιωτικό δίκτυο στο cloud και να ξέρεις ποιος μπορεί να συνδεθεί πού.
est_minutes: 6
skills: [cloud.infra]
citations:
  - { source: aws-docs, url: "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-cidr-blocks.html", section: "Amazon VPC: VPC CIDR blocks", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: aws-docs, url: "https://docs.aws.amazon.com/vpc/latest/userguide/configure-subnets.html", section: "Amazon VPC: Subnets", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
  - { source: aws-docs, url: "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html", section: "Amazon VPC: Security groups", doc_version: "AWS docs 2026", last_verified: 2026-10-10 }
---
## VPC: το δικό σου δίκτυο

Ένα **VPC** (Virtual Private Cloud) είναι ένα ιδιωτικό δίκτυο μέσα στο cloud του παρόχου. Όταν το
φτιάχνεις, του δίνεις ένα εύρος διευθύνσεων σε μορφή **CIDR**, π.χ. `10.0.0.0/16`.

Ο αριθμός μετά την κάθετο λέει πόσα bits είναι σταθερά. Τα υπόλοιπα από τα 32 bits είναι για
διευθύνσεις:

| CIDR | Ελεύθερα bits | Διευθύνσεις |
|---|---|---|
| `/16` | 16 | 65.536 |
| `/24` | 8 | 256 |
| `/28` | 4 | 16 |

Συνήθως χρησιμοποιούμε ιδιωτικά εύρη, όπως `10.0.0.0/8`, `172.16.0.0/12` και `192.168.0.0/16`.

## Subnets: κομμάτια του δικτύου

Ένα VPC χωρίζεται σε **subnets**, συνήθως ένα ή περισσότερα σε κάθε Availability Zone.

- **Public subnet**: έχει διαδρομή (route) προς το internet μέσω internet gateway. Εδώ μπαίνει π.χ.
  ένας load balancer.
- **Private subnet**: δεν έχει απευθείας διαδρομή προς το internet. Εδώ μπαίνουν π.χ. οι βάσεις δεδομένων.

## Security groups: ποιος περνάει

Ένα **security group** είναι σαν firewall γύρω από έναν server. Γράφεις κανόνες για το ποια
κίνηση **επιτρέπεται** να μπει και να βγει. Δύο πράγματα αξίζει να θυμάσαι:

- Είναι **stateful**: αν επιτρέψεις μια εισερχόμενη σύνδεση, η απάντηση βγαίνει αυτόματα, χωρίς
  ξεχωριστό κανόνα.
- Για SSH (θύρα 22) και RDP (θύρα 3389) **μην** ανοίγεις σε όλο το internet (`0.0.0.0/0`).
  Επίτρεψε μόνο συγκεκριμένες διευθύνσεις, π.χ. το δίκτυο του γραφείου σου.
