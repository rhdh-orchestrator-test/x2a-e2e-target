# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

This repository demonstrates Chef InSpec integration with Ansible for compliance automation, along with Chef server deployment scripts. The migration scope is focused on converting all components to pure Ansible while maintaining compliance testing capabilities. Estimated timeline: 1-2 weeks for a small team (2-3 people).

## Module Migration Plan

This repository contains Chef and Ansible technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible-compliance**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of web servers with HTTPS and security hardening
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS configuration, SSL/TLS security testing, Apache web server deployment, POODLE vulnerability mitigation

- **chef-server-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server with user and organization creation
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server setup, user and organization creation, system configuration for Chef Automate

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling TLSv1.2. Migration considerations include maintaining security hardening practices.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with an Ansible-native testing framework.
  
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test that verifies HTTPS functionality and security. Migration considerations include converting to an Ansible-compatible testing framework.
  
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to an Ansible-compatible testing framework.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for infrastructure management.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml as the driver)
- **Cloud Platform**: Not specified, but the deployment scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks:
  - Molecule for Ansible role testing
  - ansible-lint for static code analysis
  - testinfra for infrastructure testing (Python-based alternative to InSpec)
  - Consider maintaining InSpec as a standalone tool if its specific compliance capabilities are required

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing with various drivers (Vagrant, Docker, etc.)
  - ansible-test for Ansible Collection testing

- **Chef Automate/Infra Server (latest)**: Replace with:
  - AWX/Ansible Tower for web-based management
  - Ansible Semaphore for a lightweight alternative
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening in `poodle_fix.yml` that enforces TLSv1.2 and disables vulnerable protocols.
  - Migration approach: Create an Ansible role for Apache security hardening that includes these configurations.

- **Self-signed Certificates**: The current implementation generates self-signed certificates for HTTPS.
  - Migration approach: Use the Ansible `openssl_*` modules as already implemented or consider integrating with Let's Encrypt for production environments.

- **SSH Security**: The InSpec profile `ssh_profile.rb` checks for SSH root login restrictions.
  - Migration approach: Create an Ansible role for SSH hardening that implements these security controls and use ansible-lint or testinfra to verify compliance.

- **Vault/secrets management**: For each module, identified credential patterns:
  - chef-and-ansible-compliance: No credentials detected
  - chef-server-deployment: Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to an Ansible-compatible testing framework while maintaining the same level of compliance validation.
  - Mitigation strategy: Map InSpec resources to testinfra or other testing framework equivalents; consider maintaining InSpec as a standalone tool if necessary.

- **Chef Server Replacement**: Determining the appropriate Ansible management platform to replace Chef Automate/Infra Server functionality.
  - Mitigation strategy: Evaluate AWX/Tower, Semaphore, or CI/CD pipelines based on team requirements and infrastructure scale.

### Migration Order

1. **Ansible Playbooks** (Low risk, high value)
   - `website_https.yml`
   - `poodle_fix.yml`
   - Refactor into proper Ansible roles with variables, templates, and handlers

2. **Testing Framework** (Moderate complexity)
   - Replace Test Kitchen with Molecule
   - Convert InSpec tests to testinfra or maintain as standalone

3. **Chef Server Deployment** (High complexity, dependencies)
   - Replace Chef Automate/Infra Server deployment scripts with Ansible roles
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible rather than being a production deployment.
2. The security tests in InSpec are critical and must be maintained in some form after migration.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure alternatives.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to cloud environments.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will be to pure Ansible without maintaining any Chef components except possibly InSpec if required for specific compliance testing capabilities.