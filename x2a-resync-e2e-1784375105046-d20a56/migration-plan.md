# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use InSpec alongside Ansible for compliance automation. The migration scope is relatively small, focusing on converting the existing InSpec tests to Ansible-native solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Example showing how to use Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Ansible playbooks with Chef InSpec tests
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website with HTTPS. Can be maintained as-is or refactored to follow Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be maintained as-is or refactored.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs to be converted to Ansible-native testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs to be converted to Ansible-native testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or Molecule for testing
  - For continuous compliance: Consider integrating with tools like Ansible AWX/Tower

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower
  - For centralized management and reporting
  - For role-based access control
  - For compliance reporting

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in the Ansible migration.
  - Migration approach: Maintain the existing OpenSSL tasks but consider using Ansible Vault for storing sensitive information.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert to Ansible tasks that both configure and verify SSH settings.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault.
  - SSL certificates are generated on the fly but should be managed securely.

### Technical Challenges

- **Converting InSpec Tests to Ansible**: InSpec provides a domain-specific language for compliance testing that doesn't directly map to Ansible.
  - Mitigation: Use a combination of Ansible assert module, custom modules, and external tools like ansible-lint.

- **Replacing Chef Automate Functionality**: Chef Automate provides compliance reporting and visualization.
  - Mitigation: Consider using Ansible AWX/Tower with custom dashboards or integrating with tools like Prometheus and Grafana.

### Migration Order

1. **Ansible Playbooks** (Low risk, can be maintained as-is)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Medium complexity)
   - Convert `website_https_verify.rb` to Ansible assertions or Molecule tests
   - Convert `ssh_profile.rb` to Ansible assertions or Molecule tests

3. **Chef Deployment Scripts** (High complexity)
   - Convert `deploy-chef-server.sh` to Ansible playbook
   - Convert `deploy-automate.sh` to Ansible playbook

### Assumptions

1. The primary goal is to eliminate Chef InSpec dependencies while maintaining the same level of compliance automation.
2. The existing Ansible playbooks are functional and follow best practices.
3. There is no requirement to maintain backward compatibility with Chef InSpec.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The deployment scripts are used for setting up development or testing environments, not production systems, given the hardcoded credentials.
6. The migration will include improving security practices, such as removing hardcoded credentials.
7. The current setup uses Vagrant for local testing, which will be maintained or replaced with equivalent functionality.