# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment with Apache2, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website with Apache2. Migration consideration: Keep as-is or refactor to use Ansible collections.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache2. Migration consideration: Keep as-is or refactor to use Ansible collections.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website. Migration consideration: Convert to Ansible Molecule tests or other Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests or other Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-test for module testing
  - Option 3: pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing and development workflow

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for enterprise automation platform
  - Ansible Galaxy for role sharing
  - Git repositories for version control

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS configurations that need to be preserved:
  - Disabling SSLv3 protocol
  - Enabling TLSv1.2
  - Self-signed certificate generation
  - Migration approach: Maintain these security controls in Ansible playbooks

- **SSH Security**: The repository includes SSH security testing:
  - Disabling root login
  - Migration approach: Convert InSpec tests to Ansible-compatible tests while maintaining security checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Challenge 1: InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Use Ansible Molecule which supports multiple verifiers including TestInfra which has similar syntax to InSpec.

- **Challenge 2: Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem.
  - Mitigation: Implement Ansible Tower/AWX for web UI, reporting, and role-based access control.

- **Challenge 3: Maintaining Compliance Testing**: Ensuring the same level of compliance testing is maintained.
  - Mitigation: Map each InSpec control to equivalent Ansible checks, possibly using ansible-lint and custom modules.

### Migration Order

1. **InSpec Tests** (Medium complexity): Convert InSpec tests to Ansible Molecule or TestInfra
2. **Chef Deployment Scripts** (Low complexity): Convert bash scripts to Ansible playbooks
3. **Test Kitchen Configuration** (Low complexity): Replace with Ansible Molecule configuration

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for setting up a test environment.
3. There are no external dependencies or modules beyond what's included in the repository.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. The migration will maintain the same level of compliance testing and security controls.
7. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be kept largely as-is.