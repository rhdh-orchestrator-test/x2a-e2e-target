# MIGRATION FROM CHEF ECOSYSTEM TO ANSIBLE

## Executive Summary

This repository presents a **unique migration scenario**: it does not contain traditional Chef cookbooks requiring migration to Ansible. Instead, it is a demonstration/examples repository that already uses Ansible playbooks (v2.x+ syntax) for configuration management, while leveraging Chef InSpec for compliance testing and verification.

**Key Findings:**
- **No Chef cookbooks exist** - no recipes, metadata.rb, Berksfile, or Policyfile.rb found
- **Ansible playbooks already present** - `website_https.yml` and `poodle_fix.yml` are production-ready Ansible code
- **Chef InSpec used for compliance** - Ruby-based test profiles for SSL/TLS and SSH configuration verification
- **Chef Automate deployment scripts** - Bash scripts for setting up Chef Automate and Chef Infra Server infrastructure

**Migration Assessment:** This repository demonstrates a hybrid Chef InSpec + Ansible workflow. The primary migration consideration is whether to:
1. **Keep the hybrid model** - Continue using Ansible for config management and Chef InSpec for compliance (recommended by the white paper this repo accompanies)
2. **Fully migrate to pure Ansible** - Replace Chef InSpec tests with native Ansible testing frameworks (ansible-test, Molecule, or assert tasks)
3. **Eliminate Chef infrastructure** - Remove Chef Automate/Infra Server deployment scripts if no longer needed

**Estimated Timeline:** 1-2 weeks (primarily documentation and testing framework decisions, not code migration)

**Complexity:** LOW - The configuration management layer is already Ansible; only compliance testing framework decisions remain.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec compliance profiles rather than traditional Chef cookbooks:

### MODULE INVENTORY

**chef-and-ansible/website_https.yml**:
- Description: Ansible playbook for deploying Apache 2.4 web server with HTTPS/SSL configuration, self-signed certificate generation via OpenSSL, and virtual host setup for a "Hello World" test site
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 package installation, OpenSSL private key and CSR generation using ansible.builtin.openssl modules, self-signed certificate creation, SSL virtual host configuration on port 443, automated a2ensite/a2dissite commands, service restart handlers for apache2 and sshd
- **Status:** Already Ansible - no migration required

**chef-and-ansible/poodle_fix.yml**:
- Description: Ansible playbook for remediating the POODLE SSL vulnerability (CVE-2014-3566) by disabling SSLv3 and enforcing TLS 1.2 protocol in Apache SSL configuration
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Uses ansible.builtin.replace module to update /etc/apache2/mods-available/ssl.conf, enforces SSLProtocol -all +TLSv1.2, triggers apache2 and sshd service restarts via handlers
- **Status:** Already Ansible - no migration required

### Compliance Testing Files

**chef-and-ansible/tests/website_https_verify.rb**:
- Description: Chef InSpec compliance profile for validating HTTPS website deployment - verifies port 443 listening state, HTTP 200 response on localhost, SSL/TLS protocol enforcement (SSLv3 disabled, TLS 1.2 enabled)
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec (Ruby DSL)
- Key Features: Port resource checks, HTTP resource with SSL verification bypass for self-signed certs, SSL protocol checks via InSpec SSL resource
- **Migration Consideration:** Could be replaced with Ansible assert tasks, Molecule + Testinfra, or kept as-is for compliance-focused workflows

**chef-and-ansible/tests/ssh_profile.rb**:
- Description: Chef InSpec compliance control for STIG/CCI compliance - ensures SSH root login is disabled per security baseline SRG-OS-000112 (RHEL-08-000227, CAT I severity)
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec (Ruby DSL)
- Key Features: sshd_config resource check for PermitRootLogin setting, package check for openssh-server, full STIG metadata (vulid, ruleid, cci, fixtext), CAT I (Critical) severity rating
- **Migration Consideration:** Could use Ansible's lineinfile or template validation, but InSpec provides richer compliance reporting aligned with STIG frameworks

### Infrastructure Files

- **chef-and-ansible/kitchen.yml**: Test Kitchen configuration using Vagrant driver with ansible_playbook provisioner and InSpec verifier - demonstrates the hybrid Ansible + InSpec workflow for infrastructure testing on Ubuntu 20.04
- **chef-and-ansible/index.html**: Static HTML test file ("Hello, world!") for web server verification
- **setup-automate/deploy-automate.sh**: Bash script for deploying Chef Automate + Chef Infra Server on a single VM (on-prem or cloud) - includes user/org creation, kernel parameter tuning (vm.max_map_count, vm.dirty_expire_centisecs), and automated installation
- **setup-automate/deploy-chef-server.sh**: Bash script for standalone Chef Infra Server deployment (without Automate) - similar to deploy-automate.sh but excludes the Automate product

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly configured in kitchen.yml and package versions). Apache package version pinned to 2.4.41-4ubuntu3.10.
- **Virtual Machine Technology**: Vagrant with VirtualBox (default Vagrant provider, as specified in kitchen.yml driver configuration).
- **Cloud Platform**: Not specified - scripts support both on-premises and cloud VM deployments. The Chef Automate/Infra Server deployment scripts are cloud-agnostic and use hostnamectl for configuration.

## Migration Approach

### Key Dependencies to Address

**None for Ansible playbooks** - The existing Ansible code is self-contained and uses native Ansible modules (apt, copy, file, openssl_*, command, service).

**For Chef InSpec (if replacing):**
- **Chef InSpec gem**: Replace with Testinfra (Python-based), Molecule + Ansible assert, or Serverspec (Ruby alternative)
- **Test Kitchen (kitchen.yml)**: Replace with Molecule for Ansible-native testing workflow, or GitHub Actions/GitLab CI for CI/CD integration
- **InSpec SSL resource**: No direct Ansible equivalent - would require custom fact gathering or openssl command module calls

### Security Considerations

**Credentials and Secrets:**
- **Hardcoded credentials in setup-automate scripts**: Both `deploy-automate.sh` and `deploy-chef-server.sh` contain plaintext passwords (`userpassword='password'`), hostnames, and email addresses
  - **Migration:** Move to Ansible Vault for storing Chef Automate admin credentials, or use cloud secret managers (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
  
**SSL/TLS Configuration:**
- **Self-signed certificates**: The `website_https.yml` playbook generates self-signed certificates for testing purposes
  - **Migration:** For production, integrate with Let's Encrypt via `community.crypto.acme_certificate` module or reference existing certificate management systems
  
**POODLE Vulnerability Remediation:**
- The `poodle_fix.yml` playbook enforces TLS 1.2 only, disabling SSLv3
  - **Best Practice:** Consider enforcing TLS 1.3 where supported (modern Apache/OpenSSL versions), or minimum TLS 1.2 with modern cipher suites

**STIG Compliance:**
- The SSH profile enforces CAT I (Critical) STIG requirement for PermitRootLogin
  - **Migration:** If moving away from InSpec, ensure Ansible playbooks enforce this via lineinfile/template tasks and validate in CI/CD

### Technical Challenges

**1. Compliance Testing Framework Decision:**
- **Challenge:** Chef InSpec provides rich compliance reporting with STIG/CCI metadata that Ansible alone doesn't natively support
- **Mitigation Options:**
  - **Keep InSpec:** Continue the hybrid model as demonstrated in the white paper - Ansible for config, InSpec for compliance auditing
  - **Use Ansible + OpenSCAP:** For STIG compliance on RHEL/CentOS, integrate with SCAP Security Guide
  - **Migrate to Testinfra:** Python-based testing with pytest integration, but less STIG-focused than InSpec
  
**2. Test Kitchen Replacement:**
- **Challenge:** Test Kitchen is Chef ecosystem-specific; Molecule is the Ansible equivalent
- **Mitigation:** 
  - Rewrite `kitchen.yml` as `molecule.yml` with Vagrant driver
  - Use Molecule's verify phase with Testinfra or ansible-lint/ansible-test
  - Retain InSpec by calling it manually in Molecule's verify phase if needed

**3. Chef Infrastructure Elimination:**
- **Challenge:** If migrating away from Chef entirely, the setup-automate scripts become obsolete, but they provision the platform for InSpec reporting
- **Mitigation:** 
  - If keeping InSpec, run it in standalone mode (chef-client local mode or via InSpec CLI)
  - If eliminating Chef, replace with Ansible Tower/AWX for playbook execution and reporting

**4. Ansible Version and Module Updates:**
- **Challenge:** Playbooks use older ansible.builtin namespace syntax (introduced in Ansible 2.10+), and openssl_* modules have been moved to community.crypto collection
- **Mitigation:**
  - Update playbook headers to specify `collections: [community.crypto]`
  - Test against Ansible 2.15+ (current) to identify deprecated module parameters (e.g., apt module bare-value syntax)

### Migration Order

**This repository requires minimal migration, but the recommended workflow is:**

1. **Documentation and Decision (Week 1):**
   - Decide on compliance testing strategy (keep InSpec vs. migrate to Ansible-native)
   - Document the chosen approach and update README.md with clear guidance
   - Review and update Chef Automate deployment scripts if infrastructure is still needed

2. **Ansible Playbook Modernization (Week 1-2):**
   - Update `website_https.yml` and `poodle_fix.yml` to use community.crypto collection explicitly
   - Update Apache package versions to current Ubuntu 20.04/22.04 versions
   - Replace bare apt module syntax with explicit name/pkg parameters for Ansible 2.15+ compatibility
   - Add ansible-lint configuration and resolve any linting issues

3. **Testing Framework Migration (Week 2, if needed):**
   - If eliminating Chef InSpec: Convert .rb test profiles to Testinfra Python tests or Ansible assert tasks
   - If keeping InSpec: Update Test Kitchen configuration or migrate to Molecule with InSpec verifier
   - Create CI/CD pipeline (GitHub Actions, GitLab CI) to run playbooks and compliance tests

4. **Security Hardening (Week 2):**
   - Replace hardcoded credentials in setup-automate scripts with Ansible Vault or secret manager integration
   - Update SSL/TLS configuration to enforce TLS 1.3 minimum (if target environment supports)
   - Add certificate management playbook for production (Let's Encrypt or internal CA)

### Assumptions

1. **Repository Purpose:** This repository is assumed to be a reference/demo repository for the white paper "Using Chef InSpec to Achieve Compliance Automation with Ansible." If this is production infrastructure, different priorities apply.

2. **Chef InSpec Retention:** The white paper's thesis is that Chef InSpec complements Ansible for compliance automation. This plan assumes the organization wants to evaluate whether to keep that hybrid model or fully commit to Ansible-only tooling.

3. **Chef Automate Usage:** The setup-automate scripts suggest an existing Chef Automate infrastructure may be in use for compliance reporting. Migration assumes this infrastructure is either:
   - Still needed (keep scripts, update credentials)
   - No longer needed (remove scripts, migrate reporting to Ansible Tower/AWX)
   - Ambiguous - requires stakeholder clarification

4. **Target Ansible Version:** Migration assumes target Ansible version is 2.10+ (for collections support) and ideally 2.15+ (current stable). The existing playbooks use modern syntax but should be tested against the target version.

5. **Ubuntu Version:** Playbooks target Ubuntu 20.04 (pinned Apache package version 2.4.41-4ubuntu3.10). Migration assumes this version is still supported, or that playbooks will be updated for Ubuntu 22.04 LTS or later.

6. **Test Kitchen Usage:** The kitchen.yml file suggests Test Kitchen is currently used for local testing. Migration assumes development teams are willing to adopt Molecule (Ansible's equivalent) or move testing to CI/CD pipelines.

7. **STIG Compliance Requirements:** The SSH profile includes detailed STIG metadata (CAT I, CCI-000774, RHEL-08-000227). Migration assumes the organization has formal compliance requirements and needs equivalent validation in the migrated solution.

8. **No Production Secrets:** This analysis assumes the repository does not contain production credentials beyond the example/demo credentials in the setup scripts. All discovered passwords appear to be examples ('password', 'jtonello@chef.lab').

9. **Hybrid Model Intent:** Given the repository name "chef-examples" and content focus, this appears to be educational material demonstrating Chef InSpec + Ansible integration, not legacy Chef cookbooks awaiting migration. The "migration" may actually be a decision about standardizing on this pattern vs. pure Ansible.

10. **No External Dependencies:** No Berksfile, Policyfile, or metadata.rb found, confirming this repository has no Chef cookbook dependencies to resolve. All Ansible dependencies are on core/builtin modules except community.crypto (for OpenSSL modules).

11. **Self-Contained Testing:** The InSpec tests use localhost and self-signed certificates, suggesting this is a self-contained testing environment. Migration assumes no external certificate authorities or complex PKI integration is required.

12. **Bash Script Portability:** The deployment scripts use systemctl and assume a systemd-based Linux distribution. Migration assumes target environments are systemd-based (RHEL 7+, Ubuntu 16.04+, etc.).
