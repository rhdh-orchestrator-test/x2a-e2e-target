# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance and security configurations
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible and InSpec integration. Migration will require converting to Ansible Molecule or another Ansible-native testing framework.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be preserved as-is in the Ansible migration.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website. Will need conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Will need conversion to Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Will need conversion to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need conversion to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Ansible's built-in `assert` module for basic testing
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Ansible Lint for static code analysis
  - Option 4: Consider maintaining InSpec as a separate tool if its capabilities are required

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure these security configurations are preserved during migration.
  - Migration approach: Maintain the same SSL protocol settings (TLSv1.2) and certificate generation in Ansible playbooks.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests to verify the same security controls.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks may lose some of the declarative testing capabilities of InSpec.
  - Mitigation: Consider using a combination of Ansible's assert module and Molecule for testing, or maintain InSpec as a separate tool.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for deploying monitoring and compliance tools that can replace Chef Automate functionality.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible-compatible testing framework
   - Replace Test Kitchen with Molecule

3. **Chef Automate Deployment** (High complexity)
   - Convert Chef Automate deployment scripts to Ansible playbooks
   - Implement alternative compliance and monitoring solutions if needed

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef InSpec tests are used for compliance verification only and do not contain business logic that needs to be preserved.
3. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with secure credential management in the migration.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The self-signed certificates generated in the playbooks are for testing purposes and may need to be replaced with proper certificate management in production.
6. The migration will focus on preserving functionality rather than maintaining exact implementation details.