# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

**IMPORTANT FINDING**: This repository does not contain traditional Chef cookbooks requiring migration. Instead, it is a **demonstration repository** that showcases Chef InSpec integration with Ansible for compliance automation. The repository contains:

- **2 Ansible playbooks** (already in target format)
- **2 Chef InSpec test profiles** (for compliance verification)
- **2 Chef infrastructure deployment scripts** (for test environment setup)

**Migration Status**: **NOT APPLICABLE** - No Chef cookbook migration is required. This repository demonstrates the complementary use of Ansible (for configuration management) and Chef InSpec (for compliance testing), which is the recommended modern approach.

**Recommendation**: Retain this repository as-is. It serves as a reference implementation for teams adopting Ansible while leveraging Chef InSpec for compliance automation. The InSpec tests provide value-added compliance validation that should continue to be used alongside Ansible playbooks.

## Repository Analysis

### Current Technology Mix

This repository contains:
1. **Ansible Playbooks** (2 playbooks) - Already in target state
2. **Chef InSpec Tests** (2 test profiles) - Compliance validation (not for migration)
3. **Bash Deployment Scripts** (2 scripts) - Infrastructure setup for Chef Automate/Server

### MODULE INVENTORY

**No Chef cookbooks exist in this repository.** The repository structure shows:

#### Ansible Playbooks (Already Migrated)

- **website_https**:
    - Description: Apache web server deployment with HTTPS configuration, self-signed SSL certificates, and virtual host setup for a "Hello World" test site
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already target format)
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, document root setup at /var/www/helloworld

- **poodle_fix**:
    - Description: SSL/TLS hardening playbook that disables vulnerable protocols and enforces TLS 1.2 for Apache and SSH services
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already target format)
    - Key Features: Apache SSL protocol remediation (disable SSLv3, enforce TLS 1.2), service restart handlers for apache2 and sshd

#### Chef InSpec Test Profiles (Compliance Validation)

- **website_https_verify**:
    - Description: Compliance tests verifying HTTPS service availability, SSL/TLS protocol configuration, and web content deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Purpose: Validates port 443 listening, HTTP 200 response, SSL/TLS protocol compliance (TLS 1.2 enabled, SSLv3 disabled)
    - **Migration Note**: InSpec tests should be retained - they provide automated compliance validation for Ansible-managed infrastructure

- **ssh_profile**:
    - Description: SSH security compliance test ensuring root login is disabled per security baseline requirements
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Purpose: Validates PermitRootLogin configuration (STIG V-38607, CAT I severity)
    - **Migration Note**: InSpec tests should be retained - these security controls are independent of configuration management tools

### Infrastructure Files

- **kitchen.yml**: Test Kitchen configuration using Vagrant driver, Ansible provisioner, and InSpec verifier for integration testing workflow
- **index.html**: Static HTML test content for web server validation
- **deploy-automate.sh**: Bash script for deploying Chef Automate and Chef Infra Server on cloud/on-prem VMs (includes user and organization setup)
- **deploy-chef-server.sh**: Bash script for deploying standalone Chef Infra Server without Automate components

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox/VMware (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified - scripts support both on-premises and cloud deployment (generic VM approach)

## Migration Approach

### Key Dependencies to Address

**No Chef cookbook dependencies exist.** The existing Ansible playbooks have the following requirements:

- **Apache 2.4.41-4ubuntu3.10**: Already pinned in Ansible playbook (apt module)
- **python3-openssl**: Required for openssl_* Ansible modules - already specified in playbook
- **curl, openssl**: Supporting packages already defined in playbook
- **Test Kitchen 2.x+**: For integration testing workflow (if retained)
- **Chef InSpec 4.x+**: For compliance validation (recommended to retain)

### Security Considerations

The repository demonstrates several security practices:

- **SSL/TLS Certificate Management**: 
  - Self-signed certificates generated via Ansible openssl_* modules
  - Private keys stored at /etc/apache2/certs/apache.key with 0640 permissions
  - Migration approach: Consider integrating with organizational PKI or Let's Encrypt for production environments

- **Protocol Hardening**: 
  - SSLv3 explicitly disabled (POODLE vulnerability mitigation)
  - TLS 1.2 enforced in Apache configuration
  - Migration approach: Evaluate TLS 1.3 support for enhanced security posture

- **SSH Security Baseline**:
  - InSpec test validates PermitRootLogin=no (STIG compliance)
  - Migration approach: Extend InSpec profiles to cover additional SSH hardening controls from organizational baseline

- **Credential Management**:
  - Hardcoded credentials found in deploy scripts (username: 'jtonello', password: 'password', email: 'jtonello@chef.lab')
  - **CRITICAL**: These are demonstration values and must be replaced with Ansible Vault or external secret management for production use
  - Migration approach: Implement ansible-vault for sensitive Chef Automate/Server deployment credentials

### Technical Challenges

**No migration challenges exist** as this repository does not contain Chef cookbooks. However, adoption considerations include:

- **InSpec Integration**: 
  - Description: Teams may need guidance on integrating Chef InSpec with Ansible workflows
  - Mitigation: This repository serves as a reference implementation - document the Test Kitchen + Ansible + InSpec pattern for team consumption

- **Test Kitchen with Ansible**:
  - Description: Test Kitchen is traditionally associated with Chef but works well with Ansible provisioner
  - Mitigation: Provide training on kitchen-ansible plugin usage and integration testing workflows

- **Dual-Tool Mindset**:
  - Description: Organizations migrating from Chef may resist using any Chef-branded tools
  - Mitigation: Emphasize that InSpec is vendor-neutral (can test any infrastructure) and complements Ansible rather than competing with it

### Migration Order

**Not applicable** - No migration required. However, for teams adopting this approach:

1. **Phase 1**: Deploy Ansible playbooks (already complete in this repo)
2. **Phase 2**: Integrate InSpec tests into CI/CD pipeline (use existing test profiles)
3. **Phase 3**: Expand InSpec compliance profiles for organizational security baselines

### Assumptions

1. **Repository Purpose**: This is assumed to be a demonstration/examples repository (confirmed by README stating "working examples of Chef related to content created by Technical Product Marketing"), not a production cookbook repository requiring migration

2. **InSpec Retention**: It is assumed that Chef InSpec will continue to be used for compliance validation alongside Ansible, as this is the documented purpose of the repository per the README ("highlight how you can use InSpec alongside Ansible")

3. **Test Environment**: The Chef Automate/Server deployment scripts appear to be for setting up test environments to validate the Ansible + InSpec workflow, not production infrastructure

4. **Hardcoded Credentials**: The credentials in deployment scripts (username: jtonello, password: password) are assumed to be example values for demonstration purposes, not actual production credentials

5. **Ubuntu Target**: While kitchen.yml specifies Ubuntu 20.04, the Ansible playbooks use Ubuntu/Debian-specific package managers (apt) and service names (apache2, sshd), limiting portability to Red Hat/RHEL-based systems without modification

6. **Ansible Version**: The kitchen.yml specifies "ansible_version: latest" which could cause unpredictable behavior across different test runs - consider pinning to a specific Ansible version for consistency

7. **SSL Certificate Strategy**: Self-signed certificates are used for demonstration purposes - production deployments would require integration with organizational PKI or Let's Encrypt automation

8. **Compliance Scope**: The InSpec tests cover only basic security controls (SSH root login, SSL/TLS protocols) - comprehensive production compliance would require expanded test profiles covering the full organizational security baseline

9. **Infrastructure Deployment**: The bash deployment scripts for Chef Automate/Server suggest this repository may be part of a broader Chef ecosystem environment, where Chef tools are used for internal operations while demonstrating Ansible capabilities for customers/users

## Conclusion

**This repository requires no migration work.** It is a working example of the recommended modern approach: using Ansible for configuration management while leveraging Chef InSpec for compliance automation. The repository should be preserved as a reference implementation for teams adopting this hybrid approach.

**Recommended Actions**:
1. Document this repository as an Ansible + InSpec integration pattern for team reference
2. Update deployment scripts to use Ansible Vault for credential management
3. Consider expanding InSpec test profiles to cover additional organizational compliance requirements
4. Pin Ansible version in kitchen.yml for reproducible testing
5. Evaluate TLS 1.3 support and update protocol hardening playbooks accordingly
