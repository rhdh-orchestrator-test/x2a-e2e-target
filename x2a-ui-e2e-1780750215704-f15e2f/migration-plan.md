# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the small codebase and clear separation of concerns.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website-https-verification**:
    - Description: Chef InSpec test for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh-security-profile**:
    - Description: Chef InSpec test for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for web server deployment

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: Ansible Assert module for in-playbook validation
  - Option 3: Ansible Lint for static analysis

- **Test Kitchen**: Replace with Ansible-native testing frameworks:
  - Option 1: Ansible Molecule for test orchestration
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks for:
  - Option 1: Ansible Tower/AWX deployment
  - Option 2: GitLab CI/CD pipeline configuration

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Convert the existing Ansible playbook to use the Ansible `lineinfile` module instead of `replace`
  - Ensure TLSv1.2 requirement is maintained

- **SSH Security**: The SSH security profile must be maintained
  - Approach: Convert InSpec tests to Ansible assert statements or Molecule verify phase
  - Ensure compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate generation should use Ansible Vault for key storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's `assert` module with appropriate conditionals to replicate InSpec tests
  - Example: Replace `describe port(443) { it { should be_listening } }` with Ansible's `wait_for` module

- **Test Kitchen to Molecule**: Converting Test Kitchen workflow to Ansible Molecule
  - Mitigation: Create equivalent Molecule scenarios that match the Test Kitchen configuration
  - Ensure Vagrant driver is configured similarly

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent infrastructure
  - Mitigation: Evaluate if Chef Server is actually needed or if Ansible can handle all configuration management tasks
  - If needed, create Ansible playbooks to deploy alternative configuration management or compliance tools

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity to convert to Ansible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity, requires architectural decisions

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment
2. The Chef Automate and Chef Server deployment scripts are examples and not critical to the main functionality
3. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
4. Vagrant will continue to be used for development and testing environments
5. The security requirements (TLSv1.2, SSH hardening) must be preserved in any migration
6. No external data sources or complex state management is required
7. The migration is primarily focused on replacing Chef InSpec with Ansible-native testing while preserving the existing Ansible playbooks