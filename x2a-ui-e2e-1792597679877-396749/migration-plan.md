# MIGRATION FROM ANSIBLE EXAMPLES AND CHEF INFRASTRUCTURE BOOTSTRAP TO ANSIBLE

This repository is already primarily an Ansible demonstration rather than a conventional Chef cookbook repository. The `chef-and-ansible` directory contains two Ansible playbooks that configure an Apache HTTPS test site and tighten its TLS protocol settings, with Chef InSpec verification tests. The `setup-automate` directory contains shell-based bootstrap scripts for Chef Automate and/or Chef Infra Server, including creation of a Chef user, organization, and private key files. There are no Puppet manifests, Chef cookbooks, recipes, Berksfiles, Policyfiles, or PowerShell modules in the supplied tree.

The migration is therefore a consolidation and hardening effort: convert the existing ad hoc Ansible examples into maintainable roles and inventories, and decide whether the Chef server/Automate bootstrap is to be retired, replaced with Ansible-managed platform provisioning, or retained as an external dependency. The web-server portion is low complexity and can be migrated/refactored in approximately 1–2 weeks including testing. The Chef platform bootstrap is higher risk, primarily because it downloads a current installer, embeds credentials, creates signing material, and has an unclear target lifecycle; allow approximately 2–4 weeks for requirements clarification, secure implementation, and validation. A complete effort is roughly 3–6 weeks for one engineer, or shorter with parallel platform/security work.

## Module Migration Plan

This repository contains Ansible playbooks and shell-based Chef infrastructure bootstrap automation that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are listed below. There are no conventional Chef cookbook modules with `recipes/default.rb` or module metadata in this repository.

- **website_https**:
    - Description: Ansible playbook that installs a pinned Apache 2.4 package on Ubuntu, creates a self-signed HTTPS certificate, configures an Apache `helloworld` virtual host, deploys a static Hello World page, enables SSL, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible playbook
    - Key Features: APT package installation, OpenSSL private key/CSR/self-signed certificate generation, Apache virtual-host configuration, static content deployment, site/module activation, service handlers.

- **poodle_fix**:
    - Description: Ansible playbook intended to remediate Apache TLS configuration by replacing the SSL protocol line with TLS 1.2 only and restarting affected services.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible playbook
    - Key Features: In-place SSL configuration replacement, TLS 1.2 enforcement, Apache and SSH service notifications.

- **chef_platform_bootstrap_with_automate**:
    - Description: Bash bootstrap that configures host kernel settings, downloads the Chef Automate CLI, deploys Chef Automate together with Chef Infra Server, and creates an initial Chef user and organization.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash shell script invoking Chef Automate/Chef Infra Server
    - Key Features: Hostname and sysctl setup, remote installer download, Automate and Infra Server deployment, user/org creation, generated PEM credentials.

- **chef_infra_server_bootstrap**:
    - Description: Bash bootstrap for deploying Chef Infra Server without Automate, followed by initial user and organization creation.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash shell script invoking Chef Automate CLI and Chef Infra Server commands
    - Key Features: Host preparation, Infra Server deployment, initial administrative identity, organization creation, generated user and validator keys.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples and their relationship to Chef blog content. Update it to describe the target Ansible architecture and the retirement/retention decision for Chef infrastructure.
- `chef-and-ansible/README.md`: Explains that the examples demonstrate Chef InSpec alongside Ansible for continuous compliance. Preserve the compliance intent, but document the Ansible roles, supported OS, and test execution model.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the Ansible Playbook provisioner, the `ubuntu-20.04` platform, and Chef InSpec verification. Migrate or retain it as a transitional test harness; align its verifier tests and supported platform with the production target.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec acceptance tests for HTTPS availability, Hello World content, disabled SSLv3, and enabled TLS 1.2. Keep as a regression suite or translate key checks to Ansible Molecule/Testinfra if Chef tooling is removed.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control checking that root SSH login is not allowed. It references RHEL 8 compliance identifiers and should be incorporated into the target hardening test plan, although it is not wired into the shown Kitchen suite.
- `chef-and-ansible/index.html`: Static sample web content. Replace with an Ansible template or managed application artifact only if this demonstration content remains in scope.
- `setup-automate/deploy-automate.sh`: Platform deployment input and operational bootstrap. Replace with a version-pinned, authenticated deployment workflow or explicitly classify it as an external/manual dependency.
- `setup-automate/deploy-chef-server.sh`: Alternate Chef-only platform deployment path. It should not remain as an undocumented parallel path after migration decisions are made.

### Target Details

- **Operating System**: The explicit integration-test platform is Ubuntu 20.04, and the playbook uses `apt`, `/etc/apache2`, and Ubuntu-style `a2ensite`/`a2enmod` commands. The SSH InSpec profile contains RHEL 8 control metadata, but that identifies a compliance control rather than the configured target OS. Production OS support is therefore ambiguous; default to Ubuntu 20.04/22.04 only after confirmation, or add a separate RHEL implementation rather than assuming equivalence.
- **Virtual Machine Technology**: Vagrant is specified by Test Kitchen. The Chef bootstrap scripts otherwise describe an on-premises or cloud VM generically; no provider is identified.
- **Cloud Platform**: Not specified. The scripts support a generic VM and do not contain AWS, Azure, or GCP-specific resources or SDK configuration.

## Migration Approach

### Key Dependencies to Address

- **Ansible core and collections**: Pin a supported Ansible version and explicitly declare `community.crypto` (for the OpenSSL modules) in `collections/requirements.yml`. Replace deprecated/short module names with fully qualified collection names where appropriate.
- **Ubuntu APT and Apache 2.4.41-4ubuntu3.10**: Preserve the package baseline only if required; otherwise use a supported Ubuntu release and repository version. Make package versioning configurable per OS rather than hard-coded to an obsolete Ubuntu 20.04 build.
- **Apache utilities (`a2dissite`, `a2ensite`, `a2enmod`)**: Replace raw commands with idempotent Ansible modules where possible, or guarded commands with explicit `changed_when`/`creates` behavior. Ensure the SSL module and site state are deterministic.
- **OpenSSL/PyOpenSSL**: Use `community.crypto.openssl_privatekey`, `openssl_csr`, and `openssl_certificate` with a clearly defined certificate lifecycle. For production, use an enterprise CA/ACME process instead of self-signed certificates.
- **Vagrant and Test Kitchen**: Decide whether Vagrant/Kitchen remains the supported integration environment. If not, migrate acceptance coverage to Ansible Molecule with a compatible Ubuntu/RHEL driver.
- **Chef InSpec**: It is a test dependency, not a provisioning module. Retain it during transition or replace it with Molecule/Testinfra/Ansible assertions while preserving the HTTPS and SSH controls.
- **Chef Automate CLI and Chef Infra Server**: The shell scripts download the latest CLI from `packages.chef.io` and invoke `chef-automate deploy`. Ansible should manage only a documented, supported release and authenticated artifact, or provision the replacement platform selected by the organization. Do not blindly translate this into a generic package task without confirming Chef product support and licensing.
- **Chef-generated PEM files**: Treat user and organization keys as generated secrets. Store them in a controlled secret store and distribute them only to explicitly authorized consumers; do not commit them to the repository.

### Security Considerations

- **Plaintext credentials**: Both Chef bootstrap scripts contain a literal administrative password (`userpassword='password'`) and user identity data. Remove all credentials from source, use Ansible Vault or an external secret manager, rotate any credentials that may have been used, and require non-interactive secret injection with least privilege.
- **Remote installer integrity**: `curl` downloads a moving `current/latest` binary and pipes/decompresses it without visible checksum or signature verification. Pin a version, retrieve from a trusted internal mirror where possible, verify checksum/signature, and record provenance before execution.
- **Generated private keys**: Chef user and organization PEM files are written by the CLI, while Apache private keys are generated on the target. Set restrictive ownership and modes, protect controller-side artifacts, and define rotation/revocation procedures.
- **TLS configuration**: The website uses self-signed certificates and `ssl_verify: false` in tests. This is acceptable only for isolated demonstrations. Production migration should use trusted certificates, explicit SANs, modern TLS policy, secure cipher configuration, and certificate renewal/monitoring. Preserve the SSLv3-disabled and TLS 1.2-positive tests, while evaluating TLS 1.3 and current organizational policy.
- **File permissions**: The certificate directory is created with mode `0640`, which is not a directory execute/search permission and may prevent access or produce unsafe/incorrect behavior. Define directory mode separately from key and certificate modes; private keys should be readable only by the service account/root as required.
- **SSH and service restarts**: The playbooks run as root and restart `sshd` even when changing Apache configuration. Remove unnecessary SSH restarts and validate SSH access before any hardening change. Implement the InSpec root-login control as an explicit, tested hardening role if it is in scope.
- **Command safety**: Use `become` with a controlled deployment account instead of `remote_user: root` where operationally possible, and avoid shell/command tasks unless idempotence and failure behavior are explicit.

### Technical Challenges

- **Already-Ansible source but not a reusable design**: There are no roles, inventories, defaults, handlers directory, variable schema, or collection requirements. Refactor into roles such as `apache_https`, `tls_hardening`, and optionally `chef_platform` rather than merely copying the playbooks.
- **Playbook correctness and idempotence**: `poodle_fix.yml` notifies `Restart apache2`, but its handler is named `Restart apache`, so the notification does not match the defined handler. The website playbook also uses raw `a2*` commands and has a notification to restart SSH when enabling Apache SSL. Fix these issues and add syntax, idempotence, and convergence tests.
- **OS and version mismatch**: Ubuntu-specific paths and package names are combined with RHEL-oriented compliance metadata. Establish an OS support matrix and use distribution-aware variables/tasks before expanding beyond Ubuntu.
- **Certificate ownership and lifecycle**: Self-signed certificates are suitable for the example but not production. Agree on CA/ACME integration, SAN naming, renewal, and secret backup before migration sign-off.
- **Chef platform ambiguity**: The repository does not state whether Chef Infra Server/Automate is the target to be retired, an application that must remain, or merely a demonstration. This decision drives whether the shell scripts are migrated, wrapped, or removed.
- **External platform availability**: Automate/Infra Server deployment may require licensing, sizing, supported OS versions, network access, and product-specific configuration not represented in the scripts. Conduct a separate platform readiness review.
- **Test coverage gap**: `website_https_verify.rb` is referenced by Kitchen; `ssh_profile.rb` is not visibly included in the suite. Add explicit coverage for package state, site activation, key permissions, handler behavior, and failed/renewed certificate scenarios.

### Migration Order

1. **Inventory and decisions**: Confirm whether Chef Infra Server and Automate remain required, define supported OS/provider, identify current owners of PEM credentials, and freeze the legacy scripts for reference.
2. **Test baseline**: Run the existing Kitchen/Ansible scenario where possible, record current behavior, and correct/extend InSpec coverage for HTTPS and SSH hardening.
3. **Apache HTTPS role**: Convert `website_https.yml` into an idempotent role with OS variables, proper handlers, secure file modes, deterministic site/module management, and configurable content/certificates.
4. **TLS hardening role**: Refactor `poodle_fix.yml`, fix the handler mismatch, make protocol policy configurable, and validate Apache configuration before reload/restart.
5. **Integration and CI**: Add Molecule or an equivalent CI pipeline, linting, Ansible version/collection pinning, secret scanning, and an idempotence/convergence gate. Retain Kitchen temporarily if it is still the organization’s accepted test framework.
6. **Chef platform path**: If Chef remains, create a separately owned, version-pinned, secret-safe Ansible automation layer or document the shell scripts as an external runbook. If Chef is being retired, decommission the bootstrap scripts and migrate any dependent clients, keys, organizations, and compliance workflows.
7. **Cutover and knowledge transfer**: Pilot on non-production hosts, compare service/TLS behavior, document rollback, then promote through environments with security and platform-owner approval.

### Assumptions

- The supplied tree is complete; no hidden cookbooks, Berksfiles, Policyfiles, inventories, secrets, CI definitions, or environment configuration are assumed.
- The primary migration target is Ansible, although the web portion is already Ansible and needs restructuring rather than a literal technology conversion.
- `chef-and-ansible` is an example/test project, not evidence of a production Apache deployment.
- Ubuntu 20.04 is the only explicitly configured target platform; production OS, release support window, and whether RHEL must be supported are unresolved.
- Vagrant is used for local testing, but the production VM platform and cloud provider are unknown.
- The literal bootstrap password may have been used; it must be treated as compromised until proven otherwise.
- The generated PEM files are sensitive even though no generated PEM content is present in the repository.
- Self-signed TLS is demonstration-only; a production certificate authority and naming scheme must be selected.
- Chef Automate and Chef Infra Server requirements, licensing, sizing, upgrade policy, and consumers are not documented.
- No database, application runtime, load balancer, DNS, firewall, monitoring, backup, or certificate renewal integration is visible.
- The malformed closing `</head>` in the inline sample content and the separate `index.html` are demonstration artifacts; product owners must confirm which content is authoritative.
- Migration estimates exclude procurement, licensing, production change windows, remediation of unknown downstream Chef clients, and organization-wide compliance approval.
- Team coordination should assign separate owners for Ansible role engineering, security/secrets, Chef platform disposition, test/CI modernization, and operations cutover, with a shared OS/support matrix and rollback runbook.
