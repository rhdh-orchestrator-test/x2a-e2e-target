# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on using Chef InSpec for compliance testing alongside Ansible for configuration management. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Security hardening, SSL/TLS configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checking

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks or adapting to use Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible playbooks.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider maintaining InSpec as a separate testing tool that can work with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL/TLS Configuration**: The POODLE fix playbook addresses specific security vulnerabilities. Ensure these security hardening measures are preserved in the migrated Ansible playbooks.
- **SSH Security**: The SSH profile tests for root login restrictions. Ensure these security checks are maintained in the Ansible testing framework.
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates. Consider enhancing security by integrating with Let's Encrypt in the migrated solution.
- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials. Implement Ansible Vault or another secure secret management solution in the migrated playbooks.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible's testing capabilities may require additional modules or external tools. Ansible's built-in testing capabilities are not as comprehensive as InSpec for compliance testing.
  - Mitigation: Consider using a combination of Ansible assertions and external tools like Molecule or maintaining InSpec as a separate testing tool.

- **Chef Automate Deployment**: The Chef Automate and Chef Infra Server deployment scripts need to be converted to Ansible roles or playbooks.
  - Mitigation: Research Ansible Galaxy for existing roles that deploy similar monitoring/management solutions or create custom roles based on the installation steps in the bash scripts.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes, mainly to improve structure and follow best practices.
2. **Testing Framework**: Migrate from Test Kitchen to Molecule and convert InSpec tests to Ansible-compatible testing.
3. **Chef Deployment Scripts**: Convert the bash scripts for Chef Automate and Chef Infra Server deployment to Ansible playbooks.

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components.
2. The InSpec tests need to be converted to equivalent Ansible testing mechanisms.
3. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
4. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained in the migrated solution.
5. The repository appears to be primarily for demonstration/educational purposes rather than production use, based on the README description.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.