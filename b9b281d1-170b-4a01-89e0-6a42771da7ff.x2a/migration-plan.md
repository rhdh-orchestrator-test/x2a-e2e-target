# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef repository containing two independently identifiable cookbook modules: the root cookbook at `.` and the local `cache` cookbook at `cookbooks/cache`. The root cookbook installs and starts Nginx and publishes a static page; the cache cookbook installs and starts Redis. The migration is low complexity, with an estimated implementation and test effort of 2–4 engineer-days, or approximately 1–2 weeks when including CI, cross-platform validation, security review, and staged rollout.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. Every directory containing a Chef `recipes/default.rb` entrypoint in the supplied repository is listed separately below.

### MODULE INVENTORY

- **simple-nginx (root cookbook)**:
    - Description: Primary Chef cookbook that installs the Nginx package, enables and starts the Nginx service, and creates a root-owned static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Technology: Chef
    - Key Features: Nginx installation, service enablement and startup, static index-page deployment, default Nginx attributes for port `80`, user `www-data`, and worker processes `auto`
    - Entrypoint: `recipes/default.rb`
    - Migration complexity: Low; the recipe is short, but the declared Nginx attributes are not consumed by the reviewed recipe and require a parity decision.

- **cache**:
    - Description: Local Chef dependency cookbook that installs the Redis server package and enables and starts the Redis service.
    - Path: `cookbooks/cache`
    - Technology: Chef
    - Key Features: Redis package installation, Redis service enablement and startup
    - Entrypoint: `cookbooks/cache/recipes/default.rb`
    - Migration complexity: Low; package and service resources map directly to Ansible modules, subject to platform-specific names.

**CRITICAL PATH VERIFICATION:**

Both required Chef cookbook modules are separate inventory entries and their paths are confirmed by the supplied repository tree:

- Root cookbook module: `.` — existing repository root containing `recipes/default.rb`, `metadata.rb`, and `attributes/default.rb`.
- Cache cookbook module: `cookbooks/cache` — existing directory containing `recipes/default.rb` and `metadata.rb`.

No other directory in the supplied tree contains a Chef `recipes/default.rb`, Puppet `manifests/init.pp`, or PowerShell `.psd1` module manifest. The root cookbook and `cookbooks/cache` must not be combined into one entry because they have separate Chef entrypoints and metadata.

### Infrastructure Files

- `README.md`: Documents the metadata-only Chef dependency test and identifies `cache` as a local dependency and `nginx` as an external dependency. Convert this to Ansible role/playbook documentation.
- `metadata.rb`: Root cookbook metadata, Chef compatibility (`>= 16.0`), supported Ubuntu/CentOS versions, and dependencies on `cache` and `nginx`. Replace with Ansible role or collection metadata and explicit role dependencies.
- `attributes/default.rb`: Defines `nginx.port = 80`, `nginx.user = 'www-data'`, and `nginx.worker_processes = 'auto'`. Convert these to documented Ansible role defaults after deciding whether to implement the corresponding Nginx configuration.
- `recipes/default.rb`: Root cookbook convergence logic. Convert to an Ansible Nginx role task entrypoint, using `become: true` and handlers where configuration changes require a reload.
- `cookbooks/cache/metadata.rb`: Cache cookbook metadata and supported platforms. Replace with metadata for an Ansible Redis/cache role.
- `cookbooks/cache/recipes/default.rb`: Redis package and service convergence logic. Convert to a dedicated Redis/cache role.

### Target Details

- **Operating System**: Ubuntu `>= 18.04` and CentOS `>= 7.0` are declared. Validate at least one supported Ubuntu release and one RHEL-family release. Package, service, user, and document-root conventions may differ. If the target baseline is modern RHEL 9 or a current Ubuntu release, document that as a deliberate support change rather than silently preserving obsolete versions.
- **Virtual Machine Technology**: Not specified.
- **Cloud Platform**: Not specified. No cloud SDK, metadata endpoint, or provider-specific configuration appears in the supplied files.

## Migration Approach

### Key Dependencies to Address

- **Chef `>= 16.0`**: Replace Chef resources with idempotent Ansible tasks, role defaults, handlers, and platform variables.
- **Local `cache` dependency**: Convert `cookbooks/cache` into an internal `redis` or `cache` Ansible role. Invoke it explicitly from the deployment playbook only if Redis is actually required by the target workload.
- **External `nginx` dependency**: The root `metadata.rb` declares `nginx`, but the reviewed root recipe installs the Nginx package directly and does not show use of resources from that dependency. Verify whether it is legacy/test metadata; remove it if unnecessary, or replace it with an approved Ansible Galaxy role/internal role.
- **Package and service resources**: Map Chef `package` and `service` resources to `ansible.builtin.package`, `ansible.builtin.service` or `ansible.builtin.systemd`, and handlers.
- **Static page**: Map the Chef `file` resource to `ansible.builtin.copy` or `ansible.builtin.template`, preserving `/var/www/html/index.html`, root ownership, and mode `0644`.

### Security Considerations

- **Privilege escalation**: Package installation, service control, and writing under `/var/www/html` require administrative privileges. Use controlled `become: true` and least-privilege sudo rules.
- **File permissions**: Preserve root ownership and mode `0644`; prevent generated web content from becoming writable by the service account or other users.
- **Nginx exposure**: Port `80` is defined, but firewall rules, listener scope, TLS, authentication, rate limiting, and headers are absent from the reviewed files. Establish whether these are managed elsewhere and add them to the target security baseline.
- **Redis exposure**: The cache cookbook only starts Redis. It does not configure bind addresses, authentication, protected mode, TLS, persistence, or firewall rules. Treat Redis as unsafe for network exposure until it is bound appropriately and access controls are defined.
- **Secrets and vault management**: No Chef encrypted data bags, Chef Vault references, passwords, certificate material, or environment-variable secrets are visible in the reviewed files. If later requirements introduce credentials or TLS keys, store them in Ansible Vault or an approved external secrets manager rather than role defaults.
- **Package supply chain**: Define approved OS repositories, update policy, and package-version controls for Nginx and Redis.

### Technical Challenges

- **Unused attributes**: The root attributes define port, user, and worker-process values, but the reviewed recipe does not configure Nginx with them. Decide whether these are intended behavior or unused test data before claiming functional parity.
- **Cross-platform naming**: Ubuntu and CentOS/RHEL-family systems can use different Redis package/service names, service defaults, and web-user conventions. Use facts and explicit platform variables, then test on both families.
- **Chef dependency semantics**: Ansible requires explicit role dependencies and playbook ordering. Define whether Redis is mandatory, optional, or merely present to exercise dependency metadata.
- **Service idempotence**: Use handlers so Nginx reloads or Redis restarts only when relevant configuration changes. Test repeated playbook execution.
- **Limited repository context**: No Berksfile, Policyfile, lockfile, inventory, CI pipeline, firewall configuration, TLS configuration, or deployment topology is present. Integration requirements must be obtained from the owning team.

### Migration Order

1. Confirm the target OS baseline, external `nginx` dependency usage, Redis requirement, and intended meaning of the unused Nginx attributes.
2. Migrate and test the `cache` module at `cookbooks/cache` as a small Redis role, including secure binding and platform-specific package/service variables.
3. Migrate the root `simple-nginx` module at `.` into an Nginx role with package, service, and static-content tasks.
4. Implement Nginx configuration for port/user/worker-process values only if those attributes are confirmed as required behavior.
5. Compose the roles in an Ansible playbook, add Molecule or equivalent tests, validate repeated runs on Ubuntu and RHEL-family systems, then perform a canary rollout before retiring Chef.

### Assumptions

- The supplied tree is complete for this migration scope.
- The repository root `.` is the `simple-nginx` Chef cookbook because it contains the root `recipes/default.rb` and root `metadata.rb`.
- `cookbooks/cache` is a separate cookbook because it has its own `recipes/default.rb` and `metadata.rb`.
- The reviewed recipes represent the currently implemented behavior; external Chef roles, environments, run lists, and pipelines were not supplied.
- The declared external `nginx` dependency may be legacy or test metadata because the root recipe directly manages the Nginx package and service.
- The root recipe does not visibly invoke Redis, so the desired runtime relationship between `simple-nginx` and `cache` is ambiguous.
- No secrets, certificates, cloud provider, VM platform, monitoring, backup, HA, or firewall requirements are specified in the reviewed files.
- The timeline assumes access to Ubuntu and RHEL-family test hosts and to the team that owns the missing deployment context; undocumented dependencies may increase the estimate.
