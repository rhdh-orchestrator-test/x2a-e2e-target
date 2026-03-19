# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for configuring web servers with HTTPS. The repository also includes Chef Automate and Chef Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible alternatives:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use ansible-test for more comprehensive testing
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for Ansible Collection testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS protocols
  - Approach: Ensure the Ansible playbooks continue to enforce TLSv1.2 and disable older protocols
  
- **SSH Security**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Approach: Create Ansible tasks that configure SSH according to the same security standards

- **Self-signed Certificates**: The current implementation uses self-signed certificates
  - Approach: Maintain the same approach or consider integrating with Let's Encrypt for production environments

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms
  - Mitigation: Use Ansible assert module for basic tests and consider maintaining InSpec for complex compliance testing

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment scripts
  - Mitigation: Create Ansible playbooks that install and configure alternative compliance and configuration management tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates to follow best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing mechanisms
3. **Chef Infrastructure Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires determining replacement infrastructure

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to validate both Chef and Ansible-managed infrastructure
3. There is no complex data or state management that would complicate migration
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The migration will maintain the same level of security compliance checking
6. No external dependencies or integrations beyond what's visible in the repository
7. The self-signed certificates approach is acceptable for the target environment