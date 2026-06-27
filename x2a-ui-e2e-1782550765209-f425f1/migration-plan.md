# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server setup scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards (SRG-OS-000112)

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but setup scripts suggest on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test framework

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible automation controller (AWX/Tower) for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Use Ansible's openssl_* modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or use ansible-lint security rules.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated during playbook execution, no pre-existing secrets detected
  - Count of credentials per module:
    - chef-automate-setup: 3 (username, email, password)
    - chef-server-setup: 3 (username, email, password)
    - website_https: 0 (generates certificates during execution)
    - poodle_fix: 0

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation strategy: Use Ansible's assert module for basic checks, and consider ansible-lint for more complex compliance validation.

- **Chef Automate/Server Replacement**: Determining the appropriate replacement for Chef Automate and Chef Infra Server functionality.
  - Mitigation strategy: Evaluate AWX/Tower as a replacement for centralized management, or consider other CI/CD tools depending on specific requirements.

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Convert to roles if appropriate for better organization

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assert tasks or Molecule tests
   - Convert ssh_profile.rb to Ansible assert tasks or ansible-lint rules

3. **Chef Automate/Server Setup Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts for setting up automation infrastructure
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing, not for production deployment.
2. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes during migration.
3. There is no complex integration between Chef and Ansible components beyond what is visible in the repository.
4. The InSpec tests are used primarily for validation and can be replaced with Ansible-native testing mechanisms.
5. The Chef Automate and Chef Infra Server setup scripts are used for demonstration purposes and not part of a larger Chef ecosystem.
6. No external dependencies or integrations are required beyond what is explicitly defined in the repository.
7. The target environment is Ubuntu 20.04 running on Vagrant VMs, as specified in kitchen.yml.