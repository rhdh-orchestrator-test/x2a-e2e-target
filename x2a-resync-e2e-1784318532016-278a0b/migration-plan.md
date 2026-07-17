# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with clear functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of a web server
    - Path: chef-and-ansible
    - Technology: Chef InSpec (tests) and Ansible (playbooks)
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS functionality. Needs migration to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs migration to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible's `assert` module for basic testing
  - Option 2: Molecule for comprehensive testing
  - Option 3: Ansible Lint for static code analysis
  - Option 4: Consider keeping InSpec as a standalone tool if it's deeply integrated into workflows

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: AWX/Ansible Tower for enterprise automation
  - Option 2: Ansible Semaphore for lightweight GUI
  - Option 3: GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. This security hardening should be preserved in the migration.
  - Migration approach: Maintain the same security configurations in the Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert to Ansible assertions or continue using InSpec as a standalone tool.

- **Self-signed Certificates**: The playbooks generate self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) for certificate management.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Transition**: Moving from InSpec to Ansible-native testing requires careful mapping of test assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions.

- **Maintaining Compliance Reporting**: InSpec provides rich compliance reporting that may be lost in transition.
  - Mitigation: Evaluate if standalone InSpec should be kept for reporting purposes or if Ansible's reporting capabilities are sufficient.

- **Chef Server Replacement**: The Chef Server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation: Clearly define what aspects of Chef Server are needed in the new environment and map to Ansible Tower/AWX features.

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible): Preserve existing playbooks (website_https.yml, poodle_fix.yml)
2. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible assertions or Molecule tests
3. **Test Kitchen Configuration** (Medium complexity): Replace with Molecule or other Ansible-native testing framework
4. **Chef Deployment Scripts** (High complexity): Convert to Ansible playbooks for deploying alternative automation platforms

### Assumptions

1. The primary goal is to consolidate on Ansible rather than maintaining a hybrid Chef/Ansible environment
2. The InSpec tests are used primarily for validation and not integrated into a larger compliance reporting system
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up test/development environments rather than production systems
4. The hardcoded credentials in the deployment scripts are not used in production environments
5. The Test Kitchen configuration is used primarily for development and testing rather than CI/CD pipelines