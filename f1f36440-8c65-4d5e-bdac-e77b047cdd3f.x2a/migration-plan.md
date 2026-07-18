# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstrating compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Demonstration of using Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **chef-and-ansible/tests**:
    - Description: InSpec test profiles for compliance verification
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS website verification, SSH security compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Migration consideration: Can be kept as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be kept as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Migration consideration: Convert to Ansible-compatible testing framework like Testinfra or Molecule.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule with Testinfra for more comprehensive testing
  - Option 3: Use Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for CI/CD pipelines
  - Compliance automation can be handled by OpenSCAP with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The repository contains specific SSL/TLS security configurations in the Ansible playbooks and tests:
  - Migration approach: Preserve the same security settings in the Ansible playbooks
  - Ensure the InSpec tests for TLS 1.2 enforcement are converted to equivalent Ansible tests

- **SSH Security**: The repository includes SSH security compliance tests:
  - Migration approach: Convert the InSpec SSH security tests to Ansible-compatible tests
  - Ensure the same security controls are enforced (e.g., disabling root login)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): Replace with Ansible Vault for secure credential storage
  - Self-signed certificates: Maintain the same approach using Ansible's `openssl_*` modules

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Mitigation: Use Testinfra with Python, which provides similar functionality to InSpec
  - Consider using Ansible's built-in modules like `uri`, `command`, and `assert` for simpler tests

- **Chef Automate Replacement**: Finding equivalent functionality in the Ansible ecosystem:
  - Mitigation: Use AWX/Tower for web UI and job scheduling
  - Use GitLab CI/CD or Jenkins for pipeline automation
  - Use OpenSCAP for compliance scanning

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format):
   - `chef-and-ansible/website_https.yml`
   - `chef-and-ansible/poodle_fix.yml`

2. **InSpec Tests** (Moderate complexity):
   - `chef-and-ansible/tests/website_https_verify.rb`
   - `chef-and-ansible/tests/ssh_profile.rb`

3. **Chef Deployment Scripts** (High complexity):
   - `setup-automate/deploy-chef-server.sh`
   - `setup-automate/deploy-automate.sh`

4. **Test Kitchen Configuration** (Low complexity):
   - `chef-and-ansible/kitchen.yml`

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec with Ansible, as indicated in the README.md.
2. The existing Ansible playbooks (`website_https.yml` and `poodle_fix.yml`) are working correctly and can be preserved as-is.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment and are not part of the core functionality.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with secure alternatives in the migration.
7. The self-signed certificates used in the HTTPS website deployment are acceptable for the target environment.