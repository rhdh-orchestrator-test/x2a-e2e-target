# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate setup scripts and Ansible playbooks with Chef InSpec tests. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, with only a few Ansible playbooks and Chef InSpec tests to migrate to a pure Ansible solution. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Simple HTML file used for testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing framework or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or other Ansible management solution

### Security Considerations

- **SSL Configuration**: The migration must maintain the secure SSL configuration that disables vulnerable protocols
  - Migration approach: Use Ansible's `lineinfile` or `template` modules to configure SSL settings
  
- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Migration approach: Create equivalent Ansible tasks to enforce SSH security settings and verify compliance

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible checks
  - Mitigation: Use Ansible's assert module or integrate with Molecule for testing
  
- **Chef Automate Deployment**: Replacing Chef Automate deployment with equivalent Ansible management
  - Mitigation: Evaluate Ansible Automation Platform or other Ansible management solutions

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
2. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
3. Chef Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - High complexity

### Assumptions

1. The primary goal is to migrate to pure Ansible without Chef InSpec dependencies
2. The Chef Automate and Chef Server deployment scripts need to be replaced with equivalent Ansible functionality
3. The security compliance testing provided by InSpec needs to be maintained in the Ansible solution
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment will continue to use Vagrant for local testing
6. The hardcoded credentials in the deployment scripts are for testing only and will be replaced with secure credential management