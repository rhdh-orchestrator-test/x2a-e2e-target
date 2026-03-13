# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, primarily involving Chef InSpec tests and Ansible playbooks for a web server configuration. The repository also includes Chef Automate and Chef Infra Server setup scripts. The estimated timeline for migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, STIG compliance check

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec tests but run them from Ansible using the `inspec` command

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening for SSL/TLS:
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable protocols (SSL3, TLS 1.0, TLS 1.1)
  
- **SSH Hardening**: Maintain SSH security controls:
  - Disable root login
  - Preserve STIG compliance requirements

- **Certificate Management**: Ensure proper handling of SSL certificates:
  - Self-signed certificate generation
  - Proper file permissions for certificate files

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Consider using Ansible's assert module or integrating with tools like Molecule

- **Chef Automate/Server Setup**: Replacing Chef infrastructure setup scripts with Ansible equivalents
  - Mitigation: Create Ansible roles for infrastructure setup that achieve the same configuration outcomes

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format, may need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing or integrate InSpec execution from Ansible
3. **Chef Infrastructure Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create equivalent Ansible roles for infrastructure setup

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are intended to validate the configurations applied by the Ansible playbooks
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. No complex state management or data persistence is required
6. No external inventory or variable files are being used
7. The repository is focused on demonstrating compliance automation rather than complex application deployment
8. The Chef Automate and Chef Server setup scripts are included for demonstration purposes and may not need direct migration if the focus is on the compliance testing aspects