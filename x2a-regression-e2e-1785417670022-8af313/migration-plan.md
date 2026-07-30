# MIGRATION FROM ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The migration scope is minimal, as the repository primarily consists of example Ansible playbooks that are already in the target format. The focus will be on standardizing the existing Ansible content and integrating the InSpec testing capabilities into a pure Ansible workflow.

Estimated timeline: 1-2 days for a single developer to complete the migration, as the codebase is small and already primarily in Ansible format.

## Module Migration Plan

This repository contains Ansible playbooks with Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables only TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert tasks
  - Option 2: Use Ansible Molecule with testinfra for testing
  - Option 3: Keep InSpec as a testing tool but integrate it with Ansible-native workflows

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the playbooks
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration approach: Convert InSpec test to Ansible assert tasks or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Testing**: The repository demonstrates using Chef InSpec for compliance testing with Ansible. The main challenge is finding an equivalent testing framework within the Ansible ecosystem.
  - Mitigation strategy: Evaluate Ansible Molecule with testinfra as a replacement, or maintain InSpec as a separate testing tool

- **Bash Script Conversion**: The Chef Automate and Chef Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create Ansible roles for Chef Automate and Chef Server deployment, using the existing bash scripts as a reference

### Migration Order

1. Convert InSpec tests to Ansible-compatible testing framework (low risk, foundation for testing)
2. Standardize existing Ansible playbooks (low complexity, already in Ansible format)
3. Convert bash deployment scripts to Ansible playbooks (moderate complexity)

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment
2. The InSpec tests are intended to show compliance automation capabilities rather than being comprehensive
3. The bash scripts for Chef deployment are examples and may require customization for production use
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No external dependencies or complex infrastructure are required beyond what's explicitly defined in the repository