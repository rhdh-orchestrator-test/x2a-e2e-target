# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance testing. There are also setup scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

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
    - Key Features: Disables SSLv3 and enables only TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH configuration for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance tagging (STIG/CCI)

- **automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or AWX (open-source version of Ansible Tower)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
- **SSH Security**: The InSpec tests check for SSH root login configuration. Ensure this security check is maintained in the migrated tests.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider using Let's Encrypt or other trusted certificate authorities in production.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Consider using Ansible Vault for credential management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions.
  - Mitigation: Use Ansible's assert module or integrate with Molecule for testing.
- **Chef Automate Replacement**: Finding an equivalent for Chef Automate's compliance reporting in Ansible ecosystem.
  - Mitigation: Consider using Ansible Automation Platform or integrating with compliance tools like OpenSCAP.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires replacement with Ansible Automation Platform setup)

### Assumptions

1. The primary goal is to consolidate on Ansible as the sole automation tool, eliminating Chef components.
2. The InSpec tests need to be converted to equivalent Ansible tests or integrated with Ansible-compatible testing frameworks.
3. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible Automation Platform setup.
4. The current setup is used for demonstration/testing purposes rather than production, given the self-signed certificates and simple configurations.
5. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in the migrated solution.
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
7. Test Kitchen will be replaced with Ansible Molecule or similar Ansible-native testing framework.