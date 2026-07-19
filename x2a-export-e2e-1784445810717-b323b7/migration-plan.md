# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec (tests) and Ansible (playbooks)
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **chef-and-ansible/tests**:
    - Description: InSpec test files for compliance validation
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS website verification, SSH security compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible integration with InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be preserved as-is in the migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Needs conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Needs conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Needs conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs conversion to Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider maintaining InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated solution.
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled. This check should be preserved in the migrated testing framework.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates in the website_https.yml playbook should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks while maintaining the same level of compliance validation.
  - Mitigation: Create a mapping of InSpec resources to Ansible modules/assertions and validate each test case individually.

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem for Chef Automate features.
  - Mitigation: Clearly identify which Chef Automate features are actually being used and find targeted replacements rather than a one-to-one replacement.

### Migration Order

1. **Ansible Playbooks** (Low risk): Preserve existing Ansible playbooks (website_https.yml, poodle_fix.yml) as they are already in the target format.
   
2. **InSpec Tests** (Moderate complexity): Convert InSpec tests to Ansible-compatible testing frameworks, ensuring they validate the same compliance requirements.
   
3. **Chef Deployment Scripts** (High complexity): Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks, replacing Chef-specific functionality with Ansible alternatives.

### Assumptions

1. The primary goal is to standardize on Ansible as the configuration management tool, eliminating the dependency on Chef.
   
2. The InSpec tests are used primarily for compliance validation and can be replaced with equivalent functionality in the Ansible ecosystem.
   
3. The Chef Automate and Chef Infra Server deployment is for demonstration purposes and not a production deployment with complex configurations.
   
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
   
5. The existing Ansible playbooks are working correctly and do not need functional changes, only integration with new testing frameworks.
   
6. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.