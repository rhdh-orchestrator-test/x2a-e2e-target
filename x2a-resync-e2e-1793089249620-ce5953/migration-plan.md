# MIGRATION FROM CHEF-RELATED EXAMPLES AND EXISTING ANSIBLE PLAYBOOKS TO ANSIBLE

This repository is a small demonstration repository rather than a conventional Chef cookbook collection. Its executable configuration is already largely Ansible: two Ansible playbooks configure Apache HTTPS and TLS settings, while Chef-related content is concentrated in Chef InSpec verification tests and shell scripts that install Chef Automate/Infra Server. There are no discovered `recipes/default.rb`, `manifests/init.pp`, PowerShell module manifests, Chef `metadata.rb`, Berkshelf files, or Policyfiles. Consequently, the migration is low in application-scope but requires security remediation and validation of the existing Ansible examples. A focused implementation should take approximately 1–2 weeks, including test conversion, hardening, documentation, and CI validation; replacing the Chef platform bootstrap scripts with Ansible may add another 1–2 weeks depending on whether Chef services are still required.

## Module Migration Plan

This repository contains Ansible playbooks supported by Chef InSpec tests and Chef platform bootstrap scripts that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
Only paths present in the supplied repository tree are listed below.

- **website-https**:
    - Description: An Ansible playbook that installs a pinned Apache 2.4 package on Ubuntu, creates a self-signed certificate and key, deploys a Hello World HTTPS virtual host, enables SSL, and disables the default site.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible YAML playbook
    - Key Features: APT package installation, OpenSSL key/CSR/self-signed certificate generation, Apache virtual host configuration, site/module enablement, service handlers, and HTTPS validation targets.
    - Migration status: Already Ansible; refactor into a role or retain as a playbook after hardening and idempotence review.

- **poodle-fix**:
    - Description: An Ansible playbook intended to restrict Apache SSL protocols to TLS 1.2 and restart Apache and SSH after configuration changes.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Replacement of the Apache SSL protocol directive and service restart notifications.
    - Migration status: Already Ansible; correct handler naming, use fully qualified modules, and validate the target Apache configuration before restarting services.

- **chef-platform-bootstrap**:
    - Description: Shell-based bootstrap procedures for deploying Chef Automate with Chef Infra Server, or Chef Infra Server alone, followed by creation of a Chef user, organization, and PEM credentials.
    - Path: `setup-automate/deploy-automate.sh` and `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Automate/Infra Server CLI
    - Key Features: Hostname and kernel tuning, downloaded Chef Automate CLI, product deployment, organization/user creation, and generated user/validator key files.
    - Migration status: Not a cookbook/module. Decide whether Chef services remain a dependency. If retained, convert bootstrap operations to an Ansible role using controlled downloads and secret handling; if retiring Chef, remove this path after cutover.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples. Update it to describe the Ansible target architecture, supported operating systems, test commands, and retirement or retention of Chef services.
- `chef-and-ansible/README.md`: Explains that Ansible is paired with Chef InSpec for continuous compliance. Replace or supplement this with the Ansible role/playbook ownership model and the chosen Ansible-native compliance strategy.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, an Ansible provisioner, Ubuntu 20.04, and InSpec verification. It is important migration evidence for the test platform, but should be evaluated for replacement by Molecule and a maintained verifier.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec control checking that SSH root login is disabled. Preserve the control as a compliance requirement or translate it into Ansible assertions plus an independent compliance test.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec checks for HTTPS availability, the Hello World response, disabled SSLv3, and enabled TLS 1.2. Retain as acceptance criteria while adding Ansible/Molecule integration tests.
- `setup-automate/deploy-automate.sh`: Chef Automate plus Infra Server bootstrap script; contains platform and credential concerns requiring controlled replacement or retirement.
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server-only bootstrap script with the same concerns.

### Target Details

- **Operating System**: The explicit integration test platform is Ubuntu 20.04. The playbooks use `apt`, Debian/Ubuntu Apache paths (`/etc/apache2`), `a2ensite`, `a2enmod`, and an Ubuntu package version, so Ubuntu/Debian is the primary target. The InSpec control references RHEL 8 STIG identifiers, but that is compliance metadata rather than evidence that the playbook supports RHEL. Do not assume RHEL compatibility without a separate platform implementation.
- **Virtual Machine Technology**: Vagrant is specified by `kitchen.yml`; the underlying provider is not specified. The setup scripts describe deployment on an on-premises or cloud VM but do not identify a cloud or hypervisor.
- **Cloud Platform**: Not specified. No provider SDK, cloud metadata endpoint, or cloud-specific resource configuration was found.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime and collections**: Pin a supported `ansible-core` version and explicitly declare required collections, especially `community.crypto` for the OpenSSL modules if the current module names are not available in the selected runtime. Validate module FQCNs during implementation.
- **Ubuntu 20.04 and Apache 2.4**: Preserve the current Debian-family package/service model initially. Avoid relying on an exact package version unless the package repository is controlled; make the version a variable and test repository availability.
- **Apache utilities**: `a2dissite` and `a2ensite` are imperative commands. Replace them with Ansible modules or guarded commands and ensure the SSL module and site state are idempotent.
- **OpenSSL**: The playbook installs `openssl` and `python3-openssl` and generates a self-signed certificate. For production, replace self-signed certificates with an approved PKI/ACME process and manage renewal.
- **Chef InSpec and Test Kitchen**: These are test dependencies rather than runtime modules. Decide whether to retain InSpec for compliance and add Molecule/Ansible-native integration tests for playbook behavior.
- **Chef Automate CLI and Chef Infra Server**: The shell scripts download the latest CLI from `packages.chef.io` and invoke Chef deployment commands. If Chef remains, pin and verify the artifact and automate the workflow with Ansible; if Ansible replaces Chef entirely, treat these as decommissioning dependencies rather than migration targets.
- **Vagrant**: Retain for local Ubuntu verification only if useful; document the provider and consider containerized or cloud-based Molecule scenarios for broader coverage.

### Security Considerations

- **Hardcoded bootstrap password**: Both setup scripts visibly set `userpassword='password'`. Remove it immediately, use Ansible Vault or an external secret manager, and rotate any credentials that may have been used.
- **Generated Chef credentials**: The scripts write user and organization PEM files (`${username}.pem` and `${orgname}-validator.pem`). Protect them with restrictive permissions, avoid source control and logs, define secure transfer/destruction procedures, and replace them with short-lived or externally managed credentials where possible.
- **TLS private key and certificate**: `website_https.yml` creates `/etc/apache2/certs/apache.key`, CSR, and certificate. The certificate is self-signed and the key path is referenced directly in Apache configuration. Use Ansible Vault or a certificate management system for production keys, set directory/file modes deliberately, and establish renewal and trust distribution.
- **TLS protocol policy**: The intended policy disables SSLv3 and restricts Apache to TLS 1.2. Review whether TLS 1.3 should be enabled on the target Apache/OpenSSL combination, test compatibility, and avoid weakening policy during migration.
- **SSH exposure**: The InSpec test requires root SSH login to be disabled, but the shown playbooks do not enforce `PermitRootLogin no`. Add an explicit, validated SSH hardening role and ensure the deployment account has tested sudo access before restarting SSH.
- **Privilege escalation**: Playbooks use `remote_user: root` and `become: yes`. Standardize on a non-root administrative account with narrowly scoped sudo where operationally possible, and document the bootstrap exception.
- **Unsafe downloads and supply chain**: The setup scripts pipe a download into `gunzip`, fetch the latest artifact without a version or checksum, and execute it with root privileges. Pin versions, verify checksums/signatures, stage artifacts in a trusted repository, and use Ansible `get_url` with validation.
- **Apache configuration safety**: Use `apachectl configtest` before service restarts and preserve rollback behavior. The current virtual-host content includes a malformed HTML closing tag and legacy Apache access syntax (`allow from all` alongside `Require all granted`); validate behavior on the target Apache release.

### Technical Challenges

- **This is not a conventional Chef-to-Ansible conversion**: There are no Chef cookbooks or recipes to translate. The main work is consolidating existing Ansible examples, deciding the future of Chef Automate/Infra Server, and preserving compliance intent.
- **Handler mismatch in `poodle_fix.yml`**: The task notifies `Restart apache2`, but the declared handler is `Restart apache`. This can fail at playbook execution or leave Apache unrestarted. Normalize handler names and add a syntax/integration test.
- **Non-idempotent command usage**: `a2dissite`, `a2ensite`, and `a2enmod` are invoked through `command`. Replace or guard them so repeated runs produce no unnecessary changes and do not fail when the desired state already exists.
- **Cross-platform ambiguity**: The compliance test has RHEL 8 STIG identifiers while the deployment is Ubuntu 20.04-specific. Separate policy controls from platform implementation and create an explicit support matrix.
- **Certificate lifecycle**: Self-signed certificates are suitable for a lab but not a production migration. Define ownership, SAN requirements, trust distribution, rotation, and renewal before promoting the role.
- **Chef platform dependency decision**: Chef Automate/Infra Server may be part of the demonstration rather than a required target. Stakeholders must decide whether Ansible replaces only node configuration or also the Chef management plane.
- **Testing modernization**: Test Kitchen currently provisions through Ansible and verifies with InSpec. Preserve the useful acceptance checks while adding Molecule scenarios, linting, YAML validation, and service/configuration tests in CI.

### Migration Order

1. **Inventory and decision gate**: Confirm that no hidden Chef cookbooks or production dependencies are omitted from this example repository, and decide whether Chef Automate/Infra Server is retained or retired.
2. **Website HTTPS baseline**: Convert `website_https.yml` into a tested Ansible role/playbook, parameterize hostname, package version, certificate source, document root, and vhost settings, and fix file permissions and Apache syntax.
3. **TLS hardening**: Refactor `poodle_fix.yml` into the same Apache role, correct the handler mismatch, add config testing, and validate TLS behavior against the supported Ubuntu versions.
4. **SSH and compliance controls**: Implement SSH root-login hardening as an explicit Ansible role or profile, retain InSpec where required, and add Molecule/CI checks for both SSH and HTTPS requirements.
5. **Chef bootstrap disposition**: If Chef is retained, automate its installation with pinned, verified artifacts and vaulted credentials. If it is being replaced, document and execute a decommissioning plan for the two shell scripts and any generated PEM credentials.
6. **Release and handover**: Run repeatability, reboot, certificate, rollback, and security tests; publish the support matrix and operating runbook; then migrate ownership to the Ansible platform team.

### Assumptions

- The supplied tree is the complete relevant repository and contains no omitted Chef cookbooks, roles, inventories, vault files, or CI pipelines.
- `chef-and-ansible/website_https.yml` and `poodle_fix.yml` are examples intended for Ubuntu 20.04, not production-ready generalized roles.
- The migration target is Ansible for host configuration; the business requirement to retain or remove Chef Automate and Chef Infra Server is currently unspecified.
- Vagrant is used for local testing, but its provider and production VM platform are unspecified.
- Ubuntu 20.04 is the only explicitly supported deployment platform; RHEL support is not inferred from the InSpec STIG identifiers.
- The certificate and key generation is lab behavior. Production certificate authority, DNS/SAN requirements, and renewal mechanisms are not provided.
- The hardcoded Chef user details and password are examples, but they must be treated as compromised until confirmed otherwise and rotated if used.
- No external secret manager, Ansible Vault repository, inventory, group variables, or environment-specific values were provided.
- No network topology, firewall policy, load balancer, DNS, monitoring, backup, or incident-response requirements were supplied.
- The estimated 1–2 week effort assumes a single small environment and accessible test VMs; multi-platform support, production PKI integration, or Chef platform retirement will extend the schedule.
- Team coordination should include separate owners for Ansible implementation, security/compliance controls, PKI/credential management, test infrastructure, and the Chef platform decision, with a shared acceptance checklist based on the existing InSpec controls.
