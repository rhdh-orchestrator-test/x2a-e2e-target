# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec test profiles to convert. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate the POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests SSH root login configuration for compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and deploys Chef Automate, creates initial user and organization

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Configures system settings, downloads and deploys Chef Infra Server, creates initial user and organization

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/index.html`: Static HTML file used in the website example.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Convert InSpec profiles to equivalent Ansible roles with test tasks

- **Test Kitchen**: Replace with Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  - Option 1: Deploy an alternative configuration management system
  - Option 2: Deploy monitoring and compliance tools that integrate with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure the migrated solution:
  - Continues to disable insecure protocols (SSLv3)
  - Enables only secure protocols (TLSv1.2+)
  - Generates proper self-signed certificates

- **SSH Security**: The InSpec profile checks SSH root login configuration. Ensure the migrated solution:
  - Includes equivalent checks for SSH security
  - Implements remediation for SSH security issues

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or Molecule tests will require careful mapping of test functionality.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules
  - Consider using ansible.builtin.assert or ansible.builtin.fail modules for test assertions

- **Chef Server Deployment**: The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent functionality.
  - Mitigation: Determine if Chef Server is still needed or if it can be replaced entirely with Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, convert to Ansible assertions or Molecule tests
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires architectural decisions about replacement technology

### Assumptions

1. The repository is primarily for demonstration purposes and not a production system
2. The InSpec profiles are used for testing and compliance validation only
3. The deployment scripts are examples and not used in critical production environments
4. The target environment will continue to be Ubuntu-based systems
5. There is no requirement to maintain backward compatibility with Chef components
6. The migration is focused on converting to pure Ansible without maintaining Chef functionality
7. No external systems are dependent on the current implementation
8. The kitchen.yml configuration is only used for testing and not for production deployments