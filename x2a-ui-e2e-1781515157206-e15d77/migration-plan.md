# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components focused on compliance automation and infrastructure deployment. The migration scope is relatively small, consisting primarily of:

1. Chef InSpec compliance profiles used alongside Ansible playbooks
2. Ansible playbooks for web server configuration
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary focus will be on converting InSpec tests to Ansible-compatible testing frameworks and consolidating the Chef server deployment scripts into Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec profiles and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec profile for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **ssh_profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security control with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Use ansible-test for validation
  - Option 3: Maintain InSpec as a standalone tool called from Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure code
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace Chef server deployment with:
  - Ansible playbooks for configuration management
  - AWX/Ansible Tower for centralized control and compliance reporting

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the POODLE fix playbook
  - Ensure TLS 1.2+ is enforced in the migrated Ansible roles
  - Maintain proper certificate generation and management

- **SSH Security Controls**: The SSH compliance profile must be converted to equivalent Ansible checks
  - Consider using ansible-lint with custom rules to enforce SSH security standards
  - Implement equivalent controls in Ansible roles that configure SSH

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup-automate scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to an Ansible-compatible testing framework
  - Mitigation: Use Molecule with testinfra or maintain InSpec as a standalone tool

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec profiles
  - Mitigation: Document compliance controls in Ansible role metadata and README files
  - Consider using ansible-lockdown roles which maintain compliance metadata

- **Chef Server Functionality**: Replacing Chef Server's organization and user management
  - Mitigation: Use AWX/Tower for team-based access control and inventory management

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize existing Ansible code
   - Add documentation and role structure

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Integrate into the website_https role as a security hardening task
   - Add conditional logic for applying the fix

3. **InSpec tests** (moderate complexity)
   - Convert to Molecule/testinfra tests or maintain as standalone tests
   - Ensure all compliance checks are preserved

4. **Chef Automate deployment scripts** (high complexity)
   - Create Ansible playbooks for server configuration
   - Implement Ansible Vault for credential management
   - Document migration path for existing Chef users

### Assumptions

1. The primary purpose of this repository is demonstration/example code rather than production infrastructure
2. The InSpec profiles are used for compliance validation of infrastructure deployed by Ansible
3. There are no additional Chef cookbooks or recipes beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. There are no external dependencies or integrations not visible in the repository
7. The migration will consolidate to pure Ansible without maintaining Chef components
8. Test Kitchen is only used for development/testing and not for production deployments