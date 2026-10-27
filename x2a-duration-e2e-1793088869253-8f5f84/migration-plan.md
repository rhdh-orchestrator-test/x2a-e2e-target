# MIGRATION FROM CHEF AUTOMATE / CHEF INFRA SERVER AND AD-HOC SHELL TO ANSIBLE

This repository is a small demonstration and deployment repository rather than a conventional Chef cookbook repository. The `chef-and-ansible` directory already contains Ansible playbooks that configure Apache HTTPS and Chef InSpec tests that validate the result. The `setup-automate` directory contains shell installers for Chef Automate and/or Chef Infra Server, including user and organization bootstrap. The migration is therefore primarily a consolidation and hardening effort: retain or replace the demonstrated host configuration in Ansible, and decide whether the Chef control-plane deployment is to be retired, wrapped in Ansible, or kept as a transitional dependency.

The observed scope is low to moderate: two Ansible playbooks, two InSpec controls, one Test Kitchen configuration, and two shell-based Chef platform installers. A proof-of-concept migration can be completed in approximately 1–2 weeks; a production-ready migration with secret rotation, supported platform testing, CI, rollback, and operational documentation is more realistically 3–6 weeks. The timeline assumes there are no additional Chef cookbooks or externally managed infrastructure omitted from this tree.

## Module Migration Plan

This repository contains Ansible playbooks, InSpec verification controls, and Chef platform bootstrap scripts that need individual migration planning. No Puppet modules, Chef cookbooks (`recipes/default.rb`), PowerShell modules, Salt states, Berksfile, Policyfile, or Chef cookbook metadata were found in the supplied tree.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only modules and executable configuration units whose paths were present in the repository tree are listed below.

- **website_https**:
    - Description: Ansible playbook that installs a pinned Apache 2.4 package on Ubuntu, installs TLS/OpenSSL tooling, generates a private key, CSR, and self-signed certificate, creates a Hello World HTTPS virtual host, disables the default site, enables the custom site and SSL module, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Apache HTTPS virtual host, self-signed certificate generation, TLS-related package installation, site enablement, static test website, privileged execution as root
    - Migration Status: Already Ansible-native; refactor into a role with variables, templates, handlers, idempotent modules, and environment-specific inventory rather than treating the playbook as a final production design.

- **poodle_fix**:
    - Description: Ansible remediation playbook that replaces the Apache SSL protocol setting with TLS 1.2 only and notifies Apache and SSH service handlers.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible YAML playbook
    - Key Features: SSL configuration replacement, TLS hardening intent, service restart handlers
    - Migration Status: Already Ansible-native; consolidate with the HTTPS role and replace the broad regular-expression edit with a managed configuration fragment or template. Confirm whether restarting SSH is required before retaining that behavior.

- **chef_automate_bootstrap**:
    - Description: Shell-based deployment of Chef Automate together with Chef Infra Server, followed by creation of a Chef user, organization, and generated PEM credentials.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash invoking Chef Automate CLI and Chef Infra Server commands
    - Key Features: Hostname and kernel tuning, downloaded Chef Automate CLI, Automate plus Infra Server deployment, user/org provisioning, validator and user key generation
    - Migration Status: Replace or wrap with an Ansible role only if Chef Automate remains required. The preferred target is to remove this Chef control plane after all required node configuration is represented in Ansible.

- **chef_server_bootstrap**:
    - Description: Shell-based deployment of Chef Infra Server without Automate, followed by Chef user and organization provisioning.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash invoking Chef Automate CLI and Chef Infra Server commands
    - Key Features: Hostname and `sysctl` changes, remote CLI download, Infra Server installation, organization/user creation, PEM key generation
    - Migration Status: Replace with Ansible platform provisioning or retain only as a transitional fallback. It overlaps operationally with `chef_automate_bootstrap`; the target architecture should select one path, not maintain both.

- **verification_controls**:
    - Description: InSpec controls validate that HTTPS is listening and serves the expected page with TLS 1.2 enabled and SSLv3 disabled, and that SSH root login is disabled.
    - Path: `chef-and-ansible/tests/website_https_verify.rb` and `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec
    - Key Features: Port and HTTP checks, TLS protocol checks, SSH configuration/compliance assertions, STIG/SRG metadata
    - Migration Status: Keep as an independent compliance gate during transition, or translate into Ansible testinfra/Molecule, Goss, or an equivalent CI compliance framework. Preserve the control intent and evidence metadata if compliance reporting is required.

### Infrastructure Files

- `README.md`: Repository-level description of Chef-related examples. Update to describe the Ansible target architecture, supported platforms, ownership, and migration status.
- `chef-and-ansible/README.md`: Explains that the examples combine Ansible with Chef InSpec for continuous compliance. Retain as historical context or rewrite as the target validation guide.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, Ansible provisioner, Ubuntu 20.04, and InSpec verifier. Migrate to Molecule with a Vagrant or container driver, or explicitly retain Kitchen during the validation transition.
- `chef-and-ansible/poodle_fix.yml`: Security remediation playbook; see module inventory.
- `chef-and-ansible/website_https.yml`: Main host configuration playbook; see module inventory.
- `setup-automate/deploy-automate.sh`: Combined Chef Automate/Infra Server bootstrap; candidate for retirement or Ansible wrapper.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap; candidate for retirement or Ansible wrapper.
- `chef-and-ansible/tests/`: InSpec verification suite. Use it as an acceptance baseline while implementing Ansible tests.

### Target Details

- **Operating System**: Ubuntu 20.04 is explicitly specified by `kitchen.yml`, and the playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. The SSH InSpec control references RHEL 8 STIG identifiers, but that is compliance metadata rather than evidence that RHEL is the deployment OS. Confirm whether Ubuntu 20.04 remains supported and add a supported newer Ubuntu/RHEL matrix before production migration.
- **Virtual Machine Technology**: Vagrant is specified by Test Kitchen. The actual production VM platform is not specified; the shell comments allow on-premises or cloud VMs.
- **Cloud Platform**: Not specified. The bootstrap scripts use generic HTTPS downloads and local VM commands; no AWS, Azure, or GCP integration is visible.

## Migration Approach

### Key Dependencies to Address

- **Ansible**: Standardize on a supported Ansible Core version and Python interpreter policy. Convert the legacy short module names (`apt`, `file`, `copy`, `command`, `replace`) to fully qualified names where practical.
- **Ubuntu package repositories**: Preserve or intentionally replace the Apache version pin `2.4.41-4ubuntu3.10`; validate availability in the target repositories and define behavior when the exact version is unavailable.
- **Apache HTTP Server**: Implement an Ansible role for package installation, module/site enablement, virtual host configuration, service management, and configuration validation (`apachectl configtest`).
- **OpenSSL / `community.crypto`**: Replace the unqualified `openssl_privatekey`, `openssl_csr`, and `openssl_certificate` usage with supported `community.crypto` modules and pin the collection in `collections/requirements.yml`. Decide whether certificates are self-signed for labs or supplied by an enterprise CA in production.
- **Chef InSpec**: Keep it as a transitional acceptance/compliance dependency, or map its assertions to Molecule/testinfra or another approved Ansible validation tool.
- **Vagrant/Test Kitchen**: Decide whether Vagrant is only a local test driver. Molecule is the likely Ansible-native replacement, with CI execution and an explicitly supported image matrix.
- **Chef Automate CLI and Chef Infra Server**: The scripts download the current/latest CLI and invoke Chef commands. If Chef is retained, package/version pinning, an Ansible role, API/key handling, and supported installation procedure are required. If Chef is being removed, inventory, node bootstrap, user/org, and key-management responsibilities must be replaced before deleting the scripts.

### Security Considerations

- **Hardcoded credentials**: Both shell scripts visibly contain a plaintext user password (`userpassword='password'`) and personally identifiable account data. Remove these values immediately, rotate any credentials that may have been used, and source secrets from Ansible Vault or an approved external secret manager.
- **Generated Chef keys**: The bootstrap scripts create user and organization validator PEM files. Treat these as secrets, prevent them from entering source control or logs, define ownership/permissions, and revoke them if Chef is retired.
- **Private key and certificate**: The HTTPS playbook creates `/etc/apache2/certs/apache.key`, CSR, and self-signed certificate. Protect the private key, use restrictive ownership and mode, and replace self-signed certificates with managed CA certificates for non-test environments. The certificate directory mode `0640` is unusual for a directory and should be corrected and tested.
- **Remote installer integrity**: The scripts pipe a download from `packages.chef.io` directly into `gunzip` and execute it. Pin a known version, verify checksum/signature, use a controlled artifact repository, and avoid executing unverified network content.
- **TLS hardening**: The intended policy disables SSLv3 and enables TLS 1.2. Confirm modern TLS 1.3/TLS 1.2 requirements, cipher policy, certificate chain, hostname/SAN correctness, and Apache configuration syntax. Do not assume the current replacement is sufficient hardening.
- **SSH handling**: The InSpec control checks that root SSH login is not enabled, but neither playbook explicitly configures `PermitRootLogin`. Add an Ansible SSH-hardening role with a safe delegated-user/console rollback plan. Avoid restarting SSH until configuration validation and connectivity checks succeed.
- **Privilege and service restarts**: The playbooks run as root and restart Apache and SSH. Use `become`, least privilege where possible, validation handlers, and controlled maintenance windows. The notification name `Restart apache2` does not match the declared handler name `Restart apache` in `poodle_fix.yml`, so the playbook should be corrected and tested.
- **Secrets management per module**: `website_https` uses generated TLS private material; `poodle_fix` handles no visible credentials; each Chef bootstrap script uses plaintext bootstrap credentials and generates PEM keys. No encrypted data bags, Chef Vault, Hiera, or external secret provider configuration was found.

### Technical Challenges

- **No actual Chef cookbooks to translate**: The repository contains no Chef recipes or cookbook metadata. The migration team must confirm that this is the complete scope and obtain any external Chef policy, cookbook, node, role, or environment repositories before declaring migration complete.
- **Chef control-plane disposition**: Removing Chef Automate/Infra Server is an architectural decision, not a simple syntax conversion. Inventory its current consumers, node registration, compliance reporting, policy data, and generated keys; then define Ansible inventory, AWX/Controller, execution environments, and reporting equivalents.
- **Idempotence and portability**: `command: a2dissite`, `a2ensite`, and `a2enmod` are imperative, while paths and package naming are Ubuntu-specific. Replace with idempotent modules or guarded commands and test repeated runs.
- **Configuration correctness**: The embedded HTML contains a malformed closing title tag, and the Apache virtual host is supplied as inline content. Move site and vhost configuration into templates, validate syntax, and separate test content from production content.
- **Platform ambiguity**: Ubuntu 20.04 is the test target, while compliance labels reference RHEL 8. Define OS support and implement platform-specific variables/tasks rather than silently assuming one distribution.
- **Testing migration**: InSpec provides useful security assertions but the current test configuration has limited coverage. Preserve HTTPS/TLS/SSH acceptance tests and add idempotence, certificate expiry, package, firewall, and rollback tests in Molecule/CI.
- **Version drift**: `ansible_version: latest` and the Chef CLI `current/latest` download make outcomes non-reproducible. Pin Ansible, collections, OS images, packages, and Chef artifacts during the transition.

### Migration Order

1. **Baseline and containment**: Confirm repository scope, stop use of plaintext bootstrap credentials, rotate exposed passwords/keys, pin tool versions, and capture current Chef dependencies and target inventories.
2. **Testing foundation**: Preserve the existing InSpec controls as a baseline, introduce Molecule or an equivalent Ansible test harness, and establish Ubuntu 20.04 plus the intended current OS matrix.
3. **Apache HTTPS role**: Refactor `website_https.yml` into a reusable role with variables, templates, `community.crypto`, handlers, config validation, and safe certificate inputs. This is the lowest-risk/highest-value configuration migration because it is already Ansible-based.
4. **TLS remediation and SSH hardening**: Merge `poodle_fix.yml` into the role or a security role, correct handler notifications, explicitly manage SSH root-login policy, and add rollback/connectivity safeguards.
5. **Chef bootstrap decision and transition**: If Chef remains temporarily, create a pinned, secret-safe Ansible role around the supported Chef installation process. In parallel, map Chef organizations, users, keys, policies, and compliance workflows to Ansible Controller/AWX and an approved secrets/compliance platform.
6. **Retire or formally operate Chef scripts**: Remove both shell scripts only after consumers are migrated and keys are revoked, or document them as a controlled legacy bootstrap with ownership, versioning, checksums, and security controls.
7. **Operational rollout**: Pilot on disposable VMs, then non-production hosts, then production using staged inventory groups, change approvals, observability, rollback procedures, and team handoff documentation.

### Assumptions

- The supplied tree is complete for this migration; external Chef cookbooks, policyfiles, server configurations, and production inventories may exist outside it.
- The desired target is Ansible-managed host configuration and not necessarily an Ansible reimplementation of Chef Automate itself.
- Ubuntu 20.04 is the current lab baseline because it is the only explicit platform declaration.
- Vagrant is a test platform, not proof of the production virtualization platform.
- The Chef scripts' sample credentials are real or potentially exposed; they must be treated as compromised until proven otherwise.
- The generated certificates are laboratory self-signed certificates, not approved production PKI artifacts.
- The existing InSpec controls are acceptance/compliance requirements, although the RHEL STIG identifiers may not match the Ubuntu target.
- No firewall, DNS, load balancer, CA, monitoring, backup, or cloud integration is represented in the reviewed files.
- The intended Apache service name is `apache2`, while the SSH service name may vary by distribution and must be validated.
- Migration ownership should be split among an Ansible platform team, an application/web team for Apache content, a security/compliance team for TLS/SSH controls, and an identity/secrets team for Chef key and password rotation.
- Completion criteria should include a version-pinned reproducible build, successful repeated execution, compliance test parity, documented inventory and secrets flow, rollback, and explicit approval to retire or retain Chef.
