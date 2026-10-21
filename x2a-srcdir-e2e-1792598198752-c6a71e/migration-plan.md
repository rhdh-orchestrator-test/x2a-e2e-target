# MIGRATION FROM CHEF TO ANSIBLE

This repository is a small Chef codebase containing two independently identifiable cookbooks: the root cookbook represented by `recipes/default.rb`, and the local `cache` cookbook represented by `cookbooks/cache/recipes/default.rb`. The migration is low complexity because the recipes use only Chef package, service, and file resources. Estimated implementation and basic validation effort is 1–3 working days, with additional time required for OS certification, CI integration, security review, and production rollout.

## Module Migration Plan

This repository contains Chef cookbooks that need individual migration planning. Each `recipes/default.rb` entrypoint is listed separately.

### MODULE INVENTORY

- **simple-nginx**:
    - Description: Root Chef cookbook that installs Nginx, enables and starts its service, and creates a static welcome page at `/var/www/html/index.html`.
    - Path: `.`
    - Entrypoint: `recipes/default.rb`
    - Technology: Chef
    - Key Features: Nginx package installation, service enablement and startup, root-owned `0644` index page, and declared Nginx attributes for port, user, and worker processes.

- **cache**:
    - Description: Separate local Chef cookbook that installs Redis and enables and starts the `redis-server` service.
    - Path: `cookbooks/cache`
    - Entrypoint: `cookbooks/cache/recipes/default.rb`
    - Technology: Chef
    - Key Features: Redis package installation and service lifecycle management; no custom Redis configuration, persistence, credentials, or templates are present in the entrypoint.

**CRITICAL PATH VERIFICATION:**
The supplied repository tree explicitly contains the root directory with `recipes/default.rb`, `metadata.rb`, and `attributes/default.rb`; therefore `.` is the existing directory for the `simple-nginx` cookbook. It also explicitly contains the directory `cookbooks/cache` with `metadata.rb` and `recipes/default.rb`; therefore `cookbooks/cache` is an existing directory for the `cache` cookbook. These are the two and only two `recipes/default.rb` cookbook entrypoints shown in the supplied tree. No Puppet `manifests/init.pp` or PowerShell `.psd1` module manifests are present.

### Infrastructure Files

- `README.md`: Identifies this as a simple Nginx cookbook used to test a metadata-only dependency strategy. It names `cache` as a local dependency and `nginx` as an external dependency that is declared but not fetchable without Berkshelf or Policyfile tooling.
- `metadata.rb`: Root `simple-nginx` cookbook metadata. It declares version `1.0.0`, Chef `>= 16.0`, Ubuntu `>= 18.04` and CentOS `>= 7.0` support, and dependencies on `cache` and `nginx`.
- `attributes/default.rb`: Defines `nginx` attributes: port `80`, user `www-data`, and worker processes `auto`. The reviewed recipe does not consume these values.
- `recipes/default.rb`: Primary Nginx implementation to translate into Ansible tasks.
- `cookbooks/cache/metadata.rb`: `cache` cookbook metadata, version `1.0.0`, Chef `>= 16.0`, and Ubuntu/CentOS support.
- `cookbooks/cache/recipes/default.rb`: Primary Redis implementation to translate into a separate Ansible role or ordered role task set.

### Target Details

- **Operating System**: The source explicitly supports Ubuntu `>= 18.04` and CentOS `>= 7.0`. These old baselines require an ownership decision because they are not suitable default production targets today. If no target is specified, plan initial validation on Red Hat Enterprise Linux 9 and a current Ubuntu release, while preserving OS-family variables for package and service naming.
- **Virtual Machine Technology**: Not specified. No cloud-init, hypervisor, guest-tools, or VM-specific configuration is present.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, metadata endpoint, or cloud CLI configuration is present.

## Migration Approach

### Key Dependencies to Address

- **Chef >= 16.0**: Replace Chef convergence with Ansible plays/roles using `ansible.builtin.package`, `ansible.builtin.service`, and `ansible.builtin.file`.
- **Local `cache` cookbook, version 1.0.0**: Migrate to a separate `cache` or `redis` role. Install Redis and enable/start its service before any future consumer role.
- **External `nginx` cookbook, version unspecified**: The root metadata declares it, but the root recipe directly installs the `nginx` package and does not invoke an external cookbook resource. Confirm whether this is intentionally metadata-only or must be replaced with an Ansible role. Do not introduce a Galaxy dependency without that decision.
- **OS package repositories**: Confirm that Nginx and Redis are available from approved repositories. Abstract package and service names because Ubuntu and RHEL-family systems can differ.
- **Dependency locking**: No Berksfile, Policyfile, or lockfile appears in the supplied tree. Prefer local Ansible roles and built-in modules; if external collections are later required, pin them in `requirements.yml`.

### Security Considerations

- **Network exposure**: Port `80` is declared, but the source does not configure a firewall or bind address. Define firewall policy separately and ensure Redis is restricted to trusted hosts and is not unintentionally Internet-facing.
- **File permissions**: Preserve `/var/www/html/index.html` as `root:root` with mode `0644`; use explicit Ansible permissions.
- **Privilege escalation**: Package and service operations require privilege. Use controlled `become: true` at play/role scope.
- **Secrets and certificates**: No passwords, tokens, encrypted data bags, Chef Vault references, certificates, private keys, or environment-variable secrets are visible in the reviewed files. Any newly introduced Redis authentication, TLS keys, or certificates must use Ansible Vault or an approved external secrets manager.
- **Unused settings**: `nginx.port`, `nginx.user`, and `nginx.worker_processes` are declared but not applied by the current recipe. Treat them as unimplemented intent until confirmed rather than silently expanding migration scope.

### Technical Challenges

- **Ambiguous `nginx` dependency**: README and metadata indicate a dependency-strategy test, while the recipe has no external cookbook call. Resolve whether to preserve metadata behavior or migrate only executable behavior.
- **Unused attributes**: Decide whether to create an Nginx configuration template using the declared values or preserve the current minimal behavior. Document the decision in role defaults.
- **Cross-platform behavior**: Redis package/service names and repository availability may vary across Ubuntu and RHEL-family systems. Use OS-family variables and test both supported families.
- **Missing deployment model**: No inventory, roles, environments, firewall policy, CI pipeline, or test framework is present. Establish inventory/group variables, ownership, linting, check-mode tests, and repeated-run idempotence tests.
- **Legacy OS support**: Validate whether Ubuntu 18.04 and CentOS 7 must remain supported; otherwise migrate to supported releases and update the documented support matrix.

### Migration Order

1. Confirm target operating systems, inventory ownership, and whether this repository is a functional deployment or a metadata-strategy test.
2. Migrate the `cache` cookbook as a Redis Ansible role and validate package/service behavior and network restrictions.
3. Migrate the root `simple-nginx` cookbook as an Nginx role, including package, service, and static index tasks.
4. Decide and implement the behavior of the declared external `nginx` dependency and the currently unused attributes.
5. Run syntax checks, ansible-lint, check mode, repeated convergence, service health checks, HTTP validation on port 80, and security review before retiring Chef.

### Assumptions

- The supplied tree is complete and the repository root is the `simple-nginx` cookbook.
- `.` and `cookbooks/cache` are existing directories shown by the supplied tree and are the only directories containing `recipes/default.rb`.
- There are no Puppet or PowerShell modules because no `manifests/init.pp` or `.psd1` files appear in the tree.
- Only behavior in the two reviewed default recipes is guaranteed to be in scope.
- The root attributes are intended inputs but are currently unused; their desired effect requires owner confirmation.
- Redis is a dependency/test component; no source file demonstrates an application consuming it.
- Package repositories provide required packages, or repository management will be added as separately approved scope.
- No secrets exist outside the reviewed files; inventories and external secret systems still require a dedicated security review.
- A local Ansible implementation using built-in modules is preferred over unverified external roles.
- A team should assign owners for OS compatibility, Nginx behavior, Redis behavior, and security/secrets review, with joint acceptance testing before Chef removal.
