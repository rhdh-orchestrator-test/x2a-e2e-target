# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef-related deployment scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, as well as scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (already in Ansible format) and medium complexity for the Chef deployment scripts (need to be converted to Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile to verify SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative configuration management solution

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL configuration is maintained in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL that follows current best practices
  
- **SSH Security**: The InSpec profile checks for SSH root login being disabled.
  - Migration approach: Create an Ansible role that configures SSH securely and includes this check

- **Self-signed Certificates**: The playbook generates self-signed certificates.
  - Migration approach: Create an Ansible role that can either generate self-signed certificates or use Let's Encrypt for production environments

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Use Ansible Vault to securely store credentials

### Technical Challenges

- **InSpec Testing**: The repository uses Chef InSpec for compliance testing.
  - Mitigation: Either continue using InSpec with Ansible or migrate tests to Ansible's native testing capabilities or Molecule

- **Chef Server Deployment**: The bash scripts deploy Chef Server, which won't be needed in an Ansible-only environment.
  - Mitigation: Replace with Ansible Automation Platform deployment or remove if not needed

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to Ansible role with proper structure
   - Update to use Ansible best practices

2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to Ansible role or include in the website_https role
   - Update to use Ansible best practices

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible-compatible testing framework
   - Ensure all compliance checks are maintained

4. **Chef deployment scripts** (high complexity)
   - Convert to Ansible roles for deploying alternative configuration management solution
   - Or remove if Chef infrastructure is no longer needed

### Assumptions

1. The primary goal is to standardize on Ansible and remove Chef dependencies
2. InSpec testing is still desired but should be integrated with Ansible workflow
3. The deployment scripts for Chef Automate/Infra Server may not be needed in the final Ansible implementation
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The security requirements (SSL configuration, SSH hardening) must be maintained in the migrated solution
6. The migration should preserve the demonstration capabilities of the original repository
7. No external dependencies or integrations beyond what's visible in the repository need to be considered