# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with straightforward functionality.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment and testing, SSL/TLS compliance verification

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-test for module testing
  - Option 3: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing and development

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - Ansible Collections for configuration management
  - Ansible Content Hub for role and collection management

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL configuration for Apache. Migration should preserve the security hardening that disables SSLv3 and enables only TLSv1.2.
  - Migration approach: Preserve the same configuration parameters in Ansible tasks

- **SSH Security**: The repository includes InSpec tests for SSH security compliance.
  - Migration approach: Convert InSpec tests to Ansible-compatible tests while maintaining the same security checks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the Ansible playbook and should be handled securely
  - Count of credentials detected: 3 (username, password, email in setup scripts)

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance verification.
  - Mitigation strategy: Use Ansible's assert module or Molecule's verifier functionality to implement equivalent tests

- **Chef Automate Replacement**: Determining the appropriate Ansible components to replace Chef Automate functionality.
  - Mitigation strategy: Map Chef Automate features to Ansible Tower/AWX features and implement equivalent workflows

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - `chef-and-ansible/website_https.yml`
   - `chef-and-ansible/poodle_fix.yml`

2. **InSpec Tests** (Moderate complexity)
   - Convert `chef-and-ansible/tests/website_https_verify.rb` to Ansible tests
   - Convert `chef-and-ansible/tests/ssh_profile.rb` to Ansible tests

3. **Chef Deployment Scripts** (High complexity)
   - Convert `setup-automate/deploy-chef-server.sh` to Ansible playbook
   - Convert `setup-automate/deploy-automate.sh` to Ansible playbook

### Assumptions

1. The primary purpose of this repository is to demonstrate the integration of Chef InSpec with Ansible for compliance testing, not for production deployment.

2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible playbooks.

3. The setup-automate scripts are used for demonstration purposes and not for production deployment of Chef Automate.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.

5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.

6. The hardcoded credentials in the setup scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.

7. The migration will preserve the existing functionality while converting to pure Ansible solutions where possible.