# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef InSpec tests, Ansible playbooks, and Chef deployment scripts that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef InSpec tests used alongside Ansible for compliance automation
2. Ansible playbooks for configuring web servers with HTTPS
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on preserving the compliance testing capabilities while consolidating infrastructure management under Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website-https-compliance**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on web servers
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-compliance**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, CCI compliance checks, STIG validation

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static web content template used in the Ansible playbook. Can be directly migrated to Ansible templates.
- `README.md`: Documentation files that explain the purpose of the repository components.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with OpenSCAP using the ansible-openscap module
  - Option 3: Maintain InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for pipeline automation

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Approach: Convert to Ansible role with appropriate templates and handlers

- **SSH Hardening**: The SSH compliance checks must be maintained
  - Approach: Convert InSpec tests to Ansible assert tasks or OpenSCAP checks

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Hardcoded credentials found in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated dynamically; consider using ansible-vault for storing production certificates

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible-native solutions while maintaining the same level of compliance validation
  - Mitigation: Create custom Ansible modules or use assert modules with detailed output

- **Chef Automate Functionality**: Replacing Chef Automate's compliance reporting capabilities
  - Mitigation: Implement AWX/Tower with custom reporting dashboards or integrate with compliance tools like OpenSCAP

- **Test Automation**: Recreating the Test Kitchen workflow in Ansible
  - Mitigation: Implement Ansible Molecule for testing with similar verification capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Convert to Ansible roles with proper structure
   - Implement idempotency improvements
   - Add better variable management

2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Medium complexity
   - Convert to Ansible assert tasks or OpenSCAP checks
   - Ensure all compliance checks are preserved

3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - High complexity
   - Create Ansible playbooks to deploy AWX/Tower
   - Implement user/organization management in Ansible

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec compliance automation alongside Ansible configuration management
2. The deployment scripts are used for setting up a test/demo environment rather than production systems
3. There are no external dependencies or integrations not visible in the repository
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The compliance checks are based on standard security benchmarks (STIG/CIS)
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There is no complex state management or data persistence requirements
8. The Apache configuration is relatively simple and can be directly migrated to Ansible roles