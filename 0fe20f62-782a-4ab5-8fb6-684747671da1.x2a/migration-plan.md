# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache2, self-signed certificates, and proper SSL configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 configuration, SSL certificate generation, virtual host setup

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook to remediate POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

- **https-compliance-tests**:
    - Description: Chef InSpec tests to verify HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol security checks

- **ssh-security-profile**:
    - Description: Chef InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-infrastructure-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI tools
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file for website deployment - can be preserved as-is or converted to a template
- `README.md`: Documentation files - should be updated to reflect the new Ansible-only approach

### Target Details

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for testing Ansible roles
  - Option 2: Ansible Lint for static analysis
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Convert InSpec tests to Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Collections for content distribution

### Security Considerations

- **SSL/TLS Configuration**: Preserve the security hardening in the Ansible playbooks that disable weak protocols
- **Self-signed Certificates**: Maintain the certificate generation logic, consider enhancing with Let's Encrypt integration
- **SSH Hardening**: Convert the SSH security profile to Ansible security role or include in existing playbooks
- **Credentials in Scripts**: The Chef deployment scripts contain hardcoded credentials that should be moved to Ansible Vault or another secure secret management solution

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the declarative InSpec tests to Ansible's procedural testing approach will require careful mapping of assertions
- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting that will need to be replicated using Ansible and additional tools
- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec; this workflow will need to be redesigned

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Replace with Ansible playbooks for infrastructure setup
4. **Test Kitchen Configuration** (kitchen.yml): Replace with Ansible Molecule or equivalent testing framework

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The existing Ansible playbooks are functioning correctly and don't require significant modifications
3. There are no additional Chef cookbooks or resources not visible in the repository structure
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment scripts are examples and not used in production (due to hardcoded credentials)
6. There is no complex state management or data persistence requirements
7. The team has expertise in both Chef InSpec and Ansible, facilitating knowledge transfer