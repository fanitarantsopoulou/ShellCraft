# ShellCraft — Architecture & Design Analysis

> Status: proposal v0.1 — 2026-10-06. Δεν υπάρχει ακόμη implementation code.
> Οι τεχνικές αποφάσεις παραπέμπουν σε επίσημες πηγές (βλ. §0).

---

## 0. Research: τι επιβεβαιώθηκε από επίσημες πηγές και πώς επηρεάζει τον σχεδιασμό

| Εύρημα | Πηγή | Συνέπεια για το project |
|---|---|---|
| Το `cd` είναι **shell regular built-in**. Δεν είναι Linux command ή executable: «Since cd affects the current shell execution environment, it is always provided as a shell regular built-in». | POSIX.1-2017, `cd(1p)` — man7.org | Το `Command` entity χρειάζεται πεδίο `kind` (`shell_builtin` / `external_utility` / …) και `provider`. Η πλατφόρμα δεν θα λέει «Linux command» για όλα. |
| Το `cp` ανήκει στο **GNU coreutils**. Στο macOS (BSD) έχει διαφορετικά flags. | GNU coreutils manual | Κάθε content item δηλώνει `platform` (π.χ. `gnu-linux`). Το sandbox image πρέπει να ταιριάζει ακριβώς με το content (π.χ. Debian stable). |
| Το `rename` **υπάρχει** (util-linux: `rename [options] expression replacement file...`). Το `rename old.txt new.txt` χωρίς αρχεία δεν κάνει τίποτα. Το Debian/Ubuntu μπορεί να έχει άλλη υλοποίηση (Perl `rename`). | `rename(1)` — man7.org | Το παράδειγμα της §6 θέλει διόρθωση: το `rename` δεν είναι ανύπαρκτη εντολή. Είναι **υπαρκτή εντολή με λάθος σημασιολογία** για το task. Το distractor metadata χρειάζεται πιο λεπτή ταξινόμηση (§7). Και το `copy` υπάρχει, απλώς στο Windows `cmd`. Αυτό αξίζει να ειπωθεί στο feedback. |
| Το man-pages project τεκμηριώνει τα «Linux kernel and C library user-space interfaces». Το docs.kernel.org καλύπτει τον kernel, όχι τα user-space tools. | man7.org colophon, docs.kernel.org | Το docs.kernel.org **δεν** είναι η σωστή πηγή για `cp`, `grep`, `ip`. Χρειάζεται source hierarchy ανά είδος εργαλείου (§7.3). |
| Namespaces: cgroup, ipc, network, mount, pid, time, user, uts. | `namespaces(7)` | Βάση για το sandbox model και για μελλοντικά Advanced lessons. |
| cgroup v2: `memory.max`, `cpu.max`, `pids.max`, `io.max`. | docs.kernel.org/admin-guide/cgroup-v2 | Resource limits ανά sandbox session (§12). |
| «System call filtering isn't a sandbox.» Ένα seccomp sandbox «MUST NOT allow use of ptrace». | docs.kernel.org seccomp_filter | Το seccomp είναι ένα layer, όχι η λύση (§12–13). |
| Docker: ο daemon τρέχει με elevated privileges και «the default set of capabilities and mounts … may provide incomplete isolation». Το rootless mode μειώνει το ρίσκο. | docs.docker.com/engine/security, /rootless | Το backend δεν αποκτά ποτέ πρόσβαση στο Docker socket. Για untrusted code χρειάζεται runtime με ισχυρότερη απομόνωση. |
| Το gVisor (`runsc`) είναι OCI runtime με user-space application kernel και δουλεύει με Docker και Kubernetes. | gvisor.dev | Προτεινόμενο runtime για Linux sandbox (Phase 2). |
| `docker run`: `--read-only`, `--network none`, `--cap-drop ALL`, `--security-opt no-new-privileges`, `--pids-limit`, `--memory`, `--cpus`, `--user`, `--tmpfs`, `--rm`. | Docker CLI reference | Baseline hardening για κάθε sandbox container. |
| Kubernetes: τρέχουσα έκδοση **1.37.1** (2026-09-15). Υποστηρίζονται οι 1.35–1.37, ~1 χρόνο patch support η καθεμία. | kubernetes.io/releases | Το K8s content κάνει pin σε minor version και θέλει διαδικασία επανελέγχου κάθε ~4 μήνες. |
| Pod Security Standards (Privileged/Baseline/Restricted). Το RuntimeClass επιλέγει runtime, π.χ. sandboxed με hardware virtualization. | kubernetes.io/docs/concepts | Phase 3: K8s sandbox με Restricted PSS + sandboxed RuntimeClass. Κατά προτίμηση, cluster ανά χρήστη μέσα σε microVM. |

---

## 1. Assessment της ιδέας

**Δυνατά σημεία**
- Η φιλοσοφία «problem → hypothesis → check → fix → verify» είναι το σωστό εκπαιδευτικό target. Τα περισσότερα tutorials σταματούν στο «ποιο command είναι αυτό».
- Το deterministic core χωρίς LLM dependency είναι σωστή απόφαση: προβλέψιμο, testable, φθηνό.
- Η απαίτηση για source metadata και content-as-data είναι σπάνια και πολύτιμη.
- Η phased προσέγγιση (χωρίς sandbox στο MVP) είναι ρεαλιστική.

**Κύρια ρίσκα (κατά σειρά σοβαρότητας)**
1. **Το content είναι το bottleneck, όχι ο κώδικας.** Ένα καλό exercise με plausible distractors, accepted variants, known mistakes και citations θέλει 20–40 λεπτά. 100 exercises σημαίνουν περίπου 50 ώρες authoring. Η αρχιτεκτονική πρέπει πρώτα απ' όλα να κάνει το authoring γρήγορο και ελέγξιμο (lint, schema validation, test cases μέσα στο content).
2. **Το sandbox είναι το πιο επικίνδυνο κομμάτι.** Είναι remote code execution as a service. Αν γίνει λάθος, το project γίνεται crypto-miner ή pivot point. Πρέπει να είναι **ξεχωριστό service, σε ξεχωριστό host/VM**, και να μη μοιράζεται process ή credentials με το API.
3. **Ένα λάθος evaluator διδάσκει λάθος.** Ένας generic «έξυπνος» command evaluator θα δεχτεί λάθος εντολές ή θα απορρίψει σωστές. Λύση: η ισοδυναμία δηλώνεται ρητά στο content και τη συνοδεύουν test cases (§9).
4. **Το gamification μπορεί να καταπιεί τη μάθηση.** Αν το XP κερδίζεται με επανάληψη, ο χρήστης κάνει grinding. Τα unlocks πρέπει να βασίζονται σε mastery, όχι σε XP (§11).
5. **Το pixel-art αισθητικό μπορεί να βλάψει την αναγνωσιμότητα.** Pixel fonts σε θεωρία και code blocks είναι κακό UX. Το RPG layer είναι «πλαίσιο», όχι το κείμενο.

---

## 2. Potential architectural problems (και challenges στις παραδοχές)

| Παραδοχή | Πρόβλημα | Πρόταση |
|---|---|---|
| Δέντρο `Technology → Level → Module → Lesson` | Η γνώση δεν είναι δέντρο. Τα permissions χρειάζονται στο Docker (volumes, `--user`) και στο K8s (`securityContext`). Τα networking concepts είναι κοινά σε Linux/Docker/K8s. Το Level ως **ενδιάμεσο επίπεδο** διασπά modules: το `find` έχει beginner και intermediate χρήσεις. | Δύο ορθογώνιες δομές: (α) **περιεχόμενο**: `Track → Module → Lesson → Exercise`, με το `level` ως **attribute** και όχι ως κόμβο. (β) **γνώση**: ένα **Skill graph (DAG)** με prerequisites. Το mastery μετριέται σε skills, όχι σε lessons. Τα Learning Paths είναι διατεταγμένες επιλογές modules. Το world map οπτικοποιεί το skill/module graph. |
| Χωριστοί πίνακες `Questions`, `Answers`, `Exercise types` | Κάθε τύπος (MCQ, config, output analysis, hands-on) έχει εντελώς διαφορετικό σχήμα. Η πλήρης κανονικοποίηση οδηγεί σε δεκάδες πίνακες ή EAV anti-pattern. | Ένας πίνακας `exercise` με `type` και **typed JSONB `spec`** που ελέγχεται από Pydantic discriminated union. Κανονικοποιούνται μόνο όσα κάνουμε query/join: skills, commands, sources, attempts. |
| SQLite για dev, PostgreSQL για prod | Dialect drift: JSONB, constraints, concurrency, migrations που περνούν στο ένα και σπάνε στο άλλο. Θα το ανακαλύψεις στο deploy. | **PostgreSQL παντού** μέσω Docker Compose (κοστίζει μόνο ένα container). Τα pure unit tests (evaluators) δεν αγγίζουν DB. |
| «Content σε DB ή JSON ή YAML» | Αν η DB είναι source of truth για content, χάνεις review, diff, ιστορικό και reproducibility. | **YAML/Markdown στο git = source of truth.** Ένα `content import` το κάνει validate, compile και upsert στη DB. Αλλαγή content = PR + CI, χωρίς αλλαγή κώδικα. |
| Simulated terminal στο MVP | Ένας fake shell που μιμείται bash/coreutils είναι μεγάλο έργο. Κάθε απόκλιση από τη συμπεριφορά του πραγματικού `bash` διδάσκει **λάθος**. Χτίζεις κάτι που θα πετάξεις. | **Χωρίς simulator.** MVP: command-writing με static evaluation και output-analysis με **πραγματικά καταγεγραμμένα outputs**. Phase 2: κατευθείαν πραγματικό sandbox. |
| «Hands-on exercise: η πλατφόρμα ελέγχει αν ολοκληρώθηκε» | Αν ο έλεγχος γίνει με parsing του command history, ξεγελιέται εύκολα και απορρίπτει σωστές εναλλακτικές λύσεις. | **State-based verification**: ελέγχεται η τελική κατάσταση του συστήματος (το `/tmp/logs` υπάρχει και είναι directory), όχι το πώς έφτασε εκεί ο χρήστης. |
| Docker sandbox «σε container» | Το Docker-in-Docker χρειάζεται `--privileged`. Ένα privileged container με untrusted χρήστη ισοδυναμεί με root στον host. | Docker/K8s labs μέσα σε **microVM** (Firecracker/Kata) ανά session, ή σε managed ephemeral VMs. Ποτέ privileged container σε shared host. |
| XP / levels / achievements ως κύριο progression | Το XP μετράει δραστηριότητα, όχι γνώση. | Τα **unlocks βασίζονται σε skill mastery**. Το XP είναι reward ledger με anti-grinding κανόνες. Τα levels είναι κοσμητικά και δεν κλειδώνουν περιεχόμενο. |
| Layer-based backend (`models/`, `schemas/`, `services/` για όλα) | Κάθε feature αγγίζει 5 φακέλους. Τα bounded contexts θολώνουν και τα imports γίνονται κυκλικά. | **Modular monolith ανά domain** (`content/`, `evaluation/`, `progression/`, `auth/` …). Κάθε module έχει δικά του models/schemas/service/router (§16). |
| «Last verified» ως metadata | Χωρίς διαδικασία, το πεδίο θα μείνει στάσιμο και θα δείχνει ψευδή φρεσκάδα. | CI job που επισημαίνει citations παλαιότερες από N μήνες ή pinned σε EOL Kubernetes version. |

---

## 3. Recommended architecture (high level)

```
                ┌───────────────────────────── Browser ─────────────────────────────┐
                │  Vanilla JS (ES modules, no build) · SVG world map · xterm.js (P2)│
                └───────────────┬──────────────────────────────┬────────────────────┘
                                │ HTTPS (same origin)          │ WSS (Phase 2)
                        ┌───────▼────────┐                     │
                        │ Reverse proxy  │  static files + /api│
                        │ (Caddy/nginx)  │─────────────────────┤
                        └───────┬────────┘                     │
                                │                              │
                 ┌──────────────▼──────────────┐     ┌─────────▼──────────────┐
                 │  API — FastAPI modular      │     │  Sandbox Gateway (P2)  │
                 │  monolith                   │ ──► │  separate service,     │
                 │  auth · content · learning  │ mTLS│  separate host/VM      │
                 │  evaluation · progression   │     │  session tokens, TTL   │
                 └──────────────┬──────────────┘     └─────────┬──────────────┘
                                │                              │ (no Docker socket on API host)
                        ┌───────▼────────┐            ┌────────▼──────────────┐
                        │  PostgreSQL    │            │ Sandbox hosts         │
                        └────────────────┘            │ gVisor containers /   │
                                                      │ microVMs, no egress   │
   content/ (git, YAML+MD) ──► `content import` ──►   └───────────────────────┘
        CI: schema + lint + evaluator test cases
```

Βασικές αρχές:
- **Modular monolith** για το API. Δεν χρειάζονται microservices. Η μόνη πραγματική διαχωριστική γραμμή είναι το sandbox, για λόγους **ασφάλειας** και όχι scale.
- **Same-origin** frontend και API πίσω από reverse proxy: χωρίς CORS, με cookie auth.
- **Content pipeline**: git → validate → import. Οι εκδόσεις content είναι immutable ανά hash, ώστε τα attempts να παραπέμπουν στην ακριβή έκδοση που απάντησε ο χρήστης.
- **Τα evaluators είναι pure functions** (εκτός των sandbox evaluators, που παίρνουν injected client).
- **Χωρίς LLM dependency.** Αργότερα, ένα AI module είναι optional adapter με feature flag.

---

## 4. Frontend architecture

**Απόφαση: Vanilla JS, ES modules, χωρίς build step στο MVP.** Δεν υπάρχει πραγματικός τεχνικός λόγος για framework: 7 views, λίγο shared state, χωρίς real-time collaboration.

Εξωτερικές βιβλιοθήκες μόνο όπου χρειάζονται πραγματικά:
- **xterm.js** (Phase 2): ένας terminal emulator (VT100/ANSI, resize, selection) δεν γράφεται λογικά από το μηδέν.
- Τίποτε άλλο στο MVP. Τα Markdown γίνονται HTML **server-side στο import** (βλ. security), οπότε δεν χρειάζεται markdown lib στον browser.

Δομή:
```
frontend/
  index.html              # single shell page
  css/
    tokens.css            # palette, spacing, pixel scale, fonts (CSS custom properties)
    base.css  layout.css  components.css  world.css
  js/
    main.js               # bootstrap, router start
    router.js             # hash router (#/world, #/lesson/:id ...) ~60 LOC
    api.js                # fetch wrapper: CSRF header, error mapping, JSON
    store.js              # tiny pub/sub store (user, progress) — no framework
    views/                # world.js dashboard.js lesson.js quiz.js practice.js reference.js profile.js
    components/           # Custom Elements: <xp-bar> <skill-stars> <quiz-card> <feedback-panel> <cmd-block>
    world/                # map rendering (SVG), zone state, path animation
  assets/
    sprites/              # small PNG sprite sheets (16×16 / 32×32), image-rendering: pixelated
    tiles/                # map tiles
    fonts/                # pixel display font (headings only) + readable mono
```

- **Custom Elements (Web Components)** για επαναχρησιμοποιούμενα UI κομμάτια. Είναι native, encapsulated και framework-free.
- **World map σε SVG** (όχι Canvas): είναι DOM, άρα clickable, keyboard-focusable, accessible και εύκολο στο styling ανά state (`locked`/`available`/`mastered`). Τα tiles είναι PNG sprites μέσα σε `<image>` με `image-rendering: pixelated`. Canvas μόνο αν αργότερα χρειαστούν particles ή πολλά animated sprites.
- **Animations** με CSS `steps()` για sprite animation και σεβασμό του `prefers-reduced-motion`.

**Visual language (δική μας identity)**
- **Tile scale**: 16 px base, ×3 render. Περιορισμένη παλέτα ~24 χρωμάτων ανά biome, για συνοχή.
- **Biomes ανά track**, με μεταφορά που αντιστοιχεί στο αντικείμενο:
  - *Linux — "The Shell Woods"*: δάσος/χωριό. Τα modules είναι κτίρια (Library = filesystem, Guard Tower = permissions, Forge = processes).
  - *Networking — "The Wirelands"*: γέφυρες = links, φάροι = DNS, πύλες = ports/firewalls.
  - *Docker — "Harbor of Containers"*: λιμάνι, γερανοί, κοντέινερ (images = καλούπια, containers = φορτία).
  - *Kubernetes — "The Helm Citadel"*: φρούριο-cluster με πύργους (nodes) και φρουρούς (controllers). Futuristic.
  - *Cloud — "Sky Isles"*: πλωτά νησιά (regions/AZs).
  - **Advanced / troubleshooting = dungeons/caves** σε κάθε biome. Κάθε dungeon είναι scenario chain («Το nginx δεν απαντάει στο 8080»).
- **Αναγνωσιμότητα πρώτα**: pixel font μόνο σε headings και HUD. Θεωρία σε readable sans, κώδικας σε mono. Οι content σελίδες έχουν «parchment/terminal panel» frame, αλλά το κείμενο μέσα είναι καθαρό. Contrast WCAG AA.
- Ο **terminal** είναι διαρκές μοτίβο: το «portal» κάθε lesson είναι ένα pixel-art τερματικό.

---

## 5. Backend architecture

- **FastAPI + Pydantic v2 + SQLAlchemy 2.0 (sync) + Alembic + pytest.**
  - *Sync αντί για async SQLAlchemy*: το workload είναι CRUD με μικρά queries. Τα sync endpoints τρέχουν σε threadpool, με απλούστερα tests και λιγότερα pitfalls (lazy loading, session scope). Τα WebSockets του terminal ανήκουν στο sandbox gateway, όχι στο API. Η επανεξέταση γίνεται αν μετρηθεί πρόβλημα.
- **Domain modules** (bounded contexts), καθένα με `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`:
  - `auth`: users, sessions, password hashing, CSRF.
  - `content`: tracks, modules, lessons, exercises, commands, sources (read-only από API). Περιλαμβάνει και τον **importer**.
  - `learning`: lesson flow, exercise delivery (χωρίς σωστές απαντήσεις), attempt submission.
  - `evaluation`: evaluator registry και evaluators. **Χωρίς DB, χωρίς FastAPI imports.**
  - `progression`: mastery, XP ledger, achievements, streaks, unlocks, recommendations.
  - `paths`: learning paths και enrollment.
  - `sandbox` (Phase 2): client προς το gateway. Ποτέ δεν εκτελεί τίποτα locally.
- **Κανόνας εξαρτήσεων**: `router → service → repository/models`. Το `evaluation` δεν εξαρτάται από κανένα άλλο domain. Το `progression` ενημερώνεται μέσω **in-process domain events** (`AttemptEvaluated`, `LessonCompleted`) και όχι με απευθείας κλήσεις από το `learning`. Αυτό κρατά το gamification αποσυνδεδεμένο από τη ροή μάθησης.
- **Config** με `pydantic-settings` από env vars. Secrets μόνο από env/secret store.

---

## 6. Database schema

Κανονικοποιημένα όσα κάνουμε join/query. Typed JSONB για type-specific δομές. Όλα τα content IDs είναι **stable slugs** από το YAML (π.χ. `linux.files.cp.copy-basic`), ώστε το re-import να είναι idempotent.

### 6.1 Content (γράφεται μόνο από τον importer)

```
source              id, slug, name, publisher, kind[official_manual|man_page|standard|project_docs],
                    base_url
citation            id, source_id→source, url, section, doc_version, last_verified (date),
                    subject_type[lesson|exercise|command|...], subject_id
                    -- polymorphic link· ή join tables ανά subject αν θέλουμε FK integrity

track               id(slug), title, biome, order
module              id(slug), track_id→track, title, summary, order, map_x, map_y
lesson              id(slug), module_id→module, title, level[beginner|intermediate|advanced],
                    est_minutes, body_html (sanitized), body_md, order,
                    content_hash, version
skill               id(slug), track_id, title, description
skill_prerequisite  skill_id, requires_skill_id                       -- DAG, cycle-checked στο import
lesson_skill        lesson_id, skill_id
module_prerequisite module_id, requires_module_id                     -- map unlock edges

exercise            id(slug), lesson_id (nullable για standalone/assessment), type, level,
                    cognitive_level[recognize|apply|combine|troubleshoot|scenario],
                    prompt_html, spec JSONB (type-specific), content_hash, version, is_active
exercise_version    exercise_id, version, content_hash, spec JSONB, created_at   -- immutable history
exercise_skill      exercise_id, skill_id, weight
exercise_command    exercise_id, command_id

command             id(slug, π.χ. "cp"), name, kind[shell_builtin|external_utility|
                    shell_keyword|cli_subcommand], provider (π.χ. "GNU coreutils", "bash",
                    "util-linux", "iproute2", "procps-ng", "systemd", "Docker CLI", "kubectl"),
                    platform[gnu-linux|posix|docker|kubernetes], category, level,
                    spec JSONB (synopsis, options, examples, mistakes, when_not_to_use, output)
command_alias       command_id, alias                                    -- π.χ. "docker ps" ↔ "docker container ls"
command_relation    command_id, related_command_id, relation[related|confused_with|replaces|see_also]

learning_path       id(slug), title, description, order
learning_path_step  path_id, position, module_id
achievement         id(slug), title, description, icon, rule JSONB (declarative)
```

### 6.2 User data

```
user                id (uuid), email (unique, citext), display_name, password_hash (argon2id),
                    role[learner|author|admin], created_at, is_active
session             id (random 256-bit, hashed at rest), user_id, created_at, expires_at,
                    last_seen_at, ip, user_agent

attempt             id, user_id, exercise_id, exercise_version, submitted JSONB,
                    outcome[correct|incorrect|partial|invalid], score (0..1),
                    matched_rule (π.χ. "accepted[1]" / "mistake:mv-instead-of-cp"),
                    hints_used, duration_ms, created_at
                    INDEX (user_id, exercise_id, created_at)
lesson_progress     user_id, lesson_id, status[started|completed], started_at, completed_at
skill_mastery       user_id, skill_id, score (0..1), evidence_count, last_evidence_at
xp_event            id, user_id, amount, reason, source_type, source_id, created_at
                    UNIQUE (user_id, source_type, source_id, reason)   -- anti double-award
user_achievement    user_id, achievement_id, unlocked_at
activity_day        user_id, day (date)                                 -- streak υπολογίζεται από εδώ
path_enrollment     user_id, path_id, enrolled_at, is_primary

-- Phase 2
sandbox_session     id, user_id, exercise_id, status, runner_host, created_at, expires_at,
                    ended_at, end_reason
```

Σημειώσεις:
- Τα **σύνολα XP, level και streak είναι derived** (από `xp_event`, `activity_day`) και μπορούν να γίνουν cache σε `user_stats`. Ο ledger είναι auditable και επαναϋπολογίσιμος.
- Το **`exercise_version`** επιτρέπει διόρθωση ενός exercise χωρίς να αλλοιωθεί η ερμηνεία παλιών attempts.
- Οι πίνακες `Questions/Answers` απορροφώνται στο `exercise.spec`. Τα **Levels** είναι enum attribute και όχι πίνακας.

---

## 7. Educational content model

### 7.1 Αρχεία

```
content/
  sources.yaml                         # registry επίσημων πηγών
  paths/
    linux-fundamentals.yaml
  tracks/
    linux/
      track.yaml                       # title, biome, skills (DAG)
      modules/
        files-and-directories/
          module.yaml                  # metadata, prerequisites, map position
          lessons/
            010-copying-files.md       # frontmatter + σύντομη θεωρία (Markdown)
          exercises/
            copy-basic.yaml
  commands/
    linux/cp.yaml
    linux/cd.yaml
  achievements.yaml
```

### 7.2 Lesson: μικρό και focused

Κάθε lesson έχει **ένα learning objective**, 3–7 λεπτά θεωρίας και 3–8 exercises. Η ροή:
`Hook (πρόβλημα) → Concept → Worked example → Knowledge check → Practice → Mini-scenario`.
Το lesson **ξεκινά από πρόβλημα** («Θέλεις backup του config πριν το αλλάξεις»), όχι από command. Αυτό εφαρμόζει στην πράξη τη φιλοσοφία του project.

```markdown
---
id: linux.files.copying-files
title: Copying files safely
level: beginner
objective: Create a copy of a file without modifying the original
skills: [linux.files.copy]
commands: [cp, mv]
exercises: [copy-basic, copy-select, copy-write, copy-overwrite-scenario]
citations:
  - source: gnu-coreutils
    url: https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html
    doc_version: "coreutils 9.x"
    last_verified: 2026-10-06
---
Before you edit `nginx.conf`, you want a backup...
```

### 7.3 Source hierarchy (primary source of truth ανά είδος)

| Τι | Primary | Secondary |
|---|---|---|
| Shell builtins & syntax (`cd`, `export`, pipes, redirection) | GNU Bash Reference Manual, POSIX (Open Group) | `bash(1)` |
| GNU utilities (`cp`, `ls`, `grep`, `sed`, `find`) | GNU manuals (coreutils, grep, sed, findutils) | man-pages (man7.org) |
| util-linux, procps, iproute2, systemd | Project man pages / upstream docs | man7.org |
| Kernel concepts (namespaces, cgroups, /proc, signals) | docs.kernel.org + man-pages section 2/7 | — |
| Docker | docs.docker.com (CLI ref, Dockerfile ref, Compose, Engine) | — |
| Kubernetes | kubernetes.io/docs (Concepts, Tasks, kubectl, API ref), **pinned minor version** | — |

Blogs, Medium και Stack Overflow **δεν** επιτρέπονται ως `source`. Το lint απορρίπτει URL εκτός allowlist domains.

### 7.4 Command reference entry

```yaml
id: cp
name: cp
kind: external_utility
provider: GNU coreutils
platform: gnu-linux
category: linux/file-management
level: beginner
summary: Copy files and directories.
synopsis:
  - "cp [OPTION]... [-T] SOURCE DEST"
  - "cp [OPTION]... SOURCE... DIRECTORY"
  - "cp [OPTION]... -t DIRECTORY SOURCE..."
options:
  - { flags: ["-r", "-R", "--recursive"], summary: Copy directories recursively, level: beginner }
  - { flags: ["-i", "--interactive"], summary: Prompt before overwrite, level: beginner }
  - { flags: ["-a", "--archive"], summary: Preserve structure and attributes (recursive), level: intermediate }
examples:
  - cmd: cp old.txt new.txt
    explain: { cp: command, old.txt: source, new.txt: destination }
common_mistakes:
  - wrong: mv old.txt new.txt
    why: Renames/moves the file; no copy is created.
  - wrong: cp mydir backup
    why: Without -r, GNU cp refuses to copy a directory ("-r not specified; omitting directory").
when_not_to_use:
  - Large tree syncs or remote copies — consider rsync.
related: [{ id: mv, relation: confused_with }, { id: rm }, { id: mkdir }, { id: touch }]
citations:
  - { source: gnu-coreutils, url: ".../cp-invocation.html", doc_version: "9.x", last_verified: 2026-10-06 }
```

> Το παράδειγμα «cp mydir backup» και το μήνυμα λάθους **πρέπει να επαληθευτούν** σε πραγματικό GNU/Linux container πριν δημοσιευτούν (βλ. §7.6).

### 7.5 Distractor metadata

```yaml
options:
  - text: cp old.txt new.txt
    correct: true
  - text: mv old.txt new.txt
    correct: false
    distractor: { existence: exists, issue: wrong_semantics, command: mv }
    why: mv moves/renames; the original disappears.
  - text: rename old.txt new.txt
    correct: false
    distractor: { existence: exists, issue: wrong_semantics, command: rename,
                  note: "util-linux rename replaces a substring in names of the listed files; with no files it does nothing" }
  - text: copy old.txt new.txt
    correct: false
    distractor: { existence: nonexistent, platform_note: "copy is a Windows cmd command, not a standard Unix utility" }
```

Ταξινομία `existence`: `exists` | `nonexistent` | `platform_specific`. Ταξινομία `issue`: `wrong_semantics` | `wrong_syntax` | `wrong_flag` | `dangerous`.
Το lint απαιτεί **κάθε `nonexistent` να έχει τεκμηρίωση** (και, όταν υπάρχει sandbox, CI check ότι το `command -v copy` αποτυγχάνει στο image). Αυτό ικανοποιεί την απαίτηση «όχι τυχαίες ή παραπλανητικές εντολές».

### 7.6 Ποιότητα content
- **Schema validation** (Pydantic, τα ίδια models με το backend).
- **Lint**: allowlisted source domains, `last_verified` ≤ 12 μήνες (≤ 4 για K8s), ύπαρξη referenced commands/skills, DAG χωρίς κύκλους, 3–5 options ανά MCQ, `why` σε κάθε distractor.
- **Executable examples (Phase 2)**: τα `examples` με `verify: true` τρέχουν σε CI μέσα στο ίδιο image με το sandbox και συγκρίνονται με το δηλωμένο `expected_output`.

---

## 8. Exercise model

Κοινά πεδία για όλους τους τύπους:
```yaml
id: linux.files.copy-write
type: command_writing
level: beginner
cognitive_level: apply
skills: [{ id: linux.files.copy, weight: 1.0 }]
commands: [cp]
prompt: "Create a copy of `old.txt` named `new.txt` in the current directory."
hints:                       # προοδευτικά· κάθε hint μειώνει το XP
  - Which command duplicates a file without removing the original?
  - "Syntax: cp SOURCE DEST"
feedback:                    # εμπλουτίζεται αυτόματα από command reference
  explanation: "`cp` copies files; the source is unchanged."
  reference: cp
spec: { ... type-specific ... }
citations: [...]
```

Τύποι (`spec` ως Pydantic discriminated union):

| type | spec (σύνοψη) | MVP |
|---|---|---|
| `multiple_choice` | options[] με distractor metadata, `multi_select` | ✅ |
| `command_selection` | όπως MCQ, options = commands | ✅ |
| `fill_in_command` | `template: "____ old.txt new.txt"`, `blanks: [{accepted: [cp]}]` | ✅ |
| `command_writing` | `accepted[]`, `known_mistakes[]`, `normalization`, `test_cases` (§9) | ✅ |
| `ordering` | steps[] με σωστή σειρά (π.χ. troubleshooting flow) | ✅ (φθηνό, υψηλή εκπαιδευτική αξία) |
| `output_analysis` | πραγματικό captured output, ερώτηση MCQ/short answer | ✅ (με MCQ answer) |
| `scenario` | multi-step: context → διαδοχικές αποφάσεις (MCQ/ordering/command) με branch feedback | ⏳ late MVP / P2 |
| `configuration` / `debugging` | αρχείο (Dockerfile/YAML), `checks[]` (structured: parse YAML → assertions) | P2/P3 |
| `hands_on` | sandbox image, setup, `checks[]` state assertions, timeout | P2+ |

**Το `scenario` είναι ο τύπος που υλοποιεί τη φιλοσοφία** («A service is running but users cannot access it on port 8080»). Προτείνω να μπει απλή εκδοχή ήδη στο τέλος του MVP: σειρά MCQ/ordering βημάτων πάνω σε captured outputs. Δεν χρειάζεται sandbox.

---

## 9. Evaluation architecture

```python
# Σχηματικά — όχι implementation
class EvaluationResult(BaseModel):
    outcome: Literal["correct", "incorrect", "partial", "invalid"]
    score: float                      # 0..1
    matched_rule: str | None          # "accepted[0]", "mistake:mv-instead-of-cp"
    feedback: list[FeedbackItem]      # structured: why, syntax, breakdown, related, mistake

class Evaluator(Protocol[SpecT, SubmissionT]):
    def evaluate(self, spec: SpecT, submission: SubmissionT, ctx: EvalContext) -> EvaluationResult: ...

REGISTRY: dict[ExerciseType, Evaluator] = {...}   # MultipleChoice, Command, Text, Ordering,
                                                   # Output, Configuration, Terminal, Docker, Kubernetes
```

- **Pure & deterministic**: ίδιο input, ίδιο output. Χωρίς DB και I/O. Τα sandbox evaluators (`Terminal`, `Docker`, `Kubernetes`) παίρνουν `SandboxClient` μέσω `ctx` και αξιολογούν **structured state reports**, όχι raw text.
- **Το feedback συντίθεται** από: (1) τον κανόνα που ταίριαξε (π.χ. known mistake), (2) το exercise feedback, (3) το command reference (synopsis, breakdown, related). Έτσι παράγεται το πλούσιο feedback της §8 χωρίς copy-paste σε κάθε exercise.
- **Σωστές απαντήσεις δεν φεύγουν ποτέ προς τον client πριν το submit.** Το API σερβίρει ένα «public view» του spec.

### CommandEvaluator: command-aware, όχι «έξυπνος»

Pipeline:
1. **Parse** με POSIX shell lexing (`shlex` σε posix mode, με punctuation chars). Δεν εκτελείται τίποτα.
2. **Reject unsupported constructs** ανά exercise (`allow: [pipe, redirect]`). Subshells, `;`, `&&`, backticks και `$( )` απορρίπτονται με σαφές μήνυμα, εκτός αν επιτρέπονται ρητά.
3. **Normalize με βάση το command reference** του συγκεκριμένου command:
   - διάσπαση συνδυασμένων short flags (`-rf` → `-r -f`) **μόνο** για commands που δηλώνουν getopt-style grammar,
   - long ↔ short aliases (`--recursive` ≡ `-r` ≡ `-R` για GNU `cp`), **όπως δηλώνονται στο YAML**,
   - flags order-insensitive, positionals order-sensitive,
   - προαιρετικά ανά exercise: `./old.txt` ≡ `old.txt`, trailing slash σε directories.
4. **Match** με τη σειρά: `known_mistakes` (για στοχευμένο feedback) → `accepted` → default `incorrect` με γενικό feedback και «συγκρίνετε με τη σύνταξη».
5. Ο **χρήστης μπορεί να κάνει report** «νομίζω ότι η απάντησή μου είναι σωστή». Αυτό δημιουργεί content issue. Οι απορρίψεις σωστών εναλλακτικών λύνονται με προσθήκη στο `accepted`, όχι με χαλάρωση του evaluator.

```yaml
spec:
  accepted:
    - "cp old.txt new.txt"
    - "cp -- old.txt new.txt"
    - "cp -i old.txt new.txt"          # επιτρεπτό, με σημείωση
  known_mistakes:
    - match: "mv old.txt new.txt"
      id: mv-instead-of-cp
      feedback: "mv would rename the file — the original would no longer exist."
    - match: "cp new.txt old.txt"
      id: reversed-args
      feedback: "SOURCE comes first, DEST second."
  test_cases:                          # τρέχουν στο CI για ΚΑΘΕ exercise
    accept: ["cp old.txt new.txt", "cp  old.txt   new.txt", "cp ./old.txt new.txt"]
    reject: ["cp new.txt old.txt", "copy old.txt new.txt", "cp old.txt", "cp old.txt new.txt; rm old.txt"]
```

**Γιατί όχι generic semantic equivalence**: το αν δύο εντολές είναι ισοδύναμες εξαρτάται από filesystem state, aliases, locale και υλοποίηση (GNU vs BSD). Η ρητή δήλωση στο content και τα test cases είναι ο μόνος τρόπος να **αποδείξεις** ότι ο evaluator δεν διδάσκει λάθος. Η πραγματική σημασιολογική ορθότητα έρχεται με το sandbox (state-based).

### Testing των evaluators
- Unit tests ανά evaluator (parametrized, edge cases: quoting, unicode, κενά, κενό input, τεράστιο input).
- **Property-based tests** (Hypothesis): ο normalizer είναι idempotent, το flag reordering δεν αλλάζει το αποτέλεσμα, η αλλαγή σειράς positionals το αλλάζει.
- **Content-driven tests**: κάθε `test_cases` block κάθε exercise εκτελείται στο CI. Ένα exercise που αποτυγχάνει δεν γίνεται merge.

---

## 10. Command reference architecture

- **Ένα YAML ανά command** (§7.4), import σε `command` + `command_relation` + `citation`.
- Το `kind` και ο `provider` εμφανίζονται στο UI ως badges («shell builtin · bash», «GNU coreutils»). Ο χρήστης μαθαίνει τη διάκριση kernel / GNU / shell / distro.
- **Αναζήτηση**: PostgreSQL full-text (`tsvector` σε name, summary, options) + `pg_trgm` για typo-tolerance (`chmdo` → `chmod`). Χωρίς Elasticsearch.
- **Bi-directional links**: command ↔ lessons ↔ exercises («Practice this command» → exercises με αυτό το command και την τρέχουσα mastery).
- **Ταξινόμηση**: `category` (`linux/file-management`, `docker/containers`, `kubernetes/workloads`) και `level`. Η ιεραρχία της §12 προκύπτει από τα categories και δεν είναι hardcoded.
- Docker/kubectl subcommands: `id: docker-container-run`, `name: "docker container run"`, `command_alias: "docker run"`.

---

## 11. Progression / RPG architecture

**Διάκριση:** *Mastery = τι ξέρεις. XP = πόσο προσπάθησες. Unlocks βασίζονται μόνο σε mastery.*

### Mastery (ανά skill)
- MVP: **weighted, recency-biased score**. Κάθε evaluated attempt είναι evidence με βάρος `exercise_skill.weight × cognitive_level_weight` (recognize 0.5 → scenario 2.0). Μετράει μόνο το **πρώτο attempt** ανά exercise ανά «γύρο», ώστε το retry μέχρι να βγει σωστό να μη φουσκώνει το score. Τα hints μειώνουν το evidence.
- Το score είναι εκθετικός κινητός μέσος (π.χ. α = 0.3) με ελάχιστο `evidence_count` πριν εμφανιστεί ως «mastered».
- Αργότερα: Bayesian Knowledge Tracing ή spaced repetition (decay με τον χρόνο, επανεμφάνιση exercises), χωρίς αλλαγή schema.
- Τα «Weak topics» είναι skills με χαμηλό score και επαρκές evidence. Το «Recommended next» βγαίνει από deterministic κανόνες: (1) weak skill με διαθέσιμα exercises, (2) επόμενο lesson στο primary path του οποίου τα prerequisites είναι mastered.

### XP
- Ledger (`xp_event`) με **unique constraint** ανά source: XP για ένα exercise **μία φορά**. Bonus για πρώτη επιτυχία χωρίς hints, για υψηλό `cognitive_level`, για ολοκλήρωση module assessment.
- Character level = f(total XP), καμπύλη ~`100·n^1.5`. Είναι **κοσμητικό**: τίτλοι («Shell Apprentice» → «Kernel Ranger»), cosmetics, avatar items.

### Zones / unlocks
- Ένα module ξεκλειδώνεται όταν τα prerequisite modules έχουν περάσει το **module assessment** (π.χ. ≥ 80% σε mixed-exercise set) **ή** όταν τα αντίστοιχα skills έχουν mastery ≥ threshold.
- Το **"Skip ahead" test** επιτρέπει σε έμπειρους χρήστες να ξεκλειδώσουν ζώνες με assessment, για να μη βαριούνται.

### Achievements
- Δηλωτικοί κανόνες σε YAML (`rule: {type: skill_mastery, skill: linux.permissions.*, gte: 0.9}`, `{type: streak, gte: 7}`, `{type: first_try_scenarios, gte: 5}`). Ένας μικρός rule engine τους αξιολογεί σε domain events. Χωρίς κώδικα ανά achievement.
- Αποφεύγονται achievements που ανταμείβουν όγκο χωρίς ποιότητα («answer 1000 questions»).

### Streaks
- Από `activity_day`. Ήπια λογική (π.χ. 1 «freeze» την εβδομάδα): τα σκληρά streaks προκαλούν άγχος και churn.

---

## 12. Sandbox strategy

**Phase 1 (MVP): κανένα execution.** Static evaluation και captured outputs.

**Phase 2: Linux sandbox**
- Ξεχωριστό **Sandbox Gateway** service σε **ξεχωριστό host/VM** από API και DB. Το API του ζητά session με mTLS ή signed service token. Ο browser συνδέεται στο gateway με **short-lived, single-use, exercise-scoped token** (WSS).
- Runtime: **gVisor (`runsc`)** πάνω σε **rootless** container engine. Defense in depth ανά container:
  - `--cap-drop ALL`, `--security-opt no-new-privileges`, default seccomp, AppArmor/SELinux profile,
  - non-root user μέσα στο container και user namespace remapping,
  - `--read-only` rootfs + `--tmpfs` για home/tmp με μέγεθος όριο,
  - cgroup v2 limits: `memory.max` (π.χ. 256 MiB, χωρίς swap), `cpu.max` (π.χ. 0.5 CPU), `pids.max` (π.χ. 128), `io.max`,
  - `--network none` (τα Linux lessons δεν χρειάζονται δίκτυο· για networking labs, isolated per-session bridge **χωρίς egress**),
  - idle timeout (π.χ. 10′), hard TTL (π.χ. 45′), max concurrent sessions ανά χρήστη = 1, global capacity cap,
  - **reaper** που καθαρίζει orphaned containers ανεξάρτητα από το gateway,
  - minimal, pinned, signed image (Debian stable slim + τα εργαλεία του lesson), χωρίς secrets ή cloud metadata access (block 169.254.169.254).
- **Verification**: ο runner εκτελεί **δηλωμένα checks** (π.χ. `path_is_dir: /tmp/logs`, `file_mode: {path, mode}`, `process_running`, `port_listening`) μέσα στο sandbox, μέσω αξιόπιστου helper binary, και επιστρέφει **structured JSON**. Τα checks είναι authored content και δεν παράγονται από χρήστη.
- Όλο το terminal I/O καταγράφεται (για abuse detection και debugging) με retention policy.

**Phase 3: Docker & Kubernetes labs**
- Χρειάζονται nested container runtime, άρα **microVM ανά session** (Firecracker ή Kata Containers). Μέσα σε αυτό, rootless Docker ή `kind`/`k3s`. Το VM boundary είναι το security boundary. Ποτέ `--privileged` σε shared host.
- K8s: cluster ανά session μέσα στο microVM. Το namespace-per-user σε shared cluster **δεν** είναι αρκετό boundary για untrusted users, ακόμη και με Restricted PSS, NetworkPolicy και ResourceQuota.
- Verification μέσω Kubernetes API (π.χ. `Deployment.status.readyReplicas == 3`, Service selector ταιριάζει με pods) και όχι με parsing του `kubectl` output.
- Κόστος: τα microVMs θέλουν bare-metal ή nested-virt hosts. Αυτό είναι **επιχειρηματική απόφαση** και πρέπει να ληφθεί πριν το Phase 3.

---

## 13. Security model

| Περιοχή | Μέτρα |
|---|---|
| Authentication | Email + password (**argon2id**). Server-side sessions σε **HttpOnly, Secure, SameSite=Lax** cookie. Session rotation στο login, idle + absolute expiry. **Όχι JWT σε localStorage** (XSS → token theft). |
| CSRF | Double-submit token header σε όλα τα state-changing requests (+ SameSite). |
| Authorization | Roles `learner/author/admin`. Ownership checks σε κάθε user-scoped query, μέσω repository που απαιτεί `user_id` (προστασία από IDOR). |
| Input validation | Pydantic σε όλα τα inputs, μέγιστα μεγέθη (π.χ. command ≤ 1 KB, config ≤ 64 KB), strict enums. |
| XSS | Markdown → HTML **στο import** με sanitizer allowlist (π.χ. `nh3`). Ο client κάνει `textContent` για user data, ποτέ `innerHTML` με user input. Αυστηρό **CSP** (`script-src 'self'`, χωρίς inline). |
| Rate limiting | Στο proxy και στο app: login/register (ανά IP και account), submissions ανά λεπτό, sandbox session creation ανά ώρα. Account lockout με backoff. |
| Answer leakage | Τα σωστά specs δεν σερβίρονται ποτέ πριν το submit. Το evaluation γίνεται μόνο server-side. |
| Secrets | Env/secret store, ποτέ στο repo. `.env.example` χωρίς τιμές. Secret scanning στο CI. |
| Containers (εφαρμογής) | Non-root images, pinned digests, minimal base, `read_only` όπου γίνεται, image scanning στο CI. **Το API container δεν έχει ποτέ πρόσβαση στο `/var/run/docker.sock`**: όποιος έχει το socket έχει root στον host. |
| Sandbox | §12. Threat model: ο χρήστης είναι **κακόβουλος**. Στόχοι: escape στον host, lateral movement, crypto-mining, outbound abuse (spam/DDoS), resource exhaustion, data από άλλα sessions. |
| Logging/Audit | Structured logs, χωρίς passwords/tokens. Audit log για admin/content actions. |
| Dependencies | Lock files (uv/pip-tools), Dependabot/Renovate, `pip-audit`. |

---

## 14. MVP scope

**Στόχος MVP**: να αποδείξει ότι ο συνδυασμός «μικρό lesson → εύστοχο exercise → πλούσιο feedback → mastery → ξεκλείδωμα ζώνης» είναι **ελκυστικός και εκπαιδευτικά σωστός**.

- **Linux track, Beginner**, 4 modules: *Navigating the Filesystem* (pwd, ls, cd, paths), *Files & Directories* (mkdir, touch, cp, mv, rm, cat), *Viewing & Finding* (less, head, tail, find basics), *Permissions basics* (ls -l, chmod, users/groups intro).
- ~16 lessons, ~100–120 exercises, ~25 command reference entries, όλα με citations.
- Exercise types: `multiple_choice`, `command_selection`, `fill_in_command`, `command_writing`, `ordering`, `output_analysis` (MCQ), και **απλό `scenario`** (1 ανά module ως «boss fight»).
- Auth (register/login/logout), progress, attempts, mastery, XP ledger, ~10 achievements, streak.
- Learning path: «Linux Fundamentals» (μόνο τα beginner modules).
- UI: World map (Linux biome + «locked» silhouettes των άλλων), Dashboard, Lesson, Quiz/Practice (ενιαίο exercise player), Command Reference με search, Profile.
- Content pipeline: YAML/MD, validate, lint, import CLI, test cases στο CI.
- Docker Compose: `proxy` + `api` + `db`. Ένα `make dev`.
- Tests: unit (evaluators, mastery, XP rules), API (auth, attempts, ownership), content validation, integration (import → serve → attempt → progression).

## 15. Ρητά ΕΚΤΟΣ MVP

- Οποιοδήποτε command execution, simulated terminal ή xterm.js.
- Docker, Kubernetes, Networking, Cloud tracks (μόνο locked placeholders στο map).
- Configuration/debugging exercises πάνω σε αρχεία.
- AI/LLM οτιδήποτε.
- OAuth/SSO, email verification flows πέρα από τα βασικά, password reset μέσω email (μπορεί admin reset).
- Authoring UI. Το content γράφεται σε YAML στο git.
- Leaderboards/social. Ανταγωνισμός σε learning platform συχνά αποθαρρύνει beginners. Αν ποτέ μπει, opt-in.
- Spaced repetition / adaptive engine (το schema το επιτρέπει αργότερα).
- i18n infrastructure. Το content του MVP γράφεται **στα Ελληνικά** (§ Αποφάσεις). Το schema αφήνει χώρο για `locale` αργότερα.
- Kubernetes/production deployment της ίδιας της πλατφόρμας.
- Mobile-native app (το web πρέπει να είναι απλώς responsive).

---

## 16. Recommended directory structure

```
shellcraft/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── migrations/
│   ├── app/
│   │   ├── main.py                 # app factory, router mounting, middleware
│   │   ├── core/                   # config, db session, security primitives, events bus, errors
│   │   ├── auth/                   # models, schemas, service, router, csrf
│   │   ├── content/                # models (track, module, lesson, exercise, command, source)
│   │   │   ├── schemas/            # Pydantic content schemas — shared με importer & lint
│   │   │   ├── importer.py
│   │   │   ├── repository.py
│   │   │   └── router.py           # read-only content + command reference search
│   │   ├── learning/               # exercise delivery (public views), attempt submission
│   │   ├── evaluation/             # ΚΑΘΑΡΟ: χωρίς DB/FastAPI imports
│   │   │   ├── base.py  registry.py  feedback.py
│   │   │   ├── shell/              # lexer wrapper, normalizer, flag grammar
│   │   │   └── evaluators/         # multiple_choice.py command.py ordering.py output.py ...
│   │   ├── progression/            # mastery.py xp.py achievements.py streaks.py recommend.py
│   │   ├── paths/
│   │   └── sandbox/                # (P2) client μόνο
│   ├── cli/                        # `content validate|lint|import`, admin tasks
│   └── tests/
│       ├── unit/  api/  integration/  content/
│       └── conftest.py
├── frontend/                       # (§4)
├── content/                        # (§7.1) — μπορεί αργότερα να γίνει ξεχωριστό repo
├── sandbox/                        # (P2) gateway service, runner, images, checks helper
├── deploy/
│   ├── compose.yaml                # proxy + api + db (+ sandbox profile αργότερα)
│   ├── Caddyfile
│   └── docker/  api.Dockerfile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONTENT_GUIDE.md            # πώς γράφεται lesson/exercise, style, distractors, πηγές
│   └── adr/                        # Architecture Decision Records
├── Makefile
└── .github/workflows/              # lint, test, content-validate, image scan
```

**Γιατί domain-oriented και όχι layer-oriented**: ένα feature («achievements») ζει σε έναν φάκελο. Τα όρια (π.χ. «το evaluation δεν ξέρει τη DB») γίνονται ορατά και ελέγξιμα με import-linter στο CI. Ένα module μπορεί να βγει σε service αργότερα χωρίς ξήλωμα.

---

## 17. Implementation roadmap

| Milestone | Περιεχόμενο | Exit criteria |
|---|---|---|
| **M0 — Foundations** | Repo layout, Compose (proxy/api/db), FastAPI skeleton, config, Alembic, pytest, CI (ruff, mypy, tests), ADRs για τις αποφάσεις αυτού του εγγράφου | `make dev` σηκώνει τα πάντα. Το CI είναι πράσινο. |
| **M1 — Content model & pipeline** | Pydantic content schemas, YAML loader, lint, importer, content tables. 1 module με ~5 lessons ως pilot | `content validate && content import` idempotent. Lint πιάνει λάθη. Tests. |
| **M2 — Evaluation engine** | MCQ, command selection, fill-in, ordering, output (MCQ), CommandEvaluator με normalizer, feedback composer, content `test_cases` runner | Υψηλό coverage στο `evaluation/`. Property tests. Όλα τα test cases του pilot περνούν. |
| **M3 — Auth & learning API** | Register/login/sessions/CSRF, exercise public views, attempts, lesson progress, rate limiting | API tests για ownership/IDOR, CSRF, rate limits. Καμία διαρροή απαντήσεων (test). |
| **M4 — Progression** | Domain events, mastery, XP ledger, achievements engine, streaks, unlock rules, recommendations | Deterministic progression tests (σενάρια χρηστών → αναμενόμενη κατάσταση). |
| **M5 — Frontend** | Design tokens και visual language, router, exercise player + feedback panel, lesson view, command reference, dashboard, profile, SVG world map (Linux biome) | Πλήρης ροή χρήστη end-to-end. Keyboard navigable. Reduced-motion. Lighthouse a11y ≥ 90. |
| **M6 — MVP content & polish** | Υπόλοιπα 3 modules, scenarios («boss fights»), achievements, playtest με 3–5 πραγματικούς beginners | Το feedback των playtesters οδηγεί σε content fixes. Release. |
| **P2** | Sandbox gateway (gVisor), xterm.js, hands-on exercises, executable examples στο CI, intermediate Linux, Networking track | Threat model review. Escape/exhaustion tests (fork bomb, OOM, disk fill, egress). Load test. |
| **P3** | microVM labs, Docker track + labs, Kubernetes track + labs (pinned K8s version) | Infra cost model εγκεκριμένο. Security review. |
| **P4** | Cloud, advanced troubleshooting dungeons, spaced repetition/adaptive, optional AI hints (feature-flagged, grounded σε citations) | Η πλατφόρμα λειτουργεί πλήρως με το AI απενεργοποιημένο. |

---

## Αποφάσεις

| # | Θέμα | Απόφαση | Ημερομηνία |
|---|---|---|---|
| D1 | Γλώσσα content | **Ελληνικά.** Εξηγήσεις, θεωρία, prompts, feedback και UI στα ελληνικά. Commands, flags, options, outputs, error messages και αναφορές σε τεχνικούς όρους (π.χ. *source*, *destination*, *namespace*, *Pod*) παραμένουν **όπως στις επίσημες πηγές** (αγγλικά), γιατί αυτά θα συναντήσει ο χρήστης στο πραγματικό σύστημα και στο `man`. Το πρώτο εμφάνισμα ενός όρου δίνει και ελληνική απόδοση. Οι citations δείχνουν στις αγγλικές επίσημες πηγές. | 2026-10-06 |
| D2 | Target distro | **Debian stable.** Όλο το Linux content (outputs, error messages, διαθέσιμα εργαλεία, `rename` variant) επαληθεύεται σε pinned Debian stable image, το ίδιο που θα χρησιμοποιήσει το sandbox στο Phase 2. Τα content items δηλώνουν `platform: debian-<version>` όπου η συμπεριφορά διαφέρει ανά distro. | 2026-10-06 |
| D3 | Hosting Phase 3 (microVMs) | **Αναβάλλεται** μέχρι πριν το P3. Δεν επηρεάζει MVP/P2. | — |

### Συνέπειες του D1 (Ελληνικά)
- Η αναζήτηση στο command reference χρειάζεται PostgreSQL full-text με ρύθμιση `simple` (δεν υπάρχει built-in ελληνικός stemmer) + `unaccent` για τόνους, ώστε το «δικαιωματα» να βρίσκει «δικαιώματα». Τα `pg_trgm` καλύπτουν typos.
- Τα fonts (pixel display και readable) πρέπει να έχουν **πλήρες ελληνικό glyph set**. Πολλά pixel fonts δεν το έχουν, οπότε αυτό είναι κριτήριο επιλογής.
- Τα `TextEvaluator` answers (σύντομες απαντήσεις) θέλουν normalization: πεζά, αφαίρεση τόνων, τελικό σίγμα.
- Το schema κρατά πεδίο `locale` (default `el`) ώστε να μπορεί αργότερα να προστεθεί αγγλική έκδοση χωρίς migration δεδομένων.

### Συνέπειες του D2 (Debian)
- Ποια υλοποίηση του `rename` υπάρχει στο Debian stable και με ποιο όνομα πρέπει να **επαληθευτεί στο image** πριν γραφτεί το αντίστοιχο exercise. Το ίδιο ισχύει για κάθε `nonexistent` distractor (`command -v copy` πρέπει να αποτυγχάνει).
- Τα outputs στα `output_analysis` exercises καταγράφονται από το ίδιο pinned image.

## Ανοιχτές αποφάσεις

1. **Content license**: αν το content γίνει open source (π.χ. CC BY-SA για το content, άλλο license για τον κώδικα).
2. **Hosting Phase 3**: βλ. D3.
