# MIGRATION FROM CHEF TO ANSIBLE

This repository contains Chef-related examples and demonstration materials rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with Chef InSpec compliance tests, deployment scripts for Chef infrastructure, and documentation. This represents a **minimal migration effort** focused on consolidating testing frameworks and removing Chef infrastructure dependencies.

## Module Migration Plan

This repository contains demonstration and testing materials that require assessment for consolidation rather than traditional cookbook migration:

### MODULE INVENTORY

**No Chef cookbooks or recipes found for migration.** This repository contains:

- **website_https**: 
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates, SSL/TLS security hardening, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: OpenSSL certificate generation, Apache SSL module activation, virtual host configuration with security controls

- **poodle_fix**:
    - Description: Ansible playbook for SSL/TLS security hardening to address POODLE vulnerability by disabling SSLv3 and enforcing TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL protocol configuration, security compliance remediation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration using Ansible provisioner with InSpec verifier for compliance testing
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL/TLS security validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security control for SSH root login compliance (STIG requirement)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for on-premises/cloud environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/index.html`: Static HTML test content for web server validation

### Target Details

Based on the Ansible playbooks and test configurations:

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions or maintain as standalone compliance tool
- **Test Kitchen with Ansible provisioner**: Consider migration to molecule for Ansible role testing
- **Chef Automate/Infra Server**: Evaluate replacement with Ansible Tower/AWX or maintain for compliance reporting only

### Security Considerations

- **SSL/TLS Certificate Management**: Current implementation uses self-signed certificates - consider integration with proper CA or Let's Encrypt for production
- **SSH Security Hardening**: InSpec controls verify SSH root login restrictions - ensure equivalent Ansible security baseline
- **Apache Security Configuration**: SSL protocol restrictions and virtual host security settings require validation in target environment
- **Credential Management**: Deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault or secure credential store

### Technical Challenges

- **Testing Framework Consolidation**: Decision needed on whether to maintain InSpec for compliance testing or migrate to Ansible-native solutions
- **Infrastructure Deployment**: Chef server deployment scripts may need replacement if Chef infrastructure is being decommissioned
- **Compliance Reporting**: If Chef Automate is used for compliance dashboards, alternative reporting mechanisms may be required

### Migration Order

1. **Compliance Testing Strategy** (immediate priority): Determine whether to maintain InSpec or migrate to ansible-lint, molecule, and custom compliance modules
2. **Infrastructure Consolidation** (low priority): Evaluate need for Chef server infrastructure if only used for these examples
3. **Documentation Updates** (low priority): Update README files to reflect pure Ansible approach if Chef references are removed

### Assumptions

- This repository serves as demonstration/training material rather than production infrastructure
- The Ansible playbooks are already functional and do not require migration
- InSpec tests may be retained for compliance validation even in an Ansible-only environment
- Chef infrastructure deployment scripts may be preserved for environments that still require Chef Automate for compliance reporting
- The target environment specifications are based on the test configuration and may differ in production deployments
- No production workloads depend on the Chef infrastructure deployment scripts
- Security controls implemented in the playbooks meet current organizational security requirements