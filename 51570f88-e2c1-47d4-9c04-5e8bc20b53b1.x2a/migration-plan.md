# MIGRATION FROM CHEF-ADJACENT AUTOMATION TO ANSIBLE

## Executive Summary

This repository is not a conventional Chef cookbook repository. It contains two small Ansible playbooks under `chef-and-ansible/`, Chef InSpec verification profiles, and Bash bootstrap scripts for Chef Infra Server/Chef Automate. No Chef cookbook structure (`recipes/`, `metadata.rb`, `Berksfile`, or `Policyfile.rb`) was found, and no Puppet, Salt, or PowerShell modules were identified.

The migration to a maintainable Ansible implementation is therefore small in application scope but important from a security and operational perspective. The web-server configuration is already Ansible-based and can be refactored into a role or collection with idempotent modules. The Chef server/Automate bootstrap should be treated as a separate infrastructure transition: either retire it, replace it with an Ansible-managed platform deployment, or retain it as an external dependency while Ansible manages only its host prerequisites. A focused proof of concept should take approximately 1–2 weeks; production hardening, certificate integration, testing, and team adoption are more realistically 3–6 weeks, depending on whether Chef Automate remains in the target architecture.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related bootstrap/testing assets that need individual migration planning. It does **not** contain Chef cookbooks requiring recipe-by-recipe conversion.

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths observed in the repository tree and inspected files are listed below.

- **website_https**:
    - Description: Ansible playbook that provisions an Apache HTTPS Hello World site on an Ubuntu host, creates a self-signed certificate, configures an SSL virtual host, deploys static content, enables the SSL module/site, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Ubuntu APT package installation, Apache 2.4 package pinning, OpenSSL key/CSR/self-signed certificate generation, HTTPS virtual host, static website deployment, Apache and SSH handlers.
    - Migration action: Preserve behavior but convert to a reusable role with variables, `ansible.builtin.apt`, `ansible.builtin.template`/`copy`, `ansible.builtin.command` only where no module is suitable, and explicit service/module enablement.

- **poodle_fix**:
    - Description: Ansible playbook that changes Apache's SSL protocol configuration to allow TLS 1.2 only and restarts Apache and SSH.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Regex replacement in `/etc/apache2/mods-available/ssl.conf`, TLS hardening, service notifications.
    - Migration action: Fold into the Apache HTTPS role as an optional hardening task, using a managed template where practical and validating the resulting Apache configuration before restart.

- **chef_platform_bootstrap**:
    - Description: Bash-based bootstrap for deploying Chef Automate plus Chef Infra Server, or Chef Infra Server alone, on a VM and creating a Chef user and organization.
    - Paths: `setup-automate/deploy-automate.sh`, `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Automate/Infra Server CLI
    - Key Features: Hostname and kernel tuning, downloaded Chef Automate CLI, product deployment, Chef user/org creation, generated PEM credentials.
    - Migration action: Decide whether Chef is being retired. If retained, wrap the supported Chef CLI/API in a narrowly scoped Ansible role; do not reproduce the shell script verbatim. If retired, replace this with the target platform's Ansible-managed control-plane provisioning or remove it from the migration scope.

- **compliance_verification**:
    - Description: Chef InSpec tests that verify SSH root-login hardening and HTTPS availability/protocol behavior.
    - Paths: `chef-and-ansible/tests/ssh_profile.rb`, `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec Ruby DSL
    - Key Features: SSH `PermitRootLogin` check, port 443/listening and HTTP status checks, TLS 1.2 enabled, SSLv3 disabled.
    - Migration action: Keep as external acceptance tests during transition or port to Ansible Molecule/Testinfra/pytest while preserving the security assertions.

### Infrastructure Files

- `README.md`: Repository-level description of Chef-related examples; provides context but no deployment configuration.
- `chef-and-ansible/README.md`: Describes the examples as Ansible plus Chef InSpec compliance demonstrations.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, Ubuntu 20.04, the Ansible provisioner, and InSpec verification. It is important migration/test documentation, not a runtime module.
- `chef-and-ansible/index.html`: Standalone sample HTML content; the playbook embeds similar content directly and should be reconciled to one source of truth.
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server bootstrap entrypoint.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap variant.

### Target Details

- **Operating System:** Ubuntu 20.04 is explicitly specified in `kitchen.yml`; the playbooks use `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. Validate the supported target before production rollout, since Ubuntu 20.04 is aging and the pinned Apache package may not exist in newer repositories. The Chef platform scripts do not explicitly identify an OS.
- **Virtual Machine Technology:** Vagrant is specified as the Test Kitchen driver. The production VM platform is not specified and may be on-premises or cloud-based according to the bootstrap comments.
- **Cloud Platform:** Not specified. The Chef bootstrap claims on-premises or cloud VM compatibility but contains no provider-specific resources.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime and collections:** Standardize an Ansible version and use `ansible.builtin` modules. The current playbooks use older short module names and legacy parameter syntax.
- **Ubuntu APT repositories:** Replace or validate the hard-coded `apache2=2.4.41-4ubuntu3.10` version. Pinning improves repeatability but can block newer Ubuntu repositories; use an approved package repository or a configurable version.
- **OpenSSL Ansible modules:** The playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`; verify the installed collection/version and migrate to fully qualified module names. For production, replace self-signed certificates with enterprise PKI, ACME, or a secrets/certificate platform.
- **Apache:** Build a role that manages packages, SSL module, site configuration, content, certificate files, syntax validation, and service state. Prefer declarative module state over raw `a2dissite`/`a2ensite` commands.
- **Chef Automate/Infra Server CLI:** There is no dependency manifest. The scripts download the latest CLI from `packages.chef.io`, then call `chef-automate` and `chef-server-ctl`. Pin and verify a supported version if this platform remains, or define its replacement as an architecture decision.
- **Test Kitchen, Vagrant, and Chef InSpec:** Existing tests are valuable acceptance criteria. Decide whether to retain them temporarily or replace the harness with Molecule and Testinfra/pytest for an Ansible-native pipeline.

### Security Considerations

- **Hard-coded credentials:** Both Chef bootstrap scripts contain a literal user password (`password`), username, email, and organization information. Remove all secrets from source immediately, rotate any credentials used, and supply them through Ansible Vault, an external secrets manager, or CI secret variables.
- **Generated PEM credentials:** Chef user and organization validator PEM files are written by the bootstrap scripts. Protect their permissions, control their lifecycle, avoid artifact/log exposure, and revoke/regenerate them if compromise is possible.
- **TLS certificates and private keys:** The website playbook creates `/etc/apache2/certs/apache.key` and a self-signed certificate. Set restrictive key permissions, avoid copying keys through logs, and use centrally issued certificates for real environments. The current cert directory mode (`0640`) should be reviewed because directory execute permissions and ownership semantics matter.
- **TLS policy:** `poodle_fix.yml` disables all protocols except TLS 1.2, and InSpec checks SSLv3/TLS 1.2. Establish an approved modern policy, likely including TLS 1.3 where supported, and test client compatibility before deployment.
- **SSH handling:** The tests require root SSH login to be disabled, but the playbooks do not enforce `PermitRootLogin no`. Add explicit SSH hardening and validate configuration before restarting `sshd`; avoid coupling unrelated SSH restarts to Apache changes.
- **Untrusted download/install path:** The scripts pipe a downloaded/latest Chef Automate CLI into local processing and do not show checksum or signature verification. Pin versions, verify signatures/checksums, use an approved artifact repository, and constrain execution privileges.
- **Privilege escalation:** The web playbooks use `remote_user: root` together with `become: yes`. Move to a controlled administrative account with `become`, disable direct root access, and document required sudo permissions.
- **Input and certificate naming:** `myhost` is used as the CSR common name while the bootstrap hostname is different. Define inventory hostnames, DNS names, and certificate SANs explicitly rather than relying on defaults.

### Technical Challenges

- **No actual Chef cookbook inventory:** There are no recipes or cookbook metadata to translate. The migration team must avoid inventing cookbook boundaries and instead establish an Ansible role layout around the existing Apache and security concerns.
- **Idempotence and legacy commands:** `a2dissite`, `a2ensite`, and `a2enmod` are invoked with `command`; repeated runs and change detection should be validated. Use Ansible modules or guarded commands and run `apachectl configtest` before handlers restart services.
- **Platform/version drift:** The tested Ubuntu 20.04 environment and pinned Apache package may differ from production. Build a support matrix and test on the selected current OS before changing package versions.
- **Certificate model change:** Self-signed certificates are acceptable for a demo but not normally for production. Integrating PKI/ACME and ensuring renewal without unnecessary Apache restarts is likely the principal web-service design task.
- **Chef control-plane decision:** Automate/Infra Server deployment is a platform lifecycle concern, not merely a cookbook migration. Retaining it requires supported APIs, version pinning, persistent storage, backups, licensing, and high-availability decisions; retiring it requires inventorying any users, organizations, nodes, and pipelines that depend on it.
- **Test migration:** Existing InSpec tests are useful but one test appears to accept an uninstalled OpenSSH package as an alternative to a secure configuration. Confirm the intended control semantics before porting it to Ansible-native tests.
- **Coordination:** Assign separate owners for Apache/security role work, Chef platform disposition, secrets/PKI, and CI/test conversion. Establish a shared acceptance checklist based on the current InSpec assertions.

### Migration Order

1. **Baseline and security containment:** Remove/rotate the hard-coded Chef password, inventory PEM artifacts, document the current test environment, and decide whether Chef Automate/Infra Server is in or out of the target architecture.
2. **Apache HTTPS role:** Refactor `website_https.yml` into an idempotent reusable role, parameterize hostname/content/certificate source, and validate it on Ubuntu 20.04 and the intended production OS.
3. **TLS and SSH hardening:** Merge `poodle_fix.yml` into the role or a security profile, add SSH root-login enforcement, and add configuration validation before service restarts.
4. **Verification pipeline:** Retain InSpec during parallel operation, then port the checks to Molecule/Testinfra or another approved Ansible test framework. Require HTTPS, certificate, service, and SSH checks in CI.
5. **Chef platform transition:** If Chef remains, automate only supported APIs/CLI operations with vaulted credentials and pinned artifacts. If Chef is being retired, migrate dependent organizations/users/pipelines and decommission the bootstrap scripts after a validated cutover.
6. **Operational rollout:** Pilot on a non-production VM, perform parallel validation, then stage production deployment with rollback, certificate renewal, package repository, and ownership documentation.

### Assumptions

- The requested destination is Ansible, and the existing `website_https.yml` is the primary configuration to standardize rather than a Chef cookbook.
- No files outside the provided tree are assumed; there are no discovered `Berksfile`, `metadata.rb`, `Policyfile.rb`, cookbook recipes, or Chef environment/role files.
- `kitchen.yml` is representative of the test target, but production OS, VM sizing, network topology, DNS, firewall rules, and cloud provider are unspecified.
- The sample Apache site and self-signed certificates are demonstration assets, not necessarily production requirements.
- The literal bootstrap password may have been used in a real environment; it must be treated as compromised until proven otherwise.
- It is unclear whether Chef Automate and Chef Infra Server are still required, whether they have persistent data, and what systems consume the generated PEM files.
- It is unclear whether Apache should remain the target web server and whether the hard-coded Apache package version is still available or supported.
- Certificate authority, certificate renewal, secret-management platform, and SSH account/sudo policy are not defined.
- The intended Ansible control node version, inventory model, CI platform, collection source, and deployment approval process are unspecified.
- The InSpec control for SSH has unusual logic that treats an absent OpenSSH server as passing; security owners must confirm whether SSH must be installed and configured or merely not expose root login.
- No timeline commitments, service-level objectives, backup requirements, high-availability requirements, or rollback procedures were present; the estimates above assume a small proof of concept and a normal staged production rollout.
