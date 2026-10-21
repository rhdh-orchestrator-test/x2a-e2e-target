# MIGRATION FROM CHEF ECOSYSTEM / EXISTING ANSIBLE EXAMPLES TO ANSIBLE

This repository is a small Chef-oriented example repository whose infrastructure configuration is already expressed primarily as Ansible playbooks. It contains two Ansible scenarios for an Apache HTTPS site, Chef InSpec compliance tests, and shell scripts that install Chef Automate and/or Chef Infra Server. There are no discoverable Chef cookbooks, Puppet modules, Salt states, or PowerShell modules in the supplied tree. Consequently, this is less a large cookbook-to-role conversion and more a consolidation, hardening, and productionization effort.

The migration scope is low in volume but has meaningful security and operational risk because the scripts contain a plaintext password, the playbooks generate self-signed certificates, and the deployment scripts download and execute a current Chef binary directly from the internet. A small team familiar with Ansible, Linux, Apache, and TLS should be able to complete an initial migration in approximately 3–5 working days, including validation. Production hardening, certificate authority integration, CI, and retirement of Chef services should be planned as an additional 1–2 weeks depending on the target platform and ownership approvals.

## Module Migration Plan

This repository contains existing Ansible playbooks and Chef ecosystem support files that need individual migration planning. No conventional Chef cookbook module was found: there is no `recipes/default.rb`, `metadata.rb`, `Berksfile`, or `Policyfile.rb` in the supplied tree.

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that prepares an Ubuntu Apache web server, installs Apache and OpenSSL-related packages, creates a self-signed TLS key/certificate, publishes a Hello World site, configures an HTTPS virtual host, disables the default site, enables the site and SSL module, and restarts services.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Ubuntu `apt` package management, Apache 2.4.41 package pin, TLS 1.2-oriented test coverage, generated key/CSR/self-signed certificate, virtual host configuration, site enablement, and service handlers.

- **poodle_fix**:
    - Description: Ansible playbook intended to remediate insecure Apache SSL protocol configuration by replacing the `SSLProtocol` line with `-all +TLSv1.2` and restarting Apache and SSH.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible YAML playbook
    - Key Features: Apache SSL configuration replacement, TLS protocol restriction, privilege escalation, and service notifications.

- **website_https_verification**:
    - Description: Chef InSpec verification profile for the HTTPS example. It verifies that port 443 is listening, the site returns HTTP 200 and expected content, SSLv3 is disabled, and TLS 1.2 is enabled.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec Ruby DSL
    - Key Features: Network reachability, HTTPS response validation, and protocol-level TLS assertions.

- **ssh_root_login_control**:
    - Description: Chef InSpec compliance control checking that SSH root login is not enabled, with an alternate package assertion and RHEL 8 STIG/CAT I metadata.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec Ruby DSL
    - Key Features: `sshd_config` inspection, OpenSSH package check, STIG/VULID/CCI tags, and high-impact compliance classification.

- **chef_automate_deployment**:
    - Description: Bash bootstrap script that sets host and kernel parameters, downloads the Chef Automate CLI, deploys Chef Automate with Chef Infra Server, and creates a Chef user and organization with generated PEM files.
    - Path: `setup-automate/deploy-automate.sh`
    - Technology: Bash and Chef Automate/Infra Server CLI
    - Key Features: Combined Automate and Infra Server deployment, hostname configuration, `vm.max_map_count` and dirty-page tuning, Chef identity creation, and credential file generation.

- **chef_server_deployment**:
    - Description: Bash bootstrap script that deploys Chef Infra Server without Automate, then creates a Chef user and organization and writes user and validator PEM credentials.
    - Path: `setup-automate/deploy-chef-server.sh`
    - Technology: Bash and Chef Infra Server CLI
    - Key Features: Standalone Chef Server deployment, kernel tuning, hostname setup, organization creation, and PEM credential generation.

### Infrastructure Files

- `README.md`: Repository-level description identifying the content as Chef examples used by marketing and developer-relations materials. Migration consideration: update the documentation to describe the Ansible target architecture and clearly label any retained InSpec checks.
- `chef-and-ansible/README.md`: Explains that the examples use Chef InSpec alongside Ansible for continuous compliance. Migration consideration: preserve the compliance intent while deciding whether InSpec remains the verifier or is replaced/augmented by Ansible assertions, Molecule, Testinfra, or an enterprise compliance scanner.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant, the `ansible_playbook` provisioner, Ubuntu 20.04, and the InSpec verifier against `website_https.yml`. Migration consideration: this is test orchestration rather than a deployable module; validate whether Vagrant remains supported and move repeatable tests to CI/Molecule if appropriate.

## Target Details

- **Operating System**: The deployable website scenario explicitly targets Ubuntu 20.04 through Test Kitchen and uses `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. The SSH InSpec control contains RHEL 8 STIG references, but it does not establish that RHEL is the deployment target. Keep Ubuntu 20.04 as the compatibility baseline for this example and define a separate supported matrix before adding RHEL. Do not assume the pinned Apache package exists unchanged on newer Ubuntu releases.
- **Virtual Machine Technology**: Vagrant is specified as the Test Kitchen driver. The production VM technology is not specified; the shell scripts say on-premises or cloud VM but contain no provider-specific implementation.
- **Cloud Platform**: Not specified. No AWS, Azure, GCP, or cloud metadata integration was identified.

## Migration Approach

### Key Dependencies to Address

- **Ansible runtime and collections**: Pin a tested `ansible-core` version and explicitly declare required collections, particularly `ansible.posix` for key/service/system operations where applicable. Replace legacy short module names with fully qualified names.
- **Ubuntu 20.04 and Apache 2.4.41**: Preserve the baseline initially, but parameterize the OS, Apache package, paths, and service name. Use repository/package pinning only if the exact version is a hard requirement; otherwise test supported security updates.
- **OpenSSL and `community.crypto`**: The playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`. Declare the collection and decide whether self-signed certificates are acceptable only for development. Production should consume certificates from an approved PKI, ACME workflow, or secret store.
- **Apache site/module commands**: Replace raw `a2dissite`, `a2ensite`, and `a2enmod` commands with idempotent Ansible modules or carefully guarded commands. Ensure handlers are notified only after actual changes.
- **Vagrant/Test Kitchen/InSpec**: Retain InSpec as an independent compliance verifier if it is part of the organization’s control framework; otherwise port the functional assertions to Molecule/Testinfra or an equivalent CI test suite. Keep the security control semantics regardless of test tool.
- **Chef Automate and Chef Infra Server**: These are legacy/source-platform dependencies, not required by the Apache Ansible target. Decide explicitly whether they are being retired, retained for compliance verification, or replaced by Ansible Automation Controller/AWX and an organizational observability/compliance platform. Do not silently reproduce Chef Server provisioning in Ansible.
- **Remote download of Chef CLI**: Replace the `curl | gunzip` bootstrap with a pinned, checksum-verified artifact from an approved repository, or remove it if Chef services are being decommissioned.

### Security Considerations

- **Hardcoded credentials**: Both deployment scripts contain `userpassword='password'`. Treat this credential as compromised, rotate it, remove it from source history where policy requires, and use Ansible Vault, an external secret manager, or interactive/CI-provided secrets. Do not place the resulting user or validator PEM files in the repository or unprotected workspace.
- **TLS private keys and certificates**: `website_https.yml` creates `/etc/apache2/certs/apache.key`, CSR, and certificate. The certificate is self-signed and the key file is not explicitly assigned a restrictive mode. Enforce ownership and mode `0600` for private keys, protect generated material, and use trusted certificates for production. Define renewal and revocation procedures.
- **TLS protocol policy**: The intended policy disables SSLv3 and enables TLS 1.2. Validate the effective Apache configuration rather than only editing one line, and establish whether TLS 1.3 should be enabled on the target OpenSSL/Apache version. Add cipher, certificate-chain, hostname, and vulnerability testing.
- **Privilege and remote access**: The website playbook connects as `root` and uses `become`; reduce direct root SSH use, use a controlled administrative account, and document sudo policy. The playbooks restart `sshd` without showing a complete SSH configuration change, so test connectivity and use a safe serial/rollback strategy.
- **Configuration permissions**: Certificate directory and Apache configuration are created with modes that should be reviewed for operational correctness. Apply least privilege and avoid exposing private keys through task output or facts.
- **Supply-chain security**: The shell scripts download a changing `latest` Chef binary over HTTPS and execute it. Pin versions, verify checksums/signatures, use an internal mirror, and restrict outbound access where possible.
- **Compliance scope**: The InSpec SSH control references RHEL 8 STIG identifiers while the tested platform is Ubuntu 20.04. Map the control to the actual OS benchmark and implement the equivalent Ansible hardening without assuming the package assertion is valid: the control’s alternate assertion says `openssh-server` should not be installed, which conflicts with a server expected to provide SSH and should be reviewed with the compliance owner.

### Technical Challenges

- **Existing playbook correctness and idempotence**: `poodle_fix.yml` notifies `Restart apache2`, but its handler is named `Restart apache`; this can fail handler resolution. `website_https.yml` uses raw enable/disable commands and has handler notifications that restart SSH for changes that primarily affect Apache. Normalize handler names, handlers, and change detection before migration acceptance.
- **OS/version portability**: The playbook pins an Ubuntu-specific Apache package and uses Debian-specific paths/commands. Mitigate with an explicit supported-platform matrix, variables, package facts, and platform-specific task files.
- **Certificate lifecycle**: Generated self-signed certificates are suitable for a lab but not production. Establish ownership, SAN requirements, trust distribution, renewal, and secret delivery before converting this into a reusable role.
- **Testing transition**: Kitchen uses Vagrant plus InSpec and only covers the website scenario in its suite. Build CI around syntax checks, idempotence, service health, TLS tests, and SSH hardening; add tests for failure and rollback paths.
- **Chef platform retirement decision**: The two shell scripts represent a separate control-plane deployment, not an application module. Confirm whether Chef Automate/Infra Server remains in scope. If it is retired, archive or remove the scripts after credential and data-retention planning; if retained, manage it as a separately governed platform rather than coupling it to the Apache role.
- **Broken or weak example content**: The inline HTML contains a malformed closing `</head>` tag, and the Apache configuration mixes legacy and modern directives. Correct and validate configuration with `apachectl configtest` before treating the example as a migration reference.

### Migration Order

1. **Baseline and governance**: Confirm target OS, supported Ansible/collection versions, ownership of Chef services, certificate policy, and secret-management destination. Rotate the exposed example password immediately.
2. **website_https role/playbook**: Convert the playbook into a reusable role with defaults for package versions, hostname, document root, virtual host, certificate source, and TLS policy. Replace inline content with templates/files and make Apache operations idempotent.
3. **poodle_fix hardening**: Fold TLS protocol remediation into the Apache role or a clearly separate hardening role, correct handler names, validate effective configuration, and test safe SSH behavior.
4. **Compliance verification**: Run the existing InSpec tests against the migrated role, then add CI/idempotence checks and resolve the Ubuntu-versus-RHEL control mismatch. Decide whether to retain InSpec or port the tests.
5. **Chef Automate/Infra Server disposition**: Migrate, isolate, or decommission the two bootstrap scripts only after platform owners decide whether Chef remains required. If replacing it, implement Ansible Automation Controller/AWX and approved logging/compliance integrations separately.
6. **Release and handover**: Document inventory, variables, vault workflow, certificate renewal, rollback, test evidence, and operational ownership; perform a staged deployment before production cutover.

### Assumptions

- The supplied tree is complete; no hidden cookbook, dependency, inventory, or CI files were identified.
- No Chef cookbook module exists in this repository despite the Chef branding; the actionable server configuration is already Ansible YAML.
- The intended example target is Ubuntu 20.04, while the RHEL 8 references are compliance metadata rather than proof of the deployment OS.
- Vagrant is used for local testing only; the production virtualization/cloud platform remains unknown.
- Apache, SSH, and TLS are the primary operational scope; application deployment beyond the Hello World page is out of scope.
- The plaintext password is sample data but must still be treated as exposed until rotated and removed from history as required.
- Self-signed certificates are currently lab-only; production trust and certificate lifecycle requirements must be supplied by the security/platform teams.
- The Chef Automate and Chef Infra Server scripts may be examples rather than an active production platform; migration ownership and data requirements are not stated.
- No inventory, host variables, Ansible Vault files, certificate authority configuration, or secret backend is present, so these must be designed rather than inferred.
- Timeline estimates assume a small migration team and access to Ubuntu test VMs; infrastructure provisioning, enterprise approvals, and compliance recertification may extend the schedule.
- Team coordination should assign separate owners for the Ansible role, platform/OS compatibility, PKI and secrets, compliance tests, and Chef platform disposition, with a shared acceptance checklist and staged rollout.
