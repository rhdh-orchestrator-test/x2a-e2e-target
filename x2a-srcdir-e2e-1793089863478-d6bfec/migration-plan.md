# MIGRATION FROM CHEF TO ANSIBLE

The repository is a small Chef cookbook set centered on a `simple-nginx` cookbook and a local `cache` dependency. The migration scope is limited to package installation, service enablement/startup, a static web page, and a small set of Nginx-related attributes. No Berkshelf or Policyfile lock data is present, and no complex templates, handlers, users, firewall rules, certificates, or secrets were identified in the reviewed source. A focused migration can likely be completed in approximately 2–4 working days, including implementation, cross-platform testing, documentation, and handover; additional time may be required to resolve the intended version and role of the external `nginx` dependency.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning:

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Minimal Nginx web-server cookbook that installs the Nginx package, enables and starts its service, and writes a static welcome page to `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Key Features: Nginx package installation, service lifecycle management, root-owned static index page, default attributes for port 80, `www-data`, and automatic worker-process selection

- **cache**:
    - Description: Local cache dependency that installs Redis and ensures the `redis-server` service is enabled and running.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Redis package installation and service lifecycle management; no attributes, templates, or application-specific configuration were identified in the reviewed files

**CRITICAL PATH VERIFICATION:**
The paths above are taken directly from the repository tree. The root cookbook is represented by `metadata.rb`, `recipes/default.rb`, and `attributes/default.rb`; `cookbooks/cache` has its own `metadata.rb` and `recipes/default.rb`.

### Infrastructure Files

- `README.md`: Documents that this is a metadata-only dependency-strategy test cookbook. It identifies `cache` as a local dependency and `nginx` as an external dependency that is declared but not fetchable without Berkshelf or Policyfile tooling. Preserve this dependency rationale in the migration documentation.
- `metadata.rb`: Root Chef cookbook metadata for `simple-nginx`, including version `1.0.0`, Chef `>= 16.0`, supported Ubuntu `>= 18.04` and CentOS `>= 7.0`, and dependencies on `cache` and `nginx`. Use it as the authoritative source for scope and compatibility assumptions.
- `attributes/default.rb`: Defines `nginx` attributes for port `80`, user `www-data`, and `worker_processes` set to `auto`. These should become Ansible role defaults or variables, with explicit decisions about whether they are currently consumed by any configuration task.
- `recipes/default.rb`: Root cookbook implementation. Translate package, service, and file resources into Ansible tasks, using handlers or service tasks as appropriate.
- `cookbooks/cache/metadata.rb`: Local `cache` cookbook metadata, version `1.0.0`, Chef `>= 16.0`, and Ubuntu/CentOS support declarations.
- `cookbooks/cache/recipes/default.rb`: Installs `redis-server` and enables/starts `redis-server`. Translate this into a separate Redis role or a clearly separated dependency role.

## Target Details

- **Operating System**: The source explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. Ansible should initially target both Debian-family and Red Hat-family systems, with package/service variable mapping. The source does not establish a single exact distribution version. Redis and Nginx package names and service names must be validated on each supported target; in particular, `redis-server` is Debian-oriented and may differ on CentOS/RHEL.
- **Virtual Machine Technology**: Not specified. No virtualization, image-building, cloud-init, or guest-tools configuration was identified.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or provider-specific configuration was identified.

## Migration Approach

### Key Dependencies to Address

- **Chef >= 16.0**: Replace Chef client execution with Ansible Core and an agreed supported execution environment. Chef runtime compatibility is not required in the target, but the supported OS matrix must be retained.
- **Local `cache` cookbook**: Convert to a dedicated Ansible Redis role or dependency role. Call it before application/web configuration if the eventual workload requires Redis; for the currently reviewed recipe, it is an independent service dependency.
- **External `nginx` cookbook**: The root metadata declares `nginx`, but the repository contains no vendored implementation or version constraint. Determine whether it was intended to provide package/configuration behavior. Replace it with an internal Ansible Nginx role or a vetted Galaxy collection, avoiding duplicate package/service management with the migrated `simple-nginx` tasks.
- **Ubuntu/CentOS package and service abstractions**: Use Ansible facts and variables for package names, service names, document roots, and distribution-specific defaults. Do not assume the Debian package name or service naming works unchanged on CentOS/RHEL.
- **Chef resources**: Map `package` to `ansible.builtin.package` or distribution-specific package modules, `service` to `ansible.builtin.service`, and `file` to `ansible.builtin.copy`/`file` with owner, group, mode, and content preserved.

### Security Considerations

- **Service exposure**: Nginx is configured with port 80 in the attributes, but no firewall rule or TLS configuration is present. Decide whether the Ansible role should manage firewall exposure and document that the current behavior is HTTP-only.
- **File ownership and permissions**: Preserve the index file as owned by `root:root` with mode `0644`. Review whether a production deployment needs stricter content-management or immutable-file controls.
- **Redis hardening**: The cache cookbook only installs and starts Redis. It does not show bind-address restrictions, authentication, TLS, firewall controls, or persistence settings. Treat this as a security gap and require an explicit hardening baseline before production rollout; do not expose Redis broadly by default.
- **Nginx hardening**: No TLS certificates, security headers, access restrictions, rate limiting, or log-retention configuration were identified. The migration should not imply these controls exist; add them as separately approved requirements if this is production infrastructure.
- **Vault/secrets management**: No Chef encrypted data bags, Chef Vault references, hardcoded passwords, certificate material, or environment-variable secrets were visible in the reviewed files. The Ansible design should still establish Ansible Vault or an external secret manager for any future Redis credentials, TLS private keys, or application secrets.
- **Privilege management**: Package installation, service control, and writing under `/var/www/html` require elevated privileges. Use `become: true`, limit task scope, and test privilege boundaries in CI.

### Technical Challenges

- **Ambiguous external dependency**: The declared `nginx` cookbook is not present locally and has no version constraint. Resolve its intended responsibilities before implementation to prevent missing configuration or conflicting ownership between roles.
- **Cross-platform behavior**: The cookbook claims both Ubuntu and CentOS support, while package/service names and default paths may differ. Build a small OS-variable matrix and test at least one Ubuntu and one RHEL-compatible image.
- **Unused or partially specified attributes**: `nginx.port`, `nginx.user`, and `nginx.worker_processes` are defined, but the reviewed recipe only writes a fixed index page and does not render an Nginx configuration. Preserve them as documented defaults only if they are part of the desired target contract; otherwise mark them as legacy/unconsumed variables.
- **Dependency ordering and ownership**: Redis is a local dependency but is not referenced by the root recipe. Confirm whether it must run on the same host, on a separate host, or merely exists to test dependency discovery. Model this with inventory groups and role dependencies only after the deployment topology is agreed.
- **Idempotence and validation**: The Chef resources are inherently convergent, but the Ansible implementation should add syntax checks, idempotence tests, service health checks, and HTTP verification for the index page.
- **Production completeness**: The source is explicitly a simple metadata-only test fixture. Avoid treating the absence of firewall, TLS, monitoring, backup, and Redis security settings as evidence that they are unnecessary.

### Migration Order

1. **Repository and target contract**: Confirm the desired operating systems, deployment topology, whether Redis is required, and what the external `nginx` cookbook was expected to do. Establish Ansible inventory, collections, naming, and CI conventions.
2. **`cache` / Redis role**: Migrate the isolated package and service behavior first. Add distribution-specific variables and an explicit decision on Redis network binding and hardening.
3. **`simple-nginx` base role**: Migrate Nginx installation/service management and the static index file. Convert the reviewed attributes into role defaults only where they have an actual target use.
4. **Nginx dependency replacement and integration**: Resolve and replace the external `nginx` cookbook, consolidate ownership of configuration, and add any approved TLS/firewall/logging requirements.
5. **Cross-platform validation and handover**: Test Ubuntu and CentOS/RHEL-compatible targets, verify repeat runs are unchanged, document inventory/group variables, and retire or freeze the Chef implementation after operational sign-off.

### Assumptions

- The repository root is the `simple-nginx` Chef cookbook, despite the presence of a nested `cookbooks/` directory.
- `cookbooks/cache` is a distinct local cookbook and must be cataloged separately.
- The reviewed tree is complete; no Berksfile, Policyfile, lock file, templates, tests, or additional recipes were shown.
- `nginx` is an external dependency only; its implementation and version are unavailable in this repository.
- The requested migration covers the behavior visible in the reviewed metadata, attributes, and default recipes, not undocumented behavior from an external cookbook.
- Ubuntu and CentOS support declarations are compatibility intent, not proof that every release in those ranges has been tested.
- The `nginx` attributes may be legacy or intended for a configuration recipe that is not present; their target usage requires confirmation.
- Redis is installed on the same managed node only if the deployment owner confirms that topology; the source does not specify host separation.
- No secrets or certificates are present in the reviewed source, but future production requirements may introduce them.
- No cloud, virtualization, inventory, network, firewall, monitoring, backup, or release-pipeline requirements are specified.
- A 2–4 working-day estimate assumes one small team, no recovery of missing external cookbook behavior, and access to representative Ubuntu and CentOS/RHEL-compatible test hosts. Additional hardening or production integration will extend the timeline.
- Team coordination should assign separate owners for dependency/topology decisions, Ansible role implementation, cross-platform testing, and security review; changes should be reviewed jointly because package/service ownership overlaps with the unresolved external Nginx dependency.
