# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of the repository.

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
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment example

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible Assert module for basic validation
  - Option 3: Integration with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration

- **Chef Automate/Infra Server**: Replace with Ansible automation platform (AAP) or other infrastructure management tools:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD for pipeline orchestration
  - Option 3: Jenkins for automation scheduling

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Maintain TLSv1.2 requirement and disable insecure protocols
  - Ensure certificate generation remains secure

- **SSH Hardening**: The SSH security controls in ssh_profile.rb need to be implemented as Ansible tasks
  - Convert the InSpec control to Ansible assert or lineinfile tasks
  - Maintain compliance with referenced security standards (SRG-OS-000112, STIG ID RHEL-08-000227)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Challenge: InSpec provides domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use Ansible assert module with appropriate conditionals or integrate with TestInfra

- **Chef Server Deployment**: Converting Chef server deployment scripts to Ansible
  - Challenge: The deployment scripts use Chef-specific CLI tools that need Ansible equivalents
  - Mitigation: Research Ansible roles for deploying alternative configuration management platforms

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format and only need minor adjustments for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible testing framework
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity as they require complete rewrite as Ansible playbooks and selection of alternative tools

### Assumptions

1. The existing Ansible playbooks are functioning correctly and don't require significant refactoring
2. The organization is moving away from Chef InSpec and Chef Automate/Infra Server completely
3. The security compliance requirements represented in the InSpec tests must be maintained in the Ansible solution
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The deployment scripts are currently used for setting up development/test environments rather than production
6. No external data sources or complex integrations are present in the current implementation
7. The migration will not require changes to the underlying application (Apache web server configuration)