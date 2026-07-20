# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure
- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use ansible-test for basic functionality testing
  - Option 2: Use pytest-ansible for more advanced testing
  - Option 3: Integrate with other compliance tools like OSCAP or Ansible Compliance

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL/TLS settings for Apache. These configurations should be preserved in the migration.
  - Migration approach: Maintain the same SSL/TLS configurations in the Ansible playbooks
  
- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible-compatible tests that verify the same SSH security controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbooks and should be handled securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Research and select the most appropriate Ansible testing framework that can provide similar functionality to InSpec.

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible.
  - Mitigation: Create Ansible roles that perform the same deployment steps as the bash scripts, ensuring proper idempotence.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Update testing configuration from Test Kitchen to Ansible Molecule

3. **Chef Deployment Scripts** (High complexity)
   - Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks.
2. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible playbooks for deploying alternative configuration management or compliance tools.
3. The target environment will remain Ubuntu 20.04 on Vagrant VMs.
4. No additional functionality beyond what exists in the current repository is required.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the Ansible implementation.
6. The self-signed certificates generated in the playbooks are acceptable for the use case and don't need to be replaced with CA-signed certificates.