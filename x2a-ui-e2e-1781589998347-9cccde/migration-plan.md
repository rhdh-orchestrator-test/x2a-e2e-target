# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for web server deployment with HTTPS
2. Chef InSpec profiles for compliance testing
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The primary focus will be on:
- Converting Chef InSpec tests to Ansible-compatible testing frameworks
- Enhancing existing Ansible playbooks
- Converting Chef server deployment scripts to Ansible playbooks

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, self-signed certificates, and a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec profile that verifies HTTPS website deployment and SSL configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (specifically root login settings)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security checks, STIG compliance verification

- **chef-server-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with Testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Continue using InSpec but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for centralized automation
  - Compliance automation using OpenSCAP or similar tools

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks already implement TLS 1.2 and disable insecure protocols. This should be maintained in the migrated solution.
  
- **SSH Security**: The InSpec profile checks for SSH root login restrictions. This should be implemented as an Ansible task and tested with appropriate tools.

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL certificates)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to equivalent testing constructs.
  - Mitigation: Create a mapping document for InSpec to Testinfra/Molecule conversions and implement tests incrementally.

- **Chef Server Deployment**: The Chef server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for Chef server deployment or, preferably, replace with native Ansible infrastructure.

### Migration Order

1. **website_https.yml** (Priority 1 - already Ansible, low risk)
   - Enhance existing Ansible playbook with best practices
   - Add idempotency improvements
   - Implement proper variable handling

2. **poodle_fix.yml** (Priority 1 - already Ansible, low risk)
   - Integrate with website_https playbook as a role or included task
   - Enhance with additional security hardening

3. **InSpec Tests** (Priority 2 - moderate complexity)
   - Convert website_https_verify.rb to Molecule/Testinfra
   - Convert ssh_profile.rb to Ansible security role with testing

4. **Chef Server Deployment** (Priority 3 - high complexity)
   - Create Ansible playbooks to replace shell scripts
   - Implement secure credential handling with Ansible Vault
   - Consider replacing with AWX/Tower deployment

### Assumptions

1. The primary purpose of this repository is for demonstration and examples, not production deployment.
2. The InSpec tests are used for compliance verification of Ansible-deployed infrastructure.
3. The Chef server deployment scripts are used for setting up a test environment.
4. There are no external dependencies or integrations beyond what's visible in the repository.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. No complex state management or data persistence is required.
7. The migration will maintain the same level of security compliance testing.
8. The existing Ansible playbooks can be reused with minimal modifications.