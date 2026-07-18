# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Migration consideration: Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality and security. Migration consideration: Convert to Ansible Molecule tests or other Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests or other Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook for infrastructure deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook for infrastructure deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Ansible Test Kitchen plugin if maintaining Test Kitchen is preferred

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for web UI and job scheduling
  - Ansible Galaxy for role sharing
  - GitLab/GitHub for version control and CI/CD

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. Migration should maintain these security standards.
  - Migration approach: Preserve the existing Ansible tasks for SSL configuration.

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assert modules or Molecule verify phase.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in the playbooks
  - Migration approach: Replace hardcoded credentials with Ansible Vault and implement proper certificate management.

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Use Ansible Molecule's verify phase with Python-based tests or Testinfra.

- **Chef Automate Functionality Replacement**: Ensuring all Chef Automate functionality is properly replaced with Ansible Tower/AWX.
  - Mitigation strategy: Carefully map Chef Automate features to Ansible Tower/AWX and identify any gaps that need custom solutions.

### Migration Order

1. **Ansible Playbooks** (low risk, high value): Preserve existing Ansible playbooks (website_https.yml, poodle_fix.yml) with minimal changes.
2. **InSpec Tests** (moderate complexity): Convert InSpec tests to Ansible Molecule or other Ansible-compatible testing framework.
3. **Chef Deployment Scripts** (high complexity): Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications.
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
4. The deployment scripts are examples and may contain placeholder credentials that would be replaced in a production environment.
5. The migration will focus on preserving functionality rather than optimizing the existing code.
6. The InSpec tests are the primary focus of the migration, as they represent the Chef-specific components that need to be converted to Ansible-compatible solutions.