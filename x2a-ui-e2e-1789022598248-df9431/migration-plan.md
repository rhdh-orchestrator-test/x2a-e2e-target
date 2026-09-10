# MIGRATION FROM CHEF INFRASTRUCTURE TO ANSIBLE

This repository contains Chef infrastructure deployment scripts and Ansible playbook examples with Chef InSpec compliance testing. The migration scope is limited as the primary configuration management is already implemented in Ansible. The main migration effort involves replacing Chef infrastructure components and InSpec testing with native Ansible solutions.

**Timeline Estimate**: 2-3 weeks
**Complexity**: Low to Medium
**Risk Level**: Low (existing Ansible playbooks reduce migration complexity)

## Module Migration Plan

This repository contains Chef infrastructure deployment scripts and Ansible demonstration playbooks that need migration planning:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL/TLS configuration, virtual host management

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables SSLv3 and enforces TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script - requires replacement with Ansible automation platform
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - requires replacement with Ansible automation platform
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Vagrant driver with Ansible provisioner and InSpec verifier
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS security
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG compliance)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate**: Replace with Ansible Automation Platform (AAP) or AWX for workflow orchestration and compliance reporting
- **Chef InSpec**: Replace with Ansible compliance scanning using ansible-hardening roles or custom compliance playbooks
- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation
- **Chef Infra Server**: Replace with Ansible Automation Platform for centralized automation management

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- **SSH Security Hardening**: InSpec tests verify SSH root login restrictions - ensure equivalent Ansible security hardening
- **Compliance Testing**: InSpec STIG compliance tests need migration to Ansible compliance scanning solutions
- **Credential Management**: Deployment scripts contain hardcoded credentials - implement Ansible Vault for secrets management

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec compliance tests to Ansible native testing requires rewriting test logic
- **Chef Infrastructure Replacement**: Migrating from Chef Automate to Ansible Automation Platform involves significant infrastructure changes
- **Test Framework Migration**: Moving from Test Kitchen to Molecule requires restructuring test scenarios and verification methods
- **Compliance Reporting**: Chef Automate compliance reporting features need equivalent implementation in Ansible ecosystem

### Migration Order

1. **Infrastructure Deployment Scripts** (low risk, high value) - Convert bash deployment scripts to Ansible playbooks for AAP/AWX installation
2. **Compliance Test Migration** (moderate complexity) - Convert InSpec tests to Ansible compliance verification tasks
3. **Test Framework Migration** (high complexity) - Replace Test Kitchen with Molecule for comprehensive testing

### Assumptions

- The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already production-ready and require minimal changes
- Target environment will use Ansible Automation Platform or AWX instead of Chef Automate for centralized management
- Current Test Kitchen/Vagrant testing approach will be replaced with Molecule for role development and testing
- InSpec compliance testing will be replaced with Ansible native compliance scanning solutions
- The Ubuntu 20.04 target platform will remain consistent in the migrated environment
- Hardcoded credentials in deployment scripts will be replaced with Ansible Vault encrypted variables
- Self-signed certificate approach may need enhancement for production environments
- STIG compliance requirements will be maintained through Ansible security hardening roles