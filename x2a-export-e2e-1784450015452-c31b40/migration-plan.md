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
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for compliance testing
  - Option 3: Maintain InSpec as a separate tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and UI
  - Ansible Collections for configuration management
  - Compliance scanning can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security controls are maintained in the Ansible migration.
  - Migration approach: Preserve the existing Ansible tasks in `poodle_fix.yml` and `website_https.yml`

- **SSH Security Controls**: The repository includes SSH hardening controls (disabling root login).
  - Migration approach: Convert the InSpec test to Ansible assert or Molecule verification

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed certificates generated in playbooks
  - Migration approach: Replace with Ansible Vault for credential storage

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches.
  - Mitigation: Start with simple tests and gradually convert more complex ones. Consider using Molecule with Testinfra as it's Python-based and integrates well with Ansible.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with Ansible alternatives.
  - Mitigation: Evaluate Ansible Tower/AWX with compliance scanning plugins or integrate with external compliance tools.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `website_https.yml`
   - `poodle_fix.yml`

2. **InSpec Tests** (Moderate complexity)
   - `website_https_verify.rb`
   - `ssh_profile.rb`

3. **Chef Deployment Scripts** (High complexity)
   - `deploy-chef-server.sh`
   - `deploy-automate.sh`

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible rather than production deployment.
2. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure alternatives in production.
3. The Test Kitchen configuration is used for development and testing, not for production deployments.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The migration will preserve the existing Ansible playbooks while replacing Chef-specific components.
6. The repository does not contain any custom Chef cookbooks that would need migration.
7. The self-signed certificates are for testing purposes and would be replaced with proper certificates in production.