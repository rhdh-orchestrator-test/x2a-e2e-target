# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate compliance automation with Ansible. The migration scope is relatively small, focusing on converting the existing Chef InSpec tests to Ansible-native solutions while maintaining the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository primarily contains Ansible playbooks already, with Chef InSpec tests and Chef server deployment scripts being the main migration targets.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

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
    - Technology: Bash script with Chef commands
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script with Chef commands
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `index.html`: Sample HTML file used in the website deployment. Can be reused as-is in the Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for integration testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-native management solutions

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook specifically addresses SSL security. Ensure this security hardening is maintained in the migrated solution.
  - Migration approach: Keep the existing Ansible task that disables SSLv3 and enables TLSv1.2

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH security configuration.
  - Migration approach: Create an Ansible playbook that both configures and verifies SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native verification methods.
  - Mitigation: Use Ansible assert modules and register variables to perform similar checks

- **Chef Server Deployment**: Replacing Chef Automate/Server deployment with equivalent Ansible management solution.
  - Mitigation: Evaluate AWX/Tower or other Ansible management platforms as replacements

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks for infrastructure deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the README.md.
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and don't require significant changes.
3. There is no dependency on Chef-specific features that cannot be replicated in Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificates approach is acceptable for the migrated solution.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the production environment.
7. There are no external dependencies or integrations not visible in the repository.