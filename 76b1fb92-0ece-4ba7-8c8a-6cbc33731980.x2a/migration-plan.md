# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef setup scripts and Ansible playbooks that need individual migration planning:

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration on the web server
- `tests/ssh_profile.rb`: InSpec test to verify SSH root login is disabled
- `index.html`: Sample HTML file used by the website_https playbook

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Molecule for Ansible role testing
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible roles.
- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the migrated solution.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, consider using Ansible Vault for storing pre-generated certificates

### Technical Challenges

- **InSpec Tests Migration**: Converting InSpec tests to equivalent Ansible assertions or Molecule tests
- **Chef Server Setup**: Replacing Chef Server setup with Ansible Automation Platform or AWX setup

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Already in Ansible format, just need to be converted to roles
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible assertions or Molecule tests
3. Chef Server Setup Scripts (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible roles for setting up Ansible Automation Platform or AWX

### Assumptions

1. The primary goal is to migrate to a pure Ansible solution, eliminating Chef components
2. The InSpec tests need to be preserved in some form for compliance validation
3. The Chef Automate/Infra Server setup needs to be replaced with an equivalent Ansible management solution
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. Vagrant will continue to be used for development/testing environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data structures or state management that would require special handling
8. The security posture defined in the InSpec tests needs to be maintained