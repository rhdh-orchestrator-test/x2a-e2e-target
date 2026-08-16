# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Migration considerations include replacing Test Kitchen with Ansible-native testing frameworks.
- `index.html`: Static HTML content for the website. No migration needed as it's just content.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider Ansible Lint for static code analysis

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible Playbook integration tests using CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open-source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or Jenkins for pipeline orchestration

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable SSLv3 protocol
  - Maintain proper certificate generation and management

- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login being disabled:
  - Create equivalent Ansible assertions or molecule tests
  - Consider implementing as an Ansible role with both configuration and testing

- **Credentials Management**: 
  - The deployment scripts contain hardcoded credentials that should be moved to Ansible Vault
  - User credentials (username, password) in deploy-automate.sh and deploy-chef-server.sh
  - Consider using ansible-vault for securing these values

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - InSpec has rich resource types that may not have direct equivalents in Ansible
  - Solution: Use Ansible's assert module with command/shell modules to gather the same data
  - For complex tests, consider Python-based testing with pytest-ansible

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow:
  - Test Kitchen provides a structured testing workflow that needs to be replicated
  - Solution: Implement Molecule for similar functionality with Ansible-native approach

- **Chef Server Deployment**: Converting Chef server deployment to Ansible:
  - The deployment scripts set up Chef infrastructure that won't be needed in an Ansible-only environment
  - Solution: Replace with Ansible Automation Platform or AWX deployment playbooks

### Migration Order

1. **website_https.yml and poodle_fix.yml** (low risk, already Ansible): Verify and optimize existing Ansible playbooks
2. **InSpec Tests** (moderate complexity): Convert InSpec tests to Ansible-compatible testing
3. **Test Kitchen Configuration** (moderate complexity): Replace with Molecule or other Ansible testing framework
4. **Chef Deployment Scripts** (high complexity): Replace with Ansible Automation Platform or AWX deployment

### Assumptions

1. The primary goal is to move all testing and automation to Ansible-native solutions
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and can be preserved
3. There is no requirement to maintain backward compatibility with Chef InSpec
4. The deployment scripts for Chef Automate and Chef Infra Server will be replaced with equivalent Ansible automation
5. The target environment will remain Ubuntu 20.04 on Vagrant VMs
6. No external data sources or complex integrations exist beyond what's visible in the repository
7. The security requirements represented in the InSpec tests need to be maintained in the Ansible solution