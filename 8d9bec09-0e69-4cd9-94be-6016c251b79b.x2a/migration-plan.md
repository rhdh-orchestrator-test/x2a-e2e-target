# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is relatively low as most of the infrastructure code is already in Ansible format. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef server deployment scripts with Ansible playbooks.

Estimated timeline: 1-2 weeks for a complete migration, with the majority of time spent on test conversion and validation.

## Module Migration Plan

This repository contains a mix of Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file for testing web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider maintaining InSpec as a standalone testing tool that can work with Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-compatible CI/CD pipeline configurations

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older protocols (SSLv3)
  - Maintain proper certificate handling

- **SSH Hardening**: The SSH security profile tests must be preserved:
  - Root login restrictions
  - Proper authentication methods

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec has rich domain-specific language for compliance testing
  - Ansible's built-in testing capabilities are more limited
  - Solution: Consider using a combination of Ansible assert modules and external testing tools

- **Chef Server Deployment**: Replacing Chef server deployment scripts with Ansible:
  - The current scripts perform specific Chef server setup tasks
  - Solution: Create Ansible roles for Chef server deployment or eliminate the need for Chef server entirely

### Migration Order

1. **website-https playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-fix playbook** (low risk, already in Ansible format)
   - Review and optimize the existing Ansible playbook
   - Consider merging with the website-https role as a security enhancement

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Validate that all security checks are preserved

4. **Chef server deployment scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary goal is to consolidate on Ansible and eliminate Chef dependencies where possible
2. InSpec tests are valuable and their functionality should be preserved in some form
3. The Chef server deployment scripts may still be needed if Chef is used elsewhere in the organization
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The security requirements represented in the InSpec tests are mandatory and must be maintained
7. No complex data structures or external data sources are being used
8. The deployment scripts are used for development/testing environments and not production