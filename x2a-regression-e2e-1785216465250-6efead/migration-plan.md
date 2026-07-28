# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef automation scripts that need to be consolidated into a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with some Chef server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to convert.

**Estimated Timeline**: 1-2 weeks for complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS support, including self-signed certificate generation
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **InSpec**: Convert InSpec tests to Ansible-native testing with:
  - ansible-lint for static analysis
  - testinfra for infrastructure testing
  - ansible-test for module testing

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 only, disabling older protocols. This security hardening should be preserved in the migrated Ansible roles.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be implemented in the migrated Ansible roles.
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Self-signed certificates generated in the website_https.yml playbook
  - Recommendation: Use Ansible Vault to secure credentials

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Create a test mapping document and validate each test case individually.
  
- **Chef Server Deployment**: Converting the Chef server deployment scripts to Ansible will require understanding of Chef server architecture.
  - Mitigation: Create an Ansible role that performs equivalent setup steps, possibly using the `uri` module to interact with Chef APIs.

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Add documentation and variables
   
2. **poodle_fix playbook** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Consider merging with website_https role as a configuration option
   
3. **InSpec tests** (moderate complexity)
   - Convert to equivalent testinfra or other Ansible-compatible testing framework
   
4. **Chef server deployment scripts** (high complexity)
   - Create Ansible roles to replace the bash scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The migration will consolidate all automation into Ansible, removing the need for Chef components.
3. InSpec tests will be replaced with equivalent Ansible-compatible testing frameworks.
4. The Chef server deployment scripts are intended for development/testing environments, not production, given the hardcoded credentials.
5. The existing Ansible playbooks are functional and can be used as a reference for the migration.
6. The repository is primarily for demonstration purposes, as indicated by the README.md.