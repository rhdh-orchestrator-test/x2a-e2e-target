# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration will involve consolidating these technologies into a pure Ansible solution, leveraging Ansible's native testing capabilities or integrating with other testing frameworks.

The migration complexity is relatively low as the repository contains only a few Ansible playbooks and InSpec tests. The estimated timeline for migration is 1-2 weeks, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment and SSL configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Sample HTML file for the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities:
  - For basic tests: Use Ansible's `assert` module and `register` functionality
  - For more complex compliance testing: Integrate with Ansible Lint or Molecule for testing
  - Alternative: Use pytest-ansible for Python-based testing of Ansible deployments

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Server**: Replace deployment scripts with Ansible playbooks
  - Create Ansible roles for configuration management functions
  - Consider migrating to AWX/Ansible Tower for web UI and automation capabilities

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH security controls tested by the InSpec profile need to be implemented in Ansible
  - Create an Ansible role for SSH hardening that disables root login
  - Implement the same STIG compliance checks using Ansible or an alternative testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification tasks
  - Challenge: InSpec has specific testing constructs that may not have direct equivalents in Ansible
  - Mitigation: Use a combination of Ansible assert modules, custom modules, and potentially external testing frameworks

- **Compliance Validation**: Maintaining the compliance validation capabilities currently provided by InSpec
  - Challenge: Ensuring that all security checks are properly translated to the new testing framework
  - Mitigation: Create a comprehensive test matrix to ensure all compliance checks are covered

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent functionality
  - Challenge: Determining if Chef Server functionality is still needed or can be replaced entirely by Ansible
  - Mitigation: Evaluate current usage of Chef Server and determine if AWX/Tower or another solution is more appropriate

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Review and update for best practices

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, already in Ansible format
   - Review and update for best practices

3. **website_https_verify.rb** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all security checks are maintained

4. **ssh_profile.rb** (moderate complexity)
   - Convert InSpec profile to Ansible role with integrated tests
   - Maintain STIG compliance checks

5. **Chef Server/Automate Deployment Scripts** (high complexity)
   - Evaluate if Chef Server/Automate is still needed
   - If not, remove; if yes, create Ansible playbooks for deployment

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. The security compliance requirements (STIG standards) mentioned in the InSpec tests must be maintained
4. The Chef Server and Automate deployment scripts may be optional components and could potentially be removed if not needed
5. Test Kitchen is used primarily for development/testing and not for production deployments
6. No external dependencies or integrations beyond what's visible in the repository
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure alternatives