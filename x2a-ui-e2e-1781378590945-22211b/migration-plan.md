# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to demonstrate compliance automation. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single engineer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by enforcing TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL/TLS protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (STIG)

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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be preserved as-is or included as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic tests
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Consider Ansible Lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible-compatible management platforms

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 enforcement and disabled SSL3 as implemented in the poodle_fix.yml playbook
- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
- **Self-signed Certificates**: The certificate generation process should be maintained in the Ansible playbook
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected (username/password in both deployment scripts)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting the InSpec tests to equivalent Ansible testing frameworks will require careful mapping of InSpec resources to Ansible modules
  - Mitigation: Create a mapping document for InSpec resources to Ansible equivalents
  
- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with equivalent Ansible functionality
  - Mitigation: Research Ansible AWX/Tower deployment patterns or consider containerized deployment options

- **Test Framework Integration**: Ensuring that the new testing framework integrates well with CI/CD pipelines
  - Mitigation: Set up proof-of-concept with Molecule and CI/CD integration before full migration

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): High complexity, requires replacing Chef-specific functionality

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't require functional changes
2. The InSpec tests are currently being used for compliance validation and their functionality needs to be preserved
3. The deployment scripts are used for setting up Chef infrastructure which may be replaced by Ansible AWX/Tower
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. There are no external dependencies or integrations not visible in the provided files
6. The migration does not need to preserve backward compatibility with Chef InSpec
7. The hardcoded credentials in the deployment scripts are not used in production environments