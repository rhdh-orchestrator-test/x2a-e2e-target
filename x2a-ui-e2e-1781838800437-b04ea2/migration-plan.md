# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

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
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use ansible-test for more comprehensive testing
  - Option 4: Consider migrating to Ansible's collection-based testing framework

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced
  - Consider adding modern cipher suite configurations
  - Maintain the POODLE vulnerability fix

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure SSH root login remains disabled in the migrated solution
  - Consider adding additional SSH hardening measures

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions:
  - Port checks can use Ansible's wait_for module
  - HTTP response checks can use uri module
  - SSL protocol verification will need custom implementation with openssl_client_cert or command module

- **Chef Automate Deployment**: The bash scripts for Chef Automate and Chef Server deployment will need to be converted to Ansible tasks:
  - Consider whether Chef Automate/Server is still needed or if it should be replaced with Ansible Tower/AWX
  - If keeping Chef components, create idempotent Ansible tasks for installation and configuration

### Migration Order

1. **website_https.yml** (already in Ansible format, just needs review and potential refactoring)
2. **poodle_fix.yml** (already in Ansible format, just needs review and potential refactoring)
3. **InSpec Tests** (convert to Ansible-native testing)
4. **Chef Automate Deployment Scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary goal is to move all functionality to pure Ansible without Chef dependencies
2. The InSpec tests are valuable and should be preserved in some form rather than discarded
3. The deployment scripts for Chef Automate/Server may be optional to migrate if the infrastructure is moving away from Chef
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The self-signed certificates approach is acceptable for the migrated solution
6. No external data sources or inventory systems need to be integrated
7. The hardcoded values in the deployment scripts (hostname, username, password) are placeholders and will be properly secured in the migrated solution