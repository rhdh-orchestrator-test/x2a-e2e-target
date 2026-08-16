# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a pure Ansible solution. The repository appears to be primarily a demonstration/example repository showing how Chef InSpec can be used alongside Ansible for compliance automation, along with scripts for setting up Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec test profiles to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and their straightforward nature.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec profiles that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **website_https_verify**:
    - Description: Chef InSpec profile for verifying HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile for verifying SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Static HTML file for the website. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime verification: Use Ansible assert module or migrate to Molecule for testing
  - Alternative: Keep InSpec as a standalone tool called from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  1. Deploy alternative tools like AWX/Ansible Tower
  2. Or, if Chef Automate is still required, create Ansible playbooks to deploy it

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve:
  - Self-signed certificate generation
  - Protocol security settings (disabling SSLv3, enabling TLSv1.2)
  
- **SSH Security**: The InSpec profile checks SSH root login settings. Migration should include:
  - Equivalent Ansible tasks to verify and enforce SSH security settings
  - Consider using ansible-lint security rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets detected in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible's assert module for basic tests, consider keeping InSpec for complex compliance testing
  
- **Test Kitchen to Molecule**: Adapting the testing workflow
  - Mitigation: Create equivalent Molecule scenarios that match the current Test Kitchen setup

- **Chef Server Deployment**: If Chef Server is still needed in the environment
  - Mitigation: Create Ansible roles to deploy Chef Server or replace with Ansible Tower/AWX

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity, requires conversion to Ansible assertions or Molecule tests
3. Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Higher complexity, requires decisions about infrastructure management approach

### Assumptions

1. The repository is primarily for demonstration/educational purposes and not a production deployment
2. The InSpec profiles are used for validation and could potentially be kept as-is rather than converted
3. The deployment scripts are examples and may not need direct migration if Chef infrastructure is being replaced
4. The target environment will continue to be Ubuntu-based systems
5. There are no external dependencies or integrations not visible in the repository
6. The migration will maintain the same level of security validation currently provided by InSpec
7. Test Kitchen is only used for local development/testing and not in a CI/CD pipeline