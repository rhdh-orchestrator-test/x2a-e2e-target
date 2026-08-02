# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Chef Server deployment scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and adapting the Chef InSpec tests to work with Ansible's testing framework. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate_deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require adapting this to use Ansible's native testing tools or Molecule.
- `index.html`: Simple HTML file used as a template for the website. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec but call it from Ansible using the `command` module

- **Test Kitchen with Vagrant**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible's own testing framework

- **Chef Automate/Server Deployment**: Replace with:
  - Ansible playbooks to deploy alternative configuration management or compliance tools

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve:
  - Self-signed certificate generation
  - Proper SSL protocol configuration (TLSv1.2 only)
  - Disabling vulnerable protocols (SSLv3)

- **SSH Security**: The InSpec tests verify SSH security configurations. Migration should:
  - Maintain SSH security checks
  - Implement equivalent controls in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing methodologies.
  - Mitigation: Use Ansible's assert module for simple tests, or consider keeping InSpec for complex compliance testing.

- **Test Kitchen to Molecule**: Adapting the testing workflow from Test Kitchen to Molecule will require configuration changes.
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup.

### Migration Order

1. **website_https.yml** (Priority 1): Convert to an Ansible role with proper structure
   - Create role with tasks, templates, handlers, and defaults
   - Move inline templates to template files
   - Implement variable substitution for configurable values

2. **poodle_fix.yml** (Priority 1): Integrate into the website role or create a separate security role
   - Combine with website_https role if appropriate
   - Implement as idempotent tasks

3. **InSpec Tests** (Priority 2): Convert to Ansible testing framework
   - Create equivalent tests using Ansible's assert module or Molecule
   - Ensure all security checks are maintained

4. **Deployment Scripts** (Priority 3): Replace with Ansible playbooks
   - Create playbooks to deploy alternative configuration management tools
   - Use Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README content.
2. The InSpec tests are intended to verify both the Ansible playbook outcomes and general security compliance.
3. The deployment scripts are used for setting up Chef infrastructure, which may be replaced with alternative tools in the Ansible ecosystem.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the playbooks should be adaptable to other environments.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.