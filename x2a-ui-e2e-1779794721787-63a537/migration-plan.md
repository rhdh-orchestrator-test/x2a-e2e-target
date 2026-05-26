# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most of the content already in Ansible format. The estimated timeline for full migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use ansible-test for more comprehensive testing
  - Option 4: Consider migrating to Ansible's built-in test framework or Molecule

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security. Ensure this is incorporated into the main Apache configuration role.
- **SSH Security**: The ssh_profile.rb InSpec test checks for SSH root login. Create equivalent Ansible checks or assertions.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider using Ansible's crypto modules or integrating with a certificate authority.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or checks will require understanding the compliance requirements and implementing equivalent checks in Ansible.
  - Mitigation: Use Ansible's assert module for basic checks, and consider ansible-lint for more complex validations.

- **Chef Server Deployment**: The Chef Server deployment scripts need to be converted to Ansible roles.
  - Mitigation: Create an Ansible role that installs and configures Chef Server, or replace with equivalent Ansible functionality.

### Migration Order

1. **website_https.yml** (already in Ansible format, no migration needed)
2. **poodle_fix.yml** (already in Ansible format, no migration needed)
3. **InSpec Tests** (convert to Ansible assertions or Molecule tests)
4. **Chef Deployment Scripts** (convert to Ansible roles or playbooks)

### Assumptions

1. The primary goal is to move away from Chef InSpec for testing and use Ansible-native testing solutions.
2. The Chef Automate and Chef Server deployment scripts are intended to be replaced with equivalent Ansible functionality.
3. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions.
4. The security requirements specified in the InSpec tests need to be maintained in the Ansible implementation.
5. The repository is primarily for demonstration purposes rather than production use, given its educational nature.
6. No external Chef cookbooks or complex Chef-specific features are in use that would require special migration handling.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.