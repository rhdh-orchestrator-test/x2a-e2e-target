# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most content already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM targets

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
- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH security. Create equivalent Ansible tasks to enforce and verify this configuration.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider using Ansible's crypto modules or integrating with a certificate authority.
- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or another testing framework will require careful mapping of test logic.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible roles.
  - Mitigation: Create dedicated Ansible roles for Chef Automate and Chef Server deployment, or consider migrating to Ansible Automation Platform.

### Migration Order

1. **website_https playbook** (already in Ansible format, just needs review and potential refactoring)
2. **poodle_fix playbook** (already in Ansible format, should be integrated with the main Apache configuration)
3. **InSpec tests** (convert to Ansible-native testing)
4. **Chef deployment scripts** (convert to Ansible roles)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used with Ansible for compliance testing.
2. The deployment scripts are examples and not production-ready code.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will maintain the same functionality but using Ansible-native solutions where possible.
7. The InSpec tests are intended to be run against systems configured by Ansible.
8. The repository does not contain actual Chef cookbooks that need migration, but rather demonstrates Chef InSpec with Ansible.