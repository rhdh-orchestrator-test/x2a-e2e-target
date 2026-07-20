# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

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
  - Option 1: Ansible's `assert` module for basic compliance checks
  - Option 2: Integration with Molecule for more comprehensive testing
  - Option 3: Use community.general.inspec module to continue using InSpec tests from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline integration
  - Compliance scanning can be handled by OpenSCAP or InSpec run directly from Ansible

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable SSL3. This security practice should be maintained in the migrated solution.
  - Migration approach: Preserve the existing Ansible tasks that configure SSL/TLS settings.

- **SSH Security**: The InSpec profile checks for secure SSH configuration (disabled root login).
  - Migration approach: Convert the InSpec test to Ansible assert statements or continue using InSpec via the community.general.inspec module.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing private keys
  - Count of credentials detected: 2 (username/password in setup scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible assertions may require additional logic.
  - Mitigation: Use the community.general.inspec Ansible module to run existing InSpec tests directly from Ansible.

- **Chef Server Replacement**: The Chef Server deployment scripts need to be replaced with equivalent Ansible functionality.
  - Mitigation: Use AWX/Tower for web UI and job scheduling, GitLab CI/CD or Jenkins for pipeline integration.

### Migration Order

1. **Ansible Playbooks** (Low risk, high value): Preserve existing Ansible playbooks (website_https.yml, poodle_fix.yml) with minimal changes.
2. **InSpec Tests** (Moderate complexity): Convert InSpec tests to Ansible-compatible testing or integrate InSpec with Ansible.
3. **Chef Deployment Scripts** (High complexity): Replace Chef Automate and Chef Infra Server deployment scripts with Ansible playbooks for infrastructure management.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The existing Ansible playbooks are functioning correctly and do not need significant modifications.
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
4. The self-signed certificates generated in the playbooks are for demonstration purposes and not for production use.
5. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
6. The migration will focus on preserving the functionality demonstrated in the repository rather than implementing a full-scale production deployment.