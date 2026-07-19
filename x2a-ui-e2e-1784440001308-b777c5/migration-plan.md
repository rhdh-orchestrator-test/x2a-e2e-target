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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec. Migration considerations include replacing with Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing frameworks:
  - Option 1: Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Molecule with Goss for compliance testing
  - Option 3: Maintain InSpec as a standalone tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Content Collections for configuration management
  - Compliance scanning can be handled by OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL/TLS configuration for Apache. Migration should preserve the security settings:
  - Disabling SSLv3 protocol
  - Enabling only TLSv1.2
  - Self-signed certificate generation

- **SSH Security**: The repository includes SSH security testing:
  - Disabling root login
  - Compliance with security standards (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - SSL/TLS certificate references
  - Migration should implement Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework while maintaining the same level of compliance validation.
  - Mitigation: Use Ansible Molecule with Testinfra or Goss plugins, which provide similar functionality to InSpec.

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting with Ansible-native solutions.
  - Mitigation: Implement Ansible Tower/AWX with compliance reporting plugins or integrate with third-party compliance tools.

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - `website_https.yml` and `poodle_fix.yml` can be preserved as-is
   - Update any references to Chef-specific components

2. **InSpec Tests** (Moderate complexity)
   - Convert `website_https_verify.rb` and `ssh_profile.rb` to Ansible Molecule tests
   - Ensure compliance checks are maintained

3. **Chef Deployment Scripts** (High complexity)
   - Convert `deploy-automate.sh` and `deploy-chef-server.sh` to Ansible playbooks
   - Replace Chef-specific functionality with Ansible equivalents

### Assumptions

1. The primary purpose of this repository is to demonstrate the integration of Chef InSpec with Ansible for compliance automation, not for production deployment.

2. The Chef InSpec tests are used for compliance validation of Ansible-deployed infrastructure, not for Chef-managed infrastructure.

3. The setup-automate scripts are used for demonstration purposes and not for production deployment of Chef Automate.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the migration should be flexible enough to support other environments.

5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.

6. The migration will focus on preserving functionality rather than optimizing for Ansible best practices, though improvements should be made where possible.

7. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with Ansible Vault in the migration.