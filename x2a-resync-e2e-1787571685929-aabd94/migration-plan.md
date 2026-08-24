# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef-related setup scripts. The estimated timeline for migration would be 1-2 weeks, with low complexity as most components are already in Ansible format or are simple shell scripts that can be converted to Ansible roles.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-setup**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-setup**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test file for verifying HTTPS configuration

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the setup scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen with Ansible**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Migration should maintain or improve the security posture:
  - Ensure modern TLS protocols (TLSv1.2+) are enforced
  - Replace self-signed certificates with proper certificate management
  - Maintain security headers and configurations

- **Hardcoded Credentials**: The Chef setup scripts contain hardcoded credentials:
  - In deploy-automate.sh and deploy-chef-server.sh: username, password, email
  - Migration should use Ansible Vault or other secret management solutions

- **Vault/secrets management**:
  - No existing vault implementation detected
  - 1 instance of hardcoded credentials in each setup script

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require additional work
  - Mitigation: Use Molecule with testinfra or Ansible's assert module for similar functionality

- **Chef Server Functionality**: If the Chef Server is being used for actual configuration management, those cookbooks will need to be identified and migrated
  - Mitigation: Conduct a thorough inventory of any Chef cookbooks in use and plan separate migrations for each

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Refactor into proper Ansible roles with variables
   - Update testing framework

2. **Chef Setup Scripts** (deploy-automate.sh, deploy-chef-server.sh): Moderate complexity
   - Convert to Ansible roles for infrastructure setup
   - Implement proper secret management

3. **Testing Framework**: Moderate complexity
   - Replace InSpec tests with equivalent Ansible/Molecule tests

### Assumptions

1. This repository appears to be primarily for demonstration/educational purposes rather than production use, based on the README content and simple examples.

2. The Chef components (Automate, Infra Server) are not managing a large infrastructure and are likely used for demonstration purposes.

3. There are no actual Chef cookbooks to migrate, only setup scripts and Ansible playbooks with InSpec tests.

4. The hardcoded credentials in the setup scripts are example values and not actual production credentials.

5. The migration is focused on standardizing on Ansible rather than maintaining a hybrid Chef/Ansible environment.

6. The InSpec tests are used primarily for demonstration of compliance automation rather than extensive test coverage.

7. No external dependencies or integrations with other systems are present beyond what's explicitly shown in the files.