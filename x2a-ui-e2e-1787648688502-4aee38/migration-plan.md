# MIGRATION FROM ANSIBLE WITH CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a small set of Ansible playbooks with Chef InSpec tests that demonstrate compliance automation. The migration scope is relatively small, focusing on converting existing Ansible playbooks while preserving the compliance testing functionality currently provided by Chef InSpec. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer to complete the migration, including testing and documentation.

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

- **chef-automate-setup**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-setup**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be updated to use Ansible's native testing framework.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration. Will need to be converted to Ansible test format.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Will need to be converted to Ansible test format.
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities or integrate with other testing frameworks like Molecule, TestInfra, or Goss
- **Test Kitchen**: Replace with Ansible's native testing framework or Molecule
- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible management platform

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
- **SSH Security**: The InSpec profile checks for SSH root login restrictions. Ensure these security checks are maintained in the Ansible implementation.
- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider implementing proper certificate management in the migrated solution.
- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - SSL certificate generation and management
  - Consider using Ansible Vault for credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing framework will require careful mapping of test assertions.
- **Chef Automate/Server Setup**: Converting the Chef Automate and Chef Infra Server setup scripts to Ansible playbooks will require understanding of Chef Automate architecture.
- **Compliance Automation**: Ensuring that the compliance automation capabilities provided by InSpec are properly implemented in the Ansible solution.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Automate/Server Setup Scripts** (high complexity, requires understanding of Chef Automate architecture)

### Assumptions

1. The primary goal is to maintain the same functionality while consolidating on Ansible as the single automation tool.
2. The InSpec tests are essential for compliance validation and need equivalent functionality in the Ansible solution.
3. The repository is primarily used for demonstration purposes rather than production deployment.
4. The hardcoded credentials in the setup scripts are for demonstration purposes and will be replaced with proper secret management in the migrated solution.
5. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
6. The migration will include updating documentation to reflect the new Ansible-only approach.
7. The current Test Kitchen setup for testing will be replaced with an appropriate Ansible testing framework.