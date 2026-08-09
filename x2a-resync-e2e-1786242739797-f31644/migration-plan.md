# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository is primarily focused on showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a full infrastructure-as-code implementation. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 days given the limited scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

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
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests port 443 listening, HTTPS response, SSL protocol security

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Verifies SSH root login is disabled, includes STIG references

- **automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-lint for static analysis
  - Option 3: Keep InSpec tests but run them from Ansible using the `inspec` module

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable vulnerable protocols
  - Migration approach: Maintain the same security settings in migrated Ansible playbooks
  - Consider updating to include TLS 1.3 support

- **SSH Security**: InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible assertions or continue using InSpec tests

- **Self-signed Certificates**: The playbook generates self-signed certificates
  - Migration approach: Consider using Ansible's `community.crypto` collection for certificate management
  - Evaluate if Let's Encrypt integration would be beneficial

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or consider keeping InSpec for testing if it provides value

- **Chef Automate/Server Deployment**: The bash scripts deploy Chef infrastructure
  - Mitigation: Determine if Chef infrastructure is still needed or if it should be replaced with Ansible alternatives

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity, requires test framework decision
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The InSpec tests are valuable and should be preserved in some form
3. The Chef Automate and Chef Server deployment may not be needed in an Ansible-only environment
4. The current Ansible playbooks are compatible with Ansible 2.9+ (based on syntax)
5. No external inventory or variable files are being used
6. No complex roles or collections are being used
7. The target environment will continue to be Ubuntu 20.04 or similar
8. Vagrant will continue to be used for development/testing