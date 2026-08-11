# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for demonstration purposes, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on standardizing all automation to Ansible while preserving the compliance testing capabilities currently provided by Chef InSpec.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium
**Primary Technologies**: Chef InSpec, Ansible Playbooks, Bash scripts for Chef server deployment

## Module Migration Plan

This repository contains Chef InSpec tests, Ansible playbooks, and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **deploy-automate**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `chef-and-ansible/index.html`: Simple HTML file used for testing website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Integrate with Molecule for testing
  - Option 4: Keep InSpec as a testing tool but manage it with Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - Ansible-compatible CI/CD pipeline (Jenkins, GitHub Actions, etc.)

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLS 1.2 remains enabled and older protocols remain disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: Preserve the SSH security controls verified by the InSpec tests
  - Ensure root login remains disabled in the migrated solution

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing requires careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert or ansible.builtin.shell with grep/awk for complex validations

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely replaced
  - Mitigation: Create Ansible roles for infrastructure management that were previously handled by Chef

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Review and refactor according to Ansible best practices
   - Convert to roles for better reusability

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Medium complexity
   - Convert to Ansible-native testing or integrate InSpec with Ansible

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity
   - Replace with Ansible roles for infrastructure management
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and not a production deployment
2. The InSpec tests are used for validation only and not part of a larger compliance framework
3. There are no external dependencies or integrations not visible in the repository
4. The hardcoded credentials in the deployment scripts are for demonstration only
5. The Test Kitchen configuration is used for local testing only
6. There are no specific performance requirements for the migrated solution
7. The Apache configuration is relatively simple and doesn't include complex customizations
8. The self-signed certificates are acceptable for the use case (not production)