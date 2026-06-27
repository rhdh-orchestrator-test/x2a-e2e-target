# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

Estimated timeline: 1-2 weeks for a single developer, with most of the effort focused on converting InSpec tests to Ansible testing frameworks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, STIG compliance check

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible-native testing framework configuration.
- `index.html`: Simple HTML file used as a template for website deployment. Can be preserved as-is or converted to an Ansible template.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks that can deploy alternative compliance and configuration management solutions:
  - Option 1: Deploy AWX/Ansible Tower for enterprise Ansible management
  - Option 2: Deploy alternative compliance tools like OpenSCAP or Compliance as Code

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **Self-signed Certificates**: The current implementation generates self-signed certificates; consider enhancing with Let's Encrypt integration
- **SSH Hardening**: The SSH security controls tested by ssh_profile.rb should be implemented as Ansible tasks
- **Credentials Management**: 
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural testing approach will require careful mapping of test assertions
  - Mitigation: Create a library of reusable Ansible test tasks that mirror InSpec resource functionality

- **Compliance Validation**: Ensuring that the migrated solution maintains the same level of compliance validation as the original InSpec tests
  - Mitigation: Create a compliance validation matrix to ensure all original tests have equivalent implementations

- **Chef Server Replacement**: Determining the appropriate replacement for Chef Server functionality
  - Mitigation: Evaluate if full Chef Server replacement is needed or if simpler Ansible inventory management is sufficient

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as these are already in Ansible format and only need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as these require complete rewrite as Ansible playbooks and determination of replacement technologies

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. The security controls implemented are for demonstration purposes and may need enhancement for production use
4. The Chef Automate and Chef Server deployment scripts are intended for lab environments, not production deployments
5. There is no existing Ansible inventory or host management system in place
6. The migration will need to determine if Chef InSpec functionality should be completely replaced or if it can coexist with Ansible in the new implementation
7. No external dependencies or integrations beyond what's explicitly defined in the repository
8. No complex data structures or state management that would complicate migration