# MIGRATION FROM CHEF ECOSYSTEM EXAMPLES TO ANSIBLE

This repository is a small Chef-branded example repository whose executable infrastructure content is already primarily Ansible: the `chef-and-ansible` directory contains two Ansible playbooks, Molecule/Test Kitchen-style execution metadata, and Chef InSpec compliance tests. It also contains Bash installers for Chef Automate and Chef Infra Server. There are no Chef cookbooks, Puppet modules, Salt states, or PowerShell modules to port. The practical migration is therefore a hardening and productionization effort: preserve the existing Ansible behavior, replace ad hoc commands and embedded content with maintainable roles/collections, and decide whether the Chef server/Automate bootstrap scripts are to be retired, retained as a separate platform dependency, or replaced by Ansible-managed platform services.

The scope is small (two playbooks and two related test controls), so an initial functional migration/prototype should take approximately 2–5 working days. Production hardening, target-OS validation, secret remediation, CI integration, and acceptance testing should take approximately 1–2 additional weeks, depending on whether Chef Automate/Infra Server remains in scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef ecosystem bootstrap scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that provisions Apache on Ubuntu, installs OpenSSL tooling, generates a private key/CSR/self-signed certificate, configures an HTTPS Hello World virtual host, enables SSL, disables the default site, and serves static content.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu apt package installation, Apache 2.4.41 package pinning, self-signed TLS certificate generation, virtual-host configuration, static website deployment, service handlers.

- **poodle_fix**:
    - Description: Ansible playbook intended to restrict Apache TLS to TLS 1.2 by editing `ssl.conf` and restarting Apache and SSH services.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Regex-based SSL protocol replacement, Apache/SSH restart notifications, remediation of legacy SSL protocol exposure.

- **chef_automate_infra_server_bootstrap**:
    - Description: Bash bootstrap script that sets host kernel parameters, downloads the current Chef Automate CLI, deploys both Chef Automate and Chef Infra Server, then creates a Chef user and organization and writes PEM credentials.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash/Chef Automate and Chef Infra Server
    - Key Features: Hostname setup, `vm.max_map_count` and dirty-page tuning, online CLI download, combined Automate/Infra Server deployment, user/org credential generation.

- **chef_infra_server_bootstrap**:
    - Description: Bash bootstrap script for deploying Chef Infra Server only, including host tuning, CLI download, Chef user creation, organization creation, and PEM generation.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash/Chef Infra Server
    - Key Features: Infra Server deployment, hostname and kernel tuning, organization/user bootstrap, validator and user key output.

**CRITICAL PATH VERIFICATION:**
All paths above were present in the supplied repository tree and were inspected. There are no `manifests/init.pp`, `recipes/default.rb`, or PowerShell module manifests; no Puppet, Chef cookbook, or PowerShell module inventory should be inferred.

### Infrastructure Files

- `README.md`: Repository-level description of Chef-related examples; provides context but no runtime configuration.
- `chef-and-ansible/README.md`: Explains that the examples demonstrate Chef InSpec used alongside Ansible for continuous compliance automation.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, an Ansible playbook provisioner, InSpec verifier, and Ubuntu 20.04 platform. This is the clearest declared execution target.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec acceptance control validating HTTPS availability, Hello World content, SSLv3 disabled, and TLS 1.2 enabled.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control checking that SSH root login is not enabled; it references an RHEL 8 STIG control and contains an unusual fallback asserting that `openssh-server` is not installed.
- `chef-and-ansible/index.html`: Static sample HTML, separate from the inline website content in `website_https.yml`.
- `setup-automate/deploy-automate.sh`: Combined Chef Automate/Infra Server installer and bootstrap script.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only installer and bootstrap script.

There is no Berksfile, Policyfile, cookbook `metadata.rb`, Ansible `requirements.yml`, role structure, inventory, group variables, CI definition, or explicit secret-management configuration in the reviewed tree.

### Target Details

- **Operating System:** `chef-and-ansible/kitchen.yml` explicitly targets Ubuntu 20.04. The playbooks use `apt`, Debian/Ubuntu Apache paths, `apache2`, and `sshd`; migration acceptance should therefore begin on Ubuntu 20.04 or a supported successor. The InSpec SSH control references RHEL 8 STIG identifiers, but that is compliance guidance rather than proof that RHEL is the deployment OS. Cross-platform support is currently unproven.
- **Virtual Machine Technology:** Vagrant is configured as the Test Kitchen driver. The underlying provider is not specified.
- **Cloud Platform:** Not specified. The bootstrap comments say on-premises or cloud VM, but no provider-specific tooling or metadata is present.

## Migration Approach

1. Establish an Ansible project layout with inventories, `group_vars`, encrypted variables, roles for Apache/TLS and SSH hardening, and a top-level site playbook. Preserve the current playbook behavior before refactoring.
2. Convert inline `copy.content` blocks into Jinja2 templates and variables. Make Apache version, hostname, document root, certificate source, TLS policy, and service names configurable.
3. Replace shell/command-based `a2dissite`, `a2ensite`, and `a2enmod` operations with idempotent Ansible modules where practical, or wrap them with explicit `changed_when`/`creates` logic. Use `ansible.builtin.apt`, `template`, `file`, `openssl_*`, and `service`/`systemd` modules with fully qualified names.
4. Add explicit Apache configuration validation (`apachectl configtest`) before handlers restart services. Separate certificate generation for development from certificate deployment or ACME integration for production.
5. Decide the fate of the Chef bootstrap scripts. If Chef Infra Server/Automate is still required, model host preparation and service deployment in a separate Ansible role and obtain vendor-supported installation/version procedures. If it is out of scope, archive these scripts as legacy and remove them from the target deployment path.
6. Retain InSpec controls during transition, and add Ansible linting, syntax checks, idempotence checks, and repeatable Ubuntu acceptance tests to CI. Add an Ansible-native compliance path only if the operating model requires removing InSpec.

### Key Dependencies to Address

- **Ubuntu apt repositories and Apache 2.4.41:** The website playbook pins `apache2=2.4.41-4ubuntu3.10`, which may no longer exist in current repositories. Use a supported package version policy, an approved repository/snapshot, or an explicit compatibility variable and test it on the selected Ubuntu release.
- **Apache2 and OpenSSL:** Replace direct file editing and raw enable/disable commands with idempotent module-driven configuration and service management. Ensure the required Apache SSL module and configuration syntax are enabled.
- **`community.crypto` or equivalent Ansible crypto modules:** The playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`; declare the collection in `requirements.yml`, pin a tested version, and install it in CI.
- **Vagrant/Test Kitchen and InSpec:** These provide the existing test harness, not production dependencies. Preserve them during transition or replace them with an Ansible-native Molecule/pytest or CI workflow after equivalent coverage exists.
- **Chef Automate CLI and Chef Infra Server:** The shell scripts download the latest CLI dynamically from `packages.chef.io` and invoke vendor commands. If retained, pin a supported release, verify checksums/signatures, and document external Chef licensing and sizing requirements.
- **OpenSSH service naming:** The playbooks notify `sshd`, while Ubuntu commonly uses `ssh`. Verify the target image and parameterize the service name to avoid failed handlers.

### Security Considerations

- **Hardcoded credentials:** Both bootstrap scripts contain `userpassword='password'`, plus user email, organization, and host identity values. Treat the password as compromised, remove it from source, rotate any generated credentials, and use Ansible Vault or an external secret manager with runtime injection.
- **Generated Chef keys:** The scripts write `${username}.pem` and `${orgname}-validator.pem` in the working directory. Protect these files with restrictive permissions, avoid source control and logs, define secure storage/rotation, and clean up temporary artifacts.
- **Unverified remote download:** The scripts pipe a download of the latest CLI directly through `curl` and `gunzip` into an executable. Pin a version, use HTTPS with certificate validation, verify a published checksum/signature, and install from a controlled artifact repository.
- **TLS configuration:** The intended policy disables SSLv3 and enables TLS 1.2, but the implementation is a fragile regex replacement and does not define a complete modern cipher/protocol baseline. Use a managed Apache template, explicitly define approved protocols/ciphers, and obtain security approval before production use. Add TLS 1.3 behavior where supported.
- **Private key and certificate permissions:** The certificate directory is created with mode `0640`, which is not a directory-executable permission for normal traversal and is not a clear least-privilege policy. Set directory, key, certificate, and CSR ownership/modes separately; do not generate self-signed certificates for public production endpoints.
- **SSH hardening:** `ssh_profile.rb` checks root-login posture, but no playbook currently enforces it. Add a carefully tested SSH role, preserve an out-of-band recovery path, validate configuration before restarting SSH, and avoid locking out operators.
- **Privilege escalation:** The playbooks use `remote_user: root` and `become: yes`. Standardize on a non-root automation account with narrowly controlled sudo/become permissions where operationally possible.
- **Certificate validation:** The InSpec HTTPS test uses `ssl_verify: false`, appropriate only for the self-signed test certificate. Keep this exception confined to test environments and validate trust chains in production.

### Technical Challenges

- **Already-Ansible source, not a conventional Chef migration:** There are no cookbooks to translate. The main challenge is separating demonstration code from reusable, supported automation and defining the desired production target.
- **Idempotence and handler correctness:** `poodle_fix.yml` notifies `Restart apache2`, but its handler is named `Restart apache`; that notification will not resolve as written. The website playbook uses command-based site/module activation and may report changes on every run. Correct names and replace commands with idempotent mechanisms.
- **Platform inconsistency:** Ubuntu 20.04 is the Test Kitchen platform, while the InSpec SSH control cites RHEL 8 STIG controls. Define whether Ubuntu-only support or a cross-platform role is required, then maintain separate variable mappings and tests.
- **TLS/certificate lifecycle:** Self-signed, locally generated certificates are suitable for a demo but not for enterprise trust, renewal, revocation, or load-balanced deployments. Integrate an approved PKI/ACME process and keep private material out of Git.
- **Version drift:** `ansible_version: latest` and the Chef CLI's `current/latest` download reduce reproducibility. Pin Ansible, collections, OS images, packages, and Chef artifacts.
- **Content/configuration defects:** The inline HTML has a malformed closing head tag (`</head>` is represented incorrectly), and the separate `index.html` is not used by the playbook. Consolidate the content source and add content validation.
- **Operational impact of restarts:** Changing SSH and Apache together can cause access loss. Use staged rollout, config tests, serial deployment, and console/out-of-band access.
- **Chef platform lifecycle:** Retaining Chef Automate/Infra Server introduces product support, licensing, resource-sizing, and key-management dependencies that are not documented in this repository.

### Migration Order

1. **Baseline and test harness:** Pin Ansible and the crypto collection, reproduce the Ubuntu 20.04 Vagrant run, and make the existing InSpec HTTPS test pass. Correct handler names and document the current behavior.
2. **Apache HTTPS role:** Extract package, directory, certificate, virtual-host, content, and service logic into an idempotent role with variables and templates. Add config validation and repeat-run/idempotence testing.
3. **TLS hardening:** Integrate `poodle_fix` into the Apache role or a dedicated security role, implement a reviewed protocol/cipher policy, and verify both positive and negative protocol tests.
4. **SSH hardening:** Implement and test the root-login control with safe rollout and platform-specific service/config handling.
5. **Production secret and certificate integration:** Move credentials and certificates to Vault/PKI or an approved external provider, then test renewal and rotation.
6. **Chef platform decision and bootstrap replacement:** Last, either retire the two Chef bootstrap scripts or create a separately governed Ansible role for Chef Automate/Infra Server with pinned artifacts, secure bootstrap credentials, sizing, backup, and recovery procedures.

### Assumptions

- The requested destination is Ansible; the repository's existing Ansible playbooks are treated as the authoritative workload rather than evidence of missing Chef cookbooks.
- No unlisted external cookbooks, roles, inventories, variable files, certificates, or CI pipelines are assumed to exist.
- Ubuntu 20.04 is the initial target because it is explicitly declared in `kitchen.yml`; its support status and the required replacement release must be confirmed.
- The RHEL 8 STIG identifiers in the SSH InSpec profile describe compliance intent, not a confirmed RHEL deployment target.
- Vagrant is used for testing, but its provider and production virtualization platform are unknown.
- The self-signed certificate and Hello World site are demonstration assets; production certificate ownership, DNS, trust requirements, and application content are not specified.
- The desired role of Chef Automate/Infra Server is unclear. It may be part of the migration scope, a legacy demonstration dependency, or an environment bootstrap that should be retired.
- No database, application backend, load balancer, cloud service, or external PKI is represented in the reviewed files.
- The exact Ansible and collection versions, package repository availability, Apache service name, and SSH service name must be validated against the chosen target image.
- Existing PEM files or credentials may already have been generated outside the repository; they should be considered potentially exposed until rotated.
- Team coordination should assign separate owners for target-platform definition, Apache/TLS role implementation, SSH/security controls, secrets/PKI, Chef platform disposition, and CI/acceptance testing. Changes should be reviewed by both infrastructure and security owners, with a staged rollout and rollback plan before production adoption.
