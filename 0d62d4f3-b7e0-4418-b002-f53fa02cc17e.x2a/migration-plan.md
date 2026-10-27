# MIGRATION FROM CHEF-RELATED EXAMPLES TO ANSIBLE

The repository is primarily a small Chef ecosystem demonstration rather than a collection of Chef cookbooks. No Chef cookbook entrypoints (`recipes/default.rb`), cookbook metadata, Berkshelf files, Policyfiles, or Chef recipes were found. The `chef-and-ansible` directory already contains Ansible playbooks and Chef InSpec verification profiles, while `setup-automate` contains Bash-based deployment scripts for Chef Automate and Chef Infra Server. Consequently, the migration is low in cookbook-conversion effort but still requires decisions about whether the Chef control-plane demonstration is being retired, replaced, or retained during transition.

For the currently visible scope, a focused migration and validation can be completed in approximately 1–2 weeks: several days to establish the Ansible structure and secure variable handling, several days to convert/standardize verification and operational steps, and several days for integration, security review, and documentation. A broader production migration of the Chef server/Automate platform would be a separate infrastructure-retirement project and cannot be estimated from this repository alone.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec compliance tests, but no Chef cookbooks requiring individual recipe migration:

### MODULE INVENTORY

- **website_https Ansible playbook**:
    - Description: Provisions an Apache HTTPS Hello World site on an Ubuntu host, including Apache and OpenSSL-related packages, a self-signed certificate, an SSL virtual host, website content, and service activation.
    - Path: `chef-and-ansible/website_https.yml`
    - Technology: Ansible
    - Key Features: Ubuntu `apt` package installation, RSA/private-key and CSR/certificate generation, Apache virtual-host configuration, HTTPS enablement, and service handlers.
    - Migration status: Already Ansible; refactor into a maintainable role and improve idempotence rather than convert from Chef.

- **poodle_fix Ansible playbook**:
    - Description: Applies an Apache SSL protocol hardening change by restricting configured protocols to TLS 1.2 and restarts Apache and SSH-related services when notified.
    - Path: `chef-and-ansible/poodle_fix.yml`
    - Technology: Ansible
    - Key Features: Targeted configuration replacement and service notification handlers.
    - Migration status: Already Ansible; consolidate with the HTTPS role or retain as a distinct hardening task set after validating the intended handler behavior.

- **SSH root-login InSpec control**:
    - Description: Verifies that SSH root login is not permitted, using both the SSH daemon configuration and a package-based fallback check with security/compliance references.
    - Path: `chef-and-ansible/tests/ssh_profile.rb`
    - Technology: Chef InSpec (Ruby DSL)
    - Key Features: `PermitRootLogin` assertion, OpenSSH package check, STIG/SRG/CCI metadata, and high-impact severity classification.
    - Migration status: Preserve as a compliance requirement and port to Ansible assertions, Molecule verification, or an Ansible-compatible compliance framework; it is not a provisioning module.

- **Website HTTPS InSpec controls**:
    - Description: Verifies that port 443 is listening, HTTPS returns the expected Hello World response, SSLv3 is disabled, and TLS 1.2 is enabled.
    - Path: `chef-and-ansible/tests/website_https_verify.rb`
    - Technology: Chef InSpec (Ruby DSL)
    - Key Features: Port, HTTP response, and TLS protocol checks.
    - Migration status: Retain temporarily as black-box acceptance tests or translate into Ansible/Molecule or external TLS scanning tests.

**CRITICAL PATH VERIFICATION:**
The paths above are present in the supplied repository tree and were confirmed by reading the files. No cookbook path is listed because searches found no `recipes/default.rb` or cookbook metadata. The `.rb` files under `tests/` are InSpec controls, not Chef cookbooks.

### Infrastructure Files

- `README.md`: Repository-level description of Chef examples; migration consideration: update it to describe the supported Ansible workflow and the disposition of the Chef platform examples.
- `chef-and-ansible/README.md`: Explains that the examples demonstrate InSpec alongside Ansible for continuous compliance; migration consideration: make this the authoritative runbook for the target Ansible implementation and verification strategy.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using the Vagrant driver, Ansible playbook provisioner, Ubuntu 20.04, and InSpec verifier; migration consideration: decide whether to retain Test Kitchen for transitional testing or replace it with Molecule and a supported container/VM driver.
- `chef-and-ansible/website_https.yml`: Existing target-state Ansible provisioning playbook; migration consideration: convert ad hoc tasks to roles, variables, templates, and fully qualified modules.
- `chef-and-ansible/poodle_fix.yml`: Existing target-state Ansible hardening playbook; migration consideration: merge with or sequence after HTTPS configuration and verify safe service restart behavior.
- `chef-and-ansible/tests/ssh_profile.rb`: Security acceptance control; migration consideration: preserve its compliance intent and traceability tags in the replacement test suite.
- `chef-and-ansible/tests/website_https_verify.rb`: HTTPS acceptance control; migration consideration: preserve endpoint and protocol assertions independently of implementation.
- `setup-automate/deploy-automate.sh`: Installs Chef Automate and Chef Infra Server, creates a user and organization, and writes key files; migration consideration: treat as legacy control-plane bootstrap, not as a cookbook, and replace or retire only after Ansible ownership and operational workflows are agreed.
- `setup-automate/deploy-chef-server.sh`: Installs Chef Infra Server and creates user/org credentials; migration consideration: isolate as a decommissioning or coexistence concern rather than attempting a direct playbook conversion without requirements.

### Target Details

- **Operating System**: The application configuration targets Ubuntu 20.04, based on Test Kitchen’s platform and use of `apt`, `/etc/apache2`, `a2ensite`, and `a2enmod`. The setup scripts do not specify an OS image and may be intended for an on-premises or cloud Linux VM. Validate the final supported Ubuntu release before implementation; do not silently assume RHEL 9 for this repository.
- **Virtual Machine Technology**: Vagrant is explicitly used by `kitchen.yml`; the underlying production VM technology for the Chef server is not specified.
- **Cloud Platform**: Not specified. The setup scripts state that deployment may be on-premises or in the cloud but contain no provider-specific resources or SDK configuration.

## Migration Approach

### Key Dependencies to Address

- **Ansible**: Already the provisioning technology in the `chef-and-ansible` directory. Pin a supported Ansible/ansible-core version in CI rather than using `latest` from Test Kitchen.
- **Ansible SSL modules/collections**: The playbook uses `openssl_privatekey`, `openssl_csr`, and `openssl_certificate`; confirm the installed collection/version and required Python/OpenSSL dependencies, then use fully qualified module names.
- **Ubuntu 20.04 and APT**: Preserve the current OS/package assumptions initially, but parameterize package versions and determine whether the target should move to a supported Ubuntu LTS. The exact Apache package pin may become unavailable over time.
- **Apache HTTP Server**: Replace shell commands such as `a2ensite`, `a2dissite`, and `a2enmod` with appropriate Ansible modules or carefully controlled commands, and manage configuration with templates/files and handlers.
- **Vagrant/Test Kitchen**: Retain for short-term parity if useful; evaluate Molecule with Vagrant or another VM driver for long-term role testing.
- **Chef InSpec**: Keep during transition as an independent acceptance layer, or map its checks to Molecule/pytest/Ansible assertions and a dedicated TLS scanner. Do not lose the STIG/SRG/CCI traceability in the SSH control.
- **Chef Automate and Chef Infra Server**: These are external Chef platform components bootstrapped by Bash, not cookbook dependencies. Decide whether they remain for compliance reporting during coexistence or are decommissioned after Ansible adoption.
- **Remote access**: Current playbooks use `remote_user: root` with privilege escalation. Replace with a controlled administrative account, SSH keys, and `become: true` in the target inventory.

### Security Considerations

- **Hardcoded credentials in setup scripts**: Both deployment scripts visibly contain a plaintext `userpassword='password'`, user identity data, organization names, and generated PEM filenames. Remove credentials from source immediately, rotate any exposed credentials, and use Ansible Vault, an external secret manager, or injected CI secrets.
- **Generated Chef keys**: `user-create` and `org-create` write user and validator PEM files. Inventory, transfer, retention, and revocation of these keys must be addressed before retiring Chef or running both systems.
- **TLS private keys and certificates**: The website playbook generates `/etc/apache2/certs/apache.key`, CSR, and a self-signed certificate. Protect the private key, use restrictive ownership/mode settings, and replace the self-signed certificate with an approved CA-issued certificate for non-lab environments. Certificate distribution should use Vault or a certificate-management workflow where appropriate.
- **TLS protocol policy**: The InSpec tests require TLS 1.2 and reject SSLv3; the hardening playbook attempts to enforce TLS 1.2. Validate the complete cipher/protocol policy, avoid weakening SSH accidentally, and add tests for TLS 1.3/approved ciphers if required by policy.
- **SSH administration**: The playbooks notify an SSH restart while operating as root, and the InSpec profile checks root login. Use connection-safe rolling changes, ensure a non-root sudo account exists, and test that SSH configuration remains valid before restarting the daemon.
- **File permissions**: Several configuration paths use mode `0640`, including a directory containing private key material. Review directory traversal and key permissions explicitly; certificates, keys, Apache config, and web content should have distinct ownership and modes.
- **Untrusted downloads and supply chain**: The setup scripts stream a “latest” Chef Automate CLI from `packages.chef.io` through `curl` and `gunzip` without visible checksum/signature verification. Pin versions, verify checksums/signatures, and remove this bootstrap dependency if Chef is being retired.
- **Secrets per logical area**: Website configuration uses TLS key material; Chef platform setup uses user passwords and generated user/org PEM credentials. No encrypted data bags, Chef Vault, or environment-secret mechanism was found in the reviewed files.

### Technical Challenges

- **No actual Chef cookbooks are present**: There is no recipe, attributes, metadata, or cookbook dependency graph to translate. Confirm that the repository snapshot is complete and that no external Chef repository is in scope before declaring the migration complete.
- **Existing Ansible is procedural and not fully idempotent**: `command` calls for Apache site/module activation and an inline `replace` should be refactored into roles, templates, and module-based state management. Add change detection and syntax/config validation before handlers restart services.
- **Handler naming/notification consistency**: `poodle_fix.yml` notifies `Restart apache2` while declaring `Restart apache`; this can fail at runtime. Normalize handler names and test notifications in CI.
- **Incorrect or risky service behavior**: Some tasks notify/restart `sshd` after Apache SSL operations even when SSH configuration was not changed. Remove unrelated notifications and use `sshd -t` or equivalent validation before restart.
- **Environment-specific certificate identity**: The CSR uses common name `myhost`, while the virtual host is a generic example. Parameterize hostname, SANs, certificate source, and Apache site data through inventory/group variables.
- **Version drift**: Apache is pinned to an Ubuntu package version that may not exist in all repositories, and the Test Kitchen provisioner requests Ansible `latest`. Establish supported version matrices and reproducible CI images.
- **Test framework transition**: InSpec tests provide useful black-box checks but do not prove Ansible idempotence. Run them during coexistence, then add role-level idempotence and convergence tests before removing them.
- **Chef control-plane disposition**: Replacing server/Automate deployment is organizationally larger than converting a web playbook. Identify compliance reports, node/client credentials, policy data, and integrations before decommissioning Chef services.

### Migration Order

1. **Inventory and scope confirmation**: Confirm that no external cookbooks, Chef policy repositories, environments, or production-specific inventories are omitted. Freeze and rotate exposed example credentials.
2. **Test and baseline the existing Ansible playbooks**: Run the HTTPS playbook and both InSpec controls on Ubuntu 20.04, record expected behavior, and fix the handler mismatch and unsafe/unrelated restarts.
3. **Create an Ansible role structure**: Build a role for Apache HTTPS/site provisioning and a separate hardening role or task set. Introduce inventory variables for hostname, packages, certificate source, site content, and service policy.
4. **Harden secrets and certificates**: Move credentials and sensitive certificate material to Ansible Vault or an approved secret/certificate service; replace self-signed certificates outside lab environments.
5. **Migrate verification and CI**: Keep InSpec for transitional acceptance, add idempotence and syntax checks, and decide whether Molecule or the current Test Kitchen workflow is the supported test harness.
6. **Chef platform coexistence or retirement**: Only after consumers, reports, keys, and integrations are mapped should the team replace or decommission the Chef Infra Server/Automate bootstrap scripts.
7. **Operational handoff**: Document inventories, access controls, rollback, certificate renewal, supported OS/Ansible versions, and ownership; then run a controlled pilot before wider rollout.

### Assumptions

- The supplied tree is the complete migration scope; no external Chef cookbooks or Chef policy repositories are included.
- The `.rb` files are Chef InSpec tests and not Ruby-based Chef recipes.
- The intended managed host is Ubuntu 20.04 or a closely compatible Ubuntu release, although its support lifecycle and final target version need confirmation.
- `myhost`, `automate.chef.lab`, `jtonello`, and related values are examples, but the visible plaintext password must still be treated as compromised until proven otherwise.
- The Chef Automate/Infra Server scripts are demonstration bootstrap assets; their production dependencies, data, integrations, and retirement requirements are unknown.
- A cloud provider, VM platform beyond Vagrant test execution, network topology, DNS, firewall policy, and load-balancer configuration are not specified.
- The certificate workflow is currently lab-oriented and self-signed; production trust and renewal requirements must be supplied by the security/platform teams.
- The target Ansible control node, CI system, inventory source, secret manager, and collection version policy have not been specified.
- The required end state for Chef InSpec is ambiguous: it may be retained for compliance evidence or replaced by Ansible-compatible testing.
- Package versions and TLS requirements shown are examples and require review against the organization’s baseline.
- Migration estimates exclude discovery of omitted production Chef assets, remediation of unrelated infrastructure, and formal compliance re-certification.
