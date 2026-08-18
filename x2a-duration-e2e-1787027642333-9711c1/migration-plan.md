# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment shell scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining Chef InSpec tests for compliance validation

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository primarily contains shell scripts and simple Ansible playbooks

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for compliance validation
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash shell scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for validating SSH security configuration
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Maintain as-is for compliance testing or consider migrating to Ansible's built-in assert module for simpler tests
- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that accomplish the same server setup

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests validate SSH security configurations. Maintain these tests and implement corresponding Ansible tasks
- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly - consider using Ansible's crypto modules

### Technical Challenges

- **Chef InSpec Integration**: Determine whether to maintain Chef InSpec for testing or migrate to native Ansible testing tools
  - Mitigation: If keeping InSpec, ensure proper installation and execution from Ansible
  - Alternative: Convert InSpec tests to Ansible assert statements or Molecule tests

- **Chef Automate/Server Deployment**: Converting shell scripts to idempotent Ansible playbooks
  - Mitigation: Use Ansible's package, service, and command modules with proper state checking

### Migration Order

1. **setup-automate shell scripts** (Priority 1)
   - Convert to Ansible playbooks with proper variable management and Ansible Vault for secrets
   - Implement idempotent deployment of Chef Automate/Infra Server or alternative configuration management solution

2. **Existing Ansible playbooks** (Priority 2)
   - Review and enhance existing Ansible playbooks (website_https.yml, poodle_fix.yml)
   - Ensure best practices and idempotence

3. **Testing Framework** (Priority 3)
   - Decide on testing strategy (keep InSpec or migrate to Ansible native testing)
   - Implement chosen testing approach

### Assumptions

1. The repository is primarily used for demonstration/examples rather than production deployment
2. Chef InSpec is used for compliance testing alongside Ansible, not as the primary configuration management tool
3. The shell scripts are used for initial deployment of Chef Automate/Infra Server, not for ongoing configuration management
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex Chef cookbooks or recipes are present that would require significant refactoring
6. The hardcoded credentials in the shell scripts are examples and not used in production
7. The existing Ansible playbooks are functional and follow reasonable practices
8. There are no external dependencies or integrations not visible in the repository