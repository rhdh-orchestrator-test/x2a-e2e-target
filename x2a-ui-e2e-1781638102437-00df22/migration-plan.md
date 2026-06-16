# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on:

1. Preserving the existing Ansible playbooks (website_https.yml and poodle_fix.yml)
2. Converting Chef InSpec tests to Ansible-compatible testing frameworks
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope and the fact that most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec-website-tests**:
    - Description: Chef InSpec tests that validate HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content validation, SSL protocol security validation

- **inspec-ssh-profile**:
    - Description: Chef InSpec compliance profile for SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used for testing the web server deployment. Can be preserved as-is or incorporated into Ansible as a template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Keep InSpec but run it from Ansible using the `command` module

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible playbooks that configure equivalent monitoring and compliance solutions
  - Consider migrating to AWX/Ansible Tower as a replacement for Chef Automate

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks already handle SSL security configuration. Preserve the SSL hardening in the migration.
- **SSH Security**: The SSH compliance profile checks for secure SSH configuration. Implement equivalent checks in Ansible.
- **Credentials Management**: 
  - The Chef deployment scripts contain hardcoded credentials (username, password) that should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts (username/password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require mapping InSpec resources to Ansible modules or assertions.
  - Mitigation: Create a mapping document for InSpec resources to Ansible equivalents
  - Consider using Ansible's assert module with appropriate conditions

- **Compliance Metadata**: The InSpec SSH profile contains STIG compliance metadata that needs to be preserved.
  - Mitigation: Document compliance requirements separately or use Ansible tags and variables to store compliance metadata

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality.
  - Mitigation: Evaluate AWX/Ansible Tower or other configuration management platforms

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format. May need minor adjustments for best practices.
2. **InSpec Tests**: Convert to Ansible-compatible testing framework.
3. **Chef Deployment Scripts**: Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts.

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The target environment is Ubuntu 20.04 running on Vagrant VMs.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The deployment scripts are examples and not used in production (they contain hardcoded credentials).
5. The migration will preserve the existing functionality while moving entirely to Ansible-based solutions.
6. No specific version requirements exist for Ansible beyond what's compatible with the existing playbooks.
7. The SSH compliance profile is a standalone example and not part of a larger compliance framework.