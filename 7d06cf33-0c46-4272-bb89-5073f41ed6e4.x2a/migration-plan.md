# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks focused on demonstrating compliance automation, along with bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for web server configuration and security compliance. The estimated migration timeline is short (1-2 weeks) due to the limited number of components and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible-module**:
    - Description: Demonstration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL security compliance testing

- **setup-automate-module**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure web server. Already in Ansible format, can be directly incorporated into the migrated solution.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Already in Ansible format, can be directly incorporated into the migrated solution.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS website functionality. Needs migration to Ansible Molecule tests or standalone InSpec tests.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance. Needs migration to Ansible Molecule tests or standalone InSpec tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs replacement with Ansible playbook for alternative compliance solution.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs replacement with Ansible playbook for alternative infrastructure management.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and package versions in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with either:
  1. Continue using InSpec as a standalone tool integrated with Ansible workflows
  2. Migrate to Ansible's built-in assert module for basic tests
  3. Use Ansible Molecule for testing infrastructure

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  1. Ansible Tower/AWX for infrastructure management
  2. Compliance solution like OpenSCAP integrated with Ansible

### Security Considerations

- **SSL Configuration**: The repository includes specific SSL hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the Ansible migration.
  - Migration approach: Preserve the existing Ansible tasks in poodle_fix.yml

- **SSH Security**: The repository includes SSH security compliance tests. Ensure these security checks are maintained.
  - Migration approach: Convert InSpec SSH tests to Ansible assert tasks or maintain as standalone InSpec tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification methods.
  - Mitigation strategy: Either maintain InSpec as a standalone tool or develop equivalent Ansible assert tasks.

- **Chef Automate Replacement**: Identifying and implementing a suitable replacement for Chef Automate's compliance capabilities.
  - Mitigation strategy: Evaluate Ansible Tower/AWX with integrated compliance solutions like OpenSCAP.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk as they're already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity to convert to Ansible testing framework
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions on compliance tooling

### Assumptions

1. The primary purpose of this repository is demonstration, not production deployment
2. The InSpec tests are essential to the compliance strategy and need equivalent functionality in the migrated solution
3. A replacement for Chef Automate's compliance capabilities is required
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained in the migrated solution
6. The repository does not contain actual Chef cookbooks, only InSpec tests and Ansible playbooks
7. The migration will maintain the same level of automation for deployment and testing