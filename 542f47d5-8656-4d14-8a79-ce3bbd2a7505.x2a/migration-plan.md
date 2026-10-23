# MIGRATION FROM CHEF TO ANSIBLE

**Executive Summary**: This repository is a Chef examples repository demonstrating the integration of Chef InSpec with Ansible for compliance automation. Notably, **this repository does not contain traditional Chef cookbooks that require migration**. Instead, it contains:

1. **Existing Ansible playbooks** that are already implementation-ready
2. **Chef InSpec verification profiles** used for compliance testing
3. **Infrastructure deployment scripts** for Chef Automate and Chef Infra Server

The "migration" in this context is not about converting Chef recipes to Ansible tasks, but rather understanding how this repository demonstrates using Chef InSpec alongside Ansible. The primary work involves:

- **Documenting the existing Ansible implementation** for reference
- **Preserving Chef InSpec tests** as they are the compliance verification layer
- **Modernizing deployment scripts** if Chef infrastructure tooling is being replaced
- **Extracting reusable patterns** from the demonstration playbooks

**Complexity**: Low - The Ansible automation is already implemented  
**Estimated Timeline**: 1-2 weeks for documentation, validation, and potential modernization of deployment scripts  
**Risk Level**: Minimal - No actual cookbook-to-playbook conversion required

## Module Migration Plan

This repository is structured as a demonstration/examples repository rather than a production infrastructure-as-code repository with Chef cookbooks to migrate.

### MODULE INVENTORY

**No Chef cookbooks are present in this repository.** The file search confirmed no `recipes/*.rb`, `metadata.rb`, `Berksfile`, or `Policyfile.rb` files exist.

### Infrastructure Files

The repository contains the following infrastructure components:

#### Ansible Playbooks (Already Implemented)

- **`chef-and-ansible/website_https.yml`**: 
  - **Purpose**: Complete Apache web server deployment with HTTPS/SSL configuration
  - **Technology**: Ansible (no migration needed)
  - **Features**: 
    - Apache 2.4.41 installation on Ubuntu 20.04
    - Self-signed SSL certificate generation (OpenSSL)
    - Virtual host configuration for HTTPS
    - "Hello World" static website deployment
    - SSL/TLS enablement with certificate management
  - **Migration Considerations**: Already in Ansible format, can be used as-is or as a reference implementation

- **`chef-and-ansible/poodle_fix.yml`**: 
  - **Purpose**: Security hardening playbook to remediate POODLE vulnerability
  - **Technology**: Ansible (no migration needed)
  - **Features**: 
    - Disables SSLv3 protocol in Apache
    - Enforces TLS 1.2 only
    - Service restart handlers for Apache2 and SSH
  - **Migration Considerations**: Security-focused playbook, already in Ansible format

- **`chef-and-ansible/kitchen.yml`**: 
  - **Purpose**: Test Kitchen configuration for testing Ansible playbooks using Chef InSpec
  - **Technology**: Test Kitchen with Ansible provisioner and InSpec verifier
  - **Features**: 
    - Vagrant driver for local testing
    - Ubuntu 20.04 test platform
    - Ansible playbook provisioner
    - Chef InSpec verifier integration
  - **Migration Considerations**: Demonstrates the compliance automation pattern using InSpec with Ansible

#### Chef InSpec Verification Profiles

- **`chef-and-ansible/tests/website_https_verify.rb`**: 
  - **Purpose**: Compliance verification for HTTPS website deployment
  - **Tests**: 
    - Port 443 listening
    - HTTPS endpoint returns 200 status with correct content
    - SSLv3 disabled (POODLE protection)
    - TLS 1.2 enabled
  - **Migration Considerations**: InSpec tests should be **preserved** - they provide compliance verification layer that works with Ansible

- **`chef-and-ansible/tests/ssh_profile.rb`**: 
  - **Purpose**: SSH hardening verification (STIG compliance)
  - **Tests**: 
    - PermitRootLogin disabled
    - Aligned with RHEL-08-000227 STIG (CAT I severity)
  - **Migration Considerations**: Security compliance test, should be preserved and integrated into CI/CD pipeline

#### Deployment Scripts

- **`setup-automate/deploy-automate.sh`**: 
  - **Purpose**: Bash script to deploy Chef Automate and Chef Infra Server
  - **Features**: 
    - Configures hostname and kernel parameters
    - Downloads and deploys Chef Automate CLI
    - Creates Chef Server user and organization
    - Hardcoded credentials (security concern)
  - **Migration Considerations**: If migrating away from Chef infrastructure, this script becomes obsolete. If retaining Chef InSpec, may need modernization (remove hardcoded credentials, parameterize configuration)

- **`setup-automate/deploy-chef-server.sh`**: 
  - **Purpose**: Bash script to deploy Chef Infra Server only (without Automate)
  - **Features**: Similar to deploy-automate.sh but deploys only Infra Server
  - **Migration Considerations**: Same as deploy-automate.sh - evaluate if Chef Server infrastructure is still needed for InSpec testing

#### Documentation and Static Files

- **`README.md`**: Root repository documentation explaining this is a Chef examples repository
- **`chef-and-ansible/README.md`**: References white paper "Using Chef InSpec to Achieve Compliance Automation with Ansible"
- **`chef-and-ansible/index.html`**: Simple HTML test page for web server verification

### Target Details

Based on the analysis of the existing Ansible playbooks and Test Kitchen configuration:

- **Operating System**: Ubuntu 20.04 LTS (explicitly defined in kitchen.yml and playbooks target `apt` package manager)
- **Virtual Machine Technology**: Vagrant (for local testing as defined in kitchen.yml driver configuration)
- **Cloud Platform**: Not specified - playbooks are cloud-agnostic, can run on any platform with Ubuntu 20.04

## Migration Approach

### Key Dependencies to Address

**Chef InSpec (latest version)**: 
- **Current Use**: Compliance verification and testing framework
- **Migration Strategy**: **Do NOT replace** - Chef InSpec is the compliance automation tool being demonstrated. It works alongside Ansible as a verification layer. Continue using InSpec for compliance testing while using Ansible for configuration management.

**Test Kitchen (with ansible_playbook provisioner)**:
- **Current Use**: Testing framework orchestration
- **Migration Strategy**: Can be retained or replaced with Molecule (Ansible's native testing framework). Molecule provides similar functionality with better Ansible integration.

**OpenSSL Python libraries (python3-openssl)**:
- **Current Use**: Ansible's openssl_* modules for certificate generation
- **Migration Strategy**: Already using Ansible modules, no change needed. Ensure `community.crypto` collection is available in target environment.

**Vagrant**:
- **Current Use**: Local VM provisioning for testing
- **Migration Strategy**: Retain for local development/testing or replace with containers if preferred

### Security Considerations

**Hardcoded Credentials in Deployment Scripts**:
- **Location**: `setup-automate/deploy-automate.sh` and `deploy-chef-server.sh`
- **Issue**: Username, password, email, and organization names are hardcoded
- **Migration Approach**: 
  - If these scripts are to be retained, refactor to use environment variables or Ansible Vault
  - Convert scripts to Ansible playbooks with encrypted vars
  - Example: `ansible-vault encrypt_string 'password' --name 'chef_user_password'`

**SSL/TLS Certificate Management**:
- **Current State**: `website_https.yml` generates self-signed certificates
- **Migration Approach**: 
  - For production, replace with proper CA-signed certificates or Let's Encrypt integration
  - Use Ansible Vault to encrypt private keys: `ansible-vault encrypt files/apache.key`
  - Consider using certificate management solutions (HashiCorp Vault, cert-manager)

**SSH Security Configuration**:
- **Current State**: InSpec test verifies PermitRootLogin is disabled
- **Migration Approach**: 
  - Ensure Ansible playbooks actively configure SSH hardening (currently only tested, not enforced)
  - Add SSH configuration tasks to playbooks to enforce security baseline
  - Use Ansible's `ansible.posix.sshd_config` module for declarative SSH configuration

**Vault/Secrets Management**:
- No Chef encrypted data bags, Chef Vault, or similar secrets management detected in the existing code
- The deployment scripts contain plaintext credentials (5 credential instances: username, longusername, useremail, userpassword, orgname)
- Recommendation: Implement Ansible Vault for any sensitive data in production deployments

### Technical Challenges

**Challenge 1: Repository Purpose Misalignment**
- **Description**: This repository is not a traditional infrastructure-as-code repository but a examples/demonstration repository. It's designed to show integration patterns, not production deployments.
- **Mitigation Strategy**: 
  - Clarify with stakeholders whether this repository needs "migration" or if it's reference material
  - If it's reference material, focus on extracting patterns and documenting lessons learned
  - If production systems were built from these examples, locate the actual production repositories for migration

**Challenge 2: Chef InSpec Dependency**
- **Description**: The repository's value proposition is demonstrating Chef InSpec with Ansible. "Migrating away from Chef" would eliminate the core purpose.
- **Mitigation Strategy**: 
  - Recognize that Chef InSpec is a best-in-class compliance testing tool that complements Ansible
  - Keep using InSpec for compliance verification (CIS benchmarks, STIG, custom controls)
  - Focus migration efforts on removing Chef Server/Automate dependencies if desired, not InSpec

**Challenge 3: Test Kitchen vs Ansible Native Testing**
- **Description**: Test Kitchen is Chef ecosystem tooling; Ansible has native alternatives (Molecule)
- **Mitigation Strategy**: 
  - Evaluate if team prefers Molecule for consistency with Ansible ecosystem
  - Both tools support InSpec as verifier, so InSpec tests can be reused
  - Migration path: Convert kitchen.yml to molecule.yml, retain InSpec tests unchanged

**Challenge 4: Deployment Script Modernization**
- **Description**: Bash scripts for Chef infrastructure deployment are imperative and contain hardcoded values
- **Mitigation Strategy**: 
  - If Chef Server/Automate infrastructure is still needed, convert bash scripts to Ansible playbooks
  - Use Ansible's URI/get_url modules instead of curl
  - Parameterize all configuration with Ansible variables and Vault for secrets
  - If Chef infrastructure is being decommissioned, document the InSpec standalone installation process

### Migration Order

Given the unique nature of this repository, the "migration" is more about modernization and documentation:

**Phase 1: Assessment and Documentation (Week 1)**
1. **Clarify repository purpose** with stakeholders - is this production code or reference examples?
2. **Document existing Ansible playbooks** - they are already complete and usable
3. **Validate InSpec tests** - ensure they run successfully against current playbooks
4. **Inventory actual production systems** - if these examples were used as templates

**Phase 2: Modernization (Week 2)**
1. **Security remediation** - remove hardcoded credentials from deployment scripts
2. **Optional: Convert deployment scripts to Ansible** - if Chef infrastructure is still needed
3. **Optional: Migrate to Molecule** - if Test Kitchen is considered a blocker
4. **Enhance playbooks** - add SSH hardening tasks to match InSpec test expectations

**Phase 3: Knowledge Transfer (Ongoing)**
1. **Document the compliance automation pattern** - InSpec + Ansible integration
2. **Create runbooks** - how to use these examples in production contexts
3. **Extract reusable roles** - convert playbooks to roles if they'll be reused

### Assumptions

1. **Repository Purpose**: Assuming this is an examples/demonstration repository, not a production infrastructure codebase. If production systems were built from these examples, the actual production repositories need to be identified and migrated separately.

2. **Chef InSpec Retention**: Assuming the organization wants to retain Chef InSpec for compliance testing, as it's a best-in-class tool that works well with Ansible. If the requirement is to eliminate all Chef products, alternative compliance tools (OpenSCAP, Rudder, custom Ansible checks) would need to be evaluated.

3. **Target Environment**: Assuming Ubuntu 20.04 is the current target OS. If migrating to other distributions (RHEL, Amazon Linux), playbooks will need package manager adjustments (apt → yum/dnf).

4. **Chef Infrastructure**: Assuming Chef Server and Chef Automate deployment scripts may become obsolete if the organization is moving away from Chef for configuration management. However, Chef Automate can still be valuable for InSpec reporting and compliance dashboards even with Ansible.

5. **Testing Framework**: Assuming Test Kitchen usage is acceptable, or that migration to Molecule is optional based on team preference. Both frameworks support the InSpec verification pattern.

6. **Network Environment**: Assuming playbooks will run in environments with internet access for package downloads. Air-gapped environments would require local package repositories and modified playbooks.

7. **SSL Certificates**: Assuming self-signed certificates are acceptable for testing/demo purposes. Production deployments would need proper certificate management strategy.

8. **No Hidden Cookbooks**: Assuming the file tree and search results are complete - no Chef cookbooks exist in subdirectories that weren't shown. If cookbooks exist elsewhere, they would need to be included in the migration scope.

9. **Single Team Ownership**: Assuming a single team owns this repository. If multiple teams contribute, coordination and communication plans would need to be more detailed.

10. **Version Control**: Assuming this repository is under version control (Git) and migration work will follow standard branching/PR workflows for any changes made.

## Conclusion

This repository represents an **already-migrated state** for configuration management (Ansible playbooks exist) with Chef InSpec as the compliance verification layer. The primary value is demonstrating the integration pattern between Ansible and InSpec.

**Recommended Actions**:
1. Use existing Ansible playbooks as-is or as reference implementations
2. Preserve and continue using Chef InSpec for compliance automation
3. Modernize deployment scripts by removing hardcoded credentials
4. Document this repository's role as examples/reference material
5. Identify actual production infrastructure repositories if they exist separately

**No traditional Chef-to-Ansible cookbook migration is required for this repository.**
